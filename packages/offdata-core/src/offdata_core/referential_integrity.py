"""Semantic test identity and governed referential-integrity controls.

PCR-02 keeps semantic test identifiers stable when executable evidence is added,
and validates the governed identifier graph without granting new authority.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


REQUIREMENT_PATTERN = re.compile(r"^###\s+([A-Z]+-[0-9]{3})\s+—", re.MULTILINE)
IDENTIFIER_PATTERN = r"^[A-Z0-9]+(?:-[A-Z0-9]+)+-[0-9]{3}$"


class FrozenModel(BaseModel):
    """Strict immutable base model for governed identity records."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class TestImplementation(FrozenModel):
    """Executable evidence implementing one semantic test identity."""

    node_id: str = Field(min_length=3)
    environment: Literal["chat_first_python"]
    evidence_status: Literal["executable"] = "executable"


class SemanticTestDefinition(FrozenModel):
    """Stable test identity independent of any particular executable node path."""

    test_id: str = Field(pattern=IDENTIFIER_PATTERN)
    title: str = Field(min_length=3)
    kind: str = Field(min_length=2)
    source_kinds: tuple[str, ...]
    execution_stages: tuple[str, ...]
    requirement_ids: tuple[str, ...]
    control_ids: tuple[str, ...] = ()
    threat_ids: tuple[str, ...] = ()
    status: Literal["planned", "partially_implemented", "implemented", "retired"]
    implementations: tuple[TestImplementation, ...] = ()
    expected_result: str | None = None
    mandatory_for_real_client_data: bool = False
    sources: tuple[str, ...]

    @model_validator(mode="after")
    def validate_evidence_state(self) -> SemanticTestDefinition:
        for field_name, values in (
            ("source_kinds", self.source_kinds),
            ("execution_stages", self.execution_stages),
            ("requirement_ids", self.requirement_ids),
            ("control_ids", self.control_ids),
            ("threat_ids", self.threat_ids),
            ("sources", self.sources),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"Semantic test {self.test_id} has duplicate {field_name}.")
        node_ids = [item.node_id for item in self.implementations]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError(f"Semantic test {self.test_id} has duplicate implementations.")
        if self.status == "implemented" and not self.implementations:
            raise ValueError(f"Implemented semantic test {self.test_id} requires evidence.")
        if self.status in {"planned", "retired"} and self.implementations:
            raise ValueError(f"{self.status} semantic test {self.test_id} cannot claim evidence.")
        if self.status == "partially_implemented" and not self.implementations:
            raise ValueError(f"Partially implemented test {self.test_id} requires evidence.")
        return self


class SemanticTestCounts(FrozenModel):
    total: int = Field(gt=0)
    implemented: int = Field(ge=0)
    partially_implemented: int = Field(ge=0)
    planned: int = Field(ge=0)
    retired: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_total(self) -> SemanticTestCounts:
        subtotal = self.implemented + self.partially_implemented + self.planned + self.retired
        if subtotal != self.total:
            raise ValueError("Semantic test status counts do not reconcile.")
        return self


class SemanticTestRules(FrozenModel):
    semantic_identity_survives_status_change: Literal[True]
    completed_ids_require_executable_evidence: Literal[True]
    planned_tests_do_not_claim_execution_evidence: Literal[True]
    evidence_nodes_must_exist: Literal[True]
    evidence_nodes_must_share_a_requirement: Literal[True]
    threat_test_references_must_resolve: Literal[True]
    retired_tests_cannot_be_referenced: Literal[True]


class SemanticTestRegistryBody(FrozenModel):
    version: Literal["1.0.0"]
    status: Literal["governed_chat_first"]
    rules: SemanticTestRules
    counts: SemanticTestCounts
    tests: tuple[SemanticTestDefinition, ...]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> SemanticTestRegistryBody:
        ids = [item.test_id for item in self.tests]
        if ids != sorted(ids):
            raise ValueError("Semantic tests must be sorted by test_id.")
        if len(ids) != len(set(ids)):
            raise ValueError("Semantic test IDs must be unique.")
        return self


class SemanticTestRegistry(SemanticTestRegistryBody):
    registry_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class TestEvidenceBinding(FrozenModel):
    node_id: str = Field(min_length=3)
    environment: Literal["chat_first_python"]


class TestDefinitionSourceConfig(FrozenModel):
    version: Literal["1.0.0"]
    status: Literal["governed_chat_first"]
    sources: dict[str, str]
    rules: SemanticTestRules
    implementation_evidence: dict[str, tuple[TestEvidenceBinding, ...]]


