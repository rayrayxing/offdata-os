from __future__ import annotations

import copy

from jsonschema import Draft202012Validator

from build_pcfa03_repository_posture import REPORT_PATH, build_records
from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, digest_file, load_json
from pcfa03_launch_posture import POSTURE_PATH, posture_failures, run_self_test

POSTURE_SCHEMA_PATH = ROOT / "schemas" / "repository-visibility-licence-posture.schema.json"
WS613_PLACEHOLDER_PATH = ROOT / "configs" / "workstream6-phase0-licence-decision-placeholder.yaml"
HOSTED_TEMPLATE_PATH = (
    ROOT / "handoff" / "codex-phase0-current-hosted-controls-attestation.template.json"
)
CURRENT_HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-current-handoff.json"
ISSUE1_PATH = ROOT / "handoff" / "codex-phase0-current-issue.md"
ISSUE19_PATH = ROOT / "handoff" / "codex-phase0-current-hosted-controls-issue.md"
CURRENT_STATUS_PATH = ROOT / "docs" / "CURRENT-OPERATIONAL-STATE.md"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    state = load_json(CURRENT_STATE_PATH)
    posture = load_json(POSTURE_PATH)
    schema = load_json(POSTURE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(posture))
    _require(
        not errors,
        "PCFA-03 posture schema validation failed: "
        + "; ".join(error.message for error in errors),
    )

    expected_posture, expected_report = build_records()
    _require(posture == expected_posture, "PCFA-03 posture JSON drifted from governed YAML source")
    _require(
        REPORT_PATH.read_text(encoding="utf-8") == expected_report,
        "PCFA-03 generated evidence report drifted",
    )

    failures = posture_failures(state, posture)
    _require(not failures, "PCFA-03 posture semantics failed: " + "; ".join(failures))

    predecessor = load_json(WS613_PLACEHOLDER_PATH)
    _require(predecessor.get("work_package_id") == "WS6.13", "WS6.13 licence placeholder identity drifted")
    _require(
        predecessor.get("status") == "decision_required_not_authorized",
        "WS6.13 licence placeholder was rewritten instead of retained",
    )
    _require(
        predecessor.get("licence_state", {}).get("selected_licence") is None
        and predecessor.get("licence_state", {}).get("implicit_licence_grant") is False
        and predecessor.get("licence_state", {}).get("public_distribution_authorized") is False,
        "WS6.13 historical licence state was altered",
    )

    authority = state["current_authority"]
    _require(
        authority["repository_posture"]
        == "repository/repository-visibility-and-licence-posture.json",
        "current state does not name the PCFA-03 posture authority",
    )
    _require(
        authority["repository_posture_sha256"] == digest_file(POSTURE_PATH),
        "current state posture digest is stale",
    )
    _require(
        state["repository_readiness"]["pcfa03_repository_posture_resolved"] is True,
        "current state does not record PCFA-03 repository posture completion",
    )
    _require(
        state["manual_launch_gates"]["repository_visibility_private_verified"] is False,
        "current state must keep private-visibility hosted verification false until observed live",
    )

    hosted = load_json(HOSTED_TEMPLATE_PATH)
    _require(
        hosted.get("repository_visibility_private") is False,
        "hosted-controls template must require an explicit private-visibility attestation",
    )

    handoff = load_json(CURRENT_HANDOFF_PATH)
    _require(
        handoff["authority"].get("repository_posture")
        == "repository/repository-visibility-and-licence-posture.json",
        "current handoff omits the PCFA-03 posture authority",
    )
    _require(
        handoff["readiness"].get("pcfa03_repository_posture_resolved") is True
        and handoff["readiness"].get("repository_visibility_private_verified") is False,
        "current handoff does not separate resolved posture from pending private visibility",
    )

    for path, tokens in (
        (
            ISSUE1_PATH,
            (
                "repository/repository-visibility-and-licence-posture.json",
                "repository visibility must be `private`",
                "no public licence grant",
            ),
        ),
        (
            ISSUE19_PATH,
            (
                "repository visibility is `private`",
                "repository_visibility_private=true",
                "no public licence grant",
            ),
        ),
        (
            CURRENT_STATUS_PATH,
            (
                "PCFA-03",
                "private",
                "no public licence grant",
            ),
        ),
    ):
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            _require(token in text, f"{path.relative_to(ROOT)} missing PCFA-03 token: {token}")

    rejected = run_self_test(state)

    digest_mutation = copy.deepcopy(state)
    digest_mutation["current_authority"]["repository_posture_sha256"] = "0" * 64
    _require(
        bool(posture_failures(digest_mutation, posture)),
        "PCFA-03 current-state posture-digest mutation was not rejected",
    )
    rejected += 1
    readiness_mutation = copy.deepcopy(state)
    readiness_mutation["repository_readiness"]["pcfa03_repository_posture_resolved"] = False
    _require(
        bool(posture_failures(readiness_mutation, posture)),
        "PCFA-03 current-state readiness mutation was not rejected",
    )
    rejected += 1

    print(
        "PCFA-03 repository visibility and licence posture validation passed: "
        f"mutations_rejected={rejected}, required_visibility=private, "
        "licence=no_public_licence_grant_proprietary_internal, "
        "hosted_visibility_private_verified=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
