from __future__ import annotations

import argparse
import os
from pathlib import Path

from jsonschema import Draft202012Validator

from codex_phase0_launch_core import (
    CORRECTION_PATH,
    CURRENT_STATE_PATH,
    PREDECESSOR_CONTRACT_PATH,
    ROOT,
    build_permit,
    canonical_json,
    digest_file,
    live_repository_state,
    load_json,
    repository_state,
    semantic_failures,
)
from codex_phase0_launch_selftest import run_self_test

PERMIT_SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-permit.schema.json"


def _safe_output(path: Path, state: dict[str, object]) -> Path:
    allowed = (ROOT / str(state["launch_permit"]["output_directory"])).resolve()  # type: ignore[index]
    resolved = path.resolve()
    if resolved.parent != allowed:
        raise SystemExit(f"permit output must be directly inside {allowed}")
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail-closed PCFA-02 current-state-bound Codex Phase 0 launch preparation."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--hosted-controls", type=Path)
    parser.add_argument("--macos-report", type=Path)
    parser.add_argument("--macos-attestation", type=Path)
    parser.add_argument("--founder-approval", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    state = load_json(CURRENT_STATE_PATH)
    predecessor = load_json(PREDECESSOR_CONTRACT_PATH)
    repair = load_json(CORRECTION_PATH)
    if args.self_test:
        count = run_self_test(state, predecessor, repair)
        print(
            "PCFA-02 Codex Phase 0 launch verifier self-test passed: "
            f"{count} invalid launch, current-state or corrective-contract mutations rejected; "
            "historical package readiness was excluded from current launch decisions; "
            "the valid synthetic launch bound a descendant main, permanent release digest and "
            "current operational-state digest; no permit emitted and no repository or GitHub "
            "mutation performed."
        )
        return

    inputs = [
        args.hosted_controls,
        args.macos_report,
        args.macos_attestation,
        args.founder_approval,
    ]
    if any(path is None for path in inputs):
        raise SystemExit("all four evidence paths are required")
    paths = [path.resolve() for path in inputs if path is not None]
    if any(not path.is_file() for path in paths):
        raise SystemExit("one or more required evidence files are missing")
    hosted, doctor, mac, approval = (load_json(path) for path in paths)

    try:
        live = live_repository_state(state)
    except RuntimeError as error:
        raise SystemExit(str(error)) from error
    repo = repository_state(state)
    failures = semantic_failures(
        state,
        predecessor,
        hosted,
        doctor,
        mac,
        approval,
        repo,
        live,
        doctor_digest=digest_file(paths[1]),
        repair=repair,
    )
    if failures:
        raise SystemExit("Codex Phase 0 launch denied:\n- " + "\n- ".join(failures))

    output_value = args.output or Path(state["launch_permit"]["output_path"])
    output = _safe_output(
        output_value if output_value.is_absolute() else ROOT / output_value,
        state,
    )
    if output.exists():
        raise SystemExit(f"single-use permit already exists: {output}")

    permit = build_permit(state, predecessor, paths, approval, repo)
    errors = list(Draft202012Validator(load_json(PERMIT_SCHEMA_PATH)).iter_errors(permit))
    if errors:
        raise SystemExit(
            "launch permit schema validation failed:\n- "
            + "\n- ".join(error.message for error in errors)
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(permit), encoding="utf-8")
    os.chmod(output, 0o600)

    print(f"Codex Phase 0 launch permit issued locally: {output}")
    print(f"launch_id={permit['launch_id']}")
    print(f"approved_main_sha={permit['approved_main_sha']}")
    print(
        "final_release_parent_main_sha="
        f"{permit['final_workstream6_release_parent_main_sha']}"
    )
    print(
        "final_release_record_commit_sha="
        f"{permit['final_workstream6_release_record_commit_sha']}"
    )
    print(
        "current_operational_state_sha256="
        f"{permit['evidence_digests']['current_operational_state']}"
    )
    print(f"required_status_check={permit['required_status_check']}")
    print(
        "Next permitted action: create codex/phase-0-foundation from the approved SHA "
        "and add the launch acknowledgement as the first commit."
    )
    print(
        "Merge, Phase 1, runtime activation, real client data, paid services and "
        "external actions remain unauthorized."
    )


if __name__ == "__main__":
    main()
