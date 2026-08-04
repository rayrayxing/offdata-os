#!/usr/bin/env python3
"""Build the deterministic additional primary engagement fixture programme."""

from __future__ import annotations

from pathlib import Path

from offdata_core.fixture_programme import build_fixture_programme, write_programme


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = repository_root()
    seed = root / "fixtures" / "additional-primary-fixture-seeds.yaml"
    destination = root / "fixtures" / "additional-primary-fixtures.json"
    programme = build_fixture_programme(seed)
    write_programme(seed, destination)
    print(f"Wrote {destination.relative_to(root)}")
    print(f"- fixtures={len(programme.fixtures)}")
    print(f"- engagement_types={len({item.engagement_type for item in programme.fixtures})}")
    print(f"- evidence_records={sum(len(item.evidence_records) for item in programme.fixtures)}")
    print(f"- structured_datasets={sum(len(item.structured_data) for item in programme.fixtures)}")
    print(f"- deliberate_data_defects={sum(len(item.data_quality_defects) for item in programme.fixtures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
