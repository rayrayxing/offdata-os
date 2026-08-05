#!/usr/bin/env python3
"""Validate PCR-02 stable test identities and governed identifier references."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from offdata_core.referential_integrity import (
    build_referential_integrity_report,
    build_semantic_test_registry,
    verify_referential_integrity_report,
    verify_semantic_test_registry,
)


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    verify_semantic_test_registry(root)
    verify_referential_integrity_report(root)
    semantic = build_semantic_test_registry(root)
    report = build_referential_integrity_report(root)

    expected_counts = {
        "requirements": 123,
        "semantic_tests": 99,
        "implemented_semantic_tests": 45,
        "planned_semantic_tests": 54,
        "controls": 48,
        "threats": 20,
        "playbooks": 12,
        "agents": 11,
        "commands": 10,
        "events": 15,
        "fixtures": 17,
        "sources": 23,
        "aliases": 99,
    }
    actual = report.counts.model_dump()
    mismatches = {
        key: (actual.get(key), expected)
        for key, expected in expected_counts.items()
        if actual.get(key) != expected
    }
    if mismatches:
        raise ValueError(f"PCR-02 governed namespace counts changed: {mismatches}")
    if semantic.counts.total != 99 or semantic.counts.implemented != 45:
        raise ValueError("PCR-02 semantic test hierarchy is incomplete.")
    if semantic.counts.planned != 54:
        raise ValueError("PCR-02 must preserve exactly 54 deferred semantic tests.")
    if report.counts.executable_test_nodes < 245:
        raise ValueError("PCR-02 executable node registry is incomplete.")
    if report.issues:
        raise ValueError(f"PCR-02 referential issues remain: {report.issues}")

    registry = _json_object(root / "requirements" / "test-registry.json")
    implemented = registry.get("implemented_tests")
    planned = registry.get("planned_tests")
    if not isinstance(implemented, list) or len(implemented) != report.counts.executable_test_nodes:
        raise ValueError("Executable node registry does not reconcile to PCR-02 collection.")
    if not isinstance(planned, list) or len(planned) != 54:
        raise ValueError("Legacy planned-test view does not reconcile to semantic identities.")
    rules = registry.get("rules")
    if not isinstance(rules, dict) or rules.get("semantic_test_registry") != (
        "requirements/test-definitions.json"
    ):
        raise ValueError("Legacy registry does not point to the semantic test registry.")

    required_threat_tokens = {
        "SEC-P7-ENGAGEMENT-001",
        "SEC-P7-CONTROL-001",
        "SEC-P7-BASELINE-001",
        "SEC-P7-UNTRUSTED-001",
        "UT-QA-INDEP-001",
        "SEC-P7-DEV-DATA-001",
    }
    threat_text = (root / "security" / "threat-model.yaml").read_text(encoding="utf-8")
    if not required_threat_tokens <= set(threat_text.replace("[", " ").replace("]", " ").replace(",", " ").split()):
        raise ValueError("Threat-model repairs are incomplete.")
    for invalid in (
        "SEC-P7-CONTEXT-001",
        "SEC-P7-BACKUP-001",
        "SEC-P7-AUDIT-001",
        "SEC-P7-SUPPLY-001",
        "SEC-P7-ENV-001",
        "test_ids: [SEC-P7-INCIDENT-001, QA-008]",
    ):
        if invalid in threat_text:
            raise ValueError(f"Invalid threat test reference remains: {invalid}")

    print("PCR-02 TEST IDENTITY AND REFERENTIAL INTEGRITY VALIDATION PASSED")
    for item in (
        f"semantic_tests={semantic.counts.total}",
        f"implemented_semantic_tests={semantic.counts.implemented}",
        f"planned_semantic_tests={semantic.counts.planned}",
        f"executable_test_nodes={report.counts.executable_test_nodes}",
        f"requirements={report.counts.requirements}",
        f"controls={report.counts.controls}",
        f"threats={report.counts.threats}",
        f"playbooks={report.counts.playbooks}",
        f"agents={report.counts.agents}",
        f"commands={report.counts.commands}",
        f"events={report.counts.events}",
        f"fixtures={report.counts.fixtures}",
        f"sources={report.counts.sources}",
        f"aliases={report.counts.aliases}",
        f"reference_edges={report.counts.edges}",
        "unresolved_references=0",
    ):
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(
            f"PCR-02 TEST IDENTITY AND REFERENTIAL INTEGRITY VALIDATION FAILED: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