class ReferenceEdge(FrozenModel):
    source_kind: str = Field(min_length=2)
    source_id: str = Field(min_length=2)
    relation: str = Field(min_length=2)
    target_kind: str = Field(min_length=2)
    target_id: str = Field(min_length=2)


class ReferentialIntegrityCounts(FrozenModel):
    requirements: int = Field(gt=0)
    semantic_tests: int = Field(gt=0)
    implemented_semantic_tests: int = Field(ge=0)
    planned_semantic_tests: int = Field(ge=0)
    executable_test_nodes: int = Field(gt=0)
    controls: int = Field(gt=0)
    threats: int = Field(gt=0)
    playbooks: int = Field(gt=0)
    agents: int = Field(gt=0)
    commands: int = Field(gt=0)
    events: int = Field(gt=0)
    fixtures: int = Field(gt=0)
    sources: int = Field(gt=0)
    aliases: int = Field(gt=0)
    edges: int = Field(gt=0)


class ReferentialIntegrityReportBody(FrozenModel):
    version: Literal["1.0.0"]
    status: Literal["pass"]
    rules: dict[str, bool]
    counts: ReferentialIntegrityCounts
    edges: tuple[ReferenceEdge, ...]
    issues: tuple[str, ...]

    @model_validator(mode="after")
    def validate_pass(self) -> ReferentialIntegrityReportBody:
        if self.issues:
            raise ValueError("Passing referential-integrity report cannot contain issues.")
        if len(self.edges) != self.counts.edges:
            raise ValueError("Referential-integrity edge count does not reconcile.")
        return self


