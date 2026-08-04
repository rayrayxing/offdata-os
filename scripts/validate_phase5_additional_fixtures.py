#!/usr/bin/env python3
"""Validate the Phase 5 strategy and cost primary fixture tranche."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from offdata_core.fixture_suite import fixture_suite_document, validate_primary_fixture


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = repository_root()
    strategy = validate_primary_fixture(root / "fixtures/strategy/FIXTURE-STRAT-001")
    cost = validate_primary_fixture(root / "fixtures/cost-productivity/FIXTURE-COST-001")
    suite = fixture_suite_document(root)

    if suite["fixture_ids"] != ["FIXTURE-STRAT-001", "FIXTURE-COST-001"]:
        raise ValueError("Phase 5 fixture order or scope changed unexpectedly.")
    if strategy.evidence_rows != 25:
        raise ValueError("STRAT-001 evidence row count changed unexpectedly.")
    if cost.evidence_rows != 24:
        raise ValueError("COST-001 evidence row count changed unexpectedly.")
    if len(strategy.checks) != 12 or len(cost.checks) != 12:
        raise ValueError("Fixture validation check set is incomplete.")

    print("PHASE 5 ADDITIONAL ENGAGEMENT FIXTURE VALIDATION PASSED")
    print("- fixtures=2")
    print(f"- strategy_sources={strategy.source_count}")
    print(f"- strategy_evidence_rows={strategy.evidence_rows}")
    print(f"- cost_sources={cost.source_count}")
    print(f"- cost_evidence_rows={cost.evidence_rows}")
    print(f"- checks={len(strategy.checks) + len(cost.checks)}")
    print(f"- suite_digest={suite['suite_digest']}")
    print("- restricted_oracles=2")
    print("- answer_key_leaks=0")
    print("- untrusted_sources=2")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"PHASE 5 ADDITIONAL ENGAGEMENT FIXTURE VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
