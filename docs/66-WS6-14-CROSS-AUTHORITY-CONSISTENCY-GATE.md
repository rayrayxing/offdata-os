# WS6.14 — Cross-authority consistency gate

> [!CAUTION]
> **CONSISTENCY GATE, NOT LAUNCH AUTHORIZATION.** This package reconciles repository authority. It does not activate the final workflow, create the permanent release, satisfy manual gates, issue a permit, or authorize Codex.

- Integrated `main`: `141ac6ab458fa7354f9b3f8cc57a887f3fceac21` through `WS6.13`.
- Earliest unintegrated package: `WS6.14`.
- Authority domains checked: `12`.
- Baseline defects: `28`; repository-addressed: `25`; expected unresolved: `3`.
- Historical WS6.5/WS6.6 fingerprint/status fields remain package-time snapshots; current status comes from the WS6.3 successor current-status contract and canonical authority registry.
- `WS6-BLOCK-006`, `WS6-CONSIST-006` and `WS6-CONSIST-010` remain unresolved by design.
- WS6.15 must activate the reserved final workflow; WS6.16 must create the permanent release; hosted/manual evidence remains independent.
- `codex_start_authorized=false`.

## Domains

- `integration_state` — main_integrated_through_ws613_exact.
- `authority_registry` — unique_current_authority_and_status_match.
- `phase_namespace` — imp_p0_to_p12_disjoint_and_not_started.
- `required_workflow_identity` — exact_identity_reserved_manual_only_until_ws615.
- `issue_authority` — one_actionable_one_manual_gate_duplicate_closed.
- `launch_control` — final_release_manual_evidence_and_permit_required.
- `implementation_obligations` — 38_criteria_16_phase0_22_later.
- `developer_founder_experience` — 15_commands_60_cases_8_founder_32_cases.
- `deliverable_quality` — 6_renderers_38_cases_no_physical_or_approved_goldens.
- `operational_quality` — 8_signals_11_metrics_83_planned_zero_executable_telemetry_false.
- `licence_decision` — founder_owned_no_selection_no_implicit_grant.
- `defect_closure` — 25_repository_addressed_3_expected_unresolved.

## Defect closure overlay

- `WS6-BLOCK-001` — `repository_addressed`; owner `WS6.1`.
- `WS6-BLOCK-002` — `repository_addressed`; owner `WS6.1`.
- `WS6-BLOCK-003` — `repository_addressed`; owner `WS6.3`.
- `WS6-BLOCK-004` — `repository_addressed`; owner `WS6.2`.
- `WS6-BLOCK-005` — `repository_addressed`; owner `WS6.2`.
- `WS6-BLOCK-006` — `expected_unresolved`; owner `WS6.16`.
- `WS6-CODEXPREP-001` — `repository_addressed`; owner `WS6.13`.
- `WS6-CODEXPREP-002` — `repository_addressed`; owner `WS6.13`.
- `WS6-CODEXPREP-003` — `repository_addressed`; owner `WS6.13`.
- `WS6-CODEXPREP-004` — `repository_addressed`; owner `WS6.13`.
- `WS6-CODEXPREP-005` — `repository_addressed`; owner `WS6.13`.
- `WS6-CODEXPREP-006` — `repository_addressed`; owner `WS6.12`.
- `WS6-CODEXPREP-007` — `repository_addressed`; owner `WS6.8`.
- `WS6-CONSIST-001` — `repository_addressed`; owner `WS6.4`.
- `WS6-CONSIST-002` — `repository_addressed`; owner `WS6.5`.
- `WS6-CONSIST-003` — `repository_addressed`; owner `WS6.6`.
- `WS6-CONSIST-004` — `repository_addressed`; owner `WS6.7`.
- `WS6-CONSIST-005` — `repository_addressed`; owner `WS6.8`.
- `WS6-CONSIST-006` — `expected_unresolved`; owner `post_merge_manual`.
- `WS6-CONSIST-007` — `repository_addressed`; owner `WS6.4`.
- `WS6-CONSIST-008` — `repository_addressed`; owner `WS6.3`.
- `WS6-CONSIST-009` — `repository_addressed`; owner `WS6.13`.
- `WS6-CONSIST-010` — `expected_unresolved`; owner `WS6.16`.
- `WS6-QUALITY-001` — `repository_addressed`; owner `WS6.9`.
- `WS6-QUALITY-002` — `repository_addressed`; owner `WS6.10`.
- `WS6-QUALITY-003` — `repository_addressed`; owner `WS6.11`.
- `WS6-QUALITY-004` — `repository_addressed`; owner `WS6.12`.
- `WS6-QUALITY-005` — `repository_addressed`; owner `WS6.13`.

## Next gate

`WS6.15` is the next permitted chat-first package. No merge, IMP-P0 implementation, runtime activation or external action is authorized.