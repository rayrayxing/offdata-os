# WS6.10 — Developer experience specification

> [!CAUTION]
> **SPECIFIED, NOT IMPLEMENTED OR AUTHORISED.** This defines the future
> IMP-P0 local command surface. It creates no dispatcher, runtime or authority.

## Purpose and boundary

The future dispatcher is `./offdata`, invoked from the repository root on the
supported macOS/Apple Silicon environment. All commands are local-first,
synthetic-only and fail closed. Registered executable tests and satisfied
implementation evidence remain zero. `codex_start_authorized=false`.

The defect register suggested `docs/53-PHASE-0-DEVELOPER-EXPERIENCE-SPEC.md`,
but prefix `53` is immutable WS6.1 evidence. This `docs/62-*` file is canonical.
The wider Phase 0 topology blueprint remains deferred to WS6.13.

## Shared contract

- Human and JSON results have semantic parity and RFC 3339 UTC timestamps.
- Errors identify code, component, cause, safe remediation and retryability.
- Raw exceptions are never the primary user message.
- Secret-like keys and values are redacted before console or artifact output.
- Paths are resolved first; symlink escape and protected-path writes are denied.
- Destructive operations require a synthetic marker and exact confirmation.
- A real-client marker denies mutation.
- Network is denied by default; only declared dependency or vulnerability-data
  fetches may be explicitly opted in. Upload, OAuth, credentials and paid services
  remain prohibited.

### Global flags

`--help`, `--version`, `--json`, `--no-color`, `--quiet`, `--verbose`, `--non-interactive`, `--timeout-seconds`, `--correlation-id`

### Exit codes

| Code | Name | Retryable | Meaning |
|---:|---|:---:|---|
| `0` | `success` | `false` | completed |
| `2` | `invalid_usage` | `false` | invalid arguments |
| `3` | `unsupported_prerequisite` | `false` | unsupported local prerequisite |
| `4` | `validation_failure` | `false` | validation or quality failure |
| `5` | `dependency_unavailable` | `true` | local dependency unavailable |
| `6` | `degraded` | `true` | partial or degraded result |
| `7` | `safety_denial` | `false` | safety or authorization denial |
| `8` | `operation_failed` | `false` | failed or rolled back |
| `9` | `timeout` | `true` | timeout or retry exhausted |
| `10` | `integrity_mismatch` | `false` | digest, schema or evidence mismatch |
| `130` | `interrupted` | `true` | user interruption |

## Acceptance model

Every command has exactly four planned, unregistered cases:

- `positive`: expected state, exit code and redacted evidence are correct.
- `failure`: cause is classified, remediation is safe and success is not claimed.
- `safety`: request is denied before effects and the boundary is recorded.
- `retry`: bounded attempts, state recheck and final result are evidenced.

## Command contracts

