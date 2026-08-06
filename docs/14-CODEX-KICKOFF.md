# 14 — Codex Kickoff

## Controlling handoff

Codex must use `handoff/codex-phase0-handoff.json` as the machine-readable execution contract for the first implementation phase. The file is generated from `configs/codex-handoff.yaml`, validated against `schemas/codex-handoff.schema.json`, and semantically checked by `scripts/validate_pcr04_codex_handoff.py`. Runtime execution boundaries are separately governed by `contracts/runtime-adapter-contracts.json` and `scripts/validate_pcr05_runtime_adapters.py`. Hermes compatibility is governed by `contracts/hermes-compatibility-pack.json` and `scripts/validate_pcr06_hermes_compatibility.py`; the Northstar implementation path is governed by `contracts/northstar-integration-blueprint.json` and `scripts/validate_pcr07_northstar_blueprint.py`; and the initial deny-by-default operating posture is governed by `contracts/initial-operating-controls.json` and `scripts/validate_pcr08_initial_operating_controls.py`.

The handoff does not itself authorise execution. Phase 0 begins only after:

1. PCR-03 through PCR-08 are merged to `main`;
2. the GitHub-hosted controls tracked in issue #19 are verified;
3. the Founder explicitly approves Phase 0; and
4. a clean macOS development environment is available.

## Phase 0 kickoff prompt

Paste the following into Codex after opening `rayrayxing/offdata-os`:

```text
You are the principal engineering agent for offdata, a Founder-governed,
AI-native consulting operating system.

Open and inspect the private repository rayrayxing/offdata-os.

Treat AGENTS.md as the controlling instruction. Then load and validate
handoff/codex-phase0-handoff.json before proposing or changing code.

Run:
python scripts/validate_pcr05_runtime_adapters.py
python scripts/validate_pcr06_hermes_compatibility.py
python scripts/validate_pcr07_northstar_blueprint.py
python scripts/validate_pcr08_initial_operating_controls.py
python scripts/validate_pcr04_codex_handoff.py

Do not continue if the handoff is stale, invalid, missing a prerequisite,
or if any activation condition has not been confirmed by the Founder.

Your authorised assignment is Phase 0 only. Use the task graph P0.1-P0.4
and dependency order in the handoff. Do not begin Phase 1.

Create the branch codex/phase-0-foundation. Validate all pre-existing
chat-first assets before adding application code. Integrate the existing runtime adapter contract and
deterministic lifecycle, policy, contracts, fixtures, knowledge, security,
release, test-identity and repository-governance records. Do not create
parallel replacements for them.

Follow every required command, prohibited action, stop condition, approval
boundary and completion-report field in the handoff.

Treat `initial_operating_controls_activation_authorized=false`, `runtime_activation_authorized=false`, `hermes_activation_authorized=false` and `northstar_implementation_authorized=false` as binding. Use synthetic data only. Do not purchase services, request secrets, approve
OAuth, alter DNS, deploy production infrastructure, send external messages,
enable real client data, expose restricted oracle material, weaken tests or
progress beyond Phase 0.

Perform a separate review pass, repair defects without weakening controls,
open a DRAFT pull request, and stop at the Phase 0 gate. Do not merge.
```

## Phase completion repair prompt

```text
Review the current draft pull request against AGENTS.md,
handoff/codex-phase0-handoff.json, the approved phase requirements and
docs/10-TESTING-STRATEGY.md.

Create a defect register with severity, cause, affected requirement and repair
plan. Repair all critical, high and required medium defects without weakening
tests or changing golden expectations merely to obtain a pass.

Rerun the complete required command set in the handoff, update documentation
and provide a revised plain-English Founder report. Keep the pull request in
draft and do not progress to the next phase.
```

## Independent review prompt

```text
Act as an independent engineering, security and quality reviewer for the
current offdata phase. Do not assume the implementation is correct because
another agent produced it.

Read AGENTS.md, contracts/runtime-adapter-contracts.json, contracts/hermes-compatibility-pack.json, contracts/northstar-integration-blueprint.json, contracts/initial-operating-controls.json and handoff/codex-phase0-handoff.json. Inspect the changed files,
test evidence, costs, permissions and rollback instructions. Attempt to falsify
the claim that the approved phase is complete.

Review for requirements omissions, unsafe permissions, secret handling,
duplicate canonical implementations, hidden coupling, insufficient or hollow
tests, data-isolation failures, recovery weaknesses, unnecessary paid
dependencies and usability problems for a non-technical Founder.

Return a defect register with severity and evidence. Do not merge or approve
material work with unresolved blocking defects.
```

## Later phase progression template

```text
The Founder has explicitly approved progression to Phase [NUMBER AND NAME].

Read AGENTS.md and the current machine-readable phase handoff. Work only on the
approved phase. First verify every prior phase gate remains satisfied.

Create the canonical phase branch, implement in dependency order, run all
required tests, perform an isolated review, repair defects, open a draft pull
request and stop at the phase gate.

Do not purchase services, enter credentials, approve OAuth, deploy real client
data or perform external actions. Present a decision-ready Founder packet when
one of those actions is required.
```

## PCR-09 first Codex issue contract

Before Phase 0 can be authorised, the generated first-issue contract must remain current and pass its dedicated validator:

- `contracts/codex-phase0-issue.json`
- `scripts/validate_pcr09_codex_issue.py`

Preparing or validating this contract does not authorise Codex to start.
