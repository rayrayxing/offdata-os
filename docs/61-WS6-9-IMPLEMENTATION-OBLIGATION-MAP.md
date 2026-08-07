# WS6.9 — Implementation-obligation map

WS6.9 closes `WS6-QUALITY-001` by binding every one of the 38 PCR-10 quality criteria to exactly one implementation phase, backlog task, implementation component, planned test obligation, evidence type and blocking phase gate.

## Exact predecessor

This package is stacked on the exact WS6.8 head `46abab02ad08a3a1cca519391e0114555f11230c` and must not be integrated before WS6.8. PR #49 remains the governed predecessor and is not represented as merged to `main`.

## Blocking semantics

- The 16 PCR-10 criteria classified as `phase0_acceptance` map only to `IMP-P0` tasks and block the `IMP-P0` gate.
- The 22 criteria classified as `later_implementation_acceptance` map to their assigned later implementation phases and do not block `IMP-P0`.
- Every obligation blocks completion of its own assigned phase until its test and evidence requirements are satisfied.
- No criterion is claimed implemented, tested or evidenced by this chat-first package.

## Test-registration boundary

WS6.9 creates 38 stable planned test-obligation identifiers, but it does not register executable tests. `WS6-CODEXPREP-002` remains open and owns the later governed registration of planned IMP-P0 cases in WS6.13. Later-phase test obligations remain owned by their assigned implementation phases.

## Authority boundary

This map is implementation planning evidence, not implementation authority. It does not authorize Codex, IMP-P0 implementation or merge, IMP-P1+, runtime activation, production, real client data, paid services, OAuth, external actions or autonomous merge. `WS6-BLOCK-006` remains open and `codex_start_authorized=false`.

Next permitted work package after the governed WS6.8 → WS6.9 integration sequence: `WS6.10`.
