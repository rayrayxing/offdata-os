# 14 — Codex Kickoff

## Current state

**Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.16; the permanent Workstream 6 release/final reconciliation is complete; all manual launch gates remain pending; `codex_start_authorized=false`.**

This file is preparation guidance, not an instruction to start Codex. Do not paste a kickoff prompt into Codex, create the implementation branch or change application code until the final release and every manual launch gate have passed and a valid local single-use permit exists.

## Controlling authority

IMP-P0 is governed by:

- `AGENTS.md`;
- `repository/canonical-authority-registry.json`;
- `contracts/workstream6-phase-namespace.json`;
- `contracts/workstream6-required-workflow-identity.json`;
- `handoff/codex-phase0-handoff.json`;
- `contracts/codex-phase0-launch-control.json`;
- `handoff/codex-phase0-issue-final.md` and issue #1;
- `releases/pre-codex-final-reconciliation-2026-08-06.json`, which now exists and passes the independent gate;
- a valid local permit emitted by `scripts/prepare_codex_phase0_launch.py`.

The namespace contract makes `IMP-P0` the canonical implementation phase identifier and retains older filenames and machine keys only for compatibility. The workflow-identity contract defines the exact final check; WS6.15 activated its canonical workflow and WS6.16 bound the permanent release. Hosted branch-protection enforcement remains a manual issue #19 gate. The registry identifies which repository records are current, supporting, retained or superseded. The handoff, final issue body, a green workflow, an assignment or a branch name does not authorise execution.

## Preconditions before any Codex session

All of the following are mandatory:

1. `python scripts/require_workstream6_final_reconciliation.py` passes against the exact current `main` SHA;
2. issue #19 is closed as completed with evidence for hosted controls and exact-allowlist branch cleanup;
3. WS6.15 has activated `.github/workflows/workstream6-final-pre-codex.yml` and branch protection requires exactly `Validate final pre-Codex canonical handoff and complete release`;
4. a clean macOS doctor report and Founder environment attestation are complete and SHA-bound;
5. the Founder explicitly approves IMP-P0 only, tasks P0.1–P0.4, against the same SHA;
6. `scripts/prepare_codex_phase0_launch.py` validates all evidence and emits a valid local single-use permit;
7. `codex/phase-0-foundation` and any IMP-P0 pull request are absent before launch.

## Launch preparation command

Run the verifier only after the evidence files are completed:

```bash
python scripts/prepare_codex_phase0_launch.py \
  --hosted-controls .local/codex-phase0-launch/hosted-controls.json \
  --macos-report .local/codex-phase0-launch/macos-doctor.json \
  --macos-attestation .local/codex-phase0-launch/macos-attestation.json \
  --founder-approval .local/codex-phase0-launch/founder-approval.json
```

A successful run writes a local permit. It does not create a branch, open a pull request, activate services or authorise merge.

## Retained runtime boundary

Before any permitted session, validate `contracts/runtime-adapter-contracts.json` with `scripts/validate_pcr05_runtime_adapters.py`. The contract is provider-independent and remains inactive: `runtime_activation_authorized=false`.

## Permit-gated kickoff prompt

Use the following only after independently confirming that the permit is valid for the exact checked-out `main` SHA:

```text
You are the principal engineering agent for offdata, a Founder-governed,
AI-native consulting operating system.

Open and inspect the private repository rayrayxing/offdata-os. Treat AGENTS.md
as the controlling instruction. Load repository/canonical-authority-registry.json,
contracts/workstream6-phase-namespace.json, contracts/workstream6-required-workflow-identity.json, handoff/codex-phase0-handoff.json, contracts/codex-phase0-launch-control.json
and the valid local launch permit.

Before changing files, verify that the current main SHA, final Workstream 6
release, final issue-body digest, required status-check identity, evidence
digests, approved task scope and permit all match. Stop immediately if any
value is missing, stale or ambiguous.

Only after that verification, create codex/phase-0-foundation from the permit's
approved SHA. Add governance/codex-phase0-launch-ack.json as the first commit.

Your authorised assignment is IMP-P0 only, tasks P0.1-P0.4 in the
machine handoff's dependency order. Integrate the governed chat-first assets;
do not replace canonical lifecycle, policy, contract, fixture, security,
knowledge, release, test-identity or launch-control records.

Use synthetic data only. Do not purchase services, request or expose secrets,
approve OAuth, alter DNS, send external communications, deploy staging or
production, activate runtime or Hermes, implement Northstar beyond the approved
IMP-P0 foundation, enable real client data, weaken tests, merge the pull
request or begin IMP-P1.

Run every required command, perform an independent review, repair defects
without weakening controls, open a DRAFT pull request and stop at the Founder
gate. Do not merge.
```

## Review and repair prompt

```text
Review the current draft IMP-P0 pull request against AGENTS.md, the
canonical authority registry, machine handoff, final launch contract, launch
acknowledgement, approved permit scope and docs/10-TESTING-STRATEGY.md.

Create a defect register with severity, cause, affected requirement and repair
plan. Repair all blocking and required defects without weakening tests or
changing golden expectations merely to obtain a pass. Rerun the complete
command set, update documentation and provide a revised Founder report. Keep
the pull request in draft and do not merge or progress to IMP-P1.
```

## Independent review prompt

```text
Act as an independent engineering, security and quality reviewer. Verify the
permit, approved SHA and first-commit acknowledgement before reviewing the
implementation. Attempt to falsify the claim that IMP-P0 is complete.

Review requirements coverage, permissions, secret handling, canonical-model
duplication, hidden coupling, test quality, data isolation, recovery,
supply-chain controls, costs and usability for a non-technical Founder. Return
a defect register with evidence. Do not approve merge or IMP-P1.
```

## Later phases

No later implementation phase may reuse the IMP-P0 permit. Each phase requires a new machine handoff, explicit Founder approval, fresh evidence and its own bounded authorization. IMP-P0 completion never implies IMP-P1 authorization.
