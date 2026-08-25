---
name: gate-preparation
description: Prepare current inputs for deterministic G0-G10 evaluation.
version: 0.2.0
platforms: [macos, linux]
metadata:
  offdata:
    protected_policy: true
---
# Gate Preparation

This Skill cannot pass a gate. Only the deterministic Gate Engine may produce an authoritative GateSnapshot.

1. Read the ACTIVE/RATIFIED Gate Policy version imported from current VentureOS source.
2. Read current predecessor snapshot; stale or superseded predecessors do not count.
3. Collect only evidence eligible under the active policy and current fingerprints.
4. For G3, every contributing direct-buyer item must contain all seven attribution fields; never infer or use URL/domain fallback.
5. Bind required immutable financial snapshot where the gate uses economics.
6. Include current open concerns; only policy-defined blockers halt automatically.
7. Call `offdata_gate_evaluate` with exact policy version and report its result verbatim.
8. Any authority-relevant upstream change requires re-evaluation.
