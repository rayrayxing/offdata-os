# Offdata machine-readable contracts

## Canonical source

The Pydantic models in `packages/offdata-core/src/offdata_core/` are the runtime source of truth for typed records and cross-field validation.

`offdata-contract-bundle.schema.json` is generated from those models and contains every public record contract under `$defs`.

The standalone files below are generated aliases, not separately maintained schemas:

- `agent-envelope.schema.json`
- `context-package.schema.json`
- `founder-decision-packet.schema.json`

`offdata-configs.schema.json` validates the governed lifecycle, policy, agent and test-registry configuration files.

The canonical OpenAPI 3.1 document is generated at `api/openapi.json`. The model registry and command/event catalogue are generated under `contracts/`.

## Regeneration

Run the following from the repository root:

```bash
python scripts/build_test_registry.py
python scripts/export_machine_contracts.py
python scripts/validate_phase1_contracts.py
```

Check generated contract drift without modifying files:

```bash
python scripts/export_machine_contracts.py --check
```

Do not hand-edit generated JSON contracts. Change the source Pydantic model or deterministic exporter and regenerate.

## CI evidence

The `Machine contracts` GitHub Actions workflow regenerates and validates all machine contracts on every push and pull request. Generated schemas, OpenAPI, catalogues and the test registry are retained as a workflow artefact for 30 days.

## Validation boundary

JSON Schema validates portable structure. Pydantic runtime validators remain authoritative for cross-field rules such as approval-state coherence, no routine-only Founder packets, valid lifecycle regression and material release constraints. PostgreSQL-specific constraints and row-level security still require execution against a real PostgreSQL instance during Codex integration.
