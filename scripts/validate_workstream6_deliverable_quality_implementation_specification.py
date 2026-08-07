from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from build_workstream6_deliverable_quality_implementation_specification import (
    CONTRACT, DIMENSIONS, OQ_IDS, REPORT, ROOT, SOURCE, SPEC, SURFACES, build_records, canonical, digest
)

SCHEMA = ROOT / "schemas" / "deliverable-quality-implementation-specification.schema.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def validate(contract: dict[str, Any]) -> None:
    source = load(SOURCE)
    if contract["work_package_id"] != "WS6.12" or contract["predecessor"] != source["predecessor"]:
        raise ValueError("identity/predecessor drift")
    if contract["defect_ids"] != ["WS6-QUALITY-004"]:
        raise ValueError("defect drift")
    if contract["document_path_resolution"] != source["document_path_resolution"]:
        raise ValueError("document path drift")
    if contract["source_sha256"] != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
        raise ValueError("source digest mismatch")
    expected_counts = {
        "renderer_count": 6, "mandatory_dimension_count": 5,
        "canonical_pcr10_requirement_count": 26, "surface_requirement_binding_count": 37,
        "renderer_acceptance_case_count": 30, "cross_format_acceptance_case_count": 8,
        "acceptance_case_count": 38,
    }
    for field, expected in expected_counts.items():
        if contract[field] != expected:
            raise ValueError(f"{field} changed")
    if contract["required_surfaces"] != list(SURFACES) or contract["mandatory_dimensions"] != list(DIMENSIONS):
        raise ValueError("surface/dimension order changed")
    expected_policy_digests = {
        "repair": digest(source["repair_policy"]),
        "visual_regression": digest(source["visual_regression_policy"]),
        "accessibility": digest(source["accessibility_policy"]),
        "reconciliation": digest(source["reconciliation_policy"]),
    }
    if contract["policy_digests"] != expected_policy_digests:
        raise ValueError("policy digest drift")

    source_renderers = {x["surface"]: x for x in source["renderers"]}
    if [x["surface"] for x in contract["renderers"]] != list(SURFACES):
        raise ValueError("renderer order changed")
    all_case_ids: list[str] = []
    for renderer in contract["renderers"]:
        src = source_renderers[renderer["surface"]]
        for field in ("implementation_task", "component_id", "quality_task", "integrity_mode", "editability_mode"):
            if renderer[field] != src[field]:
                raise ValueError(f"{renderer['surface']} {field} drift")
        if renderer.get("model_quality_task") != src.get("model_quality_task"):
            raise ValueError("model QA ownership drift")
        if renderer["source_digest"] != digest(src):
            raise ValueError("renderer source digest drift")
        cases = renderer["acceptance_cases"]
        if [x["dimension"] for x in cases] != list(DIMENSIONS):
            raise ValueError("renderer dimensions changed")
        if len(cases) != 5:
            raise ValueError("renderer case count changed")
        for case in cases:
            expected_requirements = [
                x["requirement"] for x in source["pcr10_requirement_applicability"]
                if renderer["surface"] in x["surfaces"] and case["dimension"] == x["dimension"]
            ]
            expected_id = f"DQ-{renderer['surface'].upper()}-{case['dimension'].upper().replace('_', '-')}-001"
            if case["case_id"] != expected_id or case["pcr10_requirements"] != expected_requirements:
                raise ValueError("renderer case mapping drift")
            if case["evidence_type"] != f"{renderer['surface']}_{case['dimension']}_report":
                raise ValueError("renderer evidence type drift")
            if case["registration_status"] != "planned_unregistered" or case["executable_test_exists"] is not False or case["implementation_evidence_satisfied"] is not False:
                raise ValueError("renderer implementation/test claim widened")
            all_case_ids.append(case["case_id"])
    if len(all_case_ids) != 30 or len(set(all_case_ids)) != 30:
        raise ValueError("renderer case identities invalid")

    source_rules = {x["criterion_id"]: x for x in source["criterion_rules"]}
    xfmt = contract["cross_format_quality_cases"]
    if [x["criterion_id"] for x in xfmt] != list(OQ_IDS):
        raise ValueError("cross-format OQ order changed")
    for case in xfmt:
        rule = source_rules[case["criterion_id"]]
        for field in ("phase_id", "task_id", "component_id", "evidence_type"):
            if case[field] != rule[field]:
                raise ValueError(f"{case['criterion_id']} owner/evidence drift")
        if case["source_digest"] != digest(rule):
            raise ValueError("cross-format source digest drift")
        if case["case_id"] != f"DQ-XFMT-{case['criterion_id']}-001":
            raise ValueError("cross-format case ID drift")
        if case["registration_status"] != "planned_unregistered" or case["executable_test_exists"] is not False or case["implementation_evidence_satisfied"] is not False:
            raise ValueError("cross-format implementation/test claim widened")

    if contract["test_registration"] != {**source["test_registration"], "planned_case_count": 38}:
        raise ValueError("test registration boundary changed")
    if contract["implementation_evidence"] != source["implementation_evidence"]:
        raise ValueError("implementation evidence boundary changed")
    if contract["closed_defects"] != ["WS6-QUALITY-004"] or contract["remaining_quality_defects"] != ["WS6-QUALITY-005"] or contract["remaining_blocking_defects"] != ["WS6-BLOCK-006"]:
        raise ValueError("defect boundary changed")
    if contract["completion"] != source["completion"]:
        raise ValueError("completion boundary changed")
    if contract["boundaries"] != source["boundaries"]:
        raise ValueError("authorization boundary changed")
    if contract["rollback"] != source["rollback"]:
        raise ValueError("rollback drift")


