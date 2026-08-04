#!/usr/bin/env python3
"""Validate the complete Phase 1 machine-contract release without external services."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


REQUIREMENT_PATTERN = re.compile(r"^###\s+([A-Z]+-[0-9]{3})\s+—", re.MULTILINE)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return parsed


def read_yaml(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return parsed


def collect_test_nodes(root: Path) -> set[str]:
    nodes: set[str] = set()
    tests_root = root / "packages" / "offdata-core" / "tests"
    for path in sorted(tests_root.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative = path.relative_to(root).as_posix()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                nodes.add(f"{relative}::{node.name}")
    return nodes


def external_schema_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith("../schemas/"):
            refs.add(ref)
        for child in value.values():
            refs.update(external_schema_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(external_schema_refs(child))
    return refs


def main() -> int:
    root = repository_root()
    sys.path.insert(0, str(root / "packages" / "offdata-core" / "src"))

    from offdata_core.command_catalogue import (  # noqa: PLC0415
        build_command_event_catalogue,
    )
    from offdata_core.config_contracts import build_config_schema  # noqa: PLC0415
    from offdata_core.events import CommandType, EventType  # noqa: PLC0415
    from offdata_core.models import DecisionClass, LifecycleStage  # noqa: PLC0415
    from offdata_core.openapi_contract import build_openapi_document  # noqa: PLC0415
    from offdata_core.registry import (  # noqa: PLC0415
        MODEL_REGISTRY,
        build_alias_schema,
        build_model_registry_document,
        build_schema_bundle,
    )

    failures: list[str] = []
    checks: list[str] = []

    generated: dict[Path, dict[str, Any]] = {
        root / "schemas/offdata-contract-bundle.schema.json": build_schema_bundle(),
        root / "schemas/offdata-configs.schema.json": build_config_schema(),
        root / "schemas/agent-envelope.schema.json": build_alias_schema(
            "AgentEnvelope", "agent-envelope.schema.json", "Offdata Agent Envelope"
        ),
        root / "schemas/context-package.schema.json": build_alias_schema(
            "ContextPackage",
            "context-package.schema.json",
            "Offdata Minimum-Sufficient Context Package",
        ),
        root / "schemas/founder-decision-packet.schema.json": build_alias_schema(
            "FounderDecisionPacket",
            "founder-decision-packet.schema.json",
            "Offdata Founder Decision Packet",
        ),
        root / "contracts/model-registry.json": build_model_registry_document(),
        root / "contracts/command-event-catalogue.json": build_command_event_catalogue(),
        root / "api/openapi.json": build_openapi_document(),
    }
    for path, expected in generated.items():
        try:
            actual = read_json(path)
            if actual != expected:
                failures.append(f"Generated contract is stale: {path.relative_to(root)}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"Cannot validate {path.relative_to(root)}: {exc}")
    checks.append(f"generated_contracts={len(generated)}")

    try:
        bundle = read_json(root / "schemas/offdata-contract-bundle.schema.json")
        Draft202012Validator.check_schema(bundle)
        if not set(MODEL_REGISTRY) <= set(bundle.get("$defs", {})):
            failures.append("Schema bundle does not contain every registered Pydantic model.")
        checks.append(f"registered_models={len(MODEL_REGISTRY)}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"Schema bundle validation failed: {exc}")
        bundle = {"$defs": {}}

    try:
        config_schema = read_json(root / "schemas/offdata-configs.schema.json")
        Draft202012Validator.check_schema(config_schema)
        config_targets = {
            root / "configs/lifecycle.yaml": "LifecycleConfig",
            root / "configs/policy.yaml": "PolicyConfig",
            root / "configs/agents.yaml": "AgentsConfig",
            root / "requirements/test-registry.json": "TestRegistry",
        }
        for path, definition in config_targets.items():
            document = read_json(path) if path.suffix == ".json" else read_yaml(path)
            validation_schema = {
                "$schema": config_schema["$schema"],
                "$defs": config_schema["$defs"],
                "$ref": f"#/$defs/{definition}",
            }
            Draft202012Validator(validation_schema).validate(document)
        checks.append(f"validated_configs={len(config_targets)}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"Configuration validation failed: {exc}")

    try:
        lifecycle = read_yaml(root / "configs/lifecycle.yaml")
        stage_ids = [stage["id"] for stage in lifecycle["stages"]]
        if stage_ids != [stage.value for stage in LifecycleStage]:
            failures.append("Lifecycle YAML stage order differs from Python LifecycleStage.")
        policy = read_yaml(root / "configs/policy.yaml")
        if set(policy["decision_classes"]) != {item.value for item in DecisionClass}:
            failures.append("Policy YAML decision classes differ from Python DecisionClass.")
        agents = read_yaml(root / "configs/agents.yaml")
        if len(agents["agents"]) != 11:
            failures.append("Agent config must contain exactly eleven bounded roles.")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"Configuration coherence failed: {exc}")

    try:
        openapi = read_json(root / "api/openapi.json")
        if not str(openapi.get("openapi", "")).startswith("3.1."):
            failures.append("OpenAPI contract is not version 3.1.x.")
        definitions = set(bundle["$defs"])
        for ref in external_schema_refs(openapi):
            definition = ref.split("#/$defs/", maxsplit=1)[1]
            if definition not in definitions:
                failures.append(f"Unresolved OpenAPI schema definition: {definition}")
        checks.append(f"openapi_paths={len(openapi.get('paths', {}))}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"OpenAPI validation failed: {exc}")

    try:
        catalogue = read_json(root / "contracts/command-event-catalogue.json")
        if set(catalogue["commands"]) != {item.value for item in CommandType}:
            failures.append("Command catalogue does not cover the CommandType enum.")
        if set(catalogue["events"]) != {item.value for item in EventType}:
            failures.append("Event catalogue does not cover the EventType enum.")
        checks.append(f"commands={len(catalogue['commands'])}")
        checks.append(f"events={len(catalogue['events'])}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"Command/event catalogue validation failed: {exc}")

    try:
        registry = read_json(root / "requirements/test-registry.json")
        mapped_nodes = {item["node_id"] for item in registry["implemented_tests"]}
        collected_nodes = collect_test_nodes(root)
        unmapped = sorted(collected_nodes - mapped_nodes)
        stale_mappings = sorted(mapped_nodes - collected_nodes)
        if unmapped:
            failures.append(f"Executable tests missing requirement mappings: {unmapped}")
        if stale_mappings:
            failures.append(f"Test registry contains stale executable nodes: {stale_mappings}")

        catalogue_text = (root / "docs/16-REQUIREMENTS-CATALOGUE.md").read_text(
            encoding="utf-8"
        )
        catalogue_requirements = set(REQUIREMENT_PATTERN.findall(catalogue_text))
        mapped_requirements = {
            requirement
            for test in registry["implemented_tests"] + registry["planned_tests"]
            for requirement in test["requirements"]
        }
        missing_requirements = sorted(catalogue_requirements - mapped_requirements)
        unknown_requirements = sorted(mapped_requirements - catalogue_requirements)
        if missing_requirements:
            failures.append(
                "Requirements without implemented or planned test: "
                f"{missing_requirements}"
            )
        if unknown_requirements:
            failures.append(
                f"Test registry references unknown requirements: {unknown_requirements}"
            )
        checks.append(f"catalogue_requirements={len(catalogue_requirements)}")
        checks.append(f"implemented_tests={len(registry['implemented_tests'])}")
        checks.append(f"planned_tests={len(registry['planned_tests'])}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"Traceability validation failed: {exc}")

    try:
        migration = (root / "database/migrations/0001_core.sql").read_text(encoding="utf-8")
        lower = migration.lower()
        required_sql = (
            "begin;",
            "commit;",
            "create table tenants",
            "create table engagements",
            "create table commands",
            "create table domain_events",
            "create table idempotency_records",
            "enable row level security",
            "create policy",
        )
        for statement in required_sql:
            if statement not in lower:
                failures.append(f"Migration is missing required SQL marker: {statement}")
        checks.append(f"migration_lines={len(migration.splitlines())}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"Migration static validation failed: {exc}")

    if failures:
        print("PHASE 1 CONTRACT VALIDATION FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("PHASE 1 CONTRACT VALIDATION PASSED")
    for check in checks:
        print(f"- {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
