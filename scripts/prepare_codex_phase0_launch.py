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
    gh_json,
    live_repository_state,
    load_json,
    repository_state,
    semantic_failures,
)
from codex_phase0_launch_selftest import run_self_test
from pcfa03_launch_posture import (
    launch_posture_failures,
    run_self_test as run_posture_self_test,
)
from pcfa04_product_scope import (
    product_scope_failures,
    run_self_test as run_product_scope_self_test,
)
from pcfa05_mvcl import (
    mvcl_failures,
    run_self_test as run_mvcl_self_test,
)
from pcfa06_hermes_refresh import (
    hermes_refresh_failures,
    run_self_test as run_hermes_refresh_self_test,
)

PERMIT_SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-permit.schema.json"


def _safe_output(path: Path, state: dict[str, object]) -> Path:
    allowed = (ROOT / str(state["launch_permit"]["output_directory"])).resolve()  # type: ignore[index]
    resolved = path.resolve()
    if resolved.parent != allowed:
        raise SystemExit(f"permit output must be directly inside {allowed}")
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fail-closed PCFA-06 Hermes bounded-adoption, PCFA-05 MVCL, PCFA-04 product-scope, "
            "PCFA-03 repository-posture and PCFA-02 current-state-bound Codex Phase 0 launch preparation."
        )
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
        posture_count = run_posture_self_test(state)
        product_scope_count = run_product_scope_self_test(state)
        mvcl_count = run_mvcl_self_test(state)
        hermes_refresh_count = run_hermes_refresh_self_test(state)
        print(
            "PCFA-06 Codex Phase 0 launch verifier self-test passed: "
            f"{count + posture_count + product_scope_count + mvcl_count + hermes_refresh_count} invalid "
            "launch, current-state, corrective-contract, repository-posture, product-scope, MVCL or "
            "Hermes bounded-adoption mutations rejected; "
            "historical package readiness was excluded from current launch decisions; public "
            "repository visibility, product-scope drift, MVCL drift and Hermes activation/policy drift "
            "were rejected; all PCFA-04 obligations, PCFA-05 stages and PCFA-06 Hermes capabilities "
            "remain planned_not_implemented; no permit emitted and "
            "no repository or GitHub mutation performed."
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
        repository_metadata = gh_json(f"repos/{state['repository']}")
    except RuntimeError as error:
        raise SystemExit(str(error)) from error
    repo = repository_state(state)
    failures = hermes_refresh_failures(state)
    failures.extend(mvcl_failures(state))
    failures.extend(product_scope_failures(state))
    failures.extend(launch_posture_failures(state, hosted, repository_metadata))
    failures.extend(
        semantic_failures(
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
    print("repository_visibility=private")
    print("pcfa04_product_scope_addendum=validated_planned_not_implemented")
    print("pcfa05_mvcl=validated_planned_not_implemented")
    print("pcfa06_hermes_bounded_adoption=validated_planned_not_implemented_not_activated")
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
        "Merge, Phase 1, runtime activation, public distribution, real client data, paid "
        "services and external actions remain unauthorized."
    )


if __name__ == "__main__":
    main()
