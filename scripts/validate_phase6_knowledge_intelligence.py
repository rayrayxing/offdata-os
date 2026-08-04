#!/usr/bin/env python3
"""Validate the complete chat-first Phase 6 knowledge-ingestion intelligence release."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from offdata_core.knowledge import MethodRecord
from offdata_core.knowledge_ingestion import (
    AliasRule,
    DomainOverlay,
    IntendedUse,
    build_baseline,
    resolve_alias,
    rights_decision,
    verify_baseline,
)


def _object(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) if path.suffix in {".yaml", ".yml"} else json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected object: {path}")
    return value


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    knowledge = root / "knowledge"
    baseline_path = knowledge / "knowledge-ingestion-baseline.json"
    verify_baseline(root, baseline_path)
    baseline = build_baseline(root)
    profiles = baseline.source_profiles
    if len(profiles) != 23 or sum(x.source_format.value == "markdown" for x in profiles) != 11 or sum(x.source_format.value == "docx" for x in profiles) != 12:
        raise ValueError("Source-profile scope is not exactly eleven core and twelve domain sources.")
    if len(baseline.method_index) != 154 or len({x.domain for x in baseline.method_index}) != 12:
        raise ValueError("Domain method index is not exactly 154 headings across twelve domains.")
    if len(baseline.retrieval_cases) != 46:
        raise ValueError("Retrieval evaluation must contain two cases per profiled source.")

    alias_doc = _object(knowledge / "alias-map.yaml")
    aliases = tuple(AliasRule.model_validate(item) for item in alias_doc["aliases"])
    dependency_cases = _object(knowledge / "dependency-resolution-cases.yaml")["cases"]
    for case in dependency_cases:
        resolution = resolve_alias(case["query"], profiles, aliases)
        if resolution.state.value != case["expected_state"]:
            raise ValueError(f"Dependency case failed: {case['case_id']}")
        if case.get("expected_source_id") and resolution.source_id != case["expected_source_id"]:
            raise ValueError(f"Dependency target failed: {case['case_id']}")

    examples = _object(knowledge / "method-record-examples.yaml")["examples"]
    if len(examples) != 12:
        raise ValueError("Method examples must cover all twelve domain packs.")
    for raw in examples:
        MethodRecord.model_validate({key: value for key, value in raw.items() if key not in {"source_local_method_id", "reconstruction_note"}})

    overlays = _object(knowledge / "domain-overlays.yaml")["overlays"]
    if len(overlays) != 12:
        raise ValueError("Domain overlays must cover all twelve domains.")
    for raw in overlays:
        DomainOverlay.model_validate(raw)

    for profile in profiles:
        external = rights_decision(profile, IntendedUse.EXTERNAL_REDISTRIBUTION)
        if external.allowed or not external.requires_founder_confirmation:
            raise ValueError(f"External redistribution incorrectly allowed: {profile.source_id}")
        if profile.import_status != "profiled_original_not_committed":
            raise ValueError(f"Physical import incorrectly claimed: {profile.source_id}")

    baseline_document = _object(baseline_path)
    if baseline_document.get("original_source_files_committed") is not False:
        raise ValueError("The release must not claim original source binaries are committed.")

    completed = _object(root / "requirements/completed-planned-tests-phase6.json").get("completed_test_ids")
    if completed != ["UT-ALIAS-001", "UT-OVERLAY-001", "UT-RIGHTS-001"]:
        raise ValueError("Phase 6 completed planned-test register is not exact.")
    planned = _object(root / "requirements/planned-test-mappings.json")
    if "IT-INGEST-001" not in planned:
        raise ValueError("Physical source-import integration test must remain planned.")

    print("PHASE 6 KNOWLEDGE-INGESTION INTELLIGENCE VALIDATION PASSED")
    for item in (
        f"source_profiles={len(profiles)}",
        "core_markdown_sources=11",
        "domain_docx_sources=12",
        f"method_headings={len(baseline.method_index)}",
        f"aliases={baseline.alias_count}",
        f"dependency_cases={baseline.dependency_case_count}",
        f"collision_families={baseline.collision_family_count}",
        f"method_record_examples={baseline.method_record_example_count}",
        f"retrieval_cases={len(baseline.retrieval_cases)}",
        f"radar_categories={baseline.radar_category_count}",
        f"completed_planned_tests={len(completed)}",
        "physical_import_boundary=preserved",
        "automatic_method_promotion=blocked",
    ):
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"PHASE 6 KNOWLEDGE-INGESTION INTELLIGENCE VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