class ReferentialIntegrityReport(ReferentialIntegrityReportBody):
    report_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _yaml_object(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return value


def _string_tuple(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Expected string list for {label}.")
    return tuple(value)


def _record_list(document: dict[str, Any], key: str, path: Path) -> list[dict[str, Any]]:
    value = document.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"Expected object list {key} in {path}.")
    return value


def _unique_records(records: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        identifier = record.get(key)
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"Missing {label} identifier.")
        if identifier in result:
            raise ValueError(f"Duplicate {label} identifier: {identifier}")
        result[identifier] = record
    return result


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def collect_executable_test_nodes(root: Path) -> set[str]:
    """Collect all top-level pytest functions using their stable node paths."""

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


def load_implemented_node_requirements(root: Path) -> dict[str, tuple[str, ...]]:
    """Load every executable-node-to-requirement mapping."""

    merged: dict[str, tuple[str, ...]] = {}
    for path in sorted((root / "requirements").glob("implemented-test-mappings*.json")):
        document = _json_object(path)
        for node_id, raw_requirements in document.items():
            requirements = _string_tuple(raw_requirements, f"requirements for {node_id}")
            if node_id in merged:
                raise ValueError(f"Duplicate executable test mapping: {node_id}")
            merged[node_id] = requirements
    return merged


def load_completed_semantic_test_ids(root: Path) -> set[str]:
    """Load semantic tests that have transitioned from planned to implemented."""

    completed: set[str] = set()
    for path in sorted((root / "requirements").glob("completed-planned-tests*.json")):
        values = _json_object(path).get("completed_test_ids")
        ids = _string_tuple(values, f"completed_test_ids in {path}")
        overlap = completed.intersection(ids)
        if overlap:
            raise ValueError(f"Duplicate completed semantic test IDs: {sorted(overlap)}")
        completed.update(ids)
    return completed


def load_test_definition_config(root: Path) -> TestDefinitionSourceConfig:
    """Load PCR-02 test identity and executable-evidence bindings."""

    return TestDefinitionSourceConfig.model_validate(
        _yaml_object(root / "requirements" / "test-definitions.yaml")
    )


def _initial_test_seeds(root: Path) -> dict[str, dict[str, Any]]:
    planned = _json_object(root / "requirements" / "planned-test-mappings.json")
    seeds: dict[str, dict[str, Any]] = {}
    for test_id, raw in planned.items():
        if not isinstance(raw, dict):
            raise ValueError(f"Invalid planned semantic test: {test_id}")
        seeds[test_id] = {
            "test_id": test_id,
            "title": test_id,
            "kind": str(raw.get("kind", "unknown")),
            "source_kinds": {str(raw.get("kind", "unknown"))},
            "execution_stages": {str(raw.get("phase", "unknown"))},
            "requirement_ids": set(_string_tuple(raw.get("requirements"), test_id)),
            "control_ids": set(),
            "threat_ids": set(),
            "expected_result": None,
            "mandatory_for_real_client_data": False,
            "sources": {"requirements/planned-test-mappings.json"},
        }

    security_path = root / "security" / "security-test-catalogue.yaml"
    security_tests = _record_list(_yaml_object(security_path), "tests", security_path)
    for record in security_tests:
        security_test_id = record.get("test_id")
        if not isinstance(security_test_id, str):
            raise ValueError("Security test is missing test_id.")
        kind = str(record.get("kind", "unknown"))
        stage = str(record.get("execution_stage", "unknown"))
        requirements = set(_string_tuple(record.get("requirement_ids"), security_test_id))
        controls = set(_string_tuple(record.get("control_ids"), security_test_id))
        seed = seeds.setdefault(
            security_test_id,
            {
                "test_id": test_id,
                "title": str(record.get("title", test_id)),
                "kind": kind,
                "source_kinds": set(),
                "execution_stages": set(),
                "requirement_ids": set(),
                "control_ids": set(),
                "threat_ids": set(),
                "expected_result": None,
                "mandatory_for_real_client_data": False,
                "sources": set(),
            },
        )
        seed["title"] = str(record.get("title", test_id))
        seed["kind"] = kind
        seed["source_kinds"].add(kind)
        seed["execution_stages"].add(stage)
        seed["requirement_ids"].update(requirements)
        seed["control_ids"].update(controls)
        seed["expected_result"] = str(record.get("expected_result", "")) or None
        seed["mandatory_for_real_client_data"] = bool(
            record.get("mandatory_for_real_client_data", False)
        )
        seed["sources"].add("security/security-test-catalogue.yaml")

    threat_path = root / "security" / "threat-model.yaml"
    threats = _record_list(_yaml_object(threat_path), "threats", threat_path)
    for threat in threats:
        threat_id = threat.get("threat_id")
        if not isinstance(threat_id, str):
            raise ValueError("Threat is missing threat_id.")
        for test_id in _string_tuple(threat.get("test_ids"), threat_id):
            if test_id not in seeds:
                raise ValueError(
                    f"Unknown or wrong-kind test reference {test_id} from threat {threat_id}."
                )
            seeds[test_id]["threat_ids"].add(threat_id)
    return seeds


def build_semantic_test_registry(root: Path) -> SemanticTestRegistry:
    """Build the deterministic semantic test registry."""

    config = load_test_definition_config(root)
    seeds = _initial_test_seeds(root)
    completed = load_completed_semantic_test_ids(root)
    unknown_completed = sorted(completed.difference(seeds))
    if unknown_completed:
        raise ValueError(f"Completed semantic tests are undefined: {unknown_completed}")

    nodes = collect_executable_test_nodes(root)
    node_requirements = load_implemented_node_requirements(root)
    evidence_ids = set(config.implementation_evidence)
    security_path = root / "security" / "security-test-catalogue.yaml"
    security_tests = _record_list(_yaml_object(security_path), "tests", security_path)
    chat_first_security = {
        str(item["test_id"])
        for item in security_tests
        if item.get("execution_stage") == "chat_first"
    }
    implemented_ids = completed | chat_first_security
    missing_evidence = sorted(implemented_ids - evidence_ids)
    extra_evidence = sorted(evidence_ids - implemented_ids)
    if missing_evidence:
        raise ValueError(f"Implemented semantic tests lack evidence: {missing_evidence}")
    if extra_evidence:
        raise ValueError(f"Evidence is attached to non-implemented tests: {extra_evidence}")

    definitions: list[SemanticTestDefinition] = []
    for test_id in sorted(seeds):
        seed = seeds[test_id]
        status: Literal["planned", "implemented"] = (
            "implemented" if test_id in implemented_ids else "planned"
        )
        implementations: list[TestImplementation] = []
        for binding in config.implementation_evidence.get(test_id, ()):
            if binding.node_id not in nodes:
                raise ValueError(
                    f"Semantic test {test_id} references missing node {binding.node_id}."
                )
            if binding.node_id not in node_requirements:
                raise ValueError(
                    f"Semantic test {test_id} references unmapped node {binding.node_id}."
                )
            shared = set(seed["requirement_ids"]).intersection(node_requirements[binding.node_id])
            if not shared:
                raise ValueError(
                    f"Semantic test {test_id} and node {binding.node_id} share no requirement."
                )
            implementations.append(
                TestImplementation(node_id=binding.node_id, environment=binding.environment)
            )
        definitions.append(
            SemanticTestDefinition(
                test_id=test_id,
                title=str(seed["title"]),
                kind=str(seed["kind"]),
                source_kinds=tuple(sorted(seed["source_kinds"])),
                execution_stages=tuple(sorted(seed["execution_stages"])),
                requirement_ids=tuple(sorted(seed["requirement_ids"])),
                control_ids=tuple(sorted(seed["control_ids"])),
                threat_ids=tuple(sorted(seed["threat_ids"])),
                status=status,
                implementations=tuple(implementations),
                expected_result=seed["expected_result"],
                mandatory_for_real_client_data=bool(seed["mandatory_for_real_client_data"]),
                sources=tuple(sorted(seed["sources"])),
            )
        )

    counts = SemanticTestCounts(
        total=len(definitions),
        implemented=sum(item.status == "implemented" for item in definitions),
        partially_implemented=0,
        planned=sum(item.status == "planned" for item in definitions),
        retired=0,
    )
    body = SemanticTestRegistryBody(
        version="1.0.0",
        status="governed_chat_first",
        rules=config.rules,
        counts=counts,
        tests=tuple(definitions),
    )
    return SemanticTestRegistry.model_validate(
        {**body.model_dump(mode="json"), "registry_digest": _digest(body.model_dump(mode="json"))}
    )


def semantic_test_registry_document(root: Path) -> dict[str, Any]:
    return build_semantic_test_registry(root).model_dump(mode="json")


def write_semantic_test_registry(root: Path, destination: Path | None = None) -> Path:
    target = destination or root / "requirements" / "test-definitions.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(semantic_test_registry_document(root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def verify_semantic_test_registry(root: Path, committed: Path | None = None) -> None:
    target = committed or root / "requirements" / "test-definitions.json"
    expected = json.dumps(semantic_test_registry_document(root), indent=2, sort_keys=True) + "\n"
    if target.read_text(encoding="utf-8") != expected:
        raise ValueError("Committed semantic test registry is stale or modified.")


def _requirement_ids(root: Path) -> set[str]:
    text = (root / "docs" / "16-REQUIREMENTS-CATALOGUE.md").read_text(encoding="utf-8")
    return set(REQUIREMENT_PATTERN.findall(text))


def _add_edge(
    edges: set[tuple[str, str, str, str, str]],
    source_kind: str,
    source_id: str,
    relation: str,
    target_kind: str,
    target_id: str,
) -> None:
    edges.add((source_kind, source_id, relation, target_kind, target_id))


def build_referential_integrity_report(root: Path) -> ReferentialIntegrityReport:
    """Validate the governed identifier graph and return a deterministic pass report."""

    registry = build_semantic_test_registry(root)
    requirements = _requirement_ids(root)
    tests = {item.test_id: item for item in registry.tests}
    nodes = collect_executable_test_nodes(root)
    edges: set[tuple[str, str, str, str, str]] = set()

    control_path = root / "security" / "security-control-catalogue.yaml"
    controls = _unique_records(
        _record_list(_yaml_object(control_path), "controls", control_path),
        "control_id",
        "control",
    )
    playbook_path = root / "security" / "incident-playbooks.yaml"
    playbooks = _unique_records(
        _record_list(_yaml_object(playbook_path), "playbooks", playbook_path),
        "playbook_id",
        "playbook",
    )
    threat_path = root / "security" / "threat-model.yaml"
    threats = _unique_records(
        _record_list(_yaml_object(threat_path), "threats", threat_path),
        "threat_id",
        "threat",
    )

    for test in registry.tests:
        for requirement_id in test.requirement_ids:
            if requirement_id not in requirements:
                raise ValueError(
                    f"Semantic test {test.test_id} references unknown requirement {requirement_id}."
                )
            _add_edge(edges, "test", test.test_id, "verifies", "requirement", requirement_id)
        for control_id in test.control_ids:
            if control_id not in controls:
                raise ValueError(
                    f"Semantic test {test.test_id} references unknown control {control_id}."
                )
            _add_edge(edges, "test", test.test_id, "verifies", "control", control_id)

    for control_id, record in controls.items():
        for requirement_id in _string_tuple(record.get("requirements"), control_id):
            if requirement_id not in requirements:
                raise ValueError(
                    f"Control {control_id} references unknown requirement {requirement_id}."
                )
            _add_edge(edges, "control", control_id, "implements", "requirement", requirement_id)

    referenced_tests: set[str] = set()
    covered_controls: set[str] = set()
    for threat_id, threat in threats.items():
        preventive = _string_tuple(threat.get("preventive_controls"), threat_id)
        detective = _string_tuple(threat.get("detective_controls"), threat_id)
        for relation, values in (("prevented_by", preventive), ("detected_by", detective)):
            for control_id in values:
                if control_id not in controls:
                    raise ValueError(f"Threat {threat_id} references unknown control {control_id}.")
                covered_controls.add(control_id)
                _add_edge(edges, "threat", threat_id, relation, "control", control_id)
        playbook_id = threat.get("response_playbook_id")
        if not isinstance(playbook_id, str) or playbook_id not in playbooks:
            raise ValueError(f"Threat {threat_id} references unknown playbook {playbook_id}.")
        _add_edge(edges, "threat", threat_id, "responded_by", "playbook", playbook_id)
        for test_id in _string_tuple(threat.get("test_ids"), threat_id):
            if test_id not in tests:
                raise ValueError(
                    f"Threat {threat_id} references unknown or wrong-kind test {test_id}."
                )
            if tests[test_id].status == "retired":
                raise ValueError(f"Threat {threat_id} references retired test {test_id}.")
            referenced_tests.add(test_id)
            _add_edge(edges, "threat", threat_id, "tested_by", "test", test_id)

    covered_controls.update(
        control_id for test in registry.tests for control_id in test.control_ids
    )
    mandatory_controls = {
        control_id
        for control_id, record in controls.items()
        if record.get("mandatory_for_real_client_data") is True
    }
    uncovered_mandatory = sorted(mandatory_controls - covered_controls)
    if uncovered_mandatory:
        raise ValueError(f"Mandatory controls lack governed test coverage: {uncovered_mandatory}")
    if not referenced_tests:
        raise ValueError("Threat model does not reference any semantic tests.")

    agents_document = _yaml_object(root / "configs" / "agents.yaml")
    agent_records = _record_list(agents_document, "agents", root / "configs" / "agents.yaml")
    agents = _unique_records(agent_records, "agent_id", "agent")
    for requirement_id in _string_tuple(agents_document.get("source_requirements"), "agents"):
        if requirement_id not in requirements:
            raise ValueError(f"Agent configuration references unknown requirement {requirement_id}.")
        _add_edge(edges, "agent_system", "offdata-agents", "implements", "requirement", requirement_id)
    for agent_id, record in agents.items():
        skill_path = record.get("skill_package")
        if not isinstance(skill_path, str) or not (root / skill_path).is_file():
            raise ValueError(f"Agent {agent_id} references missing skill package {skill_path}.")
        _add_edge(edges, "agent", agent_id, "defined_by", "skill", skill_path)

    catalogue = _json_object(root / "contracts" / "command-event-catalogue.json")
    command_raw = catalogue.get("commands")
    event_raw = catalogue.get("events")
    if not isinstance(command_raw, dict) or not isinstance(event_raw, dict):
        raise ValueError("Command/event catalogue must contain object catalogues.")
    commands = set(command_raw)
    events = set(event_raw)
    if not commands or not events:
        raise ValueError("Command/event catalogues cannot be empty.")
    for command_id, command in command_raw.items():
        if not isinstance(command, dict):
            raise ValueError(f"Command {command_id} must be an object.")
        for requirement_id in _string_tuple(command.get("requirements"), command_id):
            if requirement_id not in requirements:
                raise ValueError(
                    f"Command {command_id} references unknown requirement {requirement_id}."
                )
            _add_edge(edges, "command", command_id, "implements", "requirement", requirement_id)
        for relation, field in (("emits_success", "success_events"), ("emits_failure", "failure_events")):
            for event_id in _string_tuple(command.get(field), f"{command_id}.{field}"):
                if event_id not in events:
                    raise ValueError(f"Command {command_id} references unknown event {event_id}.")
                _add_edge(edges, "command", command_id, relation, "event", event_id)

    fixture_document = _yaml_object(root / "fixtures" / "manifest.yaml")
    fixture_records = _record_list(
        fixture_document, "primary_engagements", root / "fixtures" / "manifest.yaml"
    ) + _record_list(
        fixture_document, "compound_engagements", root / "fixtures" / "manifest.yaml"
    )
    fixtures = _unique_records(fixture_records, "id", "fixture")
    primary_types: set[str] = set()
    for record in _record_list(
        fixture_document, "primary_engagements", root / "fixtures" / "manifest.yaml"
    ):
        fixture_id = str(record["id"])
        engagement_type = record.get("type")
        if not isinstance(engagement_type, str) or not engagement_type:
            raise ValueError(f"Primary fixture {fixture_id} is missing its engagement type.")
        if engagement_type in primary_types:
            raise ValueError(f"Duplicate primary engagement type: {engagement_type}")
        primary_types.add(engagement_type)
        _add_edge(edges, "fixture", fixture_id, "covers", "engagement_type", engagement_type)
    for record in _record_list(
        fixture_document, "compound_engagements", root / "fixtures" / "manifest.yaml"
    ):
        fixture_id = str(record["id"])
        for engagement_type in _string_tuple(record.get("domains"), fixture_id):
            if engagement_type not in primary_types:
                raise ValueError(
                    f"Compound fixture {fixture_id} references unknown engagement type "
                    f"{engagement_type}."
                )
            _add_edge(
                edges, "fixture", fixture_id, "combines", "engagement_type", engagement_type
            )

    source_document = _yaml_object(root / "knowledge" / "source-manifest.yaml")
    source_records = _record_list(
        source_document, "canonical_core_sources", root / "knowledge" / "source-manifest.yaml"
    ) + _record_list(
        source_document, "domain_methodology_sources", root / "knowledge" / "source-manifest.yaml"
    )
    sources = _unique_records(source_records, "source_id", "source")
    alias_document = _yaml_object(root / "knowledge" / "alias-map.yaml")
    alias_records = _record_list(alias_document, "aliases", root / "knowledge" / "alias-map.yaml")
    alias_pairs: set[tuple[str, str]] = set()
    for record in alias_records:
        alias = record.get("alias")
        target = record.get("resolves_to_source_id")
        if not isinstance(alias, str) or not alias:
            raise ValueError("Source alias is missing its alias value.")
        if not isinstance(target, str) or target not in sources:
            raise ValueError(f"Alias {alias} references unknown source {target}.")
        pair = (alias, target)
        if pair in alias_pairs:
            raise ValueError(f"Duplicate source alias rule: {alias} -> {target}")
        alias_pairs.add(pair)
        _add_edge(edges, "alias", alias, "resolves_to", "source", target)

    edge_models = tuple(
        ReferenceEdge(
            source_kind=item[0],
            source_id=item[1],
            relation=item[2],
            target_kind=item[3],
            target_id=item[4],
        )
        for item in sorted(edges)
    )
    counts = ReferentialIntegrityCounts(
        requirements=len(requirements),
        semantic_tests=registry.counts.total,
        implemented_semantic_tests=registry.counts.implemented,
        planned_semantic_tests=registry.counts.planned,
        executable_test_nodes=len(nodes),
        controls=len(controls),
        threats=len(threats),
        playbooks=len(playbooks),
        agents=len(agents),
        commands=len(commands),
        events=len(events),
        fixtures=len(fixtures),
        sources=len(sources),
        aliases=len(alias_pairs),
        edges=len(edge_models),
    )
    body = ReferentialIntegrityReportBody(
        version="1.0.0",
        status="pass",
        rules={
            "definitions_and_references_are_type_checked": True,
            "duplicate_identifiers_fail": True,
            "unknown_requirements_fail": True,
            "unknown_tests_fail": True,
            "unknown_controls_fail": True,
            "unknown_playbooks_fail": True,
            "retired_test_references_fail": True,
            "mandatory_controls_require_test_coverage": True,
            "agent_skill_references_must_exist": True,
            "source_alias_targets_must_exist": True,
        },
        counts=counts,
        edges=edge_models,
        issues=(),
    )
    return ReferentialIntegrityReport.model_validate(
        {**body.model_dump(mode="json"), "report_digest": _digest(body.model_dump(mode="json"))}
    )


def referential_integrity_document(root: Path) -> dict[str, Any]:
    return build_referential_integrity_report(root).model_dump(mode="json")


def write_referential_integrity_report(root: Path, destination: Path | None = None) -> Path:
    target = destination or root / "requirements" / "referential-integrity-baseline.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(referential_integrity_document(root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def verify_referential_integrity_report(root: Path, committed: Path | None = None) -> None:
    target = committed or root / "requirements" / "referential-integrity-baseline.json"
    expected = json.dumps(referential_integrity_document(root), indent=2, sort_keys=True) + "\n"
    if target.read_text(encoding="utf-8") != expected:
        raise ValueError("Committed referential-integrity baseline is stale or modified.")
