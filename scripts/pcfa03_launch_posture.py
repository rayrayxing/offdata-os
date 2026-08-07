from __future__ import annotations

import copy
from typing import Any

from codex_phase0_launch_core import ROOT, digest_file, load_json

POSTURE_PATH = ROOT / "repository" / "repository-visibility-and-licence-posture.json"
WS613_PLACEHOLDER_PATH = ROOT / "configs" / "workstream6-phase0-licence-decision-placeholder.yaml"


def posture_failures(state: dict[str, Any], posture: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    visibility = posture.get("visibility_posture", {})
    licence = posture.get("licence_posture", {})
    predecessor = posture.get("historical_predecessor", {})
    enforcement = posture.get("operational_enforcement", {})
    completion = posture.get("repository_side_completion", {})
    boundaries = posture.get("boundaries", {})
    authority = state.get("current_authority", {})
    readiness = state.get("repository_readiness", {})
    manual = state.get("manual_launch_gates", {})
    snapshots = state.get("historical_package_snapshots", [])

    require(posture.get("work_package_id") == "PCFA-03", "PCFA-03 posture identity is invalid")
    require(
        posture.get("posture_id") == "REPOSITORY-VISIBILITY-LICENCE-POSTURE",
        "PCFA-03 posture record identity drifted",
    )
    require(
        posture.get("status") == "posture_resolved_hosted_visibility_change_pending",
        "PCFA-03 posture status is invalid",
    )
    require(posture.get("repository") == state.get("repository"), "PCFA-03 repository drifted")
    require(posture.get("owner") == "Founder", "PCFA-03 posture owner drifted")
    require(posture.get("founder_decision_date") == "2026-08-07", "PCFA-03 decision date drifted")

    observation = visibility.get("package_time_observation", {})
    require(
        visibility.get("required_repository_visibility_for_codex_launch") == "private"
        and visibility.get("required_repository_visibility_for_phase0_implementation") == "private"
        and visibility.get("public_repository_is_launch_blocker") is True
        and visibility.get("live_visibility_must_be_verified_from_github") is True
        and visibility.get("hosted_visibility_change_is_manual_control") is True,
        "PCFA-03 repository visibility posture is incomplete",
    )
    require(
        observation.get("visibility") == "public"
        and observation.get("observed_date") == "2026-08-07"
        and observation.get("source") == "GitHub repository metadata"
        and observation.get("classification") == "historical_observation_only",
        "PCFA-03 package-time public-visibility observation drifted",
    )

    require(
        licence.get("mode") == "no_public_licence_grant_proprietary_internal"
        and licence.get("selected_open_source_licence") is None
        and licence.get("licence_file_required_for_private_internal_development") is False
        and licence.get("implicit_licence_grant") is False
        and licence.get("public_distribution_authorized") is False
        and licence.get("external_licence_notice_authorized") is False
        and licence.get("open_source_distribution_authorized") is False
        and licence.get("external_contributions_authorized") is False
        and licence.get("client_distribution_authorized") is False
        and licence.get("third_party_dependencies_retain_their_own_licences") is True,
        "PCFA-03 licence posture is incomplete or permissive",
    )
    require(
        licence.get("future_public_or_open_source_change_requires")
        == [
            "explicit_founder_approval",
            "licence_ADR",
            "dependency_licence_compatibility_review",
            "legal_review_if_material",
        ],
        "future public/open-source licence change controls drifted",
    )

    require(
        predecessor.get("path") == "configs/workstream6-phase0-licence-decision-placeholder.yaml"
        and predecessor.get("package") == "WS6.13"
        and predecessor.get("classification") == "retained_historical_package_snapshot"
        and predecessor.get("predecessor_status") == "decision_required_not_authorized"
        and predecessor.get("predecessor_selected_licence") is None,
        "WS6.13 licence placeholder is not retained as historical predecessor evidence",
    )
    require(
        isinstance(enforcement, dict)
        and bool(enforcement)
        and all(value is True for value in enforcement.values()),
        "PCFA-03 operational enforcement must remain fully fail-closed",
    )
    require(
        completion.get("policy_decision_resolved") is True
        and completion.get("licence_posture_resolved") is True
        and completion.get("launch_enforcement_specified") is True
        and completion.get("hosted_visibility_private_verified") is False
        and completion.get("repository_setting_change_pending") is True,
        "PCFA-03 repository-side completion state is invalid",
    )
    require(
        boundaries.get("founder_accountability_preserved") is True
        and all(
            value is False
            for key, value in boundaries.items()
            if key != "founder_accountability_preserved"
        ),
        "PCFA-03 authorization/distribution boundaries must remain fail-closed",
    )

    require(
        authority.get("repository_posture")
        == "repository/repository-visibility-and-licence-posture.json",
        "current operational state does not reference the PCFA-03 posture",
    )
    require(
        authority.get("repository_posture_sha256") == digest_file(POSTURE_PATH),
        "current operational state does not bind the exact PCFA-03 posture digest",
    )
    require(
        readiness.get("pcfa03_repository_posture_resolved") is True,
        "current operational state does not mark PCFA-03 repository posture resolved",
    )
    require(
        manual.get("repository_visibility_private_verified") is False,
        "committed current state must not pre-attest hosted private visibility",
    )
    snapshot_map = {
        item.get("path"): item.get("classification")
        for item in snapshots
        if isinstance(item, dict)
    }
    require(
        snapshot_map.get("configs/workstream6-phase0-licence-decision-placeholder.yaml")
        == "retained_historical_package_snapshot",
        "current state does not retain WS6.13 licence placeholder as historical evidence",
    )
    require(POSTURE_PATH.is_file(), "PCFA-03 posture record is missing")
    require(WS613_PLACEHOLDER_PATH.is_file(), "WS6.13 historical licence placeholder is missing")
    return failures


def hosted_visibility_failures(hosted: dict[str, Any]) -> list[str]:
    return (
        []
        if hosted.get("repository_visibility_private") is True
        else ["hosted-controls attestation must explicitly verify repository_visibility_private=true"]
    )


def live_visibility_failures(
    posture: dict[str, Any], repository_metadata: dict[str, Any]
) -> list[str]:
    required = posture.get("visibility_posture", {}).get(
        "required_repository_visibility_for_codex_launch"
    )
    visibility = repository_metadata.get("visibility")
    private = repository_metadata.get("private")
    if required == "private" and visibility == "private" and private is True:
        return []
    return [
        "live GitHub repository visibility must be private before Codex Phase 0 launch; "
        f"observed visibility={visibility!r}, private={private!r}"
    ]


def launch_posture_failures(
    state: dict[str, Any],
    hosted: dict[str, Any],
    repository_metadata: dict[str, Any],
) -> list[str]:
    posture = load_json(POSTURE_PATH)
    return (
        posture_failures(state, posture)
        + hosted_visibility_failures(hosted)
        + live_visibility_failures(posture, repository_metadata)
    )


def run_self_test(state: dict[str, Any]) -> int:
    posture = load_json(POSTURE_PATH)
    failures = posture_failures(state, posture)
    if failures:
        raise SystemExit("PCFA-03 posture rejected: " + "; ".join(failures))
    hosted = {"repository_visibility_private": True}
    live = {"visibility": "private", "private": True}
    if launch_posture_failures(state, hosted, live):
        raise SystemExit("valid private-repository PCFA-03 launch posture was rejected")

    rejected = 0
    mutations: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    public_live = copy.deepcopy(live)
    public_live.update({"visibility": "public", "private": False})
    mutations.append(("live public visibility", posture, hosted, public_live))
    unattested = copy.deepcopy(hosted)
    unattested["repository_visibility_private"] = False
    mutations.append(("hosted private visibility unattested", posture, unattested, live))

    posture_mutations = [
        (
            "launch visibility public",
            ("visibility_posture", "required_repository_visibility_for_codex_launch"),
            "public",
        ),
        (
            "phase0 visibility public",
            ("visibility_posture", "required_repository_visibility_for_phase0_implementation"),
            "public",
        ),
        ("public repository allowed", ("visibility_posture", "public_repository_is_launch_blocker"), False),
        ("open-source licence selected", ("licence_posture", "selected_open_source_licence"), "MIT"),
        ("public distribution authorized", ("licence_posture", "public_distribution_authorized"), True),
        ("external contributions authorized", ("licence_posture", "external_contributions_authorized"), True),
        ("implicit licence grant", ("licence_posture", "implicit_licence_grant"), True),
        (
            "hosted private pre-attested",
            ("repository_side_completion", "hosted_visibility_private_verified"),
            True,
        ),
        (
            "setting no longer pending",
            ("repository_side_completion", "repository_setting_change_pending"),
            False,
        ),
        ("Codex authorized", ("boundaries", "codex_start_authorized"), True),
    ]
    for label, path, replacement in posture_mutations:
        mutated = copy.deepcopy(posture)
        node: Any = mutated
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = replacement
        if not posture_failures(state, mutated):
            raise SystemExit(f"PCFA-03 posture mutation was not rejected: {label}")
        rejected += 1
    for label, posture_value, hosted_value, live_value in mutations:
        errors = (
            posture_failures(state, posture_value)
            + hosted_visibility_failures(hosted_value)
            + live_visibility_failures(posture_value, live_value)
        )
        if not errors:
            raise SystemExit(f"PCFA-03 launch mutation was not rejected: {label}")
        rejected += 1
    return rejected
