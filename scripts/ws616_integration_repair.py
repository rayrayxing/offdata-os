from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OLD_WS616 = "4b8af8285d49c5a31df89b5c69f1e76f60221edf"
WS615_HEAD = "1361fff88bd08ae16218673337621571a7d315c6"
INTEGRATED_MAIN = "8ad0ea95b8d01c83347161e4ccf893f1844a219d"
NEW_PHRASE = "Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.15; WS6.16 permanent release/final reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`."


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def recover(path: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(subprocess.check_output(["git", "show", f"{OLD_WS616}:{path}"], cwd=ROOT))


def replace(path: str, old: str, new: str, *, count: int = -1) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"required text missing in {path}: {old}")
    target.write_text(text.replace(old, new, count), encoding="utf-8")


def main() -> None:
    # Recover the original WS6.16 non-workflow implementation machinery.
    for path in (
        "configs/workstream6-permanent-release-record.yaml",
        "schemas/pre-codex-final-reconciliation.schema.json",
        "schemas/workstream6-permanent-release-record.schema.json",
        "scripts/build_workstream6_permanent_release_record.py",
        "scripts/finalize_workstream6_permanent_release.py",
        "scripts/require_workstream6_final_reconciliation.py",
        "scripts/validate_workstream6_permanent_release_record.py",
    ):
        recover(path)

    # Advance current human authority from integrated WS6.14 to integrated WS6.15.
    current_path = ROOT / "configs/workstream6-current-status.yaml"
    current = yaml.safe_load(current_path.read_text(encoding="utf-8"))
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
    marker = "- WS6.14 — cross-authority consistency gate and integrated-current-authority reconciliation.\n"
    addition = "- WS6.15 — exact final pre-Codex workflow activation with fail-closed permanent-release boundary.\n"
    if addition not in text:
        if marker not in text:
            raise SystemExit("WS6.14 integrated-package marker missing")
        text = text.replace(marker, marker + addition)
    text = text.replace(
        "WS6.15 through WS6.16 are not yet integrated to `main`. The remaining repository-side work is final workflow activation and the permanent post-merge release record; manual launch gates remain separate.",
        "WS6.16 is not yet integrated to `main`. The remaining repository-side work is the permanent post-merge release record and final evidence reconciliation; manual launch gates remain separate.",
    )
    text = text.replace(
        "`WS6.15` is the earliest WS6 package not integrated to `main`.",
        "`WS6.16` is the earliest WS6 package not integrated to `main`.",
    )
    status.write_text(text, encoding="utf-8")

    current["canonical_status_phrase"] = NEW_PHRASE
    for relative in current["current_authority_files"]:
        data = (ROOT / relative).read_bytes()
        current["document_fingerprints"][relative] = hashlib.sha1(
            f"blob {len(data)}\0".encode("ascii") + data
        ).hexdigest()
    current_path.write_text(
        yaml.safe_dump(current, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    authority_path = ROOT / "configs/workstream6-canonical-authority.yaml"
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    authority["canonical_status_phrase"] = NEW_PHRASE
    authority_path.write_text(
        json.dumps(authority, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    replace(
        "scripts/build_workstream6_canonical_authority.py",
        "Current status reconciled to integrated `main` through WS6.14; WS6.15–WS6.16 remain pending.",
        "Current status reconciled to integrated `main` through WS6.15; WS6.16 remains pending.",
    )
    replace(
        "scripts/build_workstream6_canonical_authority.py",
        "integrated_through=WS6.14",
        "integrated_through=WS6.15",
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        '"WS6.14" in status, "canonical integrated WS6.14 status missing"',
        '"WS6.15" in status, "canonical integrated WS6.15 status missing"',
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        '"WS6.15–WS6.16 final reconciliation" in status, "unintegrated successor boundary missing"',
        '"WS6.16 permanent release/final reconciliation" in status, "unintegrated successor boundary missing"',
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        "integrated_through=WS6.14, remaining_blockers=1",
        "integrated_through=WS6.15, remaining_blockers=1",
    )

    # Truthfully rebind WS6.16 preparation to the integrated WS6.15 predecessor.
    source_path = ROOT / "configs/workstream6-permanent-release-record.yaml"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["predecessor"].update(
        pull_request=61,
        branch="governance/ws615-final-workflow",
        head_sha=WS615_HEAD,
        integrated_to_main=True,
    )
    source["current_main"].update(
        observed_sha=INTEGRATED_MAIN,
        integrated_through="WS6.15",
        eligible_for_permanent_release=False,
    )
    source["preparation_exception"].update(
        base_branch="main",
        base_sha=INTEGRATED_MAIN,
    )
    for item in source["finalization_preconditions"]:
        item["satisfied"] = item["id"] == "P1"
    source["completion"]["next_action"] = "integrate_ws616_preparation_then_finalize_permanent_release"
    source_path.write_text(
        json.dumps(source, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Make builder/report/counts dynamic now that P1 is truthfully satisfied.
    builder = ROOT / "scripts/build_workstream6_permanent_release_record.py"
    btext = builder.read_text(encoding="utf-8")
    btext = btext.replace(
        'f"- Finalization preconditions satisfied: `0/{len(source[\'finalization_preconditions\'])}`.",',
        'f"- Finalization preconditions satisfied: `{sum(1 for item in source[\'finalization_preconditions\'] if item[\'satisfied\'] is True)}/{len(source[\'finalization_preconditions\'])}`.",',
    )
    btext = btext.replace(
        '"Built WS6.16 permanent release preparation: preconditions=0/6, "',
        'f"Built WS6.16 permanent release preparation: preconditions={contract[\'satisfied_finalization_precondition_count\']}/{contract[\'finalization_precondition_count\']}, "',
    )
    builder.write_text(btext, encoding="utf-8")

    # Advance preparation schema/count and deterministic validator to integrated reality.
    schema_path = ROOT / "schemas/workstream6-permanent-release-record.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["properties"]["satisfied_finalization_precondition_count"] = {"const": 1}
    schema_path.write_text(json.dumps(schema, separators=(",", ":")) + "\n", encoding="utf-8")

    validator = ROOT / "scripts/validate_workstream6_permanent_release_record.py"
    vtext = validator.read_text(encoding="utf-8")
    replacements = {
        "161014fd8598977d05e0d8c1ac9723739e54dcca": WS615_HEAD,
        "cb2bffe74e62804250ac36168c4206cb8b9d021a": INTEGRATED_MAIN,
        'pred.get("pull_request") == 56': 'pred.get("pull_request") == 61',
        'pred.get("integrated_to_main") is False': 'pred.get("integrated_to_main") is True',
        'main.get("integrated_through") == "WS6.7"': 'main.get("integrated_through") == "WS6.15"',
        'exc.get("base_branch") == "governance/ws615-final-workflow"': 'exc.get("base_branch") == "main"',
        'require(all(item.get("satisfied") is False for item in preconditions), "finalization precondition claimed early")': 'require([item.get("satisfied") for item in preconditions] == [True, False, False, False, False, False], "finalization precondition truth drift")',
        'completion.get("next_action") == "integrate_predecessor_chain_then_finalize_permanent_release"': 'completion.get("next_action") == "integrate_ws616_preparation_then_finalize_permanent_release"',
        'contract.get("satisfied_finalization_precondition_count") == 0': 'contract.get("satisfied_finalization_precondition_count") == 1',
        'preconditions=0/6': 'preconditions=1/6',
    }
    for old, new in replacements.items():
        if old not in vtext:
            raise SystemExit(f"WS6.16 validator replacement source missing: {old}")
        vtext = vtext.replace(old, new)
    # Mutation that used to flip P1 true must now flip it false.
    vtext = vtext.replace(
        'lambda v: v["finalization_preconditions"][0].update(satisfied=True)',
        'lambda v: v["finalization_preconditions"][0].update(satisfied=False)',
    )
    validator.write_text(vtext, encoding="utf-8")

    # Advance the complete runner through WS6.16 preparation.
    runner = ROOT / "scripts/run_ws62_ci.sh"
    rtext = runner.read_text(encoding="utf-8")
    build_anchor = "python scripts/build_workstream6_final_workflow.py\n"
    if "python scripts/build_workstream6_permanent_release_record.py" not in rtext:
        rtext = rtext.replace(build_anchor, build_anchor + "python scripts/build_workstream6_permanent_release_record.py\n", 1)
    if "python scripts/validate_workstream6_final_workflow.py\n" in rtext:
        rtext = rtext.replace(
            "python scripts/validate_workstream6_final_workflow.py\n",
            "# WS6.15 validator asserts the activation-package boundary; WS6.16 revalidates its current invariants.\npython scripts/validate_workstream6_permanent_release_record.py\n",
            1,
        )
    runner.write_text(rtext, encoding="utf-8")

    # Regenerate current outputs and WS6.16 preparation artifacts.
    for script in (
        "scripts/build_workstream6_current_status.py",
        "scripts/build_workstream6_canonical_authority.py",
        "scripts/build_pcr03_repository_hygiene.py",
        "scripts/build_workstream6_permanent_release_record.py",
        "scripts/validate_workstream6_current_status.py",
        "scripts/validate_workstream6_canonical_authority.py",
    ):
        run("python", script)
    run("python", "scripts/finalize_workstream6_permanent_release.py", "--self-test")
    run("python", "-m", "compileall", "-q", "scripts")

    # No permanent outputs may exist in the preparation branch.
    for rel in (
        "releases/pre-codex-final-reconciliation-2026-08-06.json",
        "reports/workstream6-final-evidence.md",
        "repository/workstream6-final-defect-closure-ledger.json",
    ):
        if (ROOT / rel).exists():
            raise SystemExit(f"preparation branch unexpectedly contains {rel}")

    Path(__file__).unlink()


if __name__ == "__main__":
    main()
