from __future__ import annotations

import copy
from typing import Any, Callable

import jsonschema

from build_workstream6_permanent_release_record import DOC, OUT, REPORT, ROOT, SRC, build_records, canon, load
from finalize_workstream6_permanent_release import self_test as finalizer_self_test

RELEASE_PATH = ROOT / "releases/pre-codex-final-reconciliation-2026-08-06.json"
FINAL_REPORT = ROOT / "reports/workstream6-final-evidence.md"
FINAL_LEDGER = ROOT / "repository/workstream6-final-defect-closure-ledger.json"
EXACT_CHECK = "Validate final pre-Codex canonical handoff and complete release"


def obj(path: str) -> dict[str, Any]:
    value = load(ROOT / path)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be object")
    return value


def source_failures(source: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(source.get("work_package_id") == "WS6.16", "work package drift")
    require(source.get("package_state") == "premerge_release_machinery_complete_postmerge_record_blocked", "package state drift")
    pred = source.get("predecessor", {})
    require(pred.get("work_package_id") == "WS6.15", "predecessor package drift")
    require(pred.get("pull_request") == 61, "predecessor PR drift")
    require(pred.get("branch") == "governance/ws615-final-workflow", "predecessor branch drift")
    require(pred.get("head_sha") == "1361fff88bd08ae16218673337621571a7d315c6", "predecessor head drift")
    require(pred.get("integrated_to_main") is True, "predecessor integration claimed early")

    main = source.get("current_main", {})
    require(main.get("observed_sha") == "8ad0ea95b8d01c83347161e4ccf893f1844a219d", "observed main drift")
    require(main.get("integrated_through") == "WS6.15", "integrated boundary drift")
    require(main.get("eligible_for_permanent_release") is False, "main eligibility claimed early")

    release = source.get("permanent_release", {})
    require(release.get("release_id") == "PRE-CODEX-FINAL-RECONCILIATION-2026-08-06", "release ID drift")
    require(release.get("path") == "releases/pre-codex-final-reconciliation-2026-08-06.json", "release path drift")
    require(release.get("final_evidence_path") == "reports/workstream6-final-evidence.md", "final evidence path drift")
    require(release.get("final_ledger_path") == "repository/workstream6-final-defect-closure-ledger.json", "final ledger path drift")
    require(release.get("record_must_be_absent_in_preparation_pr") is True, "preparation release absence weakened")
    require(release.get("creation_mode") == "post_merge_release_record_branch_only", "creation mode drift")
    require(release.get("finalization_branch") == "release/ws616-permanent-release-record", "finalization branch drift")

    exc = source.get("preparation_exception", {})
    require(exc.get("event") == "pull_request", "preparation exception event drift")
    require(exc.get("head_branch") == "governance/ws616-permanent-release-record", "preparation exception head drift")
    require(exc.get("base_branch") == "main", "preparation exception base drift")
    require(exc.get("base_sha") == "8ad0ea95b8d01c83347161e4ccf893f1844a219d", "preparation exception base SHA drift")
    require(exc.get("requires_permanent_release") is False, "preparation exception release requirement drift")
    require(exc.get("requires_release_absent") is True, "preparation exception no longer requires release absence")
    require(exc.get("must_expire_after_preparation_merge") is True, "preparation exception expiry weakened")

    binding = source.get("release_binding_contract", {})
    require(binding.get("main_binding_semantics") == "release_parent_main_sha_is_exact_integrated_main_before_release_record_commit", "main binding semantics drift")
    require(binding.get("tested_merge_reference_semantics") == "tested_merge_reference_is_exact_successful_WS6.16_preparation_PR_merge_reference", "merge-ref binding semantics drift")
    require(binding.get("final_check_name") == EXACT_CHECK, "final check identity drift")
    require(binding.get("require_successful_current_final_evidence") is True, "current final evidence requirement weakened")
    require(binding.get("predecessor_evidence_may_not_substitute") is True, "predecessor substitution allowed")
    require(binding.get("required_fields") == [
        "release_parent_main_sha","tested_merge_reference","final_check_run_id",
        "final_check_job_id","final_check_artifact_id","final_check_artifact_digest_sha256",
        "final_check_name","preparation_pr_number","preparation_head_sha"
    ], "release binding fields drift")

    preconditions = source.get("finalization_preconditions", [])
    require(len(preconditions) == 6, "finalization precondition count drift")
    require([item.get("satisfied") for item in preconditions] == [True, False, False, False, False, False], "finalization precondition truth drift")

    defects = source.get("defects", {})
    require(defects.get("close_only_after_finalization") == ["WS6-BLOCK-006", "WS6-CONSIST-010"], "release closure set drift")
    require(defects.get("manual_remaining_after_release") == ["WS6-CONSIST-006"], "manual remaining set drift")
    require(defects.get("all_blocking_defects_closed_only_after_release") is True, "blocking closure timing weakened")

    manual = source.get("manual_gates", {})
    require(all(value is False for value in manual.values()), "manual gate claimed complete")

    completion = source.get("completion", {})
    require(completion.get("release_machinery_prepared") is True, "release machinery not prepared")
    for key in ("permanent_release_record_complete","final_reconciliation_complete","all_blocking_defects_closed","ws616_complete"):
        require(completion.get(key) is False, f"{key} claimed early")
    require(completion.get("next_action") == "integrate_ws616_preparation_then_finalize_permanent_release", "next action drift")

    boundaries = source.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability lost")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved":
            require(value is False, f"boundary widened: {key}")
    return failures


def repository_failures(contract: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    ws615 = obj("contracts/workstream6-final-workflow.json")
    require(ws615.get("completion", {}).get("final_workflow_active") is True, "WS6.15 final workflow not active")
    require(ws615.get("completion", {}).get("permanent_release_complete") is False, "WS6.15 snapshot rewritten")
    require(ws615.get("completion", {}).get("next_permitted_work_package") == "WS6.16", "WS6.15 successor drift")
    require(ws615.get("canonical_identity", {}).get("job_name") == EXACT_CHECK, "final check identity drift")

    ledger = obj("repository/workstream6-defect-closure-ledger.json")
    unresolved = {
        item.get("id")
        for item in ledger.get("entries", [])
        if item.get("overlay_state") == "expected_unresolved"
    }
    require(unresolved == {"WS6-BLOCK-006", "WS6-CONSIST-006", "WS6-CONSIST-010"}, "pre-release defect set drift")

    require(not RELEASE_PATH.exists(), "permanent release exists before truthful post-merge finalization")
    require(not FINAL_REPORT.exists(), "final evidence report exists before truthful post-merge finalization")
    require(not FINAL_LEDGER.exists(), "final defect ledger exists before truthful post-merge finalization")

    final_workflow = (ROOT / ".github/workflows/workstream6-final-pre-codex.yml").read_text(encoding="utf-8")
    for token in (
        "name: Final pre-Codex canonical handoff and release",
        f"name: {EXACT_CHECK}",
        "governance/ws616-permanent-release-record",
        "EXPECTED_BASE: main",
        "8ad0ea95b8d01c83347161e4ccf893f1844a219d",
        "WS6.16 exact preparation PR verified",
        "python scripts/require_workstream6_final_reconciliation.py",
    ):
        require(token in final_workflow, f"final workflow missing WS6.16 token: {token}")

    verifier = (ROOT / "scripts/require_workstream6_final_reconciliation.py").read_text(encoding="utf-8")
    for token in (
        "release_parent_main_sha",
        "tested_merge_reference",
        "expected-artifact-digest",
        "merge-base",
        "final_defect_ledger_sha256",
        "codex_start_authorized",
    ):
        require(token in verifier, f"hardened release verifier missing token: {token}")

    require(contract.get("finalization_precondition_count") == 6, "contract precondition count drift")
    require(contract.get("satisfied_finalization_precondition_count") == 1, "contract claimed satisfied preconditions")
    require(contract.get("required_release_binding_field_count") == 9, "contract binding count drift")
    return failures


def main() -> None:
    source = load(SRC)
    failures = source_failures(source)
    if failures:
        raise SystemExit("WS6.16 source validation failed:\n- " + "\n- ".join(failures))

    contract, doc, report = build_records()
    for path, text in ((OUT, canon(contract)), (DOC, doc + "\n"), (REPORT, report + "\n")):
        if path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"stale generated file: {path.relative_to(ROOT)}")

    jsonschema.validate(contract, obj("schemas/workstream6-permanent-release-record.schema.json"))
    failures = repository_failures(contract)
    if failures:
        raise SystemExit("WS6.16 repository validation failed:\n- " + "\n- ".join(failures))

    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda v: v.update(work_package_id="WS6.15"),
        lambda v: v.update(package_state="complete"),
        lambda v: v["predecessor"].update(head_sha="bad"),
        lambda v: v["predecessor"].update(integrated_to_main=False),
        lambda v: v["current_main"].update(observed_sha="0"*40),
        lambda v: v["current_main"].update(integrated_through="WS6.14"),
        lambda v: v["current_main"].update(eligible_for_permanent_release=True),
        lambda v: v["permanent_release"].update(release_id="wrong"),
        lambda v: v["permanent_release"].update(path="wrong"),
        lambda v: v["permanent_release"].update(record_must_be_absent_in_preparation_pr=False),
        lambda v: v["permanent_release"].update(creation_mode="premerge"),
        lambda v: v["permanent_release"].update(finalization_branch="main"),
        lambda v: v["preparation_exception"].update(event="push"),
        lambda v: v["preparation_exception"].update(head_branch="main"),
        lambda v: v["preparation_exception"].update(base_branch="stale-base"),
        lambda v: v["preparation_exception"].update(base_sha="0"*40),
        lambda v: v["preparation_exception"].update(requires_permanent_release=True),
        lambda v: v["preparation_exception"].update(requires_release_absent=False),
        lambda v: v["preparation_exception"].update(must_expire_after_preparation_merge=False),
        lambda v: v["release_binding_contract"].update(main_binding_semantics="wrong"),
        lambda v: v["release_binding_contract"].update(tested_merge_reference_semantics="wrong"),
        lambda v: v["release_binding_contract"].update(final_check_name="wrong"),
        lambda v: v["release_binding_contract"].update(require_successful_current_final_evidence=False),
        lambda v: v["release_binding_contract"].update(predecessor_evidence_may_not_substitute=False),
        lambda v: v["release_binding_contract"].update(required_fields=[]),
        lambda v: v["finalization_preconditions"][0].update(satisfied=False),
        lambda v: v["defects"].update(close_only_after_finalization=[]),
        lambda v: v["defects"].update(manual_remaining_after_release=[]),
        lambda v: v["defects"].update(all_blocking_defects_closed_only_after_release=False),
        lambda v: v["manual_gates"].update(issue_19_complete=True),
        lambda v: v["manual_gates"].update(branch_cleanup_complete=True),
        lambda v: v["completion"].update(release_machinery_prepared=False),
        lambda v: v["completion"].update(permanent_release_record_complete=True),
        lambda v: v["completion"].update(final_reconciliation_complete=True),
        lambda v: v["completion"].update(all_blocking_defects_closed=True),
        lambda v: v["completion"].update(ws616_complete=True),
        lambda v: v["completion"].update(next_action="IMP-P0"),
        lambda v: v["boundaries"].update(codex_start_authorized=True),
        lambda v: v["boundaries"].update(phase0_implementation_authorized=True),
        lambda v: v["boundaries"].update(phase0_merge_authorized=True),
        lambda v: v["boundaries"].update(runtime_activation_authorized=True),
        lambda v: v["boundaries"].update(real_client_data_enabled=True),
        lambda v: v["boundaries"].update(external_actions_authorized=True),
        lambda v: v["boundaries"].update(autonomous_merge_authorized=True),
    ]
    rejected = 0
    for mutate in mutations:
        candidate = copy.deepcopy(source)
        mutate(candidate)
        if source_failures(candidate):
            rejected += 1
        else:
            raise SystemExit("WS6.16 preparation mutation not rejected")

    finalizer_self_test()
    print(
        f"WS6.16 permanent release preparation passed: {rejected} preparation mutations rejected, "
        "preconditions=1/6, release_absent=true, finalizer_self_test=passed, "
        "ws616_complete=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
