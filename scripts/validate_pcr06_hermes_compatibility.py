from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from build_pcr06_hermes_compatibility import build_hermes_compatibility

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "hermes-compatibility.yaml"
CONTRACT_PATH = ROOT / "contracts" / "hermes-compatibility-pack.json"
SCHEMA_PATH = ROOT / "schemas" / "hermes-compatibility.schema.json"
PCR05_PATH = ROOT / "contracts" / "runtime-adapter-contracts.json"
DOC_PATH = ROOT / "docs" / "45-PCR-06-HERMES-ADOPTION-AND-COMPATIBILITY-PACK.md"
STATUS_PATH = ROOT / "docs" / "20-DEVELOPMENT-STATUS.md"

Mutation = Callable[[dict[str, Any]], None]


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _set_path(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    cursor: dict[str, Any] = value
    for key in path[:-1]:
        next_value = cursor[key]
        if not isinstance(next_value, dict):
            raise AssertionError(f"Mutation path is not a mapping: {path}")
        cursor = next_value
    cursor[path[-1]] = replacement


def _validate_semantics(contract: dict[str, Any]) -> None:
    adoption = contract["adoption"]
    boundaries = contract["boundaries"]
    readiness = contract["readiness_snapshot"]
    _assert(contract["phase_id"] == "PCR-06", "Phase identity drifted")
    _assert(contract["upstream"]["assessed_release"] == "v0.18.2", "Hermes release pin drifted")
    _assert(contract["upstream"]["update_policy"] == "pinned_review_required", "Unreviewed updates enabled")
    denied_adoption = [
        "installation_authorized",
        "runtime_activation_authorized",
        "production_use_authorized",
        "provider_gateway_authorized",
        "oauth_authorized",
        "messaging_channels_authorized",
        "background_delegation_authorized",
        "autonomous_skill_writes_authorized",
        "autonomous_memory_writes_authorized",
        "yolo_mode_authorized",
        "real_client_data_enabled",
    ]
    _assert(all(adoption[key] is False for key in denied_adoption), "A denied Hermes capability was enabled")
    _assert(boundaries["canonical_write_mode"] == "commands_only", "Command-only writes were weakened")
    _assert(boundaries["runtime_memory_is_canonical"] is False, "Hermes memory became canonical")
    _assert(boundaries["founder_accountability_preserved"] is True, "Founder accountability was removed")
    _assert(readiness["local_prerequisites_passed"] is True, "Local prerequisites do not pass")
    _assert(readiness["hermes_activation_authorized"] is False, "Hermes activation was authorized")
    surfaces = {item["surface_id"]: item for item in contract["compatibility_surfaces"]}
    _assert(len(surfaces) == 4, "Exactly four Hermes compatibility surfaces are required")
    _assert(
        surfaces["HERMES-SURFACE-MEMORY"]["compatibility"] == "incompatible_for_canonical_state",
        "Hermes memory compatibility boundary drifted",
    )
    worker = contract["worker_adapter"]
    _assert(worker["pcr05_adapter_id"] == "hermes-worker-harness", "PCR-05 adapter identity drifted")
    _assert(worker["invocation_mode"] == "foreground", "Background worker execution was enabled")
    _assert(worker["concurrency_limit"] == 1, "Worker concurrency escaped the compatibility boundary")
    required_prohibitions = {
        "background_fanout",
        "autonomous_merge",
        "direct_canonical_write",
        "external_send",
        "yolo_mode",
        "skill_write_without_review",
        "memory_write_without_review",
    }
    _assert(required_prohibitions <= set(worker["prohibited_actions"]), "Worker prohibitions are incomplete")
    mappings = {item["hermes_capability"]: item for item in contract["tool_mapping"]}
    _assert(mappings["mcp"]["offdata_tool_classes"] == [], "MCP was mapped before review")
    _assert(mappings["tool_gateway"]["offdata_tool_classes"] == [], "Tool gateway was mapped before approval")
    _assert(mappings["messaging"]["policy"] == "denied_pre_activation", "Messaging was enabled")
    activation = set(contract["activation_conditions"])
    required_activation = {
        "pcr03_merged_to_main",
        "pcr04_merged_to_main",
        "pcr05_merged_to_main",
        "pcr06_merged_to_main",
        "github_hosted_controls_in_issue_19_verified",
        "explicit_founder_phase_0_approval_received",
        "clean_macos_environment_available",
        "hermes_version_and_checksum_verified",
        "hermes_sandbox_conformance_passed",
    }
    _assert(required_activation == activation, "Hermes activation conditions drifted")


def _mutation_cases() -> list[tuple[str, Mutation]]:
    cases: list[tuple[str, Mutation]] = []

    def add(path: tuple[str, ...], replacement: Any, name: str) -> None:
        def mutate(value: dict[str, Any]) -> None:
            _set_path(value, path, replacement)

        cases.append((name, mutate))

    add(("adoption", "runtime_activation_authorized"), True, "activate runtime")
    add(("adoption", "provider_gateway_authorized"), True, "enable provider gateway")
    add(("adoption", "background_delegation_authorized"), True, "enable background delegation")
    add(("adoption", "autonomous_skill_writes_authorized"), True, "enable autonomous skill writes")
    add(("adoption", "autonomous_memory_writes_authorized"), True, "enable autonomous memory writes")
    add(("adoption", "yolo_mode_authorized"), True, "enable yolo mode")
    add(("adoption", "real_client_data_enabled"), True, "enable real client data")
    add(("boundaries", "runtime_memory_is_canonical"), True, "make memory canonical")
    add(("boundaries", "canonical_write_mode"), "direct", "allow direct writes")
    add(("worker_adapter", "invocation_mode"), "background", "enable background worker")
    add(("worker_adapter", "concurrency_limit"), 8, "raise concurrency")
    add(("upstream", "update_policy"), "automatic", "enable automatic upstream updates")
    add(("readiness_snapshot", "hermes_activation_authorized"), True, "authorize Hermes")

    def remove_activation(value: dict[str, Any]) -> None:
        value["activation_conditions"].remove("hermes_sandbox_conformance_passed")

    def map_mcp(value: dict[str, Any]) -> None:
        for item in value["tool_mapping"]:
            if item["hermes_capability"] == "mcp":
                item["offdata_tool_classes"] = ["external_send"]

    def remove_prohibition(value: dict[str, Any]) -> None:
        value["worker_adapter"]["prohibited_actions"].remove("autonomous_merge")

    cases.extend(
        [
            ("remove sandbox conformance", remove_activation),
            ("map unreviewed MCP", map_mcp),
            ("remove autonomous merge prohibition", remove_prohibition),
        ]
    )
    return cases


def main() -> None:
    source = _load_yaml(SOURCE_PATH)
    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)
    pcr05 = _load_json(PCR05_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(contract), key=lambda item: list(item.path))
    _assert(not errors, "Schema validation failed: " + "; ".join(error.message for error in errors))
    _assert(_canonical_json(build_hermes_compatibility()) == CONTRACT_PATH.read_text(encoding="utf-8"), "Generated Hermes contract is stale")
    _assert(source["contract_id"] == contract["contract_id"], "Source and generated contract IDs differ")
    profiles = {item["adapter_id"]: item for item in pcr05["adapter_profiles"]}
    _assert("hermes-worker-harness" in profiles, "PCR-05 Hermes adapter is missing")
    _assert(profiles["hermes-worker-harness"]["activation_authorized"] is False, "PCR-05 Hermes adapter is active")
    _validate_semantics(contract)
    for token in ["PCR-06", "v0.18.2", "runtime_activation_authorized=false", "skill_manage", "background_fanout"]:
        _assert(token in DOC_PATH.read_text(encoding="utf-8"), f"PCR-06 documentation missing {token}")
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in ["PCR-06", "validate_pcr06_hermes_compatibility.py", "Hermes"]:
        _assert(token in status, f"Development status missing {token}")
    rejected = 0
    for name, mutate in _mutation_cases():
        candidate = copy.deepcopy(contract)
        mutate(candidate)
        try:
            schema_errors = list(validator.iter_errors(candidate))
            if schema_errors:
                rejected += 1
                continue
            _validate_semantics(candidate)
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected += 1
            continue
        raise AssertionError(f"Mutation was not rejected: {name}")
    print(
        "PCR-06 Hermes adoption and compatibility pack passed: "
        f"{len(contract['compatibility_surfaces'])} surfaces, "
        f"{len(contract['tool_mapping'])} capability mappings, "
        f"{contract['readiness_snapshot']['repository_skill_count']} repository skills, "
        f"{rejected} mutation cases rejected, "
        "local_prerequisites_passed=true, hermes_activation_authorized=false."
    )


if __name__ == "__main__":
    main()
