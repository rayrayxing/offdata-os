# PCFA-07 — Codex implementation backlog reconciliation

## Purpose

PCFA-07 converts the corrective product, consulting-loop and Hermes specifications into an exact Codex implementation backlog without implementing runtime. It does not create a new IMP phase, add a new task, widen IMP-P0 or claim execution evidence.

Canonical machine authority: `requirements/pcfa07-codex-implementation-backlog-reconciliation.json`.

## Reconciled scope

- PCFA-04 product-scope requirements: **29**.
- PCFA-05 MVCL stages: **19**.
- PCFA-05 cross-loop invariants: **15**.
- PCFA-05 negative-path cases: **13**.
- PCFA-05 Founder interrupt classes: **6**.
- PCFA-06 Hermes capability assessments: **11**.
- Total reconciled obligations: **93**.
- Planned PCFA-07 implementation-test identities: **93**.

Every one of the 93 obligations now has:

- its original requirement/obligation identity preserved;
- exact existing `P1.1`–`P12.4` task bindings;
- one primary implementation task;
- one blocking IMP phase gate;
- explicit dependency task bindings;
- Northstar component bindings;
- one unique planned test ID;
- an evidence type;
- `status=planned_not_implemented`; and
- `implementation_evidence_status=not_available_pre_implementation`.

## No Phase 0 widening

PCFA-07 assigns **zero** new obligations to IMP-P0. The only permitted Codex launch tasks remain `P0.1`, `P0.2`, `P0.3` and `P0.4`. PCFA-07 therefore prepares the later implementation backlog but does not authorize any P1+ implementation.

## Test semantics

The 93 `PCFA07-TST-*` identities are a PCFA-07 implementation-planning registry. They do not replace the historical PCR-02 semantic test registry and do not count as executed evidence. A future obligation can move out of `planned_not_implemented` only when the named implementation task produces the required evidence and the relevant blocking gate passes.

## Primary acceptance assignments

| IMP phase | Primary obligations |
| --- | ---: |
| IMP-P3 | 2 |
| IMP-P4 | 5 |
| IMP-P5 | 7 |
| IMP-P6 | 3 |
| IMP-P7 | 6 |
| IMP-P9 | 1 |
| IMP-P10 | 4 |
| IMP-P11 | 7 |
| IMP-P12 | 58 |

## Existing-task projection

| Task | Phase | Primary obligations | Bound obligations |
| --- | --- | ---: | ---: |
| `P1.1` | IMP-P1 | 0 | 5 |
| `P1.2` | IMP-P1 | 0 | 4 |
| `P1.3` | IMP-P1 | 0 | 1 |
| `P1.4` | IMP-P1 | 0 | 4 |
| `P1.5` | IMP-P1 | 0 | 4 |
| `P2.1` | IMP-P2 | 0 | 3 |
| `P2.2` | IMP-P2 | 0 | 18 |
| `P2.3` | IMP-P2 | 0 | 11 |
| `P2.4` | IMP-P2 | 0 | 4 |
| `P3.1` | IMP-P3 | 0 | 5 |
| `P3.2` | IMP-P3 | 1 | 16 |
| `P3.3` | IMP-P3 | 0 | 17 |
| `P3.4` | IMP-P3 | 1 | 14 |
| `P4.1` | IMP-P4 | 0 | 6 |
| `P4.2` | IMP-P4 | 0 | 12 |
| `P4.3` | IMP-P4 | 0 | 3 |
| `P4.4` | IMP-P4 | 5 | 36 |
| `P5.1` | IMP-P5 | 4 | 4 |
| `P5.2` | IMP-P5 | 0 | 5 |
| `P5.3` | IMP-P5 | 2 | 8 |
| `P5.4` | IMP-P5 | 1 | 10 |
| `P6.1` | IMP-P6 | 0 | 3 |
| `P6.2` | IMP-P6 | 0 | 2 |
| `P6.4` | IMP-P6 | 3 | 10 |
| `P7.1` | IMP-P7 | 3 | 21 |
| `P7.2` | IMP-P7 | 0 | 3 |
| `P7.3` | IMP-P7 | 0 | 6 |
| `P7.4` | IMP-P7 | 0 | 2 |
| `P7.5` | IMP-P7 | 3 | 28 |
| `P8.4` | IMP-P8 | 0 | 2 |
| `P9.2` | IMP-P9 | 0 | 1 |
| `P9.3` | IMP-P9 | 1 | 1 |
| `P9.4` | IMP-P9 | 0 | 1 |
| `P10.2` | IMP-P10 | 0 | 3 |
| `P10.3` | IMP-P10 | 0 | 4 |
| `P10.4` | IMP-P10 | 4 | 5 |
| `P11.2` | IMP-P11 | 2 | 5 |
| `P11.3` | IMP-P11 | 5 | 12 |
| `P12.1` | IMP-P12 | 0 | 1 |
| `P12.2` | IMP-P12 | 13 | 14 |
| `P12.3` | IMP-P12 | 44 | 45 |
| `P12.4` | IMP-P12 | 1 | 1 |

## Gate semantics

The blocking phase gate is the phase of the latest bound existing task. Earlier bound tasks are recorded as dependencies. This makes the acceptance point deterministic while preserving all earlier implementation touchpoints.

PCFA-08 remains the final cross-authority/pre-Codex acceptance package. Until PCFA-08 and the remaining manual launch gates pass, `codex_start_authorized=false`.
