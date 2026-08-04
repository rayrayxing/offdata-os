#!/usr/bin/env python3
"""Build the deterministic Phase 4 deliverable semantic baseline."""

from __future__ import annotations

from pathlib import Path

from offdata_core.ai_audit_deliverable import (
    deliverable_semantic_baseline_document,
    write_deliverable_semantic_baseline,
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    fixture = (
        repository_root()
        / "fixtures"
        / "digital-ai"
        / "FIXTURE-DAI-001"
    )
    destination = write_deliverable_semantic_baseline(fixture)
    document = deliverable_semantic_baseline_document(fixture)
    model = document["semantic_model"]
    grade = document["grade"]
    assert isinstance(model, dict)
    assert isinstance(grade, dict)
    print(f"Wrote {destination.relative_to(repository_root())}")
    print(f"- story_sections={len(model['story']['sections'])}")
    print(f"- assertions={len(model['story']['assertions'])}")
    print(f"- numbers={len(model['numbers'])}")
    print(f"- citations={len(model['citations'])}")
    print(f"- visuals={len(model['visuals'])}")
    print(f"- semantic_objects={len(model['semantic_objects'])}")
    print(f"- surface_plans={len(model['surface_plans'])}")
    print(f"- grade_checks={grade['checks_run']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