def mutations(base: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    result: list[tuple[str, dict[str, Any]]] = []
    def add(name: str, fn: Callable[[dict[str, Any]], None]) -> None:
        item = copy.deepcopy(base); fn(item); result.append((name, item))

    add("work-package", lambda x: x.__setitem__("work_package_id", "WS6.13"))
    add("predecessor", lambda x: x["predecessor"].__setitem__("head_sha", "0" * 40))
    add("integrated", lambda x: x["predecessor"].__setitem__("integrated_to_main", True))
    add("defect", lambda x: x.__setitem__("defect_ids", ["WS6-QUALITY-005"]))
    add("doc-path", lambda x: x["document_path_resolution"].__setitem__("canonical", "docs/55-DELIVERABLE-QUALITY-IMPLEMENTATION-SPEC.md"))
    add("source-digest", lambda x: x.__setitem__("source_sha256", "0" * 64))
    for field in ("renderer_count","mandatory_dimension_count","canonical_pcr10_requirement_count","surface_requirement_binding_count","renderer_acceptance_case_count","cross_format_acceptance_case_count","acceptance_case_count"):
        add("count-" + field, lambda x, f=field: x.__setitem__(f, x[f] + 1))
    add("surfaces", lambda x: x["required_surfaces"].pop())
    add("dimensions", lambda x: x["mandatory_dimensions"].pop())
    for key in base["policy_digests"]:
        add("policy-" + key, lambda x, k=key: x["policy_digests"].__setitem__(k, "0" * 64))

    for i, renderer in enumerate(base["renderers"]):
        surface = renderer["surface"]
        add("surface-" + surface, lambda x, i=i: x["renderers"][i].__setitem__("surface", "pptx" if x["renderers"][i]["surface"] != "pptx" else "docx"))
        for field in ("implementation_task","component_id","quality_task","integrity_mode","editability_mode","source_digest"):
            add(f"{surface}-{field}", lambda x, i=i, f=field: x["renderers"][i].__setitem__(f, "changed"))
        if "model_quality_task" in renderer:
            add("xlsx-model-task", lambda x, i=i: x["renderers"][i].__setitem__("model_quality_task", "P7.5"))
        for j, dimension in enumerate(DIMENSIONS):
            add(f"{surface}-remove-{dimension}", lambda x, i=i, j=j: x["renderers"][i]["acceptance_cases"].pop(j))
            add(f"{surface}-id-{dimension}", lambda x, i=i, j=j: x["renderers"][i]["acceptance_cases"][j].__setitem__("case_id", "DQ-WRONG-001"))
            add(f"{surface}-requirements-{dimension}", lambda x, i=i, j=j: x["renderers"][i]["acceptance_cases"][j]["pcr10_requirements"].append("invented"))
            add(f"{surface}-evidence-{dimension}", lambda x, i=i, j=j: x["renderers"][i]["acceptance_cases"][j].__setitem__("evidence_type", "wrong"))
            add(f"{surface}-registered-{dimension}", lambda x, i=i, j=j: x["renderers"][i]["acceptance_cases"][j].__setitem__("registration_status", "registered"))
            add(f"{surface}-executable-{dimension}", lambda x, i=i, j=j: x["renderers"][i]["acceptance_cases"][j].__setitem__("executable_test_exists", True))
            add(f"{surface}-satisfied-{dimension}", lambda x, i=i, j=j: x["renderers"][i]["acceptance_cases"][j].__setitem__("implementation_evidence_satisfied", True))

    for i, criterion in enumerate(OQ_IDS):
        for field in ("phase_id","task_id","component_id","evidence_type","source_digest","case_id"):
            add(f"{criterion}-{field}", lambda x, i=i, f=field: x["cross_format_quality_cases"][i].__setitem__(f, "wrong"))
        add(f"{criterion}-registered", lambda x, i=i: x["cross_format_quality_cases"][i].__setitem__("registration_status", "registered"))
        add(f"{criterion}-executable", lambda x, i=i: x["cross_format_quality_cases"][i].__setitem__("executable_test_exists", True))
        add(f"{criterion}-satisfied", lambda x, i=i: x["cross_format_quality_cases"][i].__setitem__("implementation_evidence_satisfied", True))

    add("planned-count", lambda x: x["test_registration"].__setitem__("planned_case_count", 37))
    add("registered-count", lambda x: x["test_registration"].__setitem__("registered_case_count", 1))
    add("executable-count", lambda x: x["test_registration"].__setitem__("executable_test_count", 1))
    add("renderer-evidence", lambda x: x["implementation_evidence"].__setitem__("satisfied_renderer_count", 1))
    add("xfmt-evidence", lambda x: x["implementation_evidence"].__setitem__("satisfied_cross_format_criterion_count", 1))
    add("closed-defects", lambda x: x.__setitem__("closed_defects", ["WS6-QUALITY-004","WS6-QUALITY-005"]))
    add("remaining-quality", lambda x: x.__setitem__("remaining_quality_defects", []))
    add("blocker", lambda x: x.__setitem__("remaining_blocking_defects", []))
    add("renderer-complete", lambda x: x["completion"].__setitem__("renderer_implementation_complete", True))
    add("hosted-complete", lambda x: x["completion"].__setitem__("hosted_exact_merge_reference_acceptance_complete", True))
    add("next", lambda x: x["completion"].__setitem__("next_permitted_work_package", "WS6.14"))
    for key in base["boundaries"]:
        add("boundary-" + key, lambda x, k=key: x["boundaries"].__setitem__(k, False if k == "founder_accountability_preserved" else True))
    add("rollback-before", lambda x: x["rollback"].__setitem__("before_merge", "none"))
    add("rollback-after", lambda x: x["rollback"].__setitem__("after_merge", "none"))
    return result


def main() -> None:
    contract = load(CONTRACT)
    schema = load(SCHEMA)
    Draft202012Validator(schema).validate(contract)
    validate(contract)
    built, spec, report = build_records()
    if canonical(built) != CONTRACT.read_text(encoding="utf-8"):
        raise ValueError("contract drift")
    if spec != SPEC.read_text(encoding="utf-8") or report != REPORT.read_text(encoding="utf-8"):
        raise ValueError("generated text drift")
    rejected = 0
    for name, mutated in mutations(contract):
        try:
            Draft202012Validator(schema).validate(mutated)
            validate(mutated)
        except Exception:
            rejected += 1
        else:
            raise ValueError(f"mutation accepted: {name}")
    print(f"WS6.12 deliverable quality implementation specification passed: {rejected} mutations rejected, renderers=6, requirements=26, bindings=37, cases=38, registered_tests=0, satisfied_evidence=0, next=WS6.13, codex_start_authorized=false.")


if __name__ == "__main__":
    main()
