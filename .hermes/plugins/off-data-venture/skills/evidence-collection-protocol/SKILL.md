---
name: evidence-collection-protocol
description: Collect attributable evidence without fabricating authority.
version: 0.2.0
platforms: [macos, linux]
metadata:
  offdata:
    protected_policy: true
---
# Evidence Collection Protocol

Authoritative admissibility is determined by OFF/DATA tools, not this Skill.

## Procedure
1. Capture original source/interaction and raw artifact/receipt where available.
2. Record occurrence and retrieval time separately.
3. Record provider/channel and legitimate identities exactly as observed.
4. Choose evidence purpose: `MARKET_RESEARCH`, `BEHAVIORAL_VALIDATION`, `DIRECT_BUYER`, `FINANCIAL`, or `OPERATING`.
5. For `DIRECT_BUYER`, never infer any missing field: account identity, actor identity, counterparty role, interaction type, occurredAt, channel, receiptRef.
6. Record environment/provisional state and content hash.
7. Call deterministic `offdata_evidence_record` then `offdata_evidence_validate`.
8. If source later changes/quarantines, dependent gate authority must become stale and be re-evaluated.

Research may influence strategy but can never be promoted to G3 merely because it is persuasive.
