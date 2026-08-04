# 18 — Immediate Workboard

## 1. Current status

The repository now contains:

- Governing Build Pack and Founder controls.
- Chat-first development allocation.
- Numbered requirements catalogue.
- Machine-readable lifecycle, approval and agent configuration.
- JSON schemas for agent envelopes, context packages and Founder decision packets.
- Synthetic engagement fixture manifest.
- Third-party tool registry.
- A deterministic Python starter package for lifecycle, policy and execution contracts.
- Unit tests developed in ChatGPT and locally exercised against Python 3.11-compatible code.

All code remains provisional until Codex installs the repository dependencies and reruns the tests on the Founder’s Mac and in GitHub Actions.

## 2. Immediate sequence

### NOW-01 — Codex validates the chat-built foundation

Owner: Codex

Tasks:

1. Read `AGENTS.md` and `docs/00-START-HERE.md`.
2. Inspect all newly added files.
3. Install `packages/offdata-core` in an isolated environment.
4. Run unit tests, formatting, linting and type checks.
5. Repair implementation defects without changing the governing intent.
6. Validate YAML and JSON schemas.
7. Add the package to the repository-wide CI.
8. Report any conflict between code and the canonical documents.

Acceptance:

- All deterministic tests pass.
- Config and schema files parse.
- No duplicate policy implementation is introduced.
- Test evidence is attached to the Phase 0 pull request.

### NOW-02 — Complete Phase 0 application shell

Owner: Codex

Tasks:

- Next.js application shell.
- FastAPI service shell.
- Local PostgreSQL.
- Local S3-compatible storage.
- Container startup and cleanup.
- Repository-wide commands.
- GitHub Actions, secret scanning and dependency scanning.
- Founder-readable setup guide.

Acceptance: clean macOS start, health checks and full test command.

### NOW-03 — Knowledge-source import preparation

Owner: ChatGPT now; Codex validates later.

Tasks suitable for ChatGPT:

- Final source manifest and canonical aliases.
- Method-record schema.
- Problem-archetype schema.
- Source-document and source-passage schemas.
- Extraction quality tests.
- Initial domain-pack index.

Tasks requiring Codex:

- Copy original files into the private repository.
- Calculate checksums.
- Parse DOCX and Markdown.
- Store passages and metadata.
- Run deterministic re-ingestion tests.

### NOW-04 — Synthetic AI-audit fixture specification

Owner: ChatGPT now; Codex generates data files and runs it later.

Required fixture components:

- Fictional SME profile.
- Initial Founder/client conversation.
- Financial and operational data.
- Process and technology inventory.
- AI use-case candidates.
- Risk and control evidence.
- Contradictions and missing information.
- Expected problem frame.
- Acceptable and rejected method stacks.
- Expected calculations and recommendations.
- Expected Founder decisions.
- PPTX, DOCX, XLSX and HTML acceptance criteria.

### NOW-05 — API and event contracts

Owner: ChatGPT

Define before database implementation:

- Engagement commands and events.
- Record-create/update/archive contracts.
- Approval request and decision events.
- Workflow checkpoint events.
- Tool-call and external-action events.
- Cost and usage events.
- Audit correlation rules.

### NOW-06 — Founder cockpit information architecture

Owner: ChatGPT; Codex implements.

Define:

- Engagement portfolio.
- Current stage and operational state.
- Founder decision inbox.
- Blockers, gaps and material risks.
- Evidence and method status.
- Deliverable review.
- Costs and agent activity.
- CRM and opportunity view.
- Methodology candidate review.

## 3. ChatGPT development queue

The next chat-built components should be completed in this order:

1. Knowledge and method schemas.
2. Engagement command/event contracts.
3. Synthetic SME AI-audit fixture.
4. Quality-defect and review schemas.
5. Story model and infographic specification schemas.
6. CRM and opportunity dossier schemas.
7. Methodology Radar candidate and promotion schemas.
8. Founder cockpit screen requirements.
9. Phase-specific Codex prompts and acceptance checklists.

## 4. Codex credit discipline

Codex should not spend credits restating documents, inventing record fields already specified or debating settled architecture. It should retrieve the governing file, implement the narrow work package, run tests and report discrepancies.

Use premium reasoning only for architecture conflicts, difficult debugging, security review and material synthesis. Use deterministic commands for builds, tests, schema validation, formatting, checksums, migrations and rendering checks.

## 5. Gate before Phase 1

Do not begin knowledge ingestion until:

- Phase 0 local environment works.
- `offdata-core` tests pass on macOS and CI.
- JSON and YAML validation is included in CI.
- The source manifest is approved.
- The original files are authorised for private-repository storage.