| Command | Owner | Purpose | Flags | Exits | Idempotency | Attempts | Case exits |
|---|---|---|---|---|---|---:|---|
| `./offdata doctor` | `P0.2` / `COMP-FOUNDATION-DEVENV` | Inspect the supported local environment without installing or activating services. | `--output`, `--strict`, `--check` | `0, 2, 3, 6, 7, 9, 130` | `read_only` | `2` | `positive=0, failure=3, safety=7, retry=0` |
| `./offdata bootstrap` | `P0.2` / `COMP-FOUNDATION-DEVENV` | Prepare only the local synthetic IMP-P0 workspace and verified dependencies. | `--check-only`, `--offline`, `--allow-network`, `--repair` | `0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 130` | `convergent` | `3` | `positive=0, failure=3, safety=7, retry=0` |
| `./offdata up` | `P0.2` / `COMP-FOUNDATION-DEVENV` | Start the approved local synthetic service profile and prove readiness. | `--detach`, `--wait`, `--component` | `0, 2, 3, 4, 5, 6, 7, 8, 9, 130` | `convergent` | `3` | `positive=0, failure=4, safety=7, retry=0` |
| `./offdata down` | `P0.2` / `COMP-FOUNDATION-DEVENV` | Stop approved local services while preserving synthetic state and evidence. | `--component`, `--remove-orphans` | `0, 2, 4, 6, 7, 8, 9, 130` | `convergent` | `2` | `positive=0, failure=6, safety=7, retry=0` |
| `./offdata restart` | `P0.2` / `COMP-FOUNDATION-DEVENV` | Perform one bounded stop/start cycle without resetting configuration or data. | `--component`, `--wait` | `0, 2, 3, 4, 5, 6, 7, 8, 9, 130` | `convergent` | `2` | `positive=0, failure=8, safety=7, retry=0` |
| `./offdata health` | `P0.2` / `COMP-FOUNDATION-DEVENV` | Report distinct liveness, readiness and dependency health without repair. | `--component`, `--wait` | `0, 2, 5, 6, 7, 9, 130` | `read_only` | `20` | `positive=0, failure=5, safety=7, retry=0` |
| `./offdata test` | `P0.3` / `COMP-FOUNDATION-QUALITY` | Run declared synthetic test suites and retain reproducible local evidence. | `--suite`, `--coverage-min`, `--fail-fast`, `--changed`, `--output` | `0, 2, 3, 4, 6, 7, 8, 9, 130` | `repeatable_artifact` | `2` | `positive=0, failure=4, safety=7, retry=0` |
| `./offdata lint` | `P0.3` / `COMP-FOUNDATION-QUALITY` | Run read-only lint checks across declared source surfaces. | `--scope`, `--output` | `0, 2, 3, 4, 7, 9, 130` | `read_only` | `2` | `positive=0, failure=4, safety=7, retry=0` |
| `./offdata format` | `P0.3` / `COMP-FOUNDATION-QUALITY` | Check or atomically format only the declared editable source allowlist. | `--check`, `--write`, `--scope` | `0, 2, 3, 4, 7, 8, 9, 130` | `convergent` | `2` | `positive=0, failure=4, safety=7, retry=0` |
| `./offdata scan` | `P0.3` / `COMP-FOUNDATION-QUALITY` | Run local secret, dependency and container scans without repository upload. | `--scope`, `--severity-threshold`, `--offline`, `--allow-network`, `--output` | `0, 2, 3, 4, 5, 6, 7, 9, 10, 130` | `repeatable_artifact` | `3` | `positive=0, failure=4, safety=7, retry=0` |
| `./offdata reset-synthetic` | `P0.2` / `COMP-FOUNDATION-DEVENV` | Reset only verified synthetic local state after a verified backup. | `--dry-run`, `--confirm`, `--backup-first`, `--preserve-cache` | `0, 2, 3, 4, 7, 8, 9, 10, 130` | `destructive_confirmed` | `1` | `positive=0, failure=10, safety=7, retry=8` |
| `./offdata backup` | `P0.4` / `COMP-FOUNDATION-SECURITY` | Create an immutable verified synthetic backup with a manifest and digest. | `--output`, `--label`, `--verify`, `--include-logs` | `0, 2, 3, 4, 6, 7, 8, 9, 10, 130` | `repeatable_artifact` | `2` | `positive=0, failure=10, safety=7, retry=0` |
| `./offdata restore` | `P0.4` / `COMP-FOUNDATION-SECURITY` | Verify and transactionally restore one compatible synthetic backup. | `--input`, `--dry-run`, `--verify-only`, `--confirm`, `--backup-current` | `0, 2, 3, 4, 7, 8, 9, 10, 130` | `destructive_confirmed` | `1` | `positive=0, failure=10, safety=7, retry=8` |
| `./offdata clean` | `P0.2` / `COMP-FOUNDATION-DEVENV` | Remove only allowlisted ephemeral build, cache and test artifacts. | `--dry-run`, `--scope`, `--confirm` | `0, 2, 4, 7, 8, 9, 130` | `convergent` | `2` | `positive=0, failure=8, safety=7, retry=0` |
| `./offdata support-bundle` | `P0.4` / `COMP-FOUNDATION-SECURITY` | Create a bounded local diagnostic bundle after redaction validation. | `--output`, `--since-hours`, `--include-logs`, `--max-size-mib` | `0, 2, 3, 4, 6, 7, 8, 9, 10, 130` | `repeatable_artifact` | `2` | `positive=0, failure=10, safety=7, retry=0` |

## Command-specific safety and retry rules

### `./offdata doctor`

- Category/mutation: `diagnostic` / `report_only`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `bounded_local_probe_timeout`.
- Non-retryable: `unsupported_platform`, `missing_required_version`, `safety_denial`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `DX-PORTS`, `DX-SECRETS`, `DX-MAC`, `XC-TIME`.

### `./offdata bootstrap`

- Category/mutation: `environment` / `local_workspace`.
- Network: `dependency_fetch_opt_in`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `declared_dependency_fetch_interruption`, `local_cache_lock`.
- Non-retryable: `credential_request`, `paid_service_request`, `invalid_digest`, `safety_denial`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `DX-PATH`, `DX-SECRETS`.

### `./offdata up`

- Category/mutation: `service_lifecycle` / `local_services`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `transient_local_dependency_readiness`, `temporary_container_start_failure`.
- Non-retryable: `port_conflict`, `invalid_configuration`, `safety_denial`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `DX-PORTS`, `OP-HEALTH`.

### `./offdata down`

