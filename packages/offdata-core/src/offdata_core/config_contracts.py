"""Structural JSON Schemas for governed offdata configuration files."""

from typing import Any

from .contract_constants import CONTRACT_VERSION, SCHEMA_BASE_URI


def build_config_schema() -> dict[str, Any]:
    """Generate schemas for lifecycle, policy, agent and test configuration."""
    strings = {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True}
    optional_strings = {"type": "array", "items": {"type": "string"}, "uniqueItems": True}
    requirements = {"type": "array", "items": {"type": "string", "pattern": "^[A-Z]+-[0-9]{3}$"}, "minItems": 1, "uniqueItems": True}
    semver = {"type": "string", "pattern": r"^[0-9]+\.[0-9]+\.[0-9]+$"}
    contract = {"type": "string", "pattern": r"^schemas/offdata-contract-bundle\.schema\.json#/\$defs/[A-Za-z0-9_]+$"}
    decisions = ["DEC-ROUTINE", "DEC-MATERIAL", "DEC-EXTERNAL", "DEC-COMMERCIAL", "DEC-LEGALREG", "DEC-IRREVERSIBLE"]
    decision_schema = {
        "type": "object",
        "required": ["minimum_evidence", "default_authority"],
        "properties": {"minimum_evidence": {"enum": ["E1", "E2", "E3", "E4"]}, "default_authority": {}},
    }
    defs: dict[str, Any] = {}
    defs["LifecycleStageConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["id", "name", "exit_gate", "required_outputs"],
        "properties": {
            "id": {"type": "string", "pattern": "^LIFE-STAGE-(0[1-9]|1[0-3])$"},
            "name": {"type": "string", "minLength": 1},
            "exit_gate": {"type": "string", "pattern": "^GATE-(0[1-9]|1[0-3])$"},
            "required_outputs": optional_strings,
        },
    }
    defs["LifecycleConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["version", "schema_version", "source_requirements", "stage_selection_rule", "stages", "operational_states", "gate_outcomes", "controls"],
        "properties": {
            "version": {"type": "string", "minLength": 1}, "schema_version": {"const": "offdata.lifecycle.v1"},
            "source_requirements": requirements, "stage_selection_rule": {"const": "earliest_unmet_mandatory_gate"},
            "stages": {"type": "array", "minItems": 13, "maxItems": 13, "items": {"$ref": "#/$defs/LifecycleStageConfig"}},
            "operational_states": {"type": "array", "uniqueItems": True, "items": {"enum": ["normal", "waiting", "blocked", "retry", "cancelled", "completed"]}},
            "gate_outcomes": {"type": "array", "uniqueItems": True, "items": {"enum": ["proceed", "proceed_with_conditions", "pause", "recycle", "stop", "close"]}},
            "controls": {"type": "object", "minProperties": 1},
        },
    }
    defs["PolicyConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["version", "schema_version", "source_requirements", "decision_classes", "strictest_class_governs", "actions", "founder_packet", "no_self_approval"],
        "properties": {
            "version": {"type": "string", "minLength": 1}, "schema_version": {"const": "offdata.policy.v1"},
            "source_requirements": requirements,
            "decision_classes": {"type": "object", "required": decisions, "additionalProperties": False, "properties": {name: decision_schema for name in decisions}},
            "strictest_class_governs": {"const": True}, "actions": {"type": "object", "minProperties": 1},
            "founder_packet": {"type": "object", "minProperties": 1}, "no_self_approval": {"type": "object", "minProperties": 1},
        },
    }
    defs["ContextProfileConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["max_records", "selection_order", "include_untrusted_as_instructions"],
        "properties": {"max_records": {"type": "integer", "minimum": 1}, "selection_order": strings, "include_untrusted_as_instructions": {"const": False}},
    }
    defs["BudgetProfileConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["timeout_seconds", "max_retries", "max_input_tokens", "max_output_tokens", "max_cost", "currency", "model_or_route"],
        "properties": {
            "timeout_seconds": {"type": "integer", "minimum": 1}, "max_retries": {"type": "integer", "minimum": 0},
            "max_input_tokens": {"type": "integer", "minimum": 1}, "max_output_tokens": {"type": "integer", "minimum": 1},
            "max_cost": {"type": "number", "exclusiveMinimum": 0}, "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
            "model_or_route": {"type": "string", "minLength": 1},
        },
    }
    defs["ProviderRouteConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["route_id", "model_or_route", "minimum_complexity", "minimum_evidence_risk", "latency_rank", "cost_rank", "output_contract"],
        "properties": {
            "route_id": {"type": "string", "minLength": 1}, "model_or_route": {"type": "string", "minLength": 1},
            "minimum_complexity": {"type": "integer", "minimum": 1, "maximum": 5}, "minimum_evidence_risk": {"type": "integer", "minimum": 1, "maximum": 5},
            "latency_rank": {"type": "integer", "minimum": 1}, "cost_rank": {"type": "integer", "minimum": 1}, "output_contract": contract,
        },
    }
    defs["AgentConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["id", "agent_id", "agent_version", "prompt_version", "purpose", "skill_package", "input_contracts", "output_contract", "allowed_record_families", "permitted_tool_classes", "prohibited_actions", "context_profile", "evidence_rules", "escalation_policy", "budget_profile", "evaluation_profile"],
        "properties": {
            "id": {"type": "string", "pattern": "^[a-z][a-z0-9_]+$"}, "agent_id": {"type": "string", "pattern": "^[a-z][a-z0-9_]+$"},
            "agent_version": semver, "prompt_version": semver, "purpose": {"type": "string", "minLength": 1},
            "skill_package": {"type": "string", "pattern": "^agents/[a-z][a-z0-9_]+/SKILL\\.md$"},
            "input_contracts": {"type": "array", "items": contract, "minItems": 1, "uniqueItems": True}, "output_contract": contract,
            "allowed_record_families": strings, "permitted_tool_classes": strings, "prohibited_actions": strings,
            "context_profile": {"type": "string", "minLength": 1}, "evidence_rules": strings, "escalation_policy": strings,
            "budget_profile": {"type": "string", "minLength": 1}, "evaluation_profile": {"type": "string", "pattern": "^AE-[A-Z]+$"},
        },
    }
    defs["AgentsConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["version", "schema_version", "source_requirements", "provider_independent", "default_output_contract", "default_context_contract", "default_write_mode", "canonical_writes_via_commands_only", "context_profiles", "budget_profiles", "routing_policy", "admission_thresholds", "mandatory_failures", "agents"],
        "properties": {
            "version": semver, "schema_version": {"const": "offdata.agents.v2"}, "source_requirements": requirements,
            "provider_independent": {"const": True}, "default_output_contract": contract, "default_context_contract": contract,
            "default_write_mode": {"const": "propose_only"}, "canonical_writes_via_commands_only": {"const": True},
            "context_profiles": {"type": "object", "minProperties": 1, "additionalProperties": {"$ref": "#/$defs/ContextProfileConfig"}},
            "budget_profiles": {"type": "object", "minProperties": 1, "additionalProperties": {"$ref": "#/$defs/BudgetProfileConfig"}},
            "routing_policy": {"type": "object", "additionalProperties": False, "required": ["preserve_output_contract", "route_dimensions", "routes"], "properties": {"preserve_output_contract": {"const": True}, "route_dimensions": strings, "routes": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/ProviderRouteConfig"}}}},
            "admission_thresholds": {"type": "object", "required": ["minimum_schema_validity", "minimum_critical_dimension", "minimum_weighted_score", "maximum_repeated_run_variance", "independent_review_required"], "properties": {"minimum_schema_validity": {"type": "number", "minimum": 0, "maximum": 1}, "minimum_critical_dimension": {"type": "number", "minimum": 0, "maximum": 100}, "minimum_weighted_score": {"type": "number", "minimum": 0, "maximum": 100}, "maximum_repeated_run_variance": {"type": "number", "minimum": 0, "maximum": 100}, "independent_review_required": {"const": True}}},
            "mandatory_failures": strings, "agents": {"type": "array", "minItems": 11, "maxItems": 11, "items": {"$ref": "#/$defs/AgentConfig"}},
        },
    }
    defs["AgentEvaluationCaseConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["case_id", "kind", "fixture", "prompt", "expected_status", "required_signals", "forbidden_signals", "mandatory_fail"],
        "properties": {"case_id": {"type": "string", "pattern": "^AE-[A-Z]+-(POS|NEG|ADV)-[0-9]{3}$"}, "kind": {"enum": ["positive", "negative", "adversarial"]}, "fixture": {"type": "string", "minLength": 1}, "prompt": {"type": "string", "minLength": 1}, "expected_status": {"enum": ["success", "partial", "blocked", "failed"]}, "required_signals": strings, "forbidden_signals": strings, "mandatory_fail": {"type": "boolean"}},
    }
    defs["AgentEvaluationProfileConfig"] = {"type": "object", "additionalProperties": False, "required": ["agent_id", "cases"], "properties": {"agent_id": {"type": "string", "pattern": "^[a-z][a-z0-9_]+$"}, "cases": {"type": "array", "minItems": 3, "maxItems": 3, "items": {"$ref": "#/$defs/AgentEvaluationCaseConfig"}}}}
    defs["AgentEvaluationConfig"] = {
        "type": "object", "additionalProperties": False,
        "required": ["version", "schema_version", "source_requirements", "profiles"],
        "properties": {"version": semver, "schema_version": {"const": "offdata.agent-evaluations.v1"}, "source_requirements": requirements, "profiles": {"type": "object", "minProperties": 11, "maxProperties": 11, "additionalProperties": {"$ref": "#/$defs/AgentEvaluationProfileConfig"}}},
    }
    defs["TestRecord"] = {
        "type": "object", "additionalProperties": False, "required": ["kind", "phase", "requirements", "evidence_status"],
        "properties": {"node_id": {"type": "string", "minLength": 1}, "test_id": {"type": "string", "minLength": 1}, "kind": {"type": "string", "minLength": 1}, "phase": {"type": "string", "minLength": 1}, "requirements": requirements, "evidence_status": {"type": "string", "minLength": 1}},
        "oneOf": [{"required": ["node_id"], "not": {"required": ["test_id"]}}, {"required": ["test_id"], "not": {"required": ["node_id"]}}],
    }
    defs["TestRegistry"] = {"type": "object", "additionalProperties": False, "required": ["version", "rules", "implemented_tests", "planned_tests"], "properties": {"version": {"type": "string", "minLength": 1}, "rules": {"type": "object", "minProperties": 1}, "implemented_tests": {"type": "array", "items": {"$ref": "#/$defs/TestRecord"}}, "planned_tests": {"type": "array", "items": {"$ref": "#/$defs/TestRecord"}}}}
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": f"{SCHEMA_BASE_URI}/offdata-configs.schema.json", "title": "Offdata Governed Configuration Schemas", "version": CONTRACT_VERSION, "$defs": defs}
