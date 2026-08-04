"""Shared enumerations used by deterministic offdata services."""

from enum import StrEnum


class LifecycleStage(StrEnum):
    MANDATE_INTAKE = "LIFE-STAGE-01"
    CONTEXT_PROBLEM = "LIFE-STAGE-02"
    RESEARCH_BASELINE = "LIFE-STAGE-03"
    HYPOTHESES_ARCHITECTURE = "LIFE-STAGE-04"
    METHODOLOGY_DESIGN = "LIFE-STAGE-05"
    PROPOSITION_PROPOSAL = "LIFE-STAGE-06"
    MOBILISATION = "LIFE-STAGE-07"
    DELIVERY_ANALYSIS = "LIFE-STAGE-08"
    QUALITY_DECISION_READINESS = "LIFE-STAGE-09"
    IMPLEMENTATION_ADOPTION = "LIFE-STAGE-10"
    BENEFITS_REALISATION = "LIFE-STAGE-11"
    CLOSEOUT_KNOWLEDGE = "LIFE-STAGE-12"
    EXPANSION_FOLLOW_ON = "LIFE-STAGE-13"


class OperationalState(StrEnum):
    NORMAL = "normal"
    WAITING = "waiting"
    BLOCKED = "blocked"
    RETRY = "retry"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class DecisionClass(StrEnum):
    ROUTINE = "DEC-ROUTINE"
    MATERIAL = "DEC-MATERIAL"
    EXTERNAL = "DEC-EXTERNAL"
    COMMERCIAL = "DEC-COMMERCIAL"
    LEGAL_REGULATORY = "DEC-LEGALREG"
    IRREVERSIBLE = "DEC-IRREVERSIBLE"


class EvidenceLevel(StrEnum):
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"


class GateOutcome(StrEnum):
    PROCEED = "proceed"
    PROCEED_WITH_CONDITIONS = "proceed_with_conditions"
    PAUSE = "pause"
    RECYCLE = "recycle"
    STOP = "stop"
    CLOSE = "close"


class ApprovalDecision(StrEnum):
    AUTO_EXECUTE = "auto_execute"
    EXECUTE_WITH_CONDITIONS = "execute_with_conditions"
    REQUEST_APPROVAL = "request_approval"
    PROHIBIT = "prohibit"
