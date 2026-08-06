# Workstream 6 — Final pre-Codex reconciliation

## WS6.0 — Baseline lock and defect register

### Purpose

WS6.0 establishes the immutable starting point for the final chat-first
reconciliation. It records the exact repository, issue, branch, workflow and
quality evidence inherited from Workstream 5, then converts the current review
findings into a machine-governed defect and scope register.

WS6.0 repairs none of the registered defects. It authorizes no Codex work.

`AGENTS.md` remains controlling. Codex remains unauthorized.

## Locked baseline

- Repository: `rayrayxing/offdata-os`
- Canonical branch: `main`
- Exact baseline SHA: `ad24030200e421016066e7039e202ff9f0c5398d`
- Baseline commit: `Merge Workstream 5 Codex Phase 0 launch control`
- Workstream 5 pull request: `#35`
- Workstream 5 head: `3bb53c76c8cb46f46ca76af205ac064c5f09ac68`
- Exact tested merge reference: `037111a86725e9fbd1109ebca4fb79a8f5b44d52`
- Workflow run: `31075587982`
- Workflow job: `92532783575`
- Artifact: `8957372302`
- Runtime result: 247 tests passed
- Coverage: 93.14 percent across 4,604 statements
- Referential integrity: 245 executable nodes, 99 semantic tests, 604 edges,
  zero unresolved references

The baseline was captured before creating
`governance/workstream6-baseline-lock`.

## Prior component state

The locked prior sequence is:

1. CF-P1 through CF-P7 — complete and integrated.
2. PCR-01 through PCR-10 — complete and integrated.
3. WS-4 — repository package complete; hosted, cleanup and clean-environment
   gates remain pending.
4. WS-5 — repository launch control complete; Founder authorization and permit
   remain pending.

The following live issue state is part of the baseline:

- issue #1 is open and contains the Workstream 5 generated body;
- issue #2 is closed as duplicate;
- issue #19 is open because hosted controls, branch cleanup and clean-macOS
  evidence remain incomplete.

The Codex Phase 0 branch and pull request were absent at the baseline.

## Branch inventory

The pre-WS6 baseline contains 28 branches, including `main` and the retained
historical phase, PCR and Workstream branches. This is evidence of incomplete
manual cleanup, not permission to delete by prefix or wildcard.

Deletion remains a later manual operation governed by the exact Workstream 4
allowlist and issue #19. `main` must never be deleted.

## Defect register

The generated register contains 28 entries:

- six blocking defects;
- twelve important defects or preparation gaps;
- ten planned quality or implementation-preparation gaps.

The six blocking defects are:

1. stale PCR-04 machine handoff;
2. stale PCR-04 validator;
3. conflicting current human authority documents;
4. Workstream 5 launch control cannot prove final Workstream 6 inclusion;
5. canonical issue and permit digests require final rebinding;
6. no final post-merge Workstream 6 release record.

Each entry records:

- stable identifier;
- severity and kind;
- evidence;
- affected authority;
- expected repair files;
- validation;
- rollback;
- owner;
- target work package;
- open status.

The YAML source is canonical for WS6.0:

`configs/workstream6-final-reconciliation.yaml`

Generated records are:

- `contracts/workstream6-final-reconciliation.json`
- `reports/workstream6-initial-defect-register.md`
- `releases/workstream6-baseline-lock-2026-08-06.json`

Do not edit generated records manually.

## Validation

WS6.0 must validate:

- the exact Workstream 5 baseline SHA and evidence;
- all 19 prior component records;
- issue #1, #2 and #19 baseline states;
- the 28-branch pre-WS6 inventory;
- all 28 unique register entries;
- exactly six blocking entries;
- all prior repository checks true;
- all manual launch gates false;
- all authority and implementation boundaries false except preserved Founder
  accountability;
- deterministic source-to-contract, report and release generation;
- JSON Schema compliance;
- mutation rejection;
- complete prior builders, validators, runtime tests, coverage, compilation,
  Ruff, strict MyPy and launch-verifier self-test.

The dedicated status check is:

`Validate WS6.0 baseline lock and complete prior components`

This is a Workstream 6 subphase check, not the final branch-protection identity
that will be defined later in WS6.6 and WS6.15.

## Scope boundary

WS6.0 may:

- record repository and GitHub evidence;
- create deterministic contracts, schemas, reports and validation;
- open and merge the bounded WS6.0 pull request after all checks pass;
- identify chat-first work that remains before Codex.

WS6.0 must not:

- repair WS6.1 or later defects;
- rewrite the canonical Phase 0 issue;
- issue a launch permit;
- create `codex/phase-0-foundation`;
- implement Next.js, FastAPI, PostgreSQL, object storage or renderers;
- activate Restate, Hermes or model providers;
- use real client data;
- use paid services;
- enable OAuth, DNS changes, external communication, staging or production;
- authorize Phase 0 merge or Phase 1.

## Completion rule

WS6.0 is complete when:

- the baseline source is committed;
- generated contract, report and release rebuild without diff;
- the schema and semantic validator pass;
- every mutation case is rejected;
- every required prior component passes its existing builder and validator;
- runtime, coverage, compilation, Ruff, strict MyPy and launch self-test pass;
- live issue and main-SHA checks pass;
- a separate review finds no unresolved blocking defect in the WS6.0 package.

Completion means only that the baseline is locked and the register is complete.
All six blocking defects remain open.

The next permitted work package is `WS6.1`.

## Rollback

Before merge, close the pull request and delete only
`governance/workstream6-baseline-lock`.

After merge, revert the WS6.0 merge as one unit only if the baseline evidence is
materially incorrect. Do not delete prior evidence, alter issue history, weaken
launch controls or infer Codex authorization.
