from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from offdata_core.referential_integrity import (
    build_referential_integrity_report,
    build_semantic_test_registry,
    verify_referential_integrity_report,
    verify_semantic_test_registry,
    write_referential_integrity_report,
    write_semantic_test_registry,
)


ROOT = Path(__file__).resolve().parents[3]
SEMANTIC_REGISTRY = ROOT / "requirements" / "test-definitions.json"
INTEGRITY_BASELINE = ROOT / "requirements" / "referential-integrity-baseline.json"


def _copy_inputs(tmp_path: Path) -> Path:
    target = tmp_path / "repository"
    copy_directories = (
        "agents",
        "requirements",
        "security",
        "packages/offdata-core/tests",
    )
    copy_files = (
        "docs/16-REQUIREMENTS-CATALOGUE.md",
        "configs/agents.yaml",
        "configs/security-regionalisation.yaml",
        "contracts/command-event-catalogue.json",
        "fixtures/manifest.yaml",
        "knowledge/source-manifest.yaml",
        "knowledge/alias-map.yaml",
    )
    for relative in copy_directories:
        shutil.copytree(ROOT / relative, target / relative)
    for relative in copy_files:
        source = ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return target


def _rewrite_yaml(path: Path, mutation: Callable[[dict[str, object]], None]) -> None:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    mutation(value)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def test_semantic_test_registry_preserves_all_test_identities() -> None:
    registry = build_semantic_test_registry(ROOT)
    assert registry.counts.total == 99
    assert registry.counts.implemented == 45
    assert registry.counts.planned == 54
    assert {item.test_id for item in registry.tests} >= {
        "META-TEST-HIERARCHY-001",
        "SEC-P7-TENANT-001",
        "IT-BACKUP-RESTORE-001",
    }


def test_completed_semantic_tests_keep_identity_and_gain_evidence() -> None:
    registry = build_semantic_test_registry(ROOT)
    records = {item.test_id: item for item in registry.tests}
    for test_id in (
        "AE-ROUTING-001",
        "IT-FIXTURE-001",
        "AE-STORY-001",
        "UT-ALIAS-001",
        "UT-PROCESSOR-REGISTER-001",
        "META-TEST-HIERARCHY-001",
    ):
        assert records[test_id].status == "implemented"
        assert records[test_id].implementations


def test_planned_semantic_tests_do_not_claim_execution_evidence() -> None:
    registry = build_semantic_test_registry(ROOT)
    planned = [item for item in registry.tests if item.status == "planned"]
    assert len(planned) == 54
    assert all(not item.implementations for item in planned)


def test_semantic_registry_and_integrity_baseline_are_reproducible(tmp_path: Path) -> None:
    first_registry = write_semantic_test_registry(ROOT, tmp_path / "first-tests.json")
    second_registry = write_semantic_test_registry(ROOT, tmp_path / "second-tests.json")
    assert first_registry.read_bytes() == second_registry.read_bytes()
    verify_semantic_test_registry(ROOT, SEMANTIC_REGISTRY)

    first_report = write_referential_integrity_report(ROOT, tmp_path / "first-report.json")
    second_report = write_referential_integrity_report(ROOT, tmp_path / "second-report.json")
    assert first_report.read_bytes() == second_report.read_bytes()
    verify_referential_integrity_report(ROOT, INTEGRITY_BASELINE)


def test_referential_integrity_report_covers_governed_namespaces() -> None:
    report = build_referential_integrity_report(ROOT)
    assert report.status == "pass"
    assert report.issues == ()
    assert report.counts.requirements == 123
    assert report.counts.semantic_tests == 99
    assert report.counts.controls == 48
    assert report.counts.threats == 20
    assert report.counts.playbooks == 12
    assert report.counts.agents == 11
    assert report.counts.commands == 10
    assert report.counts.events == 15
    assert report.counts.fixtures == 17
    assert report.counts.sources == 23
    assert report.counts.aliases == 99


