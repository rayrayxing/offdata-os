from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "initial-operating-controls.yaml"
OUTPUT_PATH = ROOT / "contracts" / "initial-operating-controls.json"
POLICY_PATH = ROOT / "configs" / "policy.yaml"
SECURITY_CONTROLS_PATH = ROOT / "security" / "security-control-catalogue.yaml"
INCIDENT_PLAYBOOKS_PATH = ROOT / "security" / "incident-playbooks.yaml"
RETENTION_POLICIES_PATH = ROOT / "security" / "retention-policies.yaml"
SECURITY_BASELINE_PATH = ROOT / "security" / "security-regionalisation-baseline.json"
DATA_CLASSIFICATION_PATH = ROOT / "security" / "data-classification.yaml"
AGENTS_PATH = ROOT / "configs" / "agents.yaml"
RUNTIME_ADAPTER_PATH = ROOT / "contracts" / "runtime-adapter-contracts.json"
PROCESSOR_REGISTER_PATH = ROOT / "security" / "provider-processor-register.yaml"
REPOSITORY_BASELINE_PATH = ROOT / "repository" / "repository-governance-baseline.json"
COMMANDS_PATH = ROOT / "contracts" / "command-event-catalogue.json"
HERMES_PATH = ROOT / "contracts" / "hermes-compatibility-pack.json"
NORTHSTAR_PATH = ROOT / "contracts" / "northstar-integration-blueprint.json"
CODEX_SOURCE_PATH = ROOT / "configs" / "codex-handoff.yaml"

