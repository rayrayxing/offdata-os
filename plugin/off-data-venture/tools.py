"""Pure deterministic off/data policy primitives.

Authoritative DB mutations must additionally enforce constraints/transactions.
These functions are deliberately model-free and safe to unit test.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

G3_REQUIRED = (
    "accountIdentity",
    "actorIdentity",
    "counterpartyRole",
    "interactionType",
    "occurredAt",
    "channel",
    "receiptRef",
)


def _present(value: Any) -> bool:
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def g3_direct_admissibility(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Fail-closed direct-buyer G3 eligibility.

    No URL/domain/source fallback is permitted. This function only establishes
    tuple completeness/basic authority conditions; imported G3 policy may add
    stricter requirements.
    """
    missing = [key for key in G3_REQUIRED if not _present(evidence.get(key))]
    reasons: list[str] = []
    if missing:
        reasons.append("MISSING_DIRECT_TUPLE:" + ",".join(missing))
    if evidence.get("purpose") != "DIRECT_BUYER":
        reasons.append("WRONG_EVIDENCE_PURPOSE")
    if evidence.get("admissibility") in {"QUARANTINED", "INADMISSIBLE", "PROVISIONAL"}:
        reasons.append("NON_AUTHORITATIVE_ADMISSIBILITY")
    if evidence.get("environment") != "LIVE":
        reasons.append("NON_LIVE_ENVIRONMENT")
    if evidence.get("isProvisional") is True:
        reasons.append("PROVISIONAL")
    return {
        "eligible": not reasons,
        "missing": missing,
        "reasons": reasons,
        "authoritativeContribution": 1 if not reasons else 0,
    }


def normalize_operation_fingerprint(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def classify_concern_action(severity: str) -> dict[str, Any]:
    table = {
        "BLOCKING": {"halts": True, "defaultAction": "BLOCK"},
        "MATERIAL_EXPERIMENT": {"halts": False, "defaultAction": "CREATE_EXPERIMENT"},
        "DESIGN_CONSTRAINT": {"halts": False, "defaultAction": "APPLY_CONSTRAINT"},
        "MONITOR": {"halts": False, "defaultAction": "MONITOR"},
    }
    if severity not in table:
        raise ValueError("UNKNOWN_CONCERN_SEVERITY")
    return table[severity]


def authority_precheck(*, kill_switch: bool, environment: str, required_environment: str,
                       grant_active: bool, authorization_active: bool,
                       gate_current: bool = True, budget_remaining: bool = True) -> dict[str, Any]:
    reasons = []
    if kill_switch:
        reasons.append("KILL_SWITCH")
    if environment != required_environment:
        reasons.append("ENVIRONMENT_MISMATCH")
    if not grant_active:
        reasons.append("NO_ACTIVE_GRANT")
    if not authorization_active:
        reasons.append("NO_ACTIVE_ACTION_AUTHORIZATION")
    if not gate_current:
        reasons.append("STALE_OR_MISSING_GATE")
    if not budget_remaining:
        reasons.append("BUDGET_EXCEEDED")
    return {"allowed": not reasons, "reasons": reasons}
