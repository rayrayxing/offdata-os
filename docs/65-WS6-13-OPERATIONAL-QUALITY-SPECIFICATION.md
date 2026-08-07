# WS6.13 — Operational quality specification

> [!CAUTION]
> Planning and schema evidence only. Telemetry, runtime, services, real-client data and external actions remain disabled.

- Operational signals: `8`
- Learning metrics: `11`
- Registered IMP-P0 planned tests: `76`
- Workflow/agent conformance cases: `7`
- Executable new tests: `0`
- Telemetry default: `false`
- `codex_start_authorized=false`.

## Operational signals

- `OP-CORR` — `structured_event_envelope`; owner `IMP-P0/P0.3/COMP-FOUNDATION-QUALITY`; privacy `pseudonymous_operational_metadata`; retention `ephemeral_synthetic_validation`; evidence `correlation_trace_report`.
- `OP-ERROR` — `error_envelope`; owner `IMP-P0/P0.3/COMP-FOUNDATION-QUALITY`; privacy `pseudonymous_operational_metadata`; retention `ephemeral_synthetic_validation`; evidence `error_taxonomy_report`.
- `OP-TRACE` — `otel_compatible_span_envelope`; owner `IMP-P0/P0.3/COMP-FOUNDATION-QUALITY`; privacy `pseudonymous_operational_metadata`; retention `ephemeral_synthetic_validation`; evidence `privacy_safe_trace_contract_report`.
- `OP-HEALTH` — `health_probe_result`; owner `IMP-P0/P0.2/COMP-FOUNDATION-DEVENV`; privacy `non_personal_operational_metadata`; retention `ephemeral_synthetic_validation`; evidence `health_semantics_report`.
- `OP-COST` — `usage_attribution_event`; owner `IMP-P4/P4.3/COMP-AGENT`; privacy `pseudonymous_operational_metadata`; retention `operational_aggregate_planned`; evidence `cost_usage_latency_attribution_report`.
- `OP-FLAGS` — `feature_flag_audit_event`; owner `IMP-P3/P3.3/COMP-API`; privacy `pseudonymous_operational_metadata`; retention `release_evidence`; evidence `kill_switch_audit_report`.
- `OP-SBOM` — `release_supply_chain_record`; owner `IMP-P0/P0.3/COMP-FOUNDATION-QUALITY`; privacy `non_personal_operational_metadata`; retention `release_evidence`; evidence `release_supply_chain_report`.
- `OP-RECOVERY` — `recovery_drill_record`; owner `IMP-P0/P0.4/COMP-FOUNDATION-SECURITY`; privacy `pseudonymous_operational_metadata`; retention `release_evidence`; evidence `recovery_drill_report`.

## Learning metrics

- `founder_correction_effort` — source `founder_decision_or_review_event`; capture `IMP-P3/P3.3`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `recommendation_override_reason` — source `founder_decision_event`; capture `IMP-P3/P3.3`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `output_editing_time` — source `deliverable_review_event`; capture `IMP-P7/P7.5`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `repeated_manual_task` — source `workload_observation`; capture `IMP-P12/P12.3`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `defect_category` — source `quality_defect_event`; capture `IMP-P7/P7.5`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `missing_evidence_or_method` — source `evidence_qa_event`; capture `IMP-P5/P5.4`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `agent_contribution_accepted_or_rejected` — source `agent_eval_event`; capture `IMP-P4/P4.4`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `task_completion_time` — source `workflow_completion_event`; capture `IMP-P3/P3.2`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `human_time_saved` — source `workload_measurement`; capture `IMP-P12/P12.3`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `quality_per_cost` — source `workload_quality_measurement`; capture `IMP-P12/P12.3`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.
- `client_facing_usefulness` — source `synthetic_founder_evaluation`; capture `IMP-P12/P12.3`; canonical measurement `IMP-P12/P12.3`; privacy `pseudonymous_or_aggregate_operational_metadata`; collection disabled.

## IMP-P0 preparation

- P0.1–P0.4 blueprint is machine-readable and planning-only.
- Four local services are loopback-only; external networking defaults denied.
- API/UI shell contracts are read-only and inactive.
- Storage/ingestion contracts allow synthetic fixtures only; real document import is false.
- 76 IMP-P0 planned tests are registered without becoming executable evidence.
- Seven wait/retry/cancel/idempotency/tool-permission/cost/context conformance cases are planned without provider execution.

## Completion

Closes `WS6-QUALITY-005` and `WS6-CODEXPREP-001` through `WS6-CODEXPREP-005`. `WS6-BLOCK-006` remains open. Next permitted package: `WS6.14`.
