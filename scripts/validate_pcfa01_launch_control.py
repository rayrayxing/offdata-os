from __future__ import annotations

from jsonschema import Draft202012Validator

from codex_phase0_launch_core import (
    CONTRACT_PATH,
    CORRECTION_PATH,
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
    _require(state["final_workstream6_gate_complete"] is True, "actual permanent release ancestry is invalid")
    _require(state["final_release_parent_is_ancestor"] is True, "release parent is not in current ancestry")
    _require(state["final_release_record_is_ancestor"] is True, "release record commit is not in current ancestry")
    _require(
        state["final_release_parent_main_sha"] != state["final_release_record_commit_sha"],
        "release parent and permanent record commit must be distinct",
    )

    _require(
        contract.get("work_package_id") == "WS6.2",
        "predecessor launch control must remain the immutable WS6.2 package snapshot",
    )
    _require(
        repair["predecessor_launch_control"]["classification"] == "retained_historical_package_snapshot",
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
    _require(hosted.get("schema_version") == "2.1.0", "hosted-controls template version drifted")
    _require(mac.get("schema_version") == "2.1.0", "clean-macOS template version drifted")
    _require(approval.get("schema_version") == "2.1.0", "Founder template version drifted")
    _require(ack.get("schema_version") == "2.1.0", "launch acknowledgement template version drifted")
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
    _require(schema["properties"]["schema_version"]["const"] == "2.1.0", "permit schema version drifted")
    digest_required = schema["properties"]["evidence_digests"]["required"]
    _require("launch_control_repair" in digest_required, "permit schema omits corrective-contract digest")
    required = schema["required"]
    _require(
        "final_workstream6_release_parent_main_sha" in required
        and "final_workstream6_release_record_commit_sha" in required,
        "permit schema omits permanent release ancestry identities",
    )

    boundaries = repair["authorization_boundaries"]
    _require(boundaries["founder_accountability_preserved"] is True, "Founder accountability drifted")
    _require(
        all(value is False for key, value in boundaries.items() if key != "founder_accountability_preserved"),
        "PCFA-01 must not authorize Codex, merge, runtime or external actions",
    )

    print(
        "PCFA-01 launch-control validation passed: actual WS6.16 schema-v2 release accepted, "
        "release-parent and permanent-record ancestry verified independently from current launch SHA, "
        "corrected evidence templates and permit schema bound, all authorization boundaries false."
    )


if __name__ == "__main__":
    main()
