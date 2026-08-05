#!/usr/bin/env python3
"""Validate PCR-01 canonical Phase 1-7 release reconciliation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from offdata_core.release_reconciliation import (
    build_canonical_release_manifest,
    verify_canonical_release_manifest,
)


FINAL_RUN = "30976222896"
FINAL_JOB = "92210649514"
FINAL_ARTIFACT = "8918355687"
FINAL_ARTIFACT_SHA256 = "3b9f14c520d31ce5f73fbecc726b032a3134042769ee84176e85d642fe2ea852"
FINAL_HEAD = "8da0f1167d9b6f4da792770b0d564379aa46c3fe"
FINAL_MERGE_REFERENCE = "264459045ce75d7d7c60cbc980a50193f08a6f16"
FINAL_MAIN_COMMIT = "7dc5531e641158e5a84fbbb9fdf07cefefd4782b"
SUPERSEDED_RUNS = ("30975868412", "30976088173")


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _require_tokens(path: Path, tokens: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError(f"Missing canonical release evidence in {path}: {missing}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "releases" / "canonical-chat-first-phase1-7-release.json"
    verify_canonical_release_manifest(root, manifest_path)
    manifest = build_canonical_release_manifest(root)

    if manifest.controlling_release.main_merge_commit != FINAL_MAIN_COMMIT:
        raise ValueError("Controlling main commit is not the merged Phase 7 release.")
    if manifest.controlling_release.pull_request_head != FINAL_HEAD:
        raise ValueError("Controlling pull-request head is not exact.")
    if manifest.controlling_release.pull_request_merge_reference != FINAL_MERGE_REFERENCE:
        raise ValueError("Controlling merge reference is not exact.")
    if str(manifest.final_validation.run_id) != FINAL_RUN:
        raise ValueError("Final validation run is not authoritative.")
    if str(manifest.final_validation.job_id) != FINAL_JOB:
        raise ValueError("Final validation job is not authoritative.")
    if str(manifest.final_validation.artifact.id) != FINAL_ARTIFACT:
        raise ValueError("Final release artifact is not authoritative.")
    if manifest.final_validation.artifact.sha256 != FINAL_ARTIFACT_SHA256:
        raise ValueError("Final release artifact digest is not authoritative.")
    if len(manifest.governed_records) != 7:
        raise ValueError("Canonical release must digest exactly seven governed records.")
    if manifest.source_profiles.total_sources != 23:
        raise ValueError("Canonical source profile count must remain 23.")
    if manifest.boundaries.real_client_data_enabled:
        raise ValueError("PCR-01 cannot enable real client data.")
    if manifest.boundaries.original_methodology_binaries_committed:
        raise ValueError("PCR-01 cannot commit original methodology binaries.")

    registry = _json_object(root / "requirements" / "test-registry.json")
    implemented = registry.get("implemented_tests")
    planned = registry.get("planned_tests")
    if not isinstance(implemented, list) or len(implemented) < 226:
        raise ValueError("PCR-01 executable test registry is incomplete.")
    if not isinstance(planned, list) or len(planned) != 55:
        raise ValueError("PCR-01 must preserve the 55 deferred planned tests.")

    canonical_tokens = (
        FINAL_RUN,
        FINAL_JOB,
        FINAL_ARTIFACT,
        FINAL_ARTIFACT_SHA256,
        FINAL_HEAD,
        FINAL_MERGE_REFERENCE,
        FINAL_MAIN_COMMIT,
        "superseded",
        *SUPERSEDED_RUNS,
    )
    _require_tokens(
        root / "docs" / "39-PHASE-7-SECURITY-AND-REGIONALISATION-COMPLETION.md",
        canonical_tokens,
    )
    _require_tokens(root / "reports" / "phase7-validation-evidence.md", canonical_tokens)
    _require_tokens(
        root / "docs" / "20-DEVELOPMENT-STATUS.md",
        (
            "releases/canonical-chat-first-phase1-7-release.json",
            FINAL_MAIN_COMMIT,
            FINAL_RUN,
            FINAL_ARTIFACT,
        ),
    )
    _require_tokens(
        root / "docs" / "40-PCR-01-CANONICAL-RELEASE-RECONCILIATION.md",
        (FINAL_RUN, FINAL_ARTIFACT, "Real client data remains prohibited"),
    )

    if list((root / "knowledge" / "source").glob("*.docx")) if (root / "knowledge" / "source").exists() else []:
        raise ValueError("Original methodology binaries must remain uncommitted in PCR-01.")

    print("PCR-01 CANONICAL RELEASE RECONCILIATION VALIDATION PASSED")
    for item in (
        f"release_id={manifest.release_id}",
        f"controlling_main_commit={FINAL_MAIN_COMMIT}",
        f"final_run={FINAL_RUN}",
        f"final_job={FINAL_JOB}",
        f"final_artifact={FINAL_ARTIFACT}",
        f"governed_records={len(manifest.governed_records)}",
        f"source_profiles={manifest.source_profiles.total_sources}",
        f"implemented_test_nodes={len(implemented)}",
        f"planned_tests={len(planned)}",
        "real_client_data_enabled=false",
        "founder_accountability=preserved",
    ):
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"PCR-01 CANONICAL RELEASE RECONCILIATION VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
