# Workstream 5 — Codex Phase 0 launch control

## Purpose

Workstream 5 defines the final fail-closed transition from completed chat-first design into an explicitly authorized Codex Phase 0 run. It does not implement Phase 0 and does not grant permission by being merged, assigned, dispatched or validated.

`AGENTS.md` remains controlling. Issue #1 remains the single canonical Phase 0 issue. Issue #19 remains the authoritative hosted-control and clean-environment evidence record.

## Launch states

1. **Repository launch control complete** — the contract, templates, verifier, schemas and workflow exist and pass. This state is committed.
2. **Manual prerequisites verified** — issue #19 is closed with evidence, the clean macOS report and attestation are complete, and the Founder approves Phase 0 against one exact current `main` SHA. This state is external and mutable.
3. **Local launch permit issued** — the verifier confirms all evidence and live repository state, then writes a single-use permit under `.local/codex-phase0-launch/`. The permit is intentionally ignored by Git.
4. **Codex branch acknowledged** — the first commit on `codex/phase-0-foundation` records the permit ID and approved base SHA in `governance/codex-phase0-launch-ack.json`.
5. **Phase 0 draft ready** — Codex opens a draft pull request and stops at the Founder gate. Merge and Phase 1 remain unauthorized.

## Required evidence

### Hosted controls

A filled copy of `handoff/codex-phase0-hosted-controls-attestation.template.json` must record:

- issue #19 closed as completed;
- MFA and the eight final repository controls;
- exact historical branch cleanup;
- a final branch inventory containing only `main` before launch;
- attachment digests for screenshots or a settings audit; and
- an explicit Founder attestation bound to the approved `main` SHA.

### Clean macOS

Run the existing non-destructive doctor from a fresh clone of final `main`:

```bash
python scripts/doctor_pre_codex_macos.py \
  --output .local/codex-phase0-launch/macos-doctor.json
```

A filled copy of `handoff/codex-phase0-clean-macos-attestation.template.json` must reference the doctor-report digest, the same exact `main` SHA and all manual environment attestations.

### Founder authorization

A filled copy of `handoff/codex-phase0-founder-authorization.template.json` must explicitly state:

- decision `approve_codex_phase0_only`;
- exact current `main` SHA;
- tasks exactly P0.1–P0.4;
- branch exactly `codex/phase-0-foundation`;
- draft pull request required;
- merge unauthorized; and
- Phase 1 unauthorized.

Assignment, issue edits, a workflow dispatch or a conversational statement is insufficient unless represented in this SHA-bound evidence record.

## Permit preparation

Store filled evidence copies under `.local/codex-phase0-launch/`, then run:

```bash
python scripts/prepare_codex_phase0_launch.py \
  --hosted-controls .local/codex-phase0-launch/hosted-controls.json \
  --macos-report .local/codex-phase0-launch/macos-doctor.json \
  --macos-attestation .local/codex-phase0-launch/macos-attestation.json \
  --founder-approval .local/codex-phase0-launch/founder-approval.json
```

The verifier checks local Git state, remote `main`, issue #1, issue #2, issue #19, existing Codex branches and open Codex pull requests. It rejects stale or inconsistent evidence and does not mutate GitHub.

A successful run writes `.local/codex-phase0-launch/permit.json` with file mode `0600`. It refuses to overwrite an existing permit.

## Revocation

A permit is invalid after any of the following:

- `main` advances;
- issue #1 changes;
- issue #19 is reopened;
- any evidence digest changes;
- Founder approval is revoked or widened;
- `codex/phase-0-foundation` already exists;
- an open Phase 0 pull request already exists; or
- Phase 0 scope changes.

Delete the stale local permit and repeat the complete evidence and approval process. Never edit a permit to make it pass.

## Codex first action

After a valid permit, Codex may create `codex/phase-0-foundation` from the approved exact SHA. Its first commit must create `governance/codex-phase0-launch-ack.json` using the committed template and include:

- permit ID;
- permit digest;
- approved base SHA;
- exact branch and P0.1–P0.4 scope;
- draft-PR requirement; and
- merge and Phase 1 denial.

Codex must then execute the complete preflight before planning or implementation.

## Security and privacy

- The local evidence directory is already covered by `.local/` in `.gitignore`.
- No credential value, environment-variable name, machine identifier or screenshot content belongs in a permit.
- Only evidence digests are copied into the permit.
- The launch verifier requires authenticated GitHub CLI access but does not create, edit, close, merge or delete GitHub resources.
- No paid service, OAuth consent, DNS change, real client data, external communication, staging or production action is authorized.

## Completion boundary

Workstream 5 repository work is complete when the deterministic contract, templates, generated issue body, schemas, verifier, workflow and permanent evidence record pass on an exact merge reference and are integrated into `main`.

Codex launch remains incomplete until issue #19 is closed with evidence, the clean macOS evidence is verified, the Founder approves one exact current `main` SHA, and the local verifier issues a valid permit. The permit authorizes only the start of Phase 0 and never its merge.
