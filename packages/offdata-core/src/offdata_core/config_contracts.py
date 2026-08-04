"""Structural JSON Schemas for governed offdata configuration files."""

from typing import Any

from .contract_constants import CONTRACT_VERSION, SCHEMA_BASE_URI


def build_config_schema() -> dict[str, Any]:
    """Generate structural schemas for governed YAML and JSON configuration files."""

    string_array = {"type": "array", "items": {"type": "string"}, "uniqueItems": True}
    requirement_array = {
        "type": "array",
        "items": {"type": "string", "pattern": "^[A-Z]+-[0-9]{3}$"},
        "minItems": 1,
        "uniqueItems": True,
    }
    decision_properties = {
        item: {
            "type": "object",
            "required": ["minimum_evidence", "default_authority"],
            "properties": {
                "minimum_evidence": {"enum": ["E1", "E2", "E3", "E4"]},
                "default_authority": {
                    "oneOf": [
                        {"type": "string", "minLength": 1},
                        {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                            "minItems": 1,
                        },
                    ]
                },
            },
        }
        for item in (
            "DEC-ROUTINE",
            "DEC-MATERIAL",
            "DEC-EXTERNAL",
            "DEC-COMMERCIAL",
            "DEC-LEGALREG",
            "DEC-IRREVERSIBLE",
        )
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SCHEMA_BASE_URI}/offdata-configs.schema.json",
        "title": "Offdata Governed Configuration Schemas",
        "version": CONTRACT_VERSION,
        "$defs": {
            "LifecycleStageConfig": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "name", "exit_gate", "required_outputs"],
                "properties": {
                    "id": {"type": "string", "pattern": "^LIFE-STAGE-(0[1-9]|1[0-3])$"},
                    "name": {"type": "string", "minLength": 1},
                    "exit_gate": {"type": "string", "pattern": "^GATE-(0[1-9]|1[0-3])$"},
                    "required_outputs": string_array,
                },
            },
            "LifecycleConfig": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "version",
                    "schema_version",
                    "source_requirements",
                    "stage_selection_rule",
                    "stages",
                    "operational_states",
                    "gate_outcomes",
                    "controls",
                ],
                "properties": {
                    "version": {"type": "string", "minLength": 1},
                    "schema_version": {"const": "offdata.lifecycle.v1"},
                    "source_requirements": requirement_array,
                    "stage_selection_rule": {"const": "earliest_unmet_mandatory_gate"},
                    "stages": {
                        "type": "array",
                        "minItems": 13,
                        "maxItems": 13,
                        "items": {"$ref": "#/$defs/LifecycleStageConfig"},
                    },
                    "operational_states": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {
                            "enum": [
                                "normal",
                                "waiting",
                                "blocked",
                                "retry",
                                "cancelled",
                                "completed",
                            ]
                        },
                    },
                    "gate_outcomes": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {
                            "enum": [
                                "proceed",
                                "proceed_with_conditions",
                                "pause",
                                "recycle",
                                "stop",
                                "close",
                            ]
                        },
                    },
                    "controls": {"type": "object", "minProperties": 1},
                },
            },
            "PolicyConfig": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "version",
                    "schema_version",
                    "source_requirements",
                    "decision_classes",
                    "strictest_class_governs",
                    "actions",
                    "founder_packet",
                    "no_self_approval",
                ],
                "properties": {
                    "version": {"type": "string", "minLength": 1},
                    "schema_version": {"const": "offdata.policy.v1"},
                    "source_requirements": requirement_array,
                    "decision_classes": {
                        "type": "object",
                        "required": list(decision_properties),
                        "additionalProperties": False,
                        "properties": decision_properties,
                    },
                    "strictest_class_governs": {"const": True},
                    "actions": {"type": "object", "minProperties": 1},
                    "founder_packet": {"type": "object", "minProperties": 1},
                    "no_self_approval": {"type": "object", "minProperties": 1},
                },
            },
            "AgentConfig": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "id",
                    "purpose",
                    "allowed_record_families",
                    "permitted_tool_classes",
                    "prohibited_actions",
                    "evaluation_profile",
                ],
                "properties": {
                    "id": {"type": "string", "pattern": "^[a-z][a-z0-9_]+$"},
                    "purpose": {"type": "string", "minLength": 1},
                    "allowed_record_families": string_array,
                    "permitted_tool_classes": string_array,
                    "prohibited_actions": string_array,
                    "evaluation_profile": {"type": "string", "minLength": 1},
                },
            },
            "AgentsConfig": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "version",
                    "schema_version",
                    "default_output_contract",
                    "default_context_contract",
                    "default_write_mode",
                    "canonical_writes_via_commands_only",
                    "agents",
                    "budgets",
                ],
                "properties": {
                    "version": {"type": "string", "minLength": 1},
                    "schema_version": {"const": "offdata.agents.v1"},
                    "default_output_contract": {"type": "string", "minLength": 1},
                    "default_context_contract": {"type": "string", "minLength": 1},
                    "default_write_mode": {"const": "propose_only"},
                    "canonical_writes_via_commands_only": {"const": True},
                    "agents": {
                        "type": "array",
                        "minItems": 11,
                        "maxItems": 11,
                        "items": {"$ref": "#/$defs/AgentConfig"},
                    },
                    "budgets": {"type": "object", "minProperties": 1},
                },
            },
            "TestRecord": {
                "type": "object",
                "additionalProperties": False,
                "required": ["kind", "phase", "requirements", "evidence_status"],
                "properties": {
                    "node_id": {"type": "string", "minLength": 1},
                    "test_id": {"type": "string", "minLength": 1},
                    "kind": {"type": "string", "minLength": 1},
                    "phase": {"type": "string", "minLength": 1},
                    "requirements": requirement_array,
                    "evidence_status": {"type": "string", "minLength": 1},
                },
                "oneOf": [
                    {"required": ["node_id"], "not": {"required": ["test_id"]}},
                    {"required": ["test_id"], "not": {"required": ["node_id"]}},
                ],
            },
            "TestRegistry": {
                "type": "object",
                "additionalProperties": False,
                "required": ["version", "rules", "implemented_tests", "planned_tests"],
                "properties": {
                    "version": {"type": "string", "minLength": 1},
                    "rules": {"type": "object", "minProperties": 1},
                    "implemented_tests": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/TestRecord"},
                    },
                    "planned_tests": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/TestRecord"},
                    },
                },
            },
        },
    }
