from __future__ import annotations

import copy
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, digest_file, load_json
from pcfa08_final_acceptance import RECORD, REPORT, build_records, record_failures, run_self_test, state_failures

SCHEMA = ROOT / "schemas" / "pcfa08-final-pre-codex-cross-authority-acceptance.schema.json"
DOC = ROOT / "docs" / "75-PCFA-08-FINAL-PRE-CODEX-CROSS-AUTHORITY-ACCEPTANCE.md"
STATUS = ROOT / "docs" / "CURRENT-OPERATIONAL-STATE.md"
HANDOFF = ROOT / "handoff" / "codex-phase0-current-handoff.json"
ISSUE1 = ROOT / "handoff" / "codex-phase0-current-issue.md"
ISSUE19 = ROOT / "handoff" / "codex-phase0-current-hosted-controls-issue.md"
HOSTED_TEMPLATE = ROOT / "handoff" / "codex-phase0-current-hosted-controls-attestation.template.json"
P4 = ROOT / "repository" / "pcfa04-product-scope-implementation-addendum.json"
P5 = ROOT / "repository" / "pcfa05-minimum-valuable-consulting-loop.json"
P6 = ROOT / "repository" / "pcfa06-hermes-bounded-adoption-refresh.json"
P7 = ROOT / "requirements" / "pcfa07-codex-implementation-backlog-reconciliation.json"


def req(ok: bool, msg: str) -> None:
    if not ok:
        raise SystemExit(msg)


def main() -> None:
    record = load_json(RECORD)
    state = load_json(CURRENT_STATE_PATH)
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record))
    req(not errors, "PCFA-08 schema validation failed: " + "; ".join(error.message for error in errors))
    expected, report = build_records()
    req(record == expected, "PCFA-08 generated record drifted from governed sources")
    req(REPORT.read_text(encoding="utf-8") == report, "PCFA-08 generated evidence report drifted")
    req(not record_failures(record), "PCFA-08 semantic validation failed: " + "; ".join(record_failures(record)))
    req(not state_failures(state, record), "PCFA-08 current-state binding failed: " + "; ".join(state_failures(state, record)))

    p4, p5, p6, p7 = (load_json(path) for path in (P4, P5, P6, P7))
    req(len(p4["requirements"]) == 29, "PCFA-04 requirement count drifted")
    req(len(p5["stages"]) == 19 and len(p5["loop_invariants"]) == 15 and len(p5["negative_cases"]) == 13 and len(p5["founder_interrupts"]) == 6, "PCFA-05 obligation counts drifted")
    req(len(p6["capability_assessments"]) == 11, "PCFA-06 capability count drifted")
    req(p7["obligation_counts"]["total_obligations"] == 93 and p7["obligation_counts"]["planned_tests"] == 93, "PCFA-07 reconciliation count drifted")
    req(p7["backlog_projection"]["phase0_new_obligation_count"] == 0, "PCFA-07 widened Phase 0")

    handoff = load_json(HANDOFF)
    req(handoff["authority"].get("final_pre_codex_cross_authority_acceptance") == str(RECORD.relative_to(ROOT)), "current handoff omits PCFA-08 authority")
    req(handoff["readiness"].get("pcfa08_final_cross_authority_acceptance_complete") is True, "current handoff omits PCFA-08 readiness")
    req(str(RECORD.relative_to(ROOT)) in handoff["read_order"], "current handoff read order omits PCFA-08")
    req("python scripts/validate_pcfa08_final_acceptance.py" in handoff["execution"]["required_commands"], "current handoff preflight omits PCFA-08")

    hosted = load_json(HOSTED_TEMPLATE)
    cleanup = hosted.get("branch_cleanup", {})
    req("deleted_branches" in cleanup and cleanup["deleted_branches"] == [], "hosted template must explicitly reserve deleted-branch SHA evidence")
    req(cleanup.get("complete") is False, "hosted template cannot pre-attest branch cleanup")

    tokens = {
        DOC: ("65", "18", "only `main`", "40-hex SHA", "codex_start_authorized=false"),
        STATUS: ("PCFA-08", "final SHA", "only `main`", "manual launch gates"),
        ISSUE1: ("PCFA-08", "65", "codex_start_authorized=false"),
        ISSUE19: ("PCFA-08", "65", "deleted_branches", "final SHA", "only `main`"),
    }
    for path, expected_tokens in tokens.items():
        text = path.read_text(encoding="utf-8")
        for token in expected_tokens:
            req(token in text, f"{path.relative_to(ROOT)} missing {token}")

    rejected = run_self_test(state)
    mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("manual complete", ("repository_acceptance", "manual_launch_evidence_complete"), True),
        ("launch complete", ("repository_acceptance", "launch_authorization_complete"), True),
        ("main deleted", ("branch_cleanup_plan", "delete_after_dependency_order_integration"), record["branch_cleanup_plan"]["delete_after_dependency_order_integration"] + ["main"]),
        ("permit bypass", ("launch_target", "implementation_may_start_only_after_valid_permit"), False),
        ("phase1", ("boundaries", "phase1_authorized"), True),
    ]
    for label, path, replacement in mutations:
        value = copy.deepcopy(record)
        node: Any = value
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = replacement
        req(bool(record_failures(value)), f"PCFA-08 semantic mutation not rejected: {label}")
        rejected += 1

    print(
        "PCFA-08 final pre-Codex cross-authority acceptance validation passed: "
        f"authorities=9, invariants=18, manual_gates=8, cleanup_branches=65, mutations_rejected={rejected}, "
        f"record_sha256={digest_file(RECORD)}, repository_acceptance=true, manual_launch_evidence=false, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
