from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "configs/workstream6-phase0-licence-decision-placeholder.yaml"
OUT = ROOT / "contracts/phase0-licence-decision-placeholder.json"
DOC = ROOT / "docs/phase0-licence-decision-placeholder.md"
REPORT = ROOT / "reports/workstream6-phase0-licence-decision-placeholder-evidence.md"

def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value

def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"

def build() -> tuple[dict, str, str]:
    source = load(SRC)
    contract = {
        **source,
        "generated_from": "configs/workstream6-phase0-licence-decision-placeholder.yaml",
        "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
    }
    doc = """# Phase 0 licence decision placeholder

> [!CAUTION]
> **NO LICENCE IS SELECTED OR GRANTED BY THIS FILE.** This is a governed decision placeholder only. It does not authorize public distribution, an external licence notice, runtime, production, Codex implementation, or any external action.

## Decision owner and timing

- Decision owner: **Founder**.
- Implementation location: `IMP-P0 / P0.1`.
- The decision must be explicit before public distribution, an external licence notice, or production release.
- Repository-only planning does not imply a licence selection.
- If legal interpretation or compatibility is material, obtain appropriate legal review before selection.

## Options to evaluate

1. Proprietary / all-rights-reserved status.
2. A permissive open-source licence.
3. A copyleft open-source licence.
4. Dual or custom licensing.

None is selected by this placeholder.

## Decision criteria

Evaluate intended distribution, third-party dependency compatibility, commercial/contribution model, patent and trademark considerations, confidentiality/proprietary-material boundaries, and whether legal review is required.

## Evidence required for closure

The final decision record must contain the explicit Founder decision, selected licence identifier or proprietary status, date, scope, dependency-compatibility review, and an approved ADR.

The planned ADR is `docs/adr/ADR-0001-licence-decision.md`, created from `templates/adr.md`.

## Current state

- Selected licence: **none**.
- Implicit licence grant: **false**.
- Public distribution authorized: **false**.
- External licence notice authorized: **false**.
- `codex_start_authorized=false`.

Until the explicit decision record exists, this placeholder remains open decision evidence only.
"""
    report = """# WS6.13 Phase 0 licence placeholder evidence

- Defect: `WS6-CONSIST-009`.
- Owner: `Founder`.
- Selected licence: `none`.
- Implicit licence grant: `false`.
- Public distribution authorized: `false`.
- ADR approved: `false`.
- `codex_start_authorized=false`.
"""
    return contract, doc, report

def main() -> None:
    contract, doc, report = build()
    OUT.write_text(canonical(contract), encoding="utf-8")
    DOC.write_text(doc, encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print(
        "Built WS6.13 licence placeholder: options=4, selected=0, "
        "implicit_grant=false, public_distribution=false, codex_start_authorized=false."
    )

if __name__ == "__main__":
    main()
