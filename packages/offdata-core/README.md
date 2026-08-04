# offdata-core

Deterministic lifecycle and approval-policy contracts for offdata.

This package deliberately contains no model calls, external integrations or side effects. It gives application services and agent runtimes a common, testable interpretation of:

- the thirteen-stage consulting lifecycle;
- operational states;
- gate outcomes;
- decision classes and evidence levels;
- stage detection and transition validation; and
- approval requirements for sensitive actions.

## Local validation

From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

Codex should integrate this package into the monorepo tooling during Phase 0 and retain its deterministic behaviour behind application APIs.

## Current scope

The initial package is intentionally narrow. It does not yet implement persistence, Restate workflows, database access, agent execution or external actions. Those capabilities must call these contracts rather than duplicate the policy logic.
