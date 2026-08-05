# PCR-01 canonical release reconciliation validation evidence

## Status

**PENDING FINAL EXACT-HEAD VALIDATION**

Date: 2026-08-05

## Canonical source release

PCR-01 reconciles the final completed Phase 1–7 source release:

- pull request: `#15`;
- pull-request head: `8da0f1167d9b6f4da792770b0d564379aa46c3fe`;
- pull-request merge reference: `264459045ce75d7d7c60cbc980a50193f08a6f16`;
- controlling `main` commit: `7dc5531e641158e5a84fbbb9fdf07cefefd4782b`;
- final Phase 1–7 run: `30976222896`;
- final Phase 1–7 job: `92210649514`;
- final Phase 1–7 artifact: `8918355687`;
- artifact SHA-256: `3b9f14c520d31ce5f73fbecc726b032a3134042769ee84176e85d642fe2ea852`.

Runs `30975868412` and `30976088173` are preserved as successful superseded snapshots. They are not the controlling release evidence.

## PCR-01 evidence to be completed

The final record will include:

- exact PCR-01 branch head and pull-request merge reference;
- workflow run and job;
- complete Phase 1–7 regression results;
- PCR-01 validator result;
- runtime test and coverage totals;
- compilation, Ruff and strict MyPy results;
- retained release artifact ID, file count, size, digest and expiry;
- explicit confirmation that real client data remains prohibited.
