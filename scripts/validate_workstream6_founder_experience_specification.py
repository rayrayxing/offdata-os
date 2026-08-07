from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream6_founder_experience_specification import build_records

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "workstream6-founder-experience-specification.yaml"
CONTRACT = ROOT / "contracts" / "founder-experience-specification.json"
SCHEMA = ROOT / "schemas" / "founder-experience-specification.schema.json"
SPEC = ROOT / "docs" / "63-WS6-11-FOUNDER-EXPERIENCE-SPECIFICATION.md"
REPORT = ROOT / "reports" / "workstream6-founder-experience-specification-evidence.md"
QUALITY = ROOT / "contracts" / "pre-codex-readiness.json"
OBLIGATION_MAP = ROOT / "requirements" / "implementation-obligation-map.json"

EXPECTED_IDS = ["FX-INBOX","FX-CONSEQUENCE","FX-AUTH","FX-PREVIEW","FX-EVIDENCE","FX-STATES","FX-ACCESS","FX-SEND"]
EXPECTED_STATES = ["draft","recommended","pending_authorization","authorized","executing","waiting","blocked","retrying","failed","stale","complete","rejected","cancelled"]
CASE_CLASSES = ["happy_path","missing_required_data","authorization_safety","stale_or_version_drift"]


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def _failures(value: dict[str, Any], source: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(value.get("work_package_id") == "WS6.11", "work package")
    predecessor = value.get("predecessor", {})
    require(predecessor.get("work_package_id") == "WS6.10", "predecessor package")
    require(predecessor.get("head_sha") == "ebd750f6e985d7a864d072a172d4d9343ce26a36", "predecessor head")
    require(predecessor.get("integrated_to_main") is False, "predecessor integration honesty")
    require(value.get("source_sha256") == hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "source digest")

    quality_ids = [item["id"] for item in _load(QUALITY)["founder_experience"]["acceptance_criteria"]]
    require(quality_ids == EXPECTED_IDS, "PCR-10 Founder criterion identity")
    criteria = value.get("criteria", [])
    require([item.get("criterion_id") for item in criteria] == EXPECTED_IDS, "contract criterion order")
    require(value.get("criterion_count") == 8 == len(criteria), "criterion count")
    require(value.get("surface_count") == 6 == len(value.get("surfaces", [])), "surface count")
    require(value.get("state_count") == 13 == len(value.get("states", [])), "state count")
    require([item.get("id") for item in value.get("states", [])] == EXPECTED_STATES, "state identity")
    require(value.get("acceptance_case_count") == 32, "acceptance case count")

    obligations = {item["criterion_id"]: item for item in _load(OBLIGATION_MAP)["obligations"] if item["criterion_id"] in EXPECTED_IDS}
    source_rules = {item["criterion_id"]: item for item in source["criterion_rules"]}
    case_ids: list[str] = []
    for item in criteria:
        cid = item.get("criterion_id")
        rule = source_rules.get(cid, {})
        obligation = obligations.get(cid, {})
        require(item.get("phase_id") == obligation.get("phase_id") == rule.get("phase_id"), f"phase {cid}")
        require(item.get("task_id") == obligation.get("task_id") == rule.get("task_id"), f"task {cid}")
        require(item.get("component_id") == obligation.get("component_id") == rule.get("component_id"), f"component {cid}")
        require(obligation.get("blocks_imp_p0") is False, f"IMP-P0 split {cid}")
        require(item.get("surface_id") == rule.get("surface_id"), f"surface {cid}")
        require(item.get("required_fields") == rule.get("required_fields"), f"required fields {cid}")
        require(item.get("invariants") == rule.get("invariants"), f"invariants {cid}")
        require(item.get("source_digest") == _digest(rule), f"source rule digest {cid}")
        require(item.get("implementation_status") == "specified_not_implemented", f"implementation honesty {cid}")
        require(item.get("evidence_satisfied") is False, f"evidence honesty {cid}")
        cases = item.get("acceptance_cases", [])
        require([case.get("case_class") for case in cases] == CASE_CLASSES, f"case classes {cid}")
        for case in cases:
            case_ids.append(str(case.get("case_id")))
            require(case.get("registration_status") == "planned_unregistered", f"registration {cid}")
            require(case.get("executable_test_exists") is False, f"executable test {cid}")
    require(len(case_ids) == len(set(case_ids)) == 32, "case identity")

    require(value.get("decision_packet_digest") == _digest(source["decision_packet"]), "decision packet digest")
    require(value.get("authorization_digest") == _digest(source["authorization"]), "authorization digest")
    require(value.get("external_send_digest") == _digest(source["external_send"]), "external send digest")
    require(value.get("evidence_drillthrough_digest") == _digest(source["evidence_drillthrough"]), "evidence digest")
    require(value.get("accessibility_digest") == _digest(source["accessibility"]), "accessibility digest")
    require(value.get("inbox_digest") == _digest(source["inbox"]), "inbox digest")

    auth = source["authorization"]
    require(auth.get("recommendation_is_authorization") is False, "recommendation separation")
    require(auth.get("founder_only") is True, "Founder authorization")
    require(auth.get("exact_preview_required") is True, "preview requirement")
    require(auth.get("execution_before_authorization") is False, "execution-before-auth")
    for key in ("version_drift_invalidates","preview_drift_invalidates","stale_invalidates","expiry_invalidates","authorization_record_append_only"):
        require(auth.get(key) is True, key)
    packet_fields = set(source["decision_packet"]["required_fields"])
    require({"consequence_if_approved","consequence_if_rejected","deadline_at","reversibility","reversibility_details","exact_next_action","evidence_refs","model_output_refs","current_state","record_version","approval_scope_digest"} <= packet_fields, "decision packet material fields")
    require(source["decision_packet"].get("unknown_reversibility_blocks_authorization") is True, "unknown reversibility")
    send = source["external_send"]
    require(send.get("default_enabled") is False and send.get("autonomous_send") is False, "send default")
    require(send.get("exact_authorization_required") is True and send.get("final_preview_required") is True and send.get("stale_or_mismatch_denies") is True, "send authorization")
    evidence = source["evidence_drillthrough"]
    require(evidence.get("read_only") is True and evidence.get("context_preserved") is True and evidence.get("unsupported_material_item_visible") is True, "evidence drillthrough")
    accessibility = source["accessibility"]
    require(accessibility.get("standard") == "WCAG_2_2_AA", "accessibility standard")
    require(accessibility.get("keyboard_all_actions") is True and accessibility.get("visible_focus") is True and accessibility.get("no_color_only") is True, "accessibility interaction")
    require(accessibility.get("text_contrast_min") == 4.5 and accessibility.get("large_text_contrast_min") == 3.0, "contrast")
    require(source["inbox"].get("target_identify_all_pending_material_decisions_seconds") == 60, "inbox timing")
    require(source["inbox"].get("all_material_pending_visible") is True, "inbox completeness")

    require(value.get("test_registration") == source["test_registration"], "test registration")
    require(value.get("test_registration", {}).get("registered_case_count") == 0, "registered cases")
    require(value.get("test_registration", {}).get("executable_test_count") == 0, "executable cases")
    require(value.get("evidence", {}).get("satisfied_evidence_count") == 0, "satisfied evidence")
    require(value.get("closed_defects") == ["WS6-QUALITY-003"], "closed defect")
    require(value.get("remaining_blocking_defects") == ["WS6-BLOCK-006"], "remaining blocker")
    require(value.get("remaining_preparation_defects") == ["WS6-CODEXPREP-002"], "remaining preparation")
    completion = value.get("completion", {})
    for key in ("all_required_prior_components_pass","stacked_on_exact_ws610_head","ws611_repository_package_complete","all_8_founder_criteria_specified"):
        require(completion.get(key) is True, key)
    for key in ("ws68_integrated_to_main","ws69_integrated_to_main","ws610_integrated_to_main","founder_experience_implemented","test_registration_complete","final_reconciliation_complete","all_blocking_defects_closed"):
        require(completion.get(key) is False, key)
    require(completion.get("next_permitted_work_package") == "WS6.12", "next package")
    boundaries = value.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability")
    for key, current in boundaries.items():
        if key != "founder_accountability_preserved":
            require(current is False, key)
    return failures


def _set(value: dict[str, Any], path: tuple[Any, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def main() -> None:
    source = _load(SOURCE)
    contract = _load(CONTRACT)
    errors = list(Draft202012Validator(_load(SCHEMA)).iter_errors(contract))
    if errors:
        raise SystemExit("WS6.11 schema validation failed: " + "; ".join(error.message for error in errors))
    expected, spec, report = build_records()
    if contract != expected:
        raise SystemExit("WS6.11 contract is not deterministic")
    expected_bytes = json.dumps(expected, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    if CONTRACT.read_text(encoding="utf-8") != expected_bytes:
        raise SystemExit("WS6.11 contract bytes are not canonical")
    if SPEC.read_text(encoding="utf-8") != spec:
        raise SystemExit("WS6.11 specification is not deterministic")
    if REPORT.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.11 report is not deterministic")
    failures = _failures(contract, source)
    if failures:
        raise SystemExit("WS6.11 semantic validation failed: " + "; ".join(failures))

    rejected = 0
    for index, item in enumerate(contract["criteria"]):
        mutations = [
            (("criteria", index, "phase_id"), "IMP-P0"),
            (("criteria", index, "component_id"), "COMP-STATE"),
            (("criteria", index, "implementation_status"), "implemented"),
            (("criteria", index, "evidence_satisfied"), True),
            (("criteria", index, "acceptance_cases", 0, "registration_status"), "registered"),
            (("criteria", index, "acceptance_cases", 0, "executable_test_exists"), True),
        ]
        for path, replacement in mutations:
            mutated = copy.deepcopy(contract)
            _set(mutated, path, replacement)
            if _failures(mutated, source):
                rejected += 1
            else:
                raise SystemExit(f"WS6.11 mutation not rejected: {item['criterion_id']} {path}")

    cases: list[tuple[tuple[Any, ...], Any]] = [
        (("work_package_id",), "WS6.10"),
        (("predecessor","head_sha"), "0"*40),
        (("predecessor","integrated_to_main"), True),
        (("criterion_count",), 7),
        (("surface_count",), 5),
        (("state_count",), 12),
        (("acceptance_case_count",), 31),
        (("closed_defects",), []),
        (("remaining_blocking_defects",), []),
        (("remaining_preparation_defects",), []),
        (("test_registration","registered_case_count"), 1),
        (("test_registration","executable_test_count"), 1),
        (("evidence","satisfied_evidence_count"), 1),
        (("completion","all_required_prior_components_pass"), False),
        (("completion","stacked_on_exact_ws610_head"), False),
        (("completion","ws610_integrated_to_main"), True),
        (("completion","founder_experience_implemented"), True),
        (("completion","test_registration_complete"), True),
        (("completion","next_permitted_work_package"), "WS6.13"),
        (("boundaries","codex_start_authorized"), True),
        (("boundaries","external_actions_authorized"), True),
        (("boundaries","autonomous_merge_authorized"), True),
    ]
    for path, replacement in cases:
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if _failures(mutated, source):
            rejected += 1
        else:
            raise SystemExit(f"WS6.11 mutation not rejected: {path}")

    structural: list[tuple[str, dict[str, Any]]] = []
    missing = copy.deepcopy(contract)
    missing["criteria"] = missing["criteria"][:-1]
    structural.append(("missing criterion", missing))
    duplicate = copy.deepcopy(contract)
    duplicate["criteria"][1]["criterion_id"] = duplicate["criteria"][0]["criterion_id"]
    structural.append(("duplicate criterion", duplicate))
    missing_state = copy.deepcopy(contract)
    missing_state["states"] = missing_state["states"][:-1]
    structural.append(("missing state", missing_state))
    duplicate_case = copy.deepcopy(contract)
    duplicate_case["criteria"][1]["acceptance_cases"][0]["case_id"] = duplicate_case["criteria"][0]["acceptance_cases"][0]["case_id"]
    structural.append(("duplicate case", duplicate_case))
    for label, mutated in structural:
        if _failures(mutated, source):
            rejected += 1
        else:
            raise SystemExit(f"WS6.11 structural mutation not rejected: {label}")

    print(
        "WS6.11 Founder experience specification passed: "
        f"{rejected} mutations rejected, criteria=8, surfaces=6, states=13, cases=32, "
        "registered_tests=0, satisfied_evidence=0, next=WS6.12, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
