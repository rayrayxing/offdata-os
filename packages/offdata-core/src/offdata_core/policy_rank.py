"""Typed evidence-level comparison helpers used by approval policy."""

from .models import EvidenceLevel

_EVIDENCE_RANK = {
    EvidenceLevel.E1: 1,
    EvidenceLevel.E2: 2,
    EvidenceLevel.E3: 3,
    EvidenceLevel.E4: 4,
}


def evidence_rank(level: EvidenceLevel) -> int:
    return _EVIDENCE_RANK[level]


def higher_evidence(first: EvidenceLevel, second: EvidenceLevel) -> EvidenceLevel:
    return max(first, second, key=evidence_rank)
