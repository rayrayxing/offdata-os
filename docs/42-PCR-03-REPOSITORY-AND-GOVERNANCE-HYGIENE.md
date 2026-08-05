# 42 — PCR-03 Repository and Governance Hygiene

## Status

**PCR-03 implemented; exact validation evidence is recorded in `reports/pcr03-validation-evidence.md`.**

Date: 2026-08-05

PCR-03 removes repository ambiguity and adds enforceable governance before Codex implementation. It does not alter the canonical Phase 1–7 product, analytical, security, source-rights, or Founder-authority conclusions.

## 1. Repository policy surface

PCR-03 adds:

- `GOVERNANCE.md` for authority, branch, pull-request, merge, source-of-truth, exception, and hosted-setting policy;
- `CONTRIBUTING.md` for safe contribution, testing, data, commit, and review requirements;
- `SECURITY.md` for private vulnerability reporting, supported-version scope, incident authority, and secret handling;
- Founder-wide `CODEOWNERS`;
- a mandatory pull-request template;
- structured defect and governance-change issue forms;
- blank-issue suppression and a private-security route;
- weekly Dependabot checks for Python and GitHub Actions with no auto-merge.

## 2. Tracked-file hygiene

Generated editable-install metadata under `packages/offdata-core/src/offdata_core.egg-info/` is removed from source control. `.gitignore` now rejects Python package metadata and additional local build state.

The PCR-03 validator rejects tracked:

- Python package metadata and caches;
- test, type-check, and lint caches;
- macOS metadata;
- environment and key material;
- real client or restricted data paths;
- private source-library paths;
- local test and browser output.

It also rejects case-colliding repository paths.

## 3. Deterministic governance baseline

`configs/repository-governance.yaml` is the governed source. `repository/repository-governance-baseline.json` is generated deterministically.

The baseline records:

- required governance files and their byte sizes;
- SHA-256 digests for controlled policy, workflow, configuration, and validator files;
- prohibited tracked-path findings;
- case-collision findings;
- mandatory workflow invariants;
- hosted GitHub settings that must be verified before Codex begins.

The build and validator scripts are:

- `scripts/build_pcr03_repository_hygiene.py`;
- `scripts/validate_pcr03_repository_hygiene.py`.

## 4. Workflow hardening

The complete repository workflow now:

- keeps read-only repository permissions;
- disables persisted checkout credentials;
- cancels superseded runs on the same branch or pull request;
- builds and clean-checks the PCR-03 governance baseline;
- runs PCR-03 after all Phase 1–7, PCR-01, and PCR-02 validation;
- retains governance policy and baseline evidence in the release artifact.

Automation remains evidence rather than approval.

## 5. Pull-request reconciliation

Obsolete Phase 5 pull requests #11 and #12 were superseded by merged PR #13. PCR-03 closes them with explicit replacement references so they can no longer be mistaken for active or controlling work.

Historical merged and validation branches may be deleted after evidence retention is confirmed. The GitHub connector used for PCR--03 does not expose branch deletion or repository-setting mutation, so hosted settings and residual branch deletion remain explicit Founder-administered checks rather than being misrepresented as completed.

## 6. Hosted settings required before Codex

Before Codex implementation begins, the Founder should verify in GitHub:

- MFA is enabled;
- `main` requires a pull request;
- the complete validation workflow is required;
- stale approvals are dismissed after new commits;
- review conversations must be resolved;
- force pushes and deletion of `main` are blocked;
- merged head branches are deleted automatically.

These controls are recorded in the deterministic baseline but cannot be proven from repository files alone.

## 7. Boundary

PCR-03 does not:

- enable real client data;
- approve processors or infrastructure;
- import original methodology binaries;
- expose restricted answer keys;
- certify production security;
- authorise external actions;
- merge future material changes without Founder approval;
- replace the Founder as accountable owner.

Real client data remains prohibited.
