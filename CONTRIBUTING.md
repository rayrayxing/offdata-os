# Contributing to offdata OS

offdata OS is currently a Founder-governed private build. Contributions are accepted only through an approved phase or maintenance task.

## Before changing the repository

1. Read `AGENTS.md`, `GOVERNANCE.md`, and the current phase document.
2. Confirm the change is inside the approved phase boundary.
3. Use synthetic or sanitised data only.
4. Create a focused branch from current `main`.
5. Do not introduce credentials, client data, original private methodology binaries, restricted answer keys, or unapproved processors.

## Change requirements

Every material change must include:

- a clear problem statement and bounded scope;
- requirement, control, test, or governance traceability where applicable;
- deterministic generation for governed artefacts;
- tests or validators that fail when the intended control is broken;
- a rollback path;
- an explicit statement of unresolved risks and Founder decisions.

Generated outputs must not be edited by hand when a governed source and builder exist.

## Pull requests

Use the repository pull-request template. Keep the pull request in draft until all mandatory checks pass. Do not merge a material change without Founder approval.

The complete repository gate must pass before merge:

- all Phase 1–7 validators;
- PCR-01 canonical-release reconciliation;
- PCR-02 test identity and referential integrity;
- PCR-03 repository and governance hygiene;
- deterministic clean-generation checks;
- pytest with the configured coverage floor;
- Python compilation;
- Ruff;
- strict MyPy.

## Data and security

Public issues and pull requests must never contain secrets, client information, private source-library files, restricted evaluation material, or exploitable vulnerability details. Follow `SECURITY.md` for security reports.

## Commit and branch hygiene

Use short-lived, purpose-specific branches. Do not reuse a merged branch for unrelated work. Avoid committing local state, build metadata, caches, generated previews, test output, editor files, or Office temporary files.

## Review standard

Reviewers must verify scope, authority, evidence, data boundaries, tests, generated-file cleanliness, rollback, and whether any Founder approval is still required. Passing automation does not replace accountable review.
