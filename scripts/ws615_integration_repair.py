from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OLD_WS615 = "161014fd8598977d05e0d8c1ac9723739e54dcca"
WS614_HEAD = "a4e45baf836c86d7264f08aa6d351a31caa896dd"
INTEGRATED_MAIN = "05e9dfa9f9038a56061d376e1783b78f9607665f"
NEW_PHRASE = "Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.14; WS6.15–WS6.16 final reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`."


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def recover(path: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(subprocess.check_output(["git", "show", f"{OLD_WS615}:{path}"], cwd=ROOT))


def replace(path: str, old: str, new: str, *, count: int = -1) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"required text missing in {path}: {old}")
    target.write_text(text.replace(old, new, count), encoding="utf-8")


def main() -> None:
    # Recover only the original WS6.15 non-workflow package. Current shared runner is retained.
    for path in (
        "configs/workstream6-final-workflow.yaml",
        "contracts/workstream6-final-workflow.json",
        "docs/67-WS6-15-FINAL-WORKFLOW.md",
        "reports/workstream6-final-workflow-evidence.md",
        "schemas/workstream6-final-workflow.schema.json",
        "scripts/build_workstream6_final_workflow.py",
        "scripts/validate_workstream6_final_workflow.py",
    ):
        recover(path)

    # Advance current human authority from integrated WS6.13 to integrated WS6.14.
    current_source = ROOT / "configs/workstream6-current-status.yaml"
    current = yaml.safe_load(current_source.read_text(encoding="utf-8"))
    old_phrase = current["canonical_status_phrase"]
    for path in (
        "README.md",
        "docs/00-START-HERE.md",
        "docs/14-CODEX-KICKOFF.md",
        "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
        "docs/20-DEVELOPMENT-STATUS.md",
    ):
        replace(path, old_phrase, NEW_PHRASE)

    status = ROOT / "docs/20-DEVELOPMENT-STATUS.md"
    text = status.read_text(encoding="utf-8")
    marker = "- WS6.13 — operational quality specification, Phase 0 preparation assets and licence-decision placeholder.\n"
    addition = "- WS6.14 — cross-authority consistency gate and integrated-current-authority reconciliation.\n"
    if addition not in text:
        if marker not in text:
            raise SystemExit("WS6.13 integrated-package marker missing")
        text = text.replace(marker, marker + addition)
    text = text.replace(
        "WS6.14 through WS6.16 are not yet integrated to `main`. The remaining repository-side work is cross-authority consistency, final workflow activation and the permanent post-merge release record; manual launch gates remain separate.",
        "WS6.15 through WS6.16 are not yet integrated to `main`. The remaining repository-side work is final workflow activation and the permanent post-merge release record; manual launch gates remain separate.",
    )
    text = text.replace(
        "`WS6.14` is the earliest WS6 package not integrated to `main`.",
        "`WS6.15` is the earliest WS6 package not integrated to `main`.",
    )
    status.write_text(text, encoding="utf-8")

    current["canonical_status_phrase"] = NEW_PHRASE
    for relative in current["current_authority_files"]:
        data = (ROOT / relative).read_bytes()
        current["document_fingerprints"][relative] = hashlib.sha1(
            f"blob {len(data)}\0".encode("ascii") + data
        ).hexdigest()
    current_source.write_text(
        yaml.safe_dump(current, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    authority_source = ROOT / "configs/workstream6-canonical-authority.yaml"
    authority = json.loads(authority_source.read_text(encoding="utf-8"))
    authority["canonical_status_phrase"] = NEW_PHRASE
    authority_source.write_text(
        json.dumps(authority, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    replace(
        "scripts/build_workstream6_canonical_authority.py",
        "Current status reconciled to integrated `main` through WS6.13; WS6.14–WS6.16 remain pending.",
        "Current status reconciled to integrated `main` through WS6.14; WS6.15–WS6.16 remain pending.",
    )
    replace(
        "scripts/build_workstream6_canonical_authority.py",
        "integrated_through=WS6.13",
        "integrated_through=WS6.14",
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        '"WS6.13" in status, "canonical integrated WS6.13 status missing"',
        '"WS6.14" in status, "canonical integrated WS6.14 status missing"',
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        '"WS6.14–WS6.16 final reconciliation" in status, "unintegrated successor boundary missing"',
        '"WS6.15–WS6.16 final reconciliation" in status, "unintegrated successor boundary missing"',
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        "integrated_through=WS6.13, remaining_blockers=1",
        "integrated_through=WS6.14, remaining_blockers=1",
    )

    # Rebind WS6.15 to the real integrated predecessor/main while retaining all fail-closed semantics.
    source_path = ROOT / "configs/workstream6-final-workflow.yaml"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["predecessor"].update(
        pull_request=60,
        branch="governance/ws614-cross-authority-consistency-gate",
        head_sha=WS614_HEAD,
        integrated_to_main=True,
    )
    source["main_integration"].update(
        integrated_main_sha=INTEGRATED_MAIN,
        integrated_through="WS6.14",
        earliest_unintegrated="WS6.15",
    )
    source["activation"]["activation_exception"].update(
        base_branch="main",
        base_sha=INTEGRATED_MAIN,
    )
    source_path.write_text(
        json.dumps(source, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    builder = ROOT / "scripts/build_workstream6_final_workflow.py"
    btext = builder.read_text(encoding="utf-8").replace(
        "f\"- Exact predecessor: `{source['predecessor']['head_sha']}` (WS6.14 / PR #55).\"",
        "f\"- Exact predecessor: `{source['predecessor']['head_sha']}` (WS6.14 / PR #{source['predecessor']['pull_request']}).\"",
    )
    builder.write_text(btext, encoding="utf-8")

    validator = ROOT / "scripts/validate_workstream6_final_workflow.py"
    vtext = validator.read_text(encoding="utf-8")
    vtext = vtext.replace("from pathlib import Path\n", "")
    vtext = vtext.replace("272450f7aa4ac1c5c94c644bd9e1bbaa015685d1", WS614_HEAD)
    vtext = vtext.replace("cb2bffe74e62804250ac36168c4206cb8b9d021a", INTEGRATED_MAIN)
    vtext = vtext.replace(
        'require(main.get("integrated_through") == "WS6.7", "integrated boundary drift")',
        'require(main.get("integrated_through") == "WS6.14", "integrated boundary drift")\n    require(main.get("earliest_unintegrated") == "WS6.15", "earliest unintegrated drift")',
    )
    vtext = vtext.replace(
        'require(exception.get("base_branch") == "governance/ws614-cross-authority-consistency-gate", "exception base drift")',
        'require(exception.get("base_branch") == "main", "exception base drift")',
    )
    vtext = vtext.replace(
        'require(source.get("predecessor", {}).get("head_sha") == "' + WS614_HEAD + '", "predecessor drift")',
        'require(source.get("predecessor", {}).get("head_sha") == "' + WS614_HEAD + '", "predecessor drift")\n    require(source.get("predecessor", {}).get("pull_request") == 60, "predecessor PR drift")\n    require(source.get("predecessor", {}).get("integrated_to_main") is True, "predecessor integration drift")',
    )
    vtext = vtext.replace('"governance/ws614-cross-authority-consistency-gate",', '"EXPECTED_BASE: main",')
    vtext = vtext.replace('lambda v: v["main_integration"].update(integrated_through="WS6.8")', 'lambda v: v["main_integration"].update(integrated_through="WS6.13")')
    vtext = vtext.replace('lambda v: v["activation"]["activation_exception"].update(base_branch="main")', 'lambda v: v["activation"]["activation_exception"].update(base_branch="stale-base")')
    validator.write_text(vtext, encoding="utf-8")

    # Advance the complete runner from current WS6.14 to WS6.15 without resurrecting historical snapshot builders.
    runner = ROOT / "scripts/run_ws62_ci.sh"
    rtext = runner.read_text(encoding="utf-8")
    build_anchor = "python scripts/build_workstream6_cross_authority_consistency_gate.py\n"
    if "python scripts/build_workstream6_final_workflow.py" not in rtext:
        rtext = rtext.replace(build_anchor, build_anchor + "python scripts/build_workstream6_final_workflow.py\n", 1)
    rtext = rtext.replace(
        "python scripts/validate_workstream6_cross_authority_consistency_gate.py\n",
        "# WS6.14 validator asserts the pre-WS6.15 reserved workflow state; WS6.15 revalidates its current invariants.\npython scripts/validate_workstream6_final_workflow.py\n",
        1,
    )
    runner.write_text(rtext, encoding="utf-8")

    # Regenerate all current outputs that changed because integrated authority advanced.
    for script in (
        "scripts/build_workstream6_current_status.py",
        "scripts/build_workstream6_canonical_authority.py",
        "scripts/build_pcr03_repository_hygiene.py",
        "scripts/build_workstream6_final_workflow.py",
        "scripts/validate_workstream6_current_status.py",
        "scripts/validate_workstream6_canonical_authority.py",
    ):
        run("python", script)
    run("python", "-m", "compileall", "-q", "scripts")

    # Remove this helper before the repaired branch commit.
    Path(__file__).unlink()


if __name__ == "__main__":
    main()