EXPECTED_DECISION_CLASSES = {
    "DEC-ROUTINE",
    "DEC-MATERIAL",
    "DEC-EXTERNAL",
    "DEC-COMMERCIAL",
    "DEC-LEGALREG",
    "DEC-IRREVERSIBLE",
}
EXPECTED_IDEMPOTENCY_COMMANDS = {
    "cancel_engagement",
    "execute_external_action",
    "propose_external_action",
    "record_agent_output",
    "record_approval",
    "release_artefact",
    "request_approval",
}
EXPECTED_BUDGET_PROFILES = {
    "standard",
    "orchestration",
    "research",
    "quantitative",
    "production",
    "quality",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def build_initial_operating_controls() -> dict[str, Any]:
    source = _load_yaml(SOURCE_PATH)
    policy = _load_yaml(POLICY_PATH)
    security_controls = _load_yaml(SECURITY_CONTROLS_PATH)
    incident_playbooks = _load_yaml(INCIDENT_PLAYBOOKS_PATH)
    retention_policies = _load_yaml(RETENTION_POLICIES_PATH)
    security_baseline = _load_json(SECURITY_BASELINE_PATH)
    classifications = _load_yaml(DATA_CLASSIFICATION_PATH)
    agents = _load_yaml(AGENTS_PATH)
    runtime = _load_json(RUNTIME_ADAPTER_PATH)
    processors = _load_yaml(PROCESSOR_REGISTER_PATH)
    repository = _load_json(REPOSITORY_BASELINE_PATH)
    catalogue = _load_json(COMMANDS_PATH)
    hermes = _load_json(HERMES_PATH)
    northstar = _load_json(NORTHSTAR_PATH)
    codex_source = _load_yaml(CODEX_SOURCE_PATH)

    control_catalogue = {
        item.get("control_id"): item
        for item in security_controls.get("controls", [])
        if isinstance(item, dict) and isinstance(item.get("control_id"), str)
    }
    assignments: list[dict[str, Any]] = []
    assigned_ids: list[str] = []
    for domain in source.get("control_domains", []):
        if not isinstance(domain, dict):
            continue
        domain_id = domain.get("domain_id")
        for control_id in domain.get("security_control_ids", []):
            if not isinstance(control_id, str):
                continue
            assigned_ids.append(control_id)
            catalogue_entry = control_catalogue.get(control_id, {})
            assignments.append(
                {
                    "control_id": control_id,
                    "domain_id": domain_id,
                    "title": catalogue_entry.get("title"),
                    "mandatory_for_real_client_data": catalogue_entry.get(
                        "mandatory_for_real_client_data"
                    ),
                    "chat_first_status": catalogue_entry.get("chat_first_status"),
                    "required_evidence": catalogue_entry.get("required_evidence", []),
                }
            )

    assigned_set = set(assigned_ids)
    duplicate_assignments = sorted(
        control_id for control_id in assigned_set if assigned_ids.count(control_id) > 1
    )
    missing_controls = sorted(set(control_catalogue) - assigned_set)
    unknown_controls = sorted(assigned_set - set(control_catalogue))

    decision_classes = set(policy.get("decision_classes", {}))
    authority_classes = {
        item.get("decision_class")
        for item in source.get("authority_matrix", [])
        if isinstance(item, dict)
    }
    playbook_ids = {
        item.get("playbook_id")
        for item in incident_playbooks.get("playbooks", [])
        if isinstance(item, dict)
    }
    configured_playbooks = set(source.get("incident_routing", {}).get("playbook_ids", []))
    retention_ids = {
        item.get("policy_id")
        for item in retention_policies.get("policies", [])
        if isinstance(item, dict)
    }
    configured_retention = set(
        source.get("retention_and_recovery", {}).get("retention_policy_ids", [])
    )
    budget_profiles = set(agents.get("budget_profiles", {}))
    required_budget_profiles = set(
        source.get("cost_and_usage", {}).get("required_budget_profiles", [])
    )
    commands = catalogue.get("commands", {})
    if not isinstance(commands, dict):
        raise ValueError("command catalogue commands must be a mapping")
    idempotency_commands = {
        command_id
        for command_id, command in commands.items()
        if isinstance(command, dict) and command.get("idempotency") == "required"
    }
    class_names = {
        item.get("classification")
        for item in classifications.get("classes", [])
        if isinstance(item, dict)
    }
    permitted_classes = set(
        source.get("operating_context", {}).get("permitted_data_classes", [])
    )
    processor_entries = processors.get("processors", [])
    hosted_controls = repository.get("hosted_settings_required_before_codex", [])
    runtime_readiness = runtime.get("readiness_snapshot", {})
    runtime_boundaries = runtime.get("boundaries", {})
    hermes_readiness = hermes.get("readiness_snapshot", {})
    northstar_readiness = northstar.get("readiness_snapshot", {})

    checks = {
        "decision_classes_exactly_mapped": (
            decision_classes == EXPECTED_DECISION_CLASSES
            and authority_classes == EXPECTED_DECISION_CLASSES
        ),
        "security_controls_exactly_once": (
            not missing_controls
            and not unknown_controls
            and not duplicate_assignments
            and len(assignments) == len(control_catalogue) == 48
        ),
        "mandatory_control_count_reconciled": (
            sum(
                1
                for item in control_catalogue.values()
                if item.get("mandatory_for_real_client_data") is True
            )
            == security_baseline.get("mandatory_real_client_control_count")
            == 18
        ),
        "incident_playbooks_exactly_mapped": (
            configured_playbooks == playbook_ids and len(playbook_ids) == 12
        ),
        "retention_policies_exactly_mapped": (
            configured_retention == retention_ids and len(retention_ids) == 4
        ),
        "budget_profiles_exactly_mapped": (
            budget_profiles == EXPECTED_BUDGET_PROFILES
            and required_budget_profiles == EXPECTED_BUDGET_PROFILES
        ),
        "idempotency_commands_reconciled": (
            idempotency_commands == EXPECTED_IDEMPOTENCY_COMMANDS
        ),
        "permitted_data_classes_exist": permitted_classes <= class_names,
        "real_client_processors_absent": processor_entries == [],
        "processor_default_deny": (
            processors.get("rules", {}).get("unregistered_processor_default") == "deny"
        ),
        "runtime_remains_inactive": (
            runtime_readiness.get("runtime_activation_authorized") is False
            and runtime_boundaries.get("runtime_activation_authorized") is False
        ),
        "hermes_remains_inactive": (
            hermes_readiness.get("hermes_activation_authorized") is False
        ),
        "northstar_remains_unauthorized": (
            northstar_readiness.get("northstar_implementation_authorized") is False
        ),
        "codex_source_remains_phase0_and_unauthorized": (
            codex_source.get("target", {}).get("phase_number") == 0
            and codex_source.get("target", {}).get("start_requires_explicit_founder_approval")
            is True
        ),
        "hosted_controls_remain_required": len(hosted_controls) == 7,
        "operating_activation_unauthorized": (
            source.get("boundaries", {}).get(
                "initial_operating_controls_activation_authorized"
            )
            is False
        ),
    }

    readiness = {
        "decision_class_count": len(decision_classes),
        "control_domain_count": len(source.get("control_domains", [])),
        "security_control_count": len(control_catalogue),
        "mandatory_real_client_control_count": sum(
            1
            for item in control_catalogue.values()
            if item.get("mandatory_for_real_client_data") is True
        ),
        "operating_gate_count": len(source.get("operating_gates", [])),
        "control_switch_count": len(source.get("control_switches", [])),
        "incident_playbook_count": len(playbook_ids),
        "retention_policy_count": len(retention_ids),
        "budget_profile_count": len(budget_profiles),
        "idempotency_required_command_count": len(idempotency_commands),
        "approved_real_client_processor_count": len(processor_entries),
        "hosted_control_requirement_count": len(hosted_controls),
        "operating_cadence_count": len(source.get("operating_cadences", [])),
        "missing_security_controls": missing_controls,
        "unknown_security_controls": unknown_controls,
        "duplicate_security_controls": duplicate_assignments,
        "checks": checks,
        "local_prerequisites_passed": all(checks.values()),
        "hosted_control_evidence_complete": False,
        "operating_environment_evidence_complete": False,
        "production_evidence_complete": False,
        "initial_operating_controls_activation_authorized": False,
        "codex_start_authorized": False,
        "runtime_activation_authorized": False,
        "hermes_activation_authorized": False,
        "northstar_implementation_authorized": False,
    }

    output = dict(source)
    output["generated_from"] = "configs/initial-operating-controls.yaml"
    output["readiness_snapshot"] = readiness
    return output


def main() -> None:
    output = build_initial_operating_controls()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(_canonical_json(output), encoding="utf-8")
    readiness = output["readiness_snapshot"]
    print(
        "Built PCR-08 initial operating controls: "
        f"{readiness['control_domain_count']} domains, "
        f"{readiness['security_control_count']} controls, "
        f"{readiness['operating_gate_count']} gates, "
        f"{readiness['control_switch_count']} switches, "
        f"local_prerequisites_passed={str(readiness['local_prerequisites_passed']).lower()}, "
        "initial_operating_controls_activation_authorized=false."
    )


if __name__ == "__main__":
    main()
