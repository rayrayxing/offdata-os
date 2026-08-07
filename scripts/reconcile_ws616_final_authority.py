from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OLD_STATUS = "Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.15; WS6.16 permanent release/final reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`."
FINAL_STATUS = "Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.16; the permanent Workstream 6 release/final reconciliation is complete; all manual launch gates remain pending; `codex_start_authorized=false`."
CURRENT_STATUS_FILES = [
    "README.md",
    "docs/00-START-HERE.md",
    "docs/14-CODEX-KICKOFF.md",
    "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
    "docs/20-DEVELOPMENT-STATUS.md",
]
ISSUE19 = "handoff/codex-phase0-hosted-controls-issue-final.md"


def replace(relative: str, old: str, new: str, *, count: int | None = None) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    observed = text.count(old)
    if observed == 0:
        raise SystemExit(f"expected text not found in {relative}: {old[:100]!r}")
    if count is not None and observed != count:
        raise SystemExit(f"unexpected replacement count in {relative}: expected {count}, got {observed}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def blob_sha(relative: str) -> str:
    data = (ROOT / relative).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def update_yaml(relative: str, mutate) -> None:
    path = ROOT / relative
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{relative} must be a mapping")
    mutate(value)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")


def main() -> None:
    release = ROOT / "releases/pre-codex-final-reconciliation-2026-08-06.json"
    if not release.is_file():
        raise SystemExit("permanent WS6.16 release is required")

    for relative in CURRENT_STATUS_FILES:
        replace(relative, OLD_STATUS, FINAL_STATUS, count=1)

    replace(
        "README.md",
        "- Required future branch-protection check: `Validate final pre-Codex canonical handoff and complete release`.",
        "- Active final check identity: `Validate final pre-Codex canonical handoff and complete release`; hosted branch-protection enforcement remains an issue #19 manual gate.",
        count=1,
    )
    replace(
        "README.md",
        "- Required permanent final release: `releases/pre-codex-final-reconciliation-2026-08-06.json`.",
        "- Permanent final release: `releases/pre-codex-final-reconciliation-2026-08-06.json`.",
        count=1,
    )
    replace(
        "README.md",
        "The phase namespace contract separates chat-first packages from `IMP-P0–12`. The workflow-identity contract reserves the exact future branch-protection check and remains manual-only and deliberately fail-closed until WS6.15 activates it. The authority registry classifies every current read-order item and retained evidence surface.",
        "The phase namespace contract separates chat-first packages from `IMP-P0–12`. The workflow-identity contract defines the exact active final check identity; WS6.15 activated the workflow and WS6.16 bound the permanent release, while hosted enforcement remains an issue #19 manual gate. The authority registry classifies every current read-order item and retained evidence surface.",
        count=1,
    )

    replace(
        "docs/00-START-HERE.md",
        "10. the future permanent release `releases/pre-codex-final-reconciliation-2026-08-06.json`.",
        "10. the permanent release `releases/pre-codex-final-reconciliation-2026-08-06.json`.",
        count=1,
    )
    replace(
        "docs/00-START-HERE.md",
        "The phase namespace contract defines `CF-P1–7`, `PCR-01–10`, `WS-*` and `IMP-P0–12`. The workflow-identity contract reserves the exact future check `Validate final pre-Codex canonical handoff and complete release`; the reserved workflow is manual-only and deliberately fails until WS6.15 activates it.",
        "The phase namespace contract defines `CF-P1–7`, `PCR-01–10`, `WS-*` and `IMP-P0–12`. The workflow-identity contract defines the exact active check `Validate final pre-Codex canonical handoff and complete release`; WS6.15 activated it and WS6.16 completed the permanent release, while hosted enforcement remains pending in issue #19.",
        count=1,
    )

    replace(
        "docs/14-CODEX-KICKOFF.md",
        "- `releases/pre-codex-final-reconciliation-2026-08-06.json` after it exists and passes the independent gate;",
        "- `releases/pre-codex-final-reconciliation-2026-08-06.json`, which now exists and passes the independent gate;",
        count=1,
    )
    replace(
        "docs/14-CODEX-KICKOFF.md",
        "The namespace contract makes `IMP-P0` the canonical implementation phase identifier and retains older filenames and machine keys only for compatibility. The workflow-identity contract reserves the exact final check, but its canonical workflow remains manual-only and fail-closed until WS6.15.",
        "The namespace contract makes `IMP-P0` the canonical implementation phase identifier and retains older filenames and machine keys only for compatibility. The workflow-identity contract defines the exact final check; WS6.15 activated its canonical workflow and WS6.16 bound the permanent release. Hosted branch-protection enforcement remains a manual issue #19 gate.",
        count=1,
    )

    replace(
        "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
        "- the future permanent release `releases/pre-codex-final-reconciliation-2026-08-06.json`;",
        "- the permanent release `releases/pre-codex-final-reconciliation-2026-08-06.json`;",
        count=1,
    )
    replace(
        "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
        "The required hosted status check is exactly `Validate final pre-Codex canonical handoff and complete release`. WS6.6 reserves that identity in `.github/workflows/workstream6-final-pre-codex.yml`; the workflow remains manual-only and deliberately fail-closed until WS6.15 activates the final implementation.",
        "The required hosted status check is exactly `Validate final pre-Codex canonical handoff and complete release`. WS6.6 reserved that identity, WS6.15 activated `.github/workflows/workstream6-final-pre-codex.yml`, and WS6.16 bound the permanent release. Hosted enforcement still requires issue #19 evidence.",
        count=1,
    )

    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "- WS6.15 — exact final pre-Codex workflow activation with fail-closed permanent-release boundary.\n",
        "- WS6.15 — exact final pre-Codex workflow activation with fail-closed permanent-release boundary.\n- WS6.16 — exact preparation acceptance, permanent post-merge release record and final evidence reconciliation.\n",
        count=1,
    )
    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "The reserved workflow is manual-only and deliberately fails closed; WS6.15 must activate its final implementation, WS6.16 must bind the permanent release, and issue #19 must still evidence hosted enforcement.",
        "WS6.15 activated the final workflow and WS6.16 bound the permanent release; issue #19 must still evidence hosted enforcement.",
        count=1,
    )
    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "`WS6-BLOCK-006` remains open until the permanent post-merge final release is produced in WS6.16.",
        "`WS6-BLOCK-006` was closed by the WS6.16 permanent release; `WS6-CONSIST-006` remains the separate manual branch-cleanup gate.",
        count=1,
    )
    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "- `.github/workflows/workstream6-final-pre-codex.yml` — reserved manual-only, fail-closed final workflow identity;",
        "- `.github/workflows/workstream6-final-pre-codex.yml` — active fail-closed final workflow identity;",
        count=1,
    )
    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "- `releases/pre-codex-final-reconciliation-2026-08-06.json` — required future permanent final release.",
        "- `releases/pre-codex-final-reconciliation-2026-08-06.json` — current permanent final Workstream 6 release.",
        count=1,
    )
    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "The exact required future branch-protection check, reserved but not yet activated or enforced, is:",
        "The exact active final check identity, with hosted branch-protection enforcement still to be evidenced in issue #19, is:",
        count=1,
    )
    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "WS6.16 is not yet integrated to `main`. The remaining repository-side work is the permanent post-merge release record and final evidence reconciliation; manual launch gates remain separate.",
        "WS6.0–WS6.16 are integrated and the permanent post-merge release record/final evidence reconciliation is complete. No repository-side WS6 package remains; manual launch gates remain separate.",
        count=1,
    )
    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "3. WS6.15 activates the canonical final workflow and branch protection requires `Validate final pre-Codex canonical handoff and complete release`;",
        "3. hosted branch protection is verified to require `Validate final pre-Codex canonical handoff and complete release`;",
        count=1,
    )
    replace(
        "docs/20-DEVELOPMENT-STATUS.md",
        "## Earliest unintegrated package\n\n`WS6.16` is the earliest WS6 package not integrated to `main`. Any later draft package remains dependent on ordered integration and exact predecessor revalidation.",
        "## Earliest unintegrated package\n\nNone. WS6.0–WS6.16 and the permanent release record are integrated. The remaining launch gates are manual and do not constitute another WS6 repository package.",
        count=1,
    )

    replace(
        ISSUE19,
        "<!-- Canonical issue #19 body for WS6.6. Keep synchronized through the WS6.6 gate. -->",
        "<!-- Current canonical issue #19 body after WS6.16 permanent release. -->",
        count=1,
    )
    replace(ISSUE19, "- [ ] All remaining WS6 packages are integrated.", "- [x] All WS6.0–WS6.16 packages are integrated.", count=1)
    replace(
        ISSUE19,
        "- [ ] `releases/pre-codex-final-reconciliation-2026-08-06.json` exists and passes `scripts/require_workstream6_final_reconciliation.py`.",
        "- [x] `releases/pre-codex-final-reconciliation-2026-08-06.json` exists and passes `scripts/require_workstream6_final_reconciliation.py`.",
        count=1,
    )
    replace(
        ISSUE19,
        "- [ ] WS6.15 has activated `.github/workflows/workstream6-final-pre-codex.yml`; until then the reserved workflow remains manual-only and deliberately fail-closed.",
        "- [x] WS6.15 activated `.github/workflows/workstream6-final-pre-codex.yml`; hosted enforcement of the exact check remains to be evidenced below.",
        count=1,
    )
    replace(
        ISSUE19,
        "The latest successful complete gate for the exact pull-request merge reference is predecessor evidence. Record the final release, run, job, artifact and digest evidence only after the final WS6 package is merged.",
        "The permanent WS6.16 release and exact preparation evidence are retained in `releases/pre-codex-final-reconciliation-2026-08-06.json` and `reports/workstream6-final-evidence.md`. Manual hosted controls, branch cleanup, clean macOS, exact-SHA Founder approval and the local permit remain pending.",
        count=1,
    )
    replace(
        ISSUE19,
        "Until the permanent final release, completed issue evidence, exact-SHA approval and permit all exist:",
        "Until completed issue evidence, exact-SHA approval and permit all exist:",
        count=1,
    )

    def mutate_current_status(value: dict) -> None:
        value["canonical_status_phrase"] = FINAL_STATUS
        value["document_fingerprints"] = {
            relative: blob_sha(relative)
            for relative in value["current_authority_files"]
        }

    update_yaml("configs/workstream6-current-status.yaml", mutate_current_status)

    def mutate_authority(value: dict) -> None:
        value["canonical_status_phrase"] = FINAL_STATUS
        for item in value.get("exact_records", []):
            if item.get("path") == ".github/workflows/workstream6-final-pre-codex.yml":
                item["reason"] = "Active exact final pre-Codex workflow identity; WS6.15 activated it and WS6.16 bound the permanent release, while hosted enforcement remains an issue #19 manual gate."
                break
        else:
            raise SystemExit("final workflow authority record missing")

    update_yaml("configs/workstream6-canonical-authority.yaml", mutate_authority)

    def mutate_handoff(value: dict) -> None:
        boundaries = value.get("boundaries", {})
        if "final_workstream6_gate_complete" not in boundaries:
            raise SystemExit("handoff final Workstream 6 boundary missing")
        boundaries["final_workstream6_gate_complete"] = True

    update_yaml("configs/codex-handoff.yaml", mutate_handoff)

    replace(
        "scripts/build_ws61_codex_handoff.py",
        '    "workstream5_launch_control_merged_to_main",\n}',
        '    "workstream5_launch_control_merged_to_main",\n    "workstream6_final_reconciliation_merged_to_main",\n}',
        count=1,
    )
    replace(
        "scripts/build_ws61_codex_handoff.py",
        '    readiness.update(\n        {\n            "final_workstream6_gate_complete": False,',
        '    final_release_path = ROOT / "releases" / "pre-codex-final-reconciliation-2026-08-06.json"\n    final_release = _load_json(final_release_path) if final_release_path.is_file() else {}\n    final_workstream6_gate_complete = (\n        final_release.get("work_package_id") == "WS6.16"\n        and final_release.get("final_reconciliation_complete") is True\n        and final_release.get("all_blocking_defects_closed") is True\n        and final_release.get("codex_start_authorized") is False\n    )\n    readiness.update(\n        {\n            "final_workstream6_gate_complete": final_workstream6_gate_complete,',
        count=1,
    )

    replace(
        "scripts/validate_ws61_codex_handoff.py",
        '    for key, value in boundaries.items():\n        if key != "founder_accountability_preserved" and value is not False:\n            failures.append(f"boundary {key} must remain false")',
        '    for key, value in boundaries.items():\n        if key == "founder_accountability_preserved":\n            continue\n        if key == "final_workstream6_gate_complete":\n            if value is not True:\n                failures.append("final Workstream 6 gate must be complete after WS6.16")\n            continue\n        if value is not False:\n            failures.append(f"boundary {key} must remain false")',
        count=1,
    )
    replace(
        "scripts/validate_ws61_codex_handoff.py",
        '    for field in (\n        "final_workstream6_gate_complete",\n        "hosted_controls_verified",\n        "clean_macos_environment_verified",\n        "explicit_founder_phase0_approval_received",\n        "launch_permit_issued",\n        "codex_start_authorized",\n    ):\n        if readiness.get(field) is not False:\n            failures.append(f"readiness field {field} must remain false")',
        '    if readiness.get("final_workstream6_gate_complete") is not True:\n        failures.append("final Workstream 6 readiness gate must be complete")\n    for field in (\n        "hosted_controls_verified",\n        "clean_macos_environment_verified",\n        "explicit_founder_phase0_approval_received",\n        "launch_permit_issued",\n        "codex_start_authorized",\n    ):\n        if readiness.get(field) is not False:\n            failures.append(f"readiness field {field} must remain false")',
        count=1,
    )
    replace(
        "scripts/validate_ws61_codex_handoff.py",
        '    for condition in EXPECTED_ACTIVATION[:10]:\n        if activation_status.get(condition) is not True:\n            failures.append(f"merged repository condition {condition} must be true")\n    for condition in EXPECTED_ACTIVATION[10:]:\n        if activation_status.get(condition) is not False:\n            failures.append(f"pending condition {condition} must remain false")\n    if readiness.get("activation_blockers") != EXPECTED_ACTIVATION[10:]:\n        failures.append("activation blockers must be the five remaining gates")',
        '    for condition in EXPECTED_ACTIVATION[:11]:\n        if activation_status.get(condition) is not True:\n            failures.append(f"merged repository condition {condition} must be true")\n    for condition in EXPECTED_ACTIVATION[11:]:\n        if activation_status.get(condition) is not False:\n            failures.append(f"pending condition {condition} must remain false")\n    if readiness.get("activation_blockers") != EXPECTED_ACTIVATION[11:]:\n        failures.append("activation blockers must be the four remaining manual gates")',
        count=1,
    )

    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        '    require(isinstance(status, str) and "WS6.15" in status, "canonical integrated WS6.15 status missing")\n    require(isinstance(status, str) and "WS6.16 permanent release/final reconciliation" in status, "unintegrated successor boundary missing")',
        '    require(isinstance(status, str) and "WS6.16" in status, "canonical integrated WS6.16 status missing")\n    require(isinstance(status, str) and "permanent Workstream 6 release/final reconciliation is complete" in status, "completed permanent release boundary missing")',
        count=1,
    )
    replace(
        "scripts/build_workstream6_canonical_authority.py",
        '"- Remaining blocking defect: `WS6-BLOCK-006`", "- Current status reconciled to integrated `main` through WS6.15; WS6.16 remains pending.", "- Every authority and implementation boundary remains fail-closed.",',
        '"- Historical WS6.4 closure snapshot: `WS6-BLOCK-006` was still pending at package time.", "- Current successor status is integrated through WS6.16 with the permanent release complete; manual launch gates remain pending.", "- Every authority and implementation boundary remains fail-closed.",',
        count=1,
    )
    replace(
        "scripts/build_workstream6_canonical_authority.py",
        'integrated_through=WS6.15, codex_start_authorized=false.',
        'integrated_through=WS6.16, permanent_release_complete=true, codex_start_authorized=false.',
        count=1,
    )
    replace(
        "scripts/build_workstream6_current_status.py",
        '"- Closed defects: `WS6-BLOCK-003`, `WS6-CONSIST-008`","- Remaining blocking defect: `WS6-BLOCK-006`","- Final release, hosted controls, branch cleanup, clean macOS, Founder approval and permit remain pending.","- `codex_start_authorized=false`; implementation, merge and Phase 1 remain unauthorized.","","## Document fingerprints","",',
        '"- Closed defects: `WS6-BLOCK-003`, `WS6-CONSIST-008`","- Historical WS6.3 remaining blocker: `WS6-BLOCK-006` (closed later by the WS6.16 permanent release).","- Current successor status is represented by the canonical status phrase; WS6.3 package completion fields remain historical.","- `codex_start_authorized=false`; implementation, merge and Phase 1 remain unauthorized.","","## Document fingerprints","",',
        count=1,
    )
    replace(
        "scripts/build_workstream6_current_status.py",
        '"Next permitted work package: `WS6.4`.","",',
        '"Historical WS6.3 next permitted work package: `WS6.4`.","",',
        count=1,
    )

    replace(
        ".github/workflows/workstream6-final-launch-control.yml",
        "                  assert pr['head']['ref'] == 'release/ws616-permanent-release-record'\n                  assert pr['base']['ref'] == 'main'\n                  assert pr['base']['sha'] == release['release_parent_main_sha']\n                  assert main_ref['object']['sha'] == release['release_parent_main_sha']",
        "                  assert pr['base']['ref'] == 'main'\n                  assert main_ref['object']['sha'] == pr['base']['sha']",
        count=1,
    )

    print("WS6.16 final authority reconciliation sources updated; generated outputs must now be rebuilt.")


if __name__ == "__main__":
    main()