- Category/mutation: `service_lifecycle` / `local_services`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `graceful_stop_timeout`, `temporary_project_lock`.
- Non-retryable: `ownership_mismatch`, `volume_deletion_request`, `safety_denial`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `DX-PATH`.

### `./offdata restart`

- Category/mutation: `service_lifecycle` / `local_services`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `transient_readiness_failure_after_start`.
- Non-retryable: `unsafe_configuration`, `port_conflict`, `integrity_mismatch`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `OP-HEALTH`.

### `./offdata health`

- Category/mutation: `diagnostic` / `report_only`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `wait_mode_readiness_poll`.
- Non-retryable: `undeclared_endpoint`, `safety_denial`, `invalid_component`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `OP-HEALTH`.

### `./offdata test`

- Category/mutation: `quality` / `test_artifacts`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `test_runner_startup_failure_before_collection`.
- Non-retryable: `test_assertion_failure`, `coverage_failure`, `collection_error_after_tests_begin`, `safety_denial`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `OP-CORR`.

### `./offdata lint`

- Category/mutation: `quality` / `report_only`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `lint_tool_startup_failure_before_analysis`.
- Non-retryable: `lint_finding`, `configuration_error`, `safety_denial`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`.

### `./offdata format`

- Category/mutation: `quality` / `source_allowlist`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `formatter_startup_failure_before_writes`, `temporary_file_lock`.
- Non-retryable: `parse_failure`, `protected_path`, `safety_denial`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `DX-PATH`.

### `./offdata scan`

- Category/mutation: `security_quality` / `scan_artifacts`.
- Network: `vulnerability_database_opt_in`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `approved_vulnerability_database_refresh_interruption`, `scanner_startup_failure`.
- Non-retryable: `security_finding`, `digest_mismatch`, `secret_exposure_risk`, `safety_denial`.
- Quality obligations: `DX-ROOT`, `DX-DIAG`, `DX-SECRETS`, `OP-SBOM`.

### `./offdata reset-synthetic`

- Category/mutation: `data_safety` / `synthetic_state`.
- Network: `denied`.
- Confirmation: `{"required": true, "token": "RESET-SYNTHETIC"}`.
- Retryable: `none`.
- Non-retryable: `any_failure_after_destructive_preflight_begins`, `missing_confirmation`, `integrity_mismatch`, `safety_denial`.
- Quality obligations: `DX-PATH`, `DX-BACKUP`, `OP-RECOVERY`.

### `./offdata backup`

- Category/mutation: `recovery` / `backup_artifact`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `transient_local_read_failure_before_archive_finalization`.
- Non-retryable: `digest_mismatch`, `label_collision`, `safety_denial`, `failure_after_finalization`.
- Quality obligations: `DX-BACKUP`, `DX-SECRETS`, `OP-RECOVERY`.

### `./offdata restore`

- Category/mutation: `recovery` / `synthetic_state`.
- Network: `denied`.
- Confirmation: `{"required": true, "token": "RESTORE-SYNTHETIC"}`.
- Retryable: `none`.
- Non-retryable: `any_failure_after_mutation_begins`, `integrity_mismatch`, `compatibility_mismatch`, `safety_denial`.
- Quality obligations: `DX-BACKUP`, `DX-PATH`, `OP-RECOVERY`.

### `./offdata clean`

- Category/mutation: `workspace_safety` / `ephemeral_artifacts`.
- Network: `denied`.
- Confirmation: `{"required_for_scopes": ["all"], "token": "CLEAN-ALL"}`.
- Retryable: `transient_file_lock_on_an_allowlisted_ephemeral_path`.
- Non-retryable: `protected_path`, `symlink_escape`, `missing_confirmation`, `safety_denial`.
- Quality obligations: `DX-PATH`, `DX-DIAG`.

### `./offdata support-bundle`

- Category/mutation: `support_evidence` / `support_artifact`.
- Network: `denied`.
- Confirmation: `{"required": false, "token": null}`.
- Retryable: `transient_read_failure_on_an_allowlisted_log_before_finalization`.
- Non-retryable: `redaction_validation_failure`, `size_limit_violation`, `safety_denial`, `digest_mismatch`.
- Quality obligations: `DX-SECRETS`, `DX-DIAG`, `OP-RECOVERY`.

## Completion boundary

WS6.10 closes only `WS6-QUALITY-002`. It does not implement `./offdata`,
register executable tests, create the WS6.13 blueprint, start services or
satisfy command evidence. `WS6-CODEXPREP-002` and `WS6-BLOCK-006` remain open.

Next permitted package: `WS6.11`, after the governed predecessor sequence.

## Rollback

Before merge, close the PR and delete only its branch. After merge, revert the
specification package as one unit. No runtime exists to roll back.
