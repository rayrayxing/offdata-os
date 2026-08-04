#!/usr/bin/env python3
"""Build restricted deterministic baselines for the Phase 5 fixture tranche."""

from __future__ import annotations

from pathlib import Path

from offdata_core.primary_fixtures import (
    ADDITIONAL_FIXTURE_PATHS,
    build_phase5_fixture_suite,
    grade_phase5_fixture_suite,
    write_phase5_fixture_baselines,
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = repository_root()
    fixtures_root = root / "fixtures"
    suite = build_phase5_fixture_suite(fixtures_root)
    grades = grade_phase5_fixture_suite(suite, fixtures_root)
    destinations = write_phase5_fixture_baselines(fixtures_root)
    for destination in destinations:
        print(f"Wrote {destination.relative_to(root)}")
    print(f"- fixtures={len(suite.fixtures)}")
    print(f"- agent_visible_inputs={sum(len(item.source_checksums) for item in suite.fixtures)}")
    print(f"- source_records={sum(len(item.source_ids) for item in suite.fixtures)}")
    print(f"- calculated_metrics={sum(len(item.metrics) for item in suite.fixtures)}")
    print(f"- grade_checks={sum(item.checks_run for item in grades)}")
    print(f"- fixture_paths={len(ADDITIONAL_FIXTURE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
