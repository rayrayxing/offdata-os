"""Machine-readable contract registry and deterministic exporters.

The registry is the single source of truth for JSON Schema, OpenAPI and command/event
catalogue artefacts. Committed generated files must remain byte-for-byte reproducible.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .api_contracts import (
    ApiError,
    ApprovalRequirement,
    CommandResponse,
    DecisionInboxItem,
    DecisionInboxOption,
    EngagementCreateRequest,
    EngagementListResponse,
    EngagementView,
    FounderEngagementSummary,
    HealthResponse,
    RecordCollectionResponse,
    TimelineItem,
)
from .command_catalogue import build_command_event_catalogue
from .config_contracts import build_config_schema
from .contract_constants import CONTRACT_VERSION, SCHEMA_BASE_URI
from .contracts import (
    AgentEnvelope,
    ContextBudget,
    ContextPackage,
    Escalation,
    FounderDecisionPacket,
    FounderOption,
    QualityCheck,
    RecordChange,
    UsageRecord,
)
from .crm import (
    Contact,
    OpportunityDossier,
    Organisation,
    OutreachAssessment,
    OutreachControl,
)
from .delivery import (
    Assertion,
    CrossFormatReconciliation,
    DeliverableManifest,
    ReconciliationResult,
    StoryModel,
    StorySection,
    VisualEntity,
    VisualRelationship,
    VisualSpecification,
)
from .events import (
    ActorRef,
    ApprovalRecord,
    ApprovalRequest,
    CommandEnvelope,
    DomainEvent,
)
from .knowledge import (
    MethodologyCandidate,
    MethodRecord,
    MethodSelection,
    ProblemArchetype,
    SourceDocument,
    SourcePassage,
)
from .lifecycle import StageDetectionResult, TransitionRequest, TransitionResult
from .openapi_contract import build_openapi_document
from .policy import PolicyContext, PolicyResult, ProposedAction
from .quality import (
    Defect,
    DimensionScore,
    ExceptionRecord,
    GateAssessment,
    IndependentSignoff,
    QualityReview,
)


MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    "StageDetectionResult": StageDetectionResult,
    "TransitionRequest": TransitionRequest,
    "TransitionResult": TransitionResult,
    "PolicyContext": PolicyContext,
    "ProposedAction": ProposedAction,
    "PolicyResult": PolicyResult,
    "RecordChange": RecordChange,
    "QualityCheck": QualityCheck,
    "Escalation": Escalation,
    "UsageRecord": UsageRecord,
    "AgentEnvelope": AgentEnvelope,
    "ContextBudget": ContextBudget,
    "ContextPackage": ContextPackage,
    "FounderOption": FounderOption,
    "FounderDecisionPacket": FounderDecisionPacket,
    "SourceDocument": SourceDocument,
    "SourcePassage": SourcePassage,
    "MethodRecord": MethodRecord,
    "ProblemArchetype": ProblemArchetype,
    "MethodSelection": MethodSelection,
    "MethodologyCandidate": MethodologyCandidate,
    "ActorRef": ActorRef,
    "CommandEnvelope": CommandEnvelope,
    "DomainEvent": DomainEvent,
    "ApprovalRequest": ApprovalRequest,
    "ApprovalRecord": ApprovalRecord,
    "DimensionScore": DimensionScore,
    "Defect": Defect,
    "QualityReview": QualityReview,
    "GateAssessment": GateAssessment,
    "ExceptionRecord": ExceptionRecord,
    "IndependentSignoff": IndependentSignoff,
    "Assertion": Assertion,
    "StorySection": StorySection,
    "StoryModel": StoryModel,
    "VisualEntity": VisualEntity,
    "VisualRelationship": VisualRelationship,
    "VisualSpecification": VisualSpecification,
    "DeliverableManifest": DeliverableManifest,
    "ReconciliationResult": ReconciliationResult,
    "CrossFormatReconciliation": CrossFormatReconciliation,
    "Organisation": Organisation,
    "Contact": Contact,
    "OpportunityDossier": OpportunityDossier,
    "OutreachControl": OutreachControl,
    "OutreachAssessment": OutreachAssessment,
    "ApiError": ApiError,
    "ApprovalRequirement": ApprovalRequirement,
    "CommandResponse": CommandResponse,
    "EngagementCreateRequest": EngagementCreateRequest,
    "EngagementView": EngagementView,
    "EngagementListResponse": EngagementListResponse,
    "TimelineItem": TimelineItem,
    "FounderEngagementSummary": FounderEngagementSummary,
    "DecisionInboxOption": DecisionInboxOption,
    "DecisionInboxItem": DecisionInboxItem,
    "RecordCollectionResponse": RecordCollectionResponse,
    "HealthResponse": HealthResponse,
}


def model_import_path(model: type[BaseModel]) -> str:
    return f"{model.__module__}:{model.__name__}"


def build_model_registry_document() -> dict[str, Any]:
    return {
        "version": CONTRACT_VERSION,
        "schema_dialect": "https://json-schema.org/draft/2020-12/schema",
        "models": {
            name: {
                "python": model_import_path(model),
                "schema_ref": (
                    f"../schemas/offdata-contract-bundle.schema.json#/$defs/{name}"
                ),
            }
            for name, model in sorted(MODEL_REGISTRY.items())
        },
    }


def _merge_definition(
    definitions: dict[str, Any], name: str, schema: Mapping[str, Any]
) -> None:
    candidate = dict(schema)
    existing = definitions.get(name)
    if existing is not None and existing != candidate:
        raise ValueError(f"Conflicting generated JSON Schema definition: {name}")
    definitions[name] = candidate


def build_schema_bundle() -> dict[str, Any]:
    """Generate one Draft 2020-12 bundle containing every Pydantic contract."""

    definitions: dict[str, Any] = {}
    for name, model in sorted(MODEL_REGISTRY.items()):
        schema = model.model_json_schema(ref_template="#/$defs/{model}")
        nested = schema.pop("$defs", {})
        for nested_name, nested_schema in sorted(nested.items()):
            _merge_definition(definitions, nested_name, nested_schema)
        _merge_definition(definitions, name, schema)

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SCHEMA_BASE_URI}/offdata-contract-bundle.schema.json",
        "title": "Offdata Machine Contract Bundle",
        "description": (
            "Generated from the offdata-core Pydantic models. Do not edit by hand; "
            "run scripts/export_machine_contracts.py."
        ),
        "version": CONTRACT_VERSION,
        "$defs": {name: definitions[name] for name in sorted(definitions)},
        "x-offdata-model-registry": {
            name: model_import_path(model)
            for name, model in sorted(MODEL_REGISTRY.items())
        },
    }


def build_alias_schema(model_name: str, filename: str, title: str) -> dict[str, Any]:
    """Generate a stable standalone alias to one canonical bundled definition."""

    if model_name not in MODEL_REGISTRY:
        raise KeyError(f"Unknown contract model: {model_name}")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SCHEMA_BASE_URI}/{filename}",
        "title": title,
        "$ref": f"offdata-contract-bundle.schema.json#/$defs/{model_name}",
        "x-offdata-canonical-bundle": "offdata-contract-bundle.schema.json",
        "x-offdata-model": model_name,
    }


def write_json(path: Path, document: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def export_all(repository_root: Path) -> list[Path]:
    """Generate every committed Phase 1 machine contract."""

    outputs = {
        repository_root / "schemas/offdata-contract-bundle.schema.json": build_schema_bundle(),
        repository_root / "schemas/offdata-configs.schema.json": build_config_schema(),
        repository_root / "schemas/agent-envelope.schema.json": build_alias_schema(
            "AgentEnvelope", "agent-envelope.schema.json", "Offdata Agent Envelope"
        ),
        repository_root / "schemas/context-package.schema.json": build_alias_schema(
            "ContextPackage",
            "context-package.schema.json",
            "Offdata Minimum-Sufficient Context Package",
        ),
        repository_root / "schemas/founder-decision-packet.schema.json": build_alias_schema(
            "FounderDecisionPacket",
            "founder-decision-packet.schema.json",
            "Offdata Founder Decision Packet",
        ),
        repository_root / "contracts/model-registry.json": build_model_registry_document(),
        repository_root
        / "contracts/command-event-catalogue.json": build_command_event_catalogue(),
        repository_root / "api/openapi.json": build_openapi_document(),
    }
    for path, document in outputs.items():
        write_json(path, document)
    return sorted(outputs)