def test_dangling_or_wrong_kind_threat_test_reference_fails(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    threat_path = copied / "security" / "threat-model.yaml"

    def mutate(value: dict[str, object]) -> None:
        threats = value["threats"]
        assert isinstance(threats, list)
        assert isinstance(threats[0], dict)
        threats[0]["test_ids"] = ["QA-008"]

    _rewrite_yaml(threat_path, mutate)
    with pytest.raises(ValueError, match="Unknown or wrong-kind test reference"):
        build_semantic_test_registry(copied)


def test_missing_executable_evidence_node_fails(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    definitions = copied / "requirements" / "test-definitions.yaml"

    def mutate(value: dict[str, object]) -> None:
        evidence = value["implementation_evidence"]
        assert isinstance(evidence, dict)
        records = evidence["META-TEST-HIERARCHY-001"]
        assert isinstance(records, list)
        assert isinstance(records[0], dict)
        records[0]["node_id"] = "packages/offdata-core/tests/test_missing.py::test_missing"

    _rewrite_yaml(definitions, mutate)
    with pytest.raises(ValueError, match="references missing node"):
        build_semantic_test_registry(copied)


def test_evidence_node_must_share_a_requirement_with_semantic_test(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    definitions = copied / "requirements" / "test-definitions.yaml"

    def mutate(value: dict[str, object]) -> None:
        evidence = value["implementation_evidence"]
        assert isinstance(evidence, dict)
        records = evidence["META-TEST-HIERARCHY-001"]
        assert isinstance(records, list)
        assert isinstance(records[0], dict)
        records[0]["node_id"] = (
            "packages/offdata-core/tests/test_release_reconciliation.py::"
            "test_release_boundaries_cannot_enable_real_client_data"
        )

    _rewrite_yaml(definitions, mutate)
    with pytest.raises(ValueError, match="share no requirement"):
        build_semantic_test_registry(copied)


def test_planned_test_cannot_receive_executable_evidence(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    definitions = copied / "requirements" / "test-definitions.yaml"

    def mutate(value: dict[str, object]) -> None:
        evidence = value["implementation_evidence"]
        assert isinstance(evidence, dict)
        evidence["IT-ADAPTER-001"] = [
            {
                "node_id": (
                    "packages/offdata-core/tests/test_agent_system.py::"
                    "test_provider_route_preserves_output_contract_and_uses_risk"
                ),
                "environment": "chat_first_python",
            }
        ]

    _rewrite_yaml(definitions, mutate)
    with pytest.raises(ValueError, match="Evidence is attached to non-implemented tests"):
        build_semantic_test_registry(copied)


def test_unknown_control_reference_fails(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    threat_path = copied / "security" / "threat-model.yaml"

    def mutate(value: dict[str, object]) -> None:
        threats = value["threats"]
        assert isinstance(threats, list)
        assert isinstance(threats[0], dict)
        threats[0]["preventive_controls"] = ["CTRL-NOT-DEFINED"]

    _rewrite_yaml(threat_path, mutate)
    with pytest.raises(ValueError, match="references unknown control"):
        build_referential_integrity_report(copied)


def test_unknown_playbook_reference_fails(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    threat_path = copied / "security" / "threat-model.yaml"

    def mutate(value: dict[str, object]) -> None:
        threats = value["threats"]
        assert isinstance(threats, list)
        assert isinstance(threats[0], dict)
        threats[0]["response_playbook_id"] = "IR-NOT-DEFINED"

    _rewrite_yaml(threat_path, mutate)
    with pytest.raises(ValueError, match="references unknown playbook"):
        build_referential_integrity_report(copied)


def test_duplicate_control_identifier_fails(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    control_path = copied / "security" / "security-control-catalogue.yaml"

    def mutate(value: dict[str, object]) -> None:
        controls = value["controls"]
        assert isinstance(controls, list)
        controls.append(dict(controls[0]))

    _rewrite_yaml(control_path, mutate)
    with pytest.raises(ValueError, match="Duplicate control identifier"):
        build_referential_integrity_report(copied)


def test_unknown_alias_target_fails(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    alias_path = copied / "knowledge" / "alias-map.yaml"

    def mutate(value: dict[str, object]) -> None:
        aliases = value["aliases"]
        assert isinstance(aliases, list)
        assert isinstance(aliases[0], dict)
        aliases[0]["resolves_to_source_id"] = "SOURCE-NOT-DEFINED"

    _rewrite_yaml(alias_path, mutate)
    with pytest.raises(ValueError, match="references unknown source"):
        build_referential_integrity_report(copied)


def test_missing_agent_skill_package_fails(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    agents_path = copied / "configs" / "agents.yaml"

    def mutate(value: dict[str, object]) -> None:
        agents = value["agents"]
        assert isinstance(agents, list)
        assert isinstance(agents[0], dict)
        agents[0]["skill_package"] = "agents/not_defined/SKILL.md"

    _rewrite_yaml(agents_path, mutate)
    with pytest.raises(ValueError, match="references missing skill package"):
        build_referential_integrity_report(copied)


def test_command_cannot_reference_unknown_event(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    catalogue_path = copied / "contracts" / "command-event-catalogue.json"
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    catalogue["commands"]["create_engagement"]["success_events"] = ["event_not_defined"]
    catalogue_path.write_text(json.dumps(catalogue), encoding="utf-8")
    with pytest.raises(ValueError, match="references unknown event"):
        build_referential_integrity_report(copied)


def test_compound_fixture_cannot_reference_unknown_engagement_type(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    fixture_path = copied / "fixtures" / "manifest.yaml"

    def mutate(value: dict[str, object]) -> None:
        compound = value["compound_engagements"]
        assert isinstance(compound, list)
        assert isinstance(compound[0], dict)
        compound[0]["domains"] = ["not_a_governed_engagement_type"]

    _rewrite_yaml(fixture_path, mutate)
    with pytest.raises(ValueError, match="references unknown engagement type"):
        build_referential_integrity_report(copied)


def test_mandatory_control_without_test_coverage_fails(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    tests_path = copied / "security" / "security-test-catalogue.yaml"

    def mutate(value: dict[str, object]) -> None:
        tests = value["tests"]
        assert isinstance(tests, list)
        for test in tests:
            assert isinstance(test, dict)
            controls = test.get("control_ids")
            if isinstance(controls, list):
                test["control_ids"] = [
                    item for item in controls if item != "CTRL-ENCRYPTION-IN-TRANSIT"
                ]

    _rewrite_yaml(tests_path, mutate)
    with pytest.raises(ValueError, match="Mandatory controls lack governed test coverage"):
        build_referential_integrity_report(copied)


def test_restricted_logging_policy_is_metadata_only_or_none() -> None:
    document = yaml.safe_load(
        (ROOT / "security" / "data-classification.yaml").read_text(encoding="utf-8")
    )
    classes = {item["classification"]: item for item in document["classes"]}
    for classification in ("client_confidential", "highly_restricted"):
        record = classes[classification]
        assert record["raw_payload_logging_allowed"] is False
        assert record["default_log_mode"] in {"metadata_only", "none"}


def test_crm_security_boundary_excludes_confidential_content() -> None:
    document = yaml.safe_load(
        (ROOT / "configs" / "security-regionalisation.yaml").read_text(encoding="utf-8")
    )
    prohibited = set(document["regionalisation"]["prohibited_global_metadata_fields"])
    assert {
        "client_name",
        "contact_details",
        "evidence_text",
        "source_passage",
        "model_input",
        "model_output",
        "recommendation_text",
        "personal_data",
    } <= prohibited
