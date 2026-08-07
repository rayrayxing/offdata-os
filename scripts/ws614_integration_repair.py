from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OLD_WS614 = "272450f7aa4ac1c5c94c644bd9e1bbaa015685d1"
INTEGRATED_MAIN = "141ac6ab458fa7354f9b3f8cc57a887f3fceac21"
WS613_HEAD = "e22a8357c98c31b62c654ba3734b51b5671232f7"
OLD_PHRASE = "Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.7; later WS6 work remains unintegrated, final Workstream 6 reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`."
NEW_PHRASE = "Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.13; WS6.14–WS6.16 final reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`."


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def capture(*args: str) -> bytes:
    return subprocess.check_output(args, cwd=ROOT)


def recover(path: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(capture("git", "show", f"{OLD_WS614}:{path}"))


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"required replacement source missing in {path}: {old}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    # Recover the WS6.14 package files that are safe for an Actions token to modify.
    for path in (
        "configs/workstream6-cross-authority-consistency-gate.yaml",
        "schemas/workstream6-cross-authority-consistency-gate.schema.json",
        "scripts/build_workstream6_cross_authority_consistency_gate.py",
        "scripts/validate_workstream6_cross_authority_consistency_gate.py",
        "scripts/run_ws62_ci.sh",
    ):
        recover(path)

    # Advance all human current-status surfaces from the pre-integration WS6.7 snapshot.
    for path in (
        "README.md",
        "docs/00-START-HERE.md",
        "docs/14-CODEX-KICKOFF.md",
        "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
        "docs/20-DEVELOPMENT-STATUS.md",
    ):
        replace(path, OLD_PHRASE, NEW_PHRASE)

    status = ROOT / "docs/20-DEVELOPMENT-STATUS.md"
    text = status.read_text(encoding="utf-8")
    marker = "- WS6.7 — configuration contradictions and zero-spend committed defaults.\n"
    additions = (
        "- WS6.8 — issue and backlog normalization;\n"
        "- WS6.9 — implementation-obligation map;\n"
        "- WS6.10 — developer experience specification;\n"
        "- WS6.11 — Founder experience specification;\n"
        "- WS6.12 — deliverable quality implementation specification and renderer preparation;\n"
        "- WS6.13 — operational quality specification, Phase 0 preparation assets and licence-decision placeholder.\n"
    )
    if additions not in text:
        if marker not in text:
            raise SystemExit("WS6.7 integrated-package marker missing")
        text = text.replace(marker, marker + additions)
    text = text.replace(
        "WS6.8 through WS6.16 are not integrated to `main`. Draft stacked packages may be prepared sequentially, but they do not change integration authority or permit later packages to merge ahead of predecessors. The remaining work includes issue/backlog normalization, implementation obligations, developer and Founder experience specifications, deliverable and operational quality preparation, cross-authority consistency, final workflow activation, permanent evidence reconciliation and the post-merge release.",
        "WS6.14 through WS6.16 are not yet integrated to `main`. The remaining repository-side work is cross-authority consistency, final workflow activation and the permanent post-merge release record; manual launch gates remain separate.",
    )
    text = text.replace(
        "`WS6.8` is the earliest WS6 package not integrated to `main`.",
        "`WS6.14` is the earliest WS6 package not integrated to `main`.",
    )
    status.write_text(text, encoding="utf-8")

    # WS6.3 remains historical provenance, but its named current surfaces must fingerprint today's truth.
    current_source = ROOT / "configs/workstream6-current-status.yaml"
    current = yaml.safe_load(current_source.read_text(encoding="utf-8"))
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

    gate_source = ROOT / "configs/workstream6-cross-authority-consistency-gate.yaml"
    gate = json.loads(gate_source.read_text(encoding="utf-8"))
    gate["predecessor"]["head_sha"] = WS613_HEAD
    gate["predecessor"]["integrated_to_main"] = True
    gate["main_integration"]["integrated_main_sha"] = INTEGRATED_MAIN
    gate["main_integration"]["integrated_through"] = "WS6.13"
    gate["main_integration"]["earliest_unintegrated"] = "WS6.14"
    gate["canonical_status_phrase"] = NEW_PHRASE
    gate["authority_domains"][0]["assertion"] = "main_integrated_through_ws613_exact"
    gate_source.write_text(
        json.dumps(gate, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # The WS6.4 source remains provenance; its builder/validator validate current semantics.
    replace(
        "scripts/build_workstream6_canonical_authority.py",
        "Current status reconciled to integrated `main` through WS6.7; later WS6 packages remain unintegrated.",
        "Current status reconciled to integrated `main` through WS6.13; WS6.14–WS6.16 remain pending.",
    )
    replace(
        "scripts/build_workstream6_canonical_authority.py",
        "integrated_through=WS6.7",
        "integrated_through=WS6.13",
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        '"WS6.7" in status, "canonical integrated WS6.7 status missing"',
        '"WS6.13" in status, "canonical integrated WS6.13 status missing"',
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        '"later WS6 work remains unintegrated" in status, "unintegrated successor boundary missing"',
        '"WS6.14–WS6.16 final reconciliation" in status, "unintegrated successor boundary missing"',
    )
    replace(
        "scripts/validate_workstream6_canonical_authority.py",
        "integrated_through=WS6.7, remaining_blockers=1",
        "integrated_through=WS6.13, remaining_blockers=1",
    )

    builder = ROOT / "scripts/build_workstream6_cross_authority_consistency_gate.py"
    btext = builder.read_text(encoding="utf-8").replace(
        "f\"- Integrated main: `{source['main_integration']['integrated_main_sha']}` through `WS6.7`.\"",
        "f\"- Integrated main: `{source['main_integration']['integrated_main_sha']}` through `{source['main_integration']['integrated_through']}`.\"",
    )
    builder.write_text(btext, encoding="utf-8")

    validator = ROOT / "scripts/validate_workstream6_cross_authority_consistency_gate.py"
    vtext = validator.read_text(encoding="utf-8")
    replacements = {
        '"5a7c39f55c9d2e69e1be45894dfb82db53af4fa8"': f'"{WS613_HEAD}"',
        '"cb2bffe74e62804250ac36168c4206cb8b9d021a"': f'"{INTEGRATED_MAIN}"',
        'main.get("integrated_through")=="WS6.7"': 'main.get("integrated_through")=="WS6.13"',
        'main.get("earliest_unintegrated")=="WS6.8"': 'main.get("earliest_unintegrated")=="WS6.14"',
        '"WS6.7" in source.get("canonical_status_phrase","") and "later WS6 work remains unintegrated" in source.get("canonical_status_phrase","")': '"WS6.13" in source.get("canonical_status_phrase","") and "WS6.14–WS6.16 final reconciliation" in source.get("canonical_status_phrase","")',
        'v["main_integration"].update(integrated_through="WS6.8")': 'v["main_integration"].update(integrated_through="WS6.12")',
        'v["main_integration"].update(earliest_unintegrated="WS6.9")': 'v["main_integration"].update(earliest_unintegrated="WS6.13")',
        "integrated_through=WS6.7": "integrated_through=WS6.13",
    }
    for old, new in replacements.items():
        vtext = vtext.replace(old, new)
    validator.write_text(vtext, encoding="utf-8")

    # Generate all deterministic current outputs and validate the reconstructed authority model.
    for script in (
        "scripts/build_workstream6_current_status.py",
        "scripts/build_workstream6_canonical_authority.py",
        "scripts/build_pcr03_repository_hygiene.py",
        "scripts/build_workstream6_cross_authority_consistency_gate.py",
        "scripts/validate_workstream6_current_status.py",
        "scripts/validate_workstream6_canonical_authority.py",
        "scripts/validate_workstream6_cross_authority_consistency_gate.py",
    ):
        run("python", script)
    run("python", "-m", "compileall", "-q", "scripts")

    # Remove this non-authoritative helper before the branch commit.
    Path(__file__).unlink()


if __name__ == "__main__":
    main()
