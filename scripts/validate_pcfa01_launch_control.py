from __future__ import annotations

from jsonschema import Draft202012Validator

from codex_phase0_launch_core import (
    CONTRACT_PATH,
    CORRECTION_PATH,
    CURRENT_STATE_PATH,
    FINAL_RELEASE_PATH,
    ROOT,
    _final_release_state,
    final_release_record_failures,
    load_json,
    repair_failures,
)

PERMIT_SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-permit.schema.json"
TEMPLATE_PATHS = {
    "hosted_controls": ROOT / "handoff" / "pcfa01-codex-phase0-hosted-controls-attestation.template.json",
    "clean_macos": ROOT / "handoff" / "pcfa01-codex-phase0-clean-macos-attestation.template.json",
    "founder_approval": ROOT / "handoff" / "pcfa01-codex-phase0-founder-authorization.template.json",
    "launch_ack": ROOT / "handoff" / "pcfa01-codex-phase0-launch-ack.template.json",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    contract = load_json(CONTRACT_PATH)
    repair = load_json(CORRECTION_PATH)
    release = load_json(FINAL_RELEASE_PATH)

    failures = repair_failures(contract, repair)
    _require(not failures, "PCFA-01 corrective contract failed: " + "; ".join(failures))

    release_failures = final_release_record_failures(release)
    _require(not release_failures, "WS6.16 schema-v2 release failed: " + "; ".join(release_failures))
    _require(
        "integrated_main_sha" not in release and "main_sha" not in release,
        "WS6.16 release unexpectedly exposes a legacy launch-main field",
    )
    _require(
        release["release_parent_main_sha"]
        == "d3c4cb6097d0257a5bfdfc309ae4b3b1c2e7364c",
        "WS6.16 release-parent identity drifted",
    )

    state = _final_release_state()
    _require(
        state["final_workstream6_gate_complete"] is True,
        "actual permanent release ancestry is invalid",
    )
    _require(
        state["final_release_parent_is_ancestor"] is True,
        "release parent is not in current ancestry",
    )
    _require(
        state["final_release_record_is_ancestor"] is True,
        "release record commit is not in current ancestry",
    )
    _require(
        state["final_release_parent_main_sha"] != state["final_release_record_commit_sha"],
        "release parent and permanent record commit must be distinct",
    )

    _require(
        contract.get("work_package_id") == "WS6.2",
        "predecessor launch control must remain the immutable WS6.2 package snapshot",
    )
    _require(
        repair["predecessor_launch_control"]["classification"]
        == "retained_historical_package_snapshot",
        "PCFA-01 did not classify the predecessor launch-control snapshot correctly",
    )
    _require(
        repair["launch_sha_binding"]["excluded_from_current_launch_sha_equality"]
        == ["release_parent_main_sha", "permanent_release_record_commit_sha"],
        "PCFA-01 historical release SHA exclusion drifted",
    )

    hosted = load_json(TEMPLATE_PATHS["hosted_controls"])
    mac = load_json(TEMPLATE_PATHS["clean_macos"])
    approval = load_json(TEMPLATE_PATHS["founder_approval"])
    ack = load_json(TEMPLATE_PATHS["launch_ack"])
    _require(
        hosted.get("schema_version") == "2.1.0",
        "PCFA-01 hosted-controls snapshot version drifted",
    )
    _require(
        mac.get("schema_version") == "2.1.0",
        "PCFA-01 clean-macOS snapshot version drifted",
    )
    _require(
        approval.get("schema_version") == "2.1.0",
        "PCFA-01 Founder snapshot version drifted",
    )
    _require(
        ack.get("schema_version") == "2.1.0",
        "PCFA-01 launch acknowledgement snapshot version drifted",
    )
    for value, label in (
        (hosted, "hosted-controls"),
        (mac, "clean-macOS"),
        (approval, "Founder approval"),
    ):
        _require(
            "final_workstream6_release_sha256" in value,
            f"{label} template does not bind the permanent release digest",
        )
    _require(
        "canonical_issue_body_sha256" in hosted and "issue_19_body_sha256" in hosted,
        "hosted-controls template does not bind issue #1 and issue #19 bodies",
    )
    _require(
        "canonical_issue_body_sha256" in approval,
        "Founder approval template does not bind canonical issue #1 body",
    )
    _require(
        "final_workstream6_release_parent_main_sha" in ack
        and "final_workstream6_release_record_commit_sha" in ack,
        "launch acknowledgement does not preserve release-parent and release-record identities",
    )

    schema = load_json(PERMIT_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    _require(
        schema["properties"]["schema_version"]["const"] in {"2.1.0", "2.2.0"},
        "successor permit schema is incompatible with the PCFA-01 repair",
    )
    digest_required = schema["properties"]["evidence_digests"]["required"]
    _require(
        "launch_control_repair" in digest_required,
        "permit schema omits the PCFA-01 corrective-contract digest",
    )
    required = schema["required"]
    _require(
        "final_workstream6_release_parent_main_sha" in required
        and "final_workstream6_release_record_commit_sha" in required,
        "permit schema omits permanent release ancestry identities",
    )

    if CURRENT_STATE_PATH.is_file():
        successor = load_json(CURRENT_STATE_PATH)
        snapshot_map = {
            item.get("path"): item.get("classification")
            for item in successor.get("historical_package_snapshots", [])
            if isinstance(item, dict)
        }
        for path in (
            "handoff/pcfa01-codex-phase0-hosted-controls-attestation.template.json",
            "handoff/pcfa01-codex-phase0-clean-macos-attestation.template.json",
            "handoff/pcfa01-codex-phase0-founder-authorization.template.json",
            "handoff/pcfa01-codex-phase0-launch-ack.template.json",
        ):
            _require(
                snapshot_map.get(path) == "retained_corrective_package_snapshot",
                f"PCFA-01 corrective asset not retained by successor current state: {path}",
            )
        _require(
            "current_operational_state" in digest_required,
            "successor permit does not bind its current operational-state authority",
        )

    boundaries = repair["authorization_boundaries"]
    _require(
        boundaries["founder_accountability_preserved"] is True,
        "Founder accountability drifted",
    )
    _require(
        all(
            value is False
            for key, value in boundaries.items()
            if key != "founder_accountability_preserved"
        ),
        "PCFA-01 must not authorize Codex, merge, runtime or external actions",
    )

    print(
        "PCFA-01 launch-control successor validation passed: actual WS6.16 schema-v2 release "
        "accepted, release-parent and permanent-record ancestry remain independent from the "
        "current launch SHA, PCFA-01 v2.1 assets are retained snapshots, and the current permit "
        "still binds the PCFA-01 corrective contract; all authorization boundaries remain false."
    )


if __name__ == "__main__":
    main()
