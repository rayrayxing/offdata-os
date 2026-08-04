#!/usr/bin/env python3
"""Build the deterministic Phase 6 knowledge-ingestion intelligence baseline."""
from pathlib import Path
from offdata_core.knowledge_ingestion import build_baseline, write_baseline

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "knowledge/knowledge-ingestion-baseline.json"

if __name__ == "__main__":
    baseline = build_baseline(ROOT)
    write_baseline(ROOT, DESTINATION)
    print(f"Wrote {DESTINATION.relative_to(ROOT)}")
    print(f"- source_profiles={len(baseline.source_profiles)}")
    print(f"- method_headings={len(baseline.method_index)}")
    print(f"- retrieval_cases={len(baseline.retrieval_cases)}")
    print(f"- aliases={baseline.alias_count}")
    print(f"- dependency_cases={baseline.dependency_case_count}")
    print(f"- collision_families={baseline.collision_family_count}")
    print(f"- method_record_examples={baseline.method_record_example_count}")
    print(f"- radar_categories={baseline.radar_category_count}")
