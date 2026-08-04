"""Deterministic OpenAPI 3.1 contract builder."""

from typing import Any

from .contract_constants import CONTRACT_VERSION


def _schema_ref(name: str) -> dict[str, str]:
    return {
        "$ref": (
            "../schemas/offdata-contract-bundle.schema.json"
            f"#/$defs/{name}"
        )
    }


def _error_responses() -> dict[str, Any]:
    return {
        "400": {"$ref": "#/components/responses/BadRequest"},
        "401": {"$ref": "#/components/responses/Unauthorised"},
        "403": {"$ref": "#/components/responses/Forbidden"},
        "404": {"$ref": "#/components/responses/NotFound"},
        "409": {"$ref": "#/components/responses/Conflict"},
        "422": {"$ref": "#/components/responses/ValidationError"},
    }


def _json_response(
    schema: dict[str, Any], description: str = "Successful response"
) -> dict[str, Any]:
    return {
        "description": description,
        "content": {"application/json": {"schema": schema}},
    }


def _json_request(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "required": True,
        "content": {"application/json": {"schema": schema}},
    }


def _engagement_parameter() -> dict[str, Any]:
    return {
        "name": "engagement_id",
        "in": "path",
        "required": True,
        "schema": {"type": "string", "minLength": 1},
    }


def _collection_paths(record_name: str, tag: str) -> dict[str, Any]:
    """Return GET/POST operations for a generic engagement-scoped record family."""

    return {
        "get": {
            "operationId": f"list{record_name}",
            "tags": [tag],
            "parameters": [_engagement_parameter()],
            "responses": {
                "200": _json_response(_schema_ref("RecordCollectionResponse")),
                **_error_responses(),
            },
        },
        "post": {
            "operationId": f"create{record_name}",
            "tags": [tag],
            "parameters": [_engagement_parameter()],
            "requestBody": _json_request({"type": "object", "additionalProperties": True}),
            "responses": {
                "202": _json_response(_schema_ref("CommandResponse"), "Command accepted"),
                **_error_responses(),
            },
        },
    }


