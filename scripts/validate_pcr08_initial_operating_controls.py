from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator

from build_pcr08_initial_operating_controls import build_initial_operating_controls

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "initial-operating-controls.yaml"
CONTRACT = ROOT / "contracts" / "initial-operating-controls.json"
SCHEMA = ROOT / "schemas" / "initial-operating-controls.schema.json"
DOC = ROOT / "docs" / "47-PCR-08-INITIAL-OPERATING-CONTROL-CONFIGURATION.md"
Mutation = Callable[[dict[str, Any]], None]

DECISIONS = {
    "DEC-ROUTINE", "DEC-MATERIAL", "DEC-EXTERNAL", "DEC-COMMERCIAL",
    "DEC-LEGALREG", "DEC-IRREVERSIBLE",
}
GATES = {
    "OPC-GATE-CODEX-START", "OPC-GATE-RUNTIME-ACTIVATION",
    "OPC-GATE-HERMES-ACTIVATION", "OPC-GATE-NORTHSTAR-IMPLEMENTATION",
    "OPC-GATE-REAL-CLIENT-DATA", "OPC-GATE-EXTERNAL-ACTION",
    "OPC-GATE-PAID-SERVICE", "OPC-GATE-PRODUCTION-DEPLOYMENT",
}
SWITCHES = {
    "OPC-SW-AGENT-EXECUTION", "OPC-SW-TOOL-RUNTIME",
    "OPC-SW-EXTERNAL-ACTIONS", "OPC-SW-PROVIDER-NETWORK",
    "OPC-SW-WORKFLOW-CLASS", "OPC-SW-PRODUCTION-DEPLOYMENT",
}
CADENCES = {
    "OPC-CAD-PER-CHANGE", "OPC-CAD-PER-RELEASE", "OPC-CAD-DAILY-ACTIVE",
    "OPC-CAD-WEEKLY-ACTIVE", "OPC-CAD-MONTHLY-ACTIVE",
    "OPC-CAD-QUARTERLY-ACTIVE", "OPC-CAD-ANNUAL-ACTIVE",
}
ACTIVATION = {
    "pcr03_merged_to_main", "pcr04_merged_to_main", "pcr05_merged_to_main",
    "pcr06_merged_to_main", "pcr07_merged_to_main", "pcr08_merged_to_main",
    "github_hosted_controls_in_issue_19_verified",
    "explicit_founder_phase_0_approval_received", "clean_macos_environment_available",
}
BUDGETS = {"standard", "orchestration", "research", "quantitative", "production", "quality"}
DENIED = {
    "initial_operating_controls_activation_authorized", "codex_start_authorized",
    "runtime_activation_authorized", "hermes_activation_authorized",
    "northstar_implementation_authorized", "real_client_data_enabled",
    "external_actions_authorized", "paid_services_authorized",
    "production_deployment_authorized", "autonomous_merge_authorized",
}


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text()) if path.suffix in {".yaml", ".yml"} else json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def set_path(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    cursor = value
    for key in path[:-1]:
        next_value = cursor[key]
        if not isinstance(next_value, dict):
            raise AssertionError(path)
        cursor = next_value
    cursor[path[-1]] = replacement


def validate(value: dict[str, Any]) -> None:
    context = value["operating_context"]
    require(value["phase_id"] == "PCR-08", "phase")
    require(value["status"] == "initial_configuration_only", "status")
    require(context["operator_model"] == "founder_only", "operator")
    require(context["operating_mode"] == "local_synthetic_pre_codex", "mode")
    require(context["managed_region"] == "Singapore", "region")
    require(context["permitted_data_classes"] == ["public", "internal"], "data classes")
    require(context["canonical_write_mode"] == "commands_only", "writes")
    require(context["network_default"] == "deny", "network")
    for key in [
        "provider_training_allowed", "credential_values_permitted", "real_client_data_enabled",
        "external_actions_enabled", "paid_services_enabled", "production_deployment_enabled",
        "autonomous_merge_enabled",
    ]:
        require(context[key] is False, key)

    authority = {item["decision_class"]: item for item in value["authority_matrix"]}
    require(set(authority) == DECISIONS, "decision classes")
    require(authority["DEC-ROUTINE"]["execution_mode"] == "policy_bounded_auto_execute", "routine")
    require(authority["DEC-EXTERNAL"]["execution_mode"] == "proposal_only_pre_activation", "external")
    require(authority["DEC-COMMERCIAL"]["delegation_allowed"] is False, "commercial")
    require(authority["DEC-LEGALREG"]["qualified_specialist_required"] is True, "specialist")
    require(all(item["external_execution_enabled"] is False for item in authority.values()), "external execution")

    domains = {item["domain_id"]: item for item in value["control_domains"]}
    require(len(domains) == 10, "domains")
    require(all(item["accountable_owner"] == "Founder" for item in domains.values()), "owners")
    require(all(item["independent_review_required"] is True for item in domains.values()), "review")
    assigned = [control for domain in domains.values() for control in domain["security_control_ids"]]
    require(len(assigned) == len(set(assigned)) == 48, "control assignment")
    gates = {item["gate_id"]: item for item in value["operating_gates"]}
    require(set(gates) == GATES, "gates")
    require(all(item["authorized"] is False for item in gates.values()), "gate authorized")
    require({"global_switch_enabled", "exact_scoped_unexpired_approval", "idempotency_key", "audit_correlation"} <= set(gates["OPC-GATE-EXTERNAL-ACTION"]["required_conditions"]), "external gate")
    require({"all_mandatory_controls_current", "exact_environment_and_region_evidence", "processor_register_approved", "explicit_founder_approval"} <= set(gates["OPC-GATE-REAL-CLIENT-DATA"]["required_conditions"]), "data gate")

    switches = {item["switch_id"]: item for item in value["control_switches"]}
    require(set(switches) == SWITCHES, "switches")
    require(all(item["initial_state"] == "deny" and item["fail_mode"] == "fail_closed" for item in switches.values()), "switch posture")
    require(all(item["reset_authority"] == "Founder" for item in switches.values()), "switch reset")

    cost = value["cost_and_usage"]
    require(cost["paid_provider_spend_hard_cap"] == 0 and cost["purchases_authorized"] is False, "cost")
    require(set(cost["required_budget_profiles"]) == BUDGETS, "budgets")
    require(cost["adapter_may_raise_limits"] is False and cost["actual_usage_record_required"] is True, "usage")
    require(cost["alert_on_any_billable_usage"] is True, "billable alert")

    incident = value["incident_routing"]
    require(incident["agents_may_close_material_incidents"] is False, "incident closure")
    require(incident["preserve_evidence_before_repair"] is True, "incident evidence")
    require(incident["implicated_actor_may_be_sole_reviewer"] is False, "incident review")
    severity = {item["severity"]: item for item in incident["severities"]}
    require(set(severity) == {"critical", "high", "medium", "low"}, "severity")
    require(severity["critical"]["founder_notification"] == severity["high"]["founder_notification"] == "immediate", "notification")
    require(len(set(incident["playbook_ids"])) == 12, "playbooks")

    retention = value["retention_and_recovery"]
    require(len(set(retention["retention_policy_ids"])) == 4, "retention")
    require(retention["legal_hold_overrides_deletion"] is True, "legal hold")
    require(retention["deletion_is_autonomous"] is False, "autonomous deletion")
    require(retention["founder_approval_required_for_deletion"] is True, "deletion approval")
    require(retention["deletion_verification_required"] is True and retention["derived_data_deletion_required"] is True, "deletion verification")
    require(retention["backup_restore_evidence_status"] == "pending_operating_environment", "backup evidence")
    require(retention["recovery_objectives_status"] == "unset_until_measured", "recovery objectives")

    provider = value["provider_and_processor"]
    require(provider["unregistered_processor_default"] == "deny", "processor default")
    require(provider["approved_real_client_processor_count"] == 0, "processor count")
    for key in ["oauth_authorized", "provider_gateway_authorized", "provider_training_allowed", "credential_values_permitted", "paid_service_activation_authorized"]:
        require(provider[key] is False, key)

    cadence = {item["cadence_id"]: item for item in value["operating_cadences"]}
    require(set(cadence) == CADENCES, "cadences")
    require(cadence["OPC-CAD-PER-CHANGE"]["enabled_now"] is True, "per change")
    require(cadence["OPC-CAD-PER-RELEASE"]["enabled_now"] is True, "per release")
    require(all(not item["enabled_now"] for key, item in cadence.items() if key not in {"OPC-CAD-PER-CHANGE", "OPC-CAD-PER-RELEASE"}), "active cadence")

    exception = value["exception_policy"]
    require(exception["silent_waivers_permitted"] is False, "waivers")
    for key in ["exact_scope_required", "expiry_required", "compensating_controls_required", "independent_review_required", "founder_approval_required"]:
        require(exception[key] is True, key)
    require(len(set(exception["non_waivable_boundaries"])) == 6, "non-waivable")

    evidence = value["control_evidence"]
    require(evidence["chat_first_configuration_current"] is True, "chat-first evidence")
    require(all(evidence[key] is False for key in ["hosted_control_evidence_complete", "operating_environment_evidence_complete", "production_evidence_complete"]), "evidence honesty")
    require(evidence["evidence_expiry_enforced"] is True, "evidence expiry")
    require(set(value["activation_conditions"]) == ACTIVATION, "activation conditions")
    require(all(value["boundaries"][key] is False for key in DENIED), "boundary")
    require(value["boundaries"]["founder_accountability_preserved"] is True, "accountability")

    expected = {
        "decision_class_count": 6, "control_domain_count": 10, "security_control_count": 48,
        "mandatory_real_client_control_count": 18, "operating_gate_count": 8,
        "control_switch_count": 6, "incident_playbook_count": 12, "retention_policy_count": 4,
        "budget_profile_count": 6, "idempotency_required_command_count": 7,
        "approved_real_client_processor_count": 0, "hosted_control_requirement_count": 7,
        "operating_cadence_count": 7,
    }
    readiness = value["readiness_snapshot"]
    require(all(readiness[key] == expected_value for key, expected_value in expected.items()), "readiness counts")
    require(readiness["missing_security_controls"] == readiness["unknown_security_controls"] == readiness["duplicate_security_controls"] == [], "control reconciliation")
    require(all(readiness["checks"].values()) and readiness["local_prerequisites_passed"] is True, "prerequisites")
    for key in ["hosted_control_evidence_complete", "operating_environment_evidence_complete", "production_evidence_complete", *DENIED - {"real_client_data_enabled", "external_actions_authorized", "paid_services_authorized", "production_deployment_authorized", "autonomous_merge_authorized"}]:
        require(readiness[key] is False, key)


def mutations() -> list[tuple[str, Mutation]]:
    cases: list[tuple[str, Mutation]] = []

    def add(path: tuple[str, ...], replacement: Any, name: str) -> None:
        def mutate(value: dict[str, Any]) -> None:
            set_path(value, path, replacement)

        cases.append((name, mutate))

    for path, replacement, name in [
        (("phase_id",), "PCR-09", "phase"), (("status",), "operating_active", "status"),
        (("operating_context", "operator_model"), "multi_user", "operator"),
        (("operating_context", "permitted_data_classes"), ["public", "internal", "client_confidential"], "client data"),
        (("operating_context", "canonical_write_mode"), "direct", "direct writes"),
        (("operating_context", "network_default"), "allow", "network"),
        (("operating_context", "provider_training_allowed"), True, "training"),
        (("operating_context", "credential_values_permitted"), True, "credentials"),
        (("operating_context", "real_client_data_enabled"), True, "real data"),
        (("operating_context", "external_actions_enabled"), True, "external"),
        (("cost_and_usage", "paid_provider_spend_hard_cap"), 1, "spend"),
        (("cost_and_usage", "purchases_authorized"), True, "purchase"),
        (("cost_and_usage", "adapter_may_raise_limits"), True, "budget"),
        (("provider_and_processor", "approved_real_client_processor_count"), 1, "processor"),
        (("provider_and_processor", "oauth_authorized"), True, "oauth"),
        (("retention_and_recovery", "deletion_is_autonomous"), True, "deletion"),
        (("retention_and_recovery", "backup_restore_evidence_status"), "passed", "backup"),
        (("retention_and_recovery", "recovery_objectives_status"), "met", "recovery"),
        (("incident_routing", "agents_may_close_material_incidents"), True, "incident closure"),
        (("incident_routing", "implicated_actor_may_be_sole_reviewer"), True, "incident review"),
        (("exception_policy", "silent_waivers_permitted"), True, "waiver"),
        (("exception_policy", "exact_scope_required"), False, "scope"),
        (("control_evidence", "hosted_control_evidence_complete"), True, "hosted evidence"),
        (("control_evidence", "operating_environment_evidence_complete"), True, "operating evidence"),
        (("control_evidence", "production_evidence_complete"), True, "production evidence"),
        (("boundaries", "initial_operating_controls_activation_authorized"), True, "operating activation"),
        (("boundaries", "codex_start_authorized"), True, "codex"),
        (("boundaries", "runtime_activation_authorized"), True, "runtime"),
        (("boundaries", "hermes_activation_authorized"), True, "hermes"),
        (("boundaries", "northstar_implementation_authorized"), True, "Northstar"),
        (("boundaries", "founder_accountability_preserved"), False, "accountability"),
    ]:
        add(path, replacement, name)

    def remove_control(v: dict[str, Any]) -> None:
        v["control_domains"][0]["security_control_ids"].pop()

    def duplicate_control(v: dict[str, Any]) -> None:
        control_id = v["control_domains"][0]["security_control_ids"][0]
        v["control_domains"][1]["security_control_ids"].append(control_id)

    def enable_gate(v: dict[str, Any]) -> None:
        v["operating_gates"][0]["authorized"] = True

    def remove_idempotency(v: dict[str, Any]) -> None:
        gate = next(
            item for item in v["operating_gates"]
            if item["gate_id"] == "OPC-GATE-EXTERNAL-ACTION"
        )
        gate["required_conditions"].remove("idempotency_key")

    def enable_switch(v: dict[str, Any]) -> None:
        v["control_switches"][2]["initial_state"] = "allow"

    def fail_open(v: dict[str, Any]) -> None:
        v["control_switches"][0]["fail_mode"] = "fail_open"

    def enable_daily(v: dict[str, Any]) -> None:
        cadence = next(
            item for item in v["operating_cadences"]
            if item["cadence_id"] == "OPC-CAD-DAILY-ACTIVE"
        )
        cadence["enabled_now"] = True

    def remove_condition(v: dict[str, Any]) -> None:
        v["activation_conditions"].remove("pcr08_merged_to_main")

    cases.extend([
        ("remove control", remove_control), ("duplicate control", duplicate_control),
        ("enable gate", enable_gate), ("remove idempotency", remove_idempotency),
        ("enable switch", enable_switch), ("fail open", fail_open),
        ("enable daily", enable_daily), ("remove condition", remove_condition),
    ])
    return cases


def main() -> None:
    source, contract, schema = load(SOURCE), load(CONTRACT), load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(contract))
    require(not errors, "; ".join(error.message for error in errors))
    require(canonical(build_initial_operating_controls()) == CONTRACT.read_text(), "stale contract")
    require(source["contract_id"] == contract["contract_id"], "contract id")
    validate(contract)
    documentation = DOC.read_text()
    for token in ["PCR-08", "forty-eight security controls", "Founder-only", "paid-provider hard cap of zero", "initial_operating_controls_activation_authorized=false", "operating evidence remains pending", "commands-only"]:
        require(token in documentation, token)
    rejected = 0
    cases = mutations()
    for name, mutate in cases:
        candidate = copy.deepcopy(contract)
        mutate(candidate)
        try:
            if list(validator.iter_errors(candidate)):
                rejected += 1
                continue
            validate(candidate)
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected += 1
            continue
        raise AssertionError(f"Mutation was not rejected: {name}")
    readiness = contract["readiness_snapshot"]
    print(
        "PCR-08 initial operating-control configuration passed: "
        f"{readiness['control_domain_count']} domains, {readiness['security_control_count']} controls, "
        f"{readiness['operating_gate_count']} gates, {readiness['control_switch_count']} switches, "
        f"{len(cases)} mutation cases rejected, local_prerequisites_passed=true, "
        "initial_operating_controls_activation_authorized=false."
    )


if __name__ == "__main__":
    main()
