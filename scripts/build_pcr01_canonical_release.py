#!/usr/bin/env python3
"""Build the deterministic PCR-01 canonical Phase 1-7 release manifest."""

from pathlib import Path

from offdata_core.release_reconciliation import (
    build_canonical_release_manifest,
    write_canonical_release_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "releases" / "canonical-chat-first-phase1-7-release.json"


if __name__ == "__main__":
    manifest = build_canonical_release_manifest(ROOT)
    write_canonical_release_manifest(ROOT, DESTINATION)
    print(f"Wrote {DESTINATION.relative_to(ROOT)}")
    print(f"- release_id={manifest.release_id}")
    print(f"- governed_records={len(manifest.governed_records)}")
    print(f"- source_profiles={manifest.source_profiles.total_sources}")
    print(f"- final_run={manifest.final_validation.run_id}")
    print(f"- final_artifact={manifest.final_validation.artifact.id}")
    print(f"- manifest_digest={manifest.manifest_digest}")