def build_openapi_document() -> dict[str, Any]:
    """Generate the canonical OpenAPI 3.1 contract."""

    paths: dict[str, Any] = {
        "/health": {
            "get": {
                "operationId": "healthCheck",
                "tags": ["operations"],
                "security": [],
                "responses": {
                    "200": _json_response(_schema_ref("HealthResponse")),
                },
            }
        },
        "/v1/engagements": {
            "get": {
                "operationId": "listEngagements",
                "tags": ["engagements"],
                "parameters": [
                    {
                        "name": "cursor",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "schema": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 25,
                        },
                    },
                ],
                "responses": {
                    "200": _json_response(_schema_ref("EngagementListResponse")),
                    **_error_responses(),
                },
            },
            "post": {
                "operationId": "createEngagement",
                "tags": ["engagements"],
                "requestBody": _json_request(_schema_ref("EngagementCreateRequest")),
                "responses": {
                    "202": _json_response(
                        _schema_ref("CommandResponse"), "Creation command accepted"
                    ),
                    **_error_responses(),
                },
            },
        },
        "/v1/engagements/{engagement_id}": {
            "get": {
                "operationId": "getEngagement",
                "tags": ["engagements"],
                "parameters": [_engagement_parameter()],
                "responses": {
                    "200": _json_response(_schema_ref("EngagementView")),
                    **_error_responses(),
                },
            }
        },
        "/v1/engagements/{engagement_id}/commands": {
            "post": {
                "operationId": "submitEngagementCommand",
                "tags": ["engagements"],
                "parameters": [_engagement_parameter()],
                "requestBody": _json_request(_schema_ref("CommandEnvelope")),
                "responses": {
                    "202": _json_response(_schema_ref("CommandResponse"), "Command accepted"),
                    **_error_responses(),
                },
            }
        },
        "/v1/engagements/{engagement_id}/events": {
            "get": {
                "operationId": "listEngagementEvents",
                "tags": ["engagements"],
                "parameters": [_engagement_parameter()],
                "responses": {
                    "200": _json_response(
                        {"type": "array", "items": _schema_ref("DomainEvent")}
                    ),
                    **_error_responses(),
                },
            }
        },
        "/v1/engagements/{engagement_id}/timeline": {
            "get": {
                "operationId": "getEngagementTimeline",
                "tags": ["engagements"],
                "parameters": [_engagement_parameter()],
                "responses": {
                    "200": _json_response(
                        {"type": "array", "items": _schema_ref("TimelineItem")}
                    ),
                    **_error_responses(),
                },
            }
        },
        "/v1/engagements/{engagement_id}/founder-summary": {
            "get": {
                "operationId": "getFounderEngagementSummary",
                "tags": ["founder"],
                "parameters": [_engagement_parameter()],
                "responses": {
                    "200": _json_response(_schema_ref("FounderEngagementSummary")),
                    **_error_responses(),
                },
            }
        },
        "/v1/engagements/{engagement_id}/decision-inbox": {
            "get": {
                "operationId": "listFounderDecisionInbox",
                "tags": ["founder"],
                "parameters": [_engagement_parameter()],
                "responses": {
                    "200": _json_response(
                        {"type": "array", "items": _schema_ref("DecisionInboxItem")}
                    ),
                    **_error_responses(),
                },
            }
        },
    }

    for action in ("pause", "resume", "cancel"):
        paths[f"/v1/engagements/{{engagement_id}}/{action}"] = {
            "post": {
                "operationId": f"{action}Engagement",
                "tags": ["engagements"],
                "parameters": [_engagement_parameter()],
                "requestBody": _json_request(_schema_ref("CommandEnvelope")),
                "responses": {
                    "202": _json_response(_schema_ref("CommandResponse")),
                    **_error_responses(),
                },
            }
        }

    collection_specs = {
        "hypotheses": ("Hypotheses", "analysis"),
        "method-selections": ("MethodSelections", "analysis"),
        "claims": ("Claims", "evidence"),
        "evidence": ("Evidence", "evidence"),
        "analyses": ("Analyses", "analysis"),
        "recommendations": ("Recommendations", "analysis"),
        "quality-findings": ("QualityFindings", "quality"),
        "approvals": ("Approvals", "approvals"),
        "deliverables": ("Deliverables", "delivery"),
        "initiatives": ("Initiatives", "implementation"),
        "benefits": ("Benefits", "implementation"),
        "decisions": ("Decisions", "engagements"),
    }
    for path_name, (record_name, tag) in collection_specs.items():
        paths[f"/v1/engagements/{{engagement_id}}/{path_name}"] = _collection_paths(
            record_name, tag
        )

    paths["/v1/engagements/{engagement_id}/mandate"] = {
        "get": {
            "operationId": "getMandate",
            "tags": ["engagements"],
            "parameters": [_engagement_parameter()],
            "responses": {
                "200": _json_response({"type": "object", "additionalProperties": True}),
                **_error_responses(),
            },
        },
        "put": {
            "operationId": "updateMandate",
            "tags": ["engagements"],
            "parameters": [_engagement_parameter()],
            "requestBody": _json_request({"type": "object", "additionalProperties": True}),
            "responses": {
                "202": _json_response(_schema_ref("CommandResponse")),
                **_error_responses(),
            },
        },
    }

    paths["/v1/engagements/{engagement_id}/decisions/{decision_id}/resolve"] = {
        "post": {
            "operationId": "resolveDecision",
            "tags": ["founder"],
            "parameters": [
                _engagement_parameter(),
                {
                    "name": "decision_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1},
                },
            ],
            "requestBody": _json_request(_schema_ref("ApprovalRecord")),
            "responses": {
                "202": _json_response(_schema_ref("CommandResponse")),
                **_error_responses(),
            },
        }
    }

    paths["/v1/engagements/{engagement_id}/release-gates/{gate_id}/evaluate"] = {
        "post": {
            "operationId": "evaluateReleaseGate",
            "tags": ["quality"],
            "parameters": [
                _engagement_parameter(),
                {
                    "name": "gate_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1},
                },
            ],
            "requestBody": _json_request(_schema_ref("QualityReview")),
            "responses": {
                "200": _json_response(_schema_ref("GateAssessment")),
                **_error_responses(),
            },
        }
    }

    error_response = {
        "description": "Error response",
        "content": {"application/json": {"schema": _schema_ref("ApiError")}},
    }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "offdata Engagement API",
            "version": CONTRACT_VERSION,
            "description": (
                "Canonical command, query and Founder-read-model API. Mutations are "
                "commands and may return pending approval rather than execute."
            ),
        },
        "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
        "servers": [{"url": "http://localhost:8000", "description": "Local development"}],
        "security": [{"bearerAuth": []}],
        "tags": [
            {"name": "engagements"},
            {"name": "founder"},
            {"name": "analysis"},
            {"name": "evidence"},
            {"name": "quality"},
            {"name": "approvals"},
            {"name": "delivery"},
            {"name": "implementation"},
            {"name": "operations"},
        ],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            },
            "responses": {
                "BadRequest": error_response,
                "Unauthorised": error_response,
                "Forbidden": error_response,
                "NotFound": error_response,
                "Conflict": error_response,
                "ValidationError": error_response,
            },
        },
        "x-offdata-command-catalogue": "../contracts/command-event-catalogue.json",
        "x-offdata-requirements": [
            "DATA-001",
            "DATA-002",
            "DATA-003",
            "DATA-004",
            "DATA-005",
            "AUTH-001",
            "AUTH-003",
            "AUTH-004",
            "AUTH-005",
            "AUTH-007",
            "AGENT-003",
            "AGENT-004",
        ],
    }
