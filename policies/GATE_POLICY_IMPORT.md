# Gate Policy Import and Ratification

Exact G0–G10 policy is source-controlled business authority and must not be reconstructed from memory.

## Procedure

1. Locate the actual current VentureOS checkout supplied by owner. Record absolute path, branch, HEAD SHA and dirty state.
2. Locate gate/rubric/evidence/predecessor/approval/finance implementation and its tests/docs.
3. Extract for every G0–G10:
   - purpose and authorized transition/resource class;
   - evidence/metric inputs;
   - numeric/semantic thresholds;
   - predecessor;
   - environment/provisional constraints;
   - policy/rubric version;
   - financial snapshot dependency;
   - invalidation/staleness triggers;
   - owner/manual approval requirements.
4. Compare the source result with `KNOWN_GATE_INVARIANTS.yaml` and prior independent audit defects. Never silently weaken an invariant because current source is buggy; record conflict for ratification.
5. Generate versioned deterministic off/data gate policy and positive/negative fixtures.
6. Run independent Codex review of source mapping, especially G3, G4 approval path, G8 retention/billing/cash, G9 margin/snapshot and G10 ROI/snapshot/concurrency.
7. Only after ratification mark `GATE_POLICY_IMPORT=PASS`.

## Fail closed

If source is unavailable: `BLOCKED_SOURCE_REQUIRED`.
If source and known policy conflict: `BLOCKED_POLICY_CONFLICT`.
Never invent G0–G10 definitions to unblock installation.