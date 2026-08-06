# 49 — PCR-10 Pre-Codex Release and Quality Acceptance

## Purpose

PCR-10 is the final bounded chat-first phase and is now integrated into `main` with PCR-03 through PCR-09. It does not build the application. It converts existing product, architecture, testing, Founder-experience and deliverable-quality intent into one deterministic pre-start readiness contract.

## Integrated release state

PCR-03 through PCR-10 were merged sequentially into `main` using merge commits. Each retargeted successor was compared with its previously validated stacked merge reference and had zero content differences before merge. The post-merge reconciliation marks only the eight PCR merge conditions complete. Issue #19 hosted controls, the clean macOS environment and explicit Founder Phase 0 approval remain incomplete, so Codex start authorization remains false.

The controlling machine record is `contracts/pre-codex-readiness.json`, generated from `configs/pre-codex-readiness.yaml` and validated by `scripts/validate_pcr10_pre_codex_readiness.py`.

## Authority and phase boundary

`AGENTS.md` remains the controlling instruction. `handoff/codex-phase0-handoff.json` remains the Phase 0 execution task graph. PCR-10 owns the final pre-start release and quality gate and the final generated issue body at `handoff/codex-phase0-issue-pcr10.md`.

PCR-10 does not authorize Codex. The exact activation sequence requires PCR-03 through PCR-10 merged to `main`, issue #19 hosted controls verified, a clean macOS environment and explicit Founder approval. Runtime, Hermes, Northstar, real-client-data, paid-service, external-action, production and autonomous-merge authorization remain false.

## Release integrity acceptance

The integrated pre-Codex release must have one authoritative `main` SHA, one release ID, exact PCR merge commits, generated-record and test-registry digests, the latest successful complete workflow, a defect and waiver register, rollback instructions and durable evidence beyond expiring CI artifacts.

No critical or high defect is acceptable. A clean-clone rebuild must produce no generated diff and every referenced path and command must exist.

## Developer experience acceptance

Phase 0 must provide root-level `doctor`, `bootstrap`, `up`, `down`, `restart`, `health`, `test`, `lint`, `format`, `scan`, `reset-synthetic`, `backup`, `restore`, `clean` and `support-bundle` commands.

Failures must explain cause and safe remediation. Port conflicts and unsupported versions must be detected. Cleanup must be path-safe and synthetic-data scoped. Credentials must never appear in logs or support bundles. Backup and restore must be demonstrable on the supported macOS and Apple Silicon environment.

## Founder experience acceptance

The Founder interface must expose pending material decisions, consequences, deadlines, reversibility and the exact action that follows approval. Recommendation, authorization and execution must remain distinct. Material claims and numbers must drill through to evidence and model outputs. Waiting, blocked, retrying, failed, stale and complete states must be visible. Keyboard navigation, focus, contrast and readable error states must pass. Unauthorized external sending must be impossible.

## Output-quality acceptance

Material citation resolution is 100 percent. Unsupported material claims are zero. Facts, assumptions, synthesis and recommendations are labelled. Contradicting evidence is retained.

Material-number reconciliation and cross-format agreement are 100 percent. Unexplained hard-coded material numbers are zero. Independent recalculation must pass.

PPTX, DOCX and XLSX files must open without repair warnings and remain editable. Slides must avoid clipping and pass visual regression. Documents must preserve navigation, pagination, tables and accessibility. Workbooks must preserve formulas, references, print areas and assumption/output separation. PDF, SVG and HTML outputs must render correctly, preserve accessibility and remain materially consistent with Office outputs.

## Operational and learning acceptance

Implementation must provide structured correlation IDs, retry and error taxonomy, distinct health/readiness/liveness checks, privacy-safe OpenTelemetry-compatible traces, attributable cost and latency records, visible fail-closed feature flags and kill switches, dependency provenance, SBOM evidence and executable backup, restore, rollback and support-bundle drills.

Later phases must measure Founder correction effort, override reasons, editing time, repeated manual work, defect categories, missing evidence or methods, accepted or rejected agent contribution, completion time, human time saved, quality per cost and client-facing usefulness.

## Cross-cutting acceptance

Singapore timezone handling, currency and unit consistency, data portability, schema migration, font substitution, privacy-safe telemetry and model-routing quality must be explicit and testable. Material work must not silently degrade to a lower-quality model or provider route.

## Validation and completion

PCR-10 is complete when its source, schema, generated contract, final issue body and documentation rebuild deterministically; its semantic and mutation tests pass; every retained Phase 1–7 and PCR-01–10 validator passes; all runtime tests meet the 90 percent coverage floor; compilation, Ruff and strict MyPy pass; and the live issue #1 body matches the PCR-10 generated digest while issue #2 remains closed as duplicate.

PCR-03 through PCR-10 are integrated. No additional broad chat-first architecture phase is required; the remaining pre-Codex work is hosted-control verification, permanent release evidence, clean-macOS readiness and explicit Founder Phase 0 approval.
