#!/usr/bin/env python3
"""Generate the restricted deterministic Phase 3 AI-audit oracle baseline."""

from __future__ import annotations

from pathlib import Path

from offdata_core.ai_audit_oracle import baseline_document, write_oracle_baseline


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = repository_root()
    fixture = root / "fixtures" / "digital-ai" / "FIXTURE-DAI-001"
    destination = write_oracle_baseline(fixture)
    document = baseline_document(fixture)
    oracle = document["oracle"]
    grade = document["grade"]
    if not isinstance(oracle, dict) or not isinstance(grade, dict):
        raise ValueError("Generated baseline has an invalid shape.")
    source_checksums = oracle.get("source_checksums")
    evidence_findings = oracle.get("evidence_findings")
    use_cases = oracle.get("use_cases")
    checks_run = grade.get("checks_run")
    if not isinstance(source_checksums, list):
        raise ValueError("Generated source checksums are invalid.")
    if not isinstance(evidence_findings, list):
        raise ValueError("Generated evidence findings are invalid.")
    if not isinstance(use_cases, list):
        raise ValueError("Generated use cases are invalid.")
    if not isinstance(checks_run, int):
        raise ValueError("Generated grade checks are invalid.")
    print(f"Wrote {destination.relative_to(root)}")
    print(f"- source_checksums={len(source_checksums)}")
    print(f"- evidence_findings={len(evidence_findings)}")
    print(f"- use_cases={len(use_cases)}")
    print(f"- grade_checks={checks_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
