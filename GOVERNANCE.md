# offdata OS Repository Governance

## Authority and ownership

The Founder is the accountable repository owner and final approver for material changes. `AGENTS.md` is the controlling instruction for automated engineering work.

Authority order:

1. Applicable law, platform safety controls, and explicit Founder instructions.
2. `AGENTS.md`.
3. This governance policy.
4. Approved architecture and decision records.
5. Approved phase requirements and acceptance criteria.
6. Other repository documentation.
7. Agent judgement.

`main` is the canonical branch. Historical offdata repositories, abandoned branches, chat transcripts, model memory, and unmerged pull requests are not controlling specifications.

## Change classes

### Routine internal changes

Reversible implementation, tests, synthetic fixtures, documentation corrections, and maintenance inside an approved phase may be developed autonomously on a branch.

### Material changes

Architecture, authority, data handling, security policy, retention, processors, external actions, production enablement, commercial commitments, and changes to golden expectations require explicit Founder approval before execution or merge.

### Prohibited changes

No contributor or agent may commit secrets or real client data, weaken tests to obtain a pass, expose restricted evaluation material, silently alter golden evidence, import private methodology binaries without the governed gate, or transfer Founder accountability to an automated system.

## Branch and pull-request policy

- Branch from current `main`.
- Use one bounded purpose per branch.
- Open a draft pull request for material work.
- Use the pull-request template.
- Resolve or explicitly record every review finding.
- Require the complete repository gate before merge.
- Prefer squash or rebase merge for a clear canonical history.
- Close superseded pull requests with a link to the controlling replacement.
- Delete merged or abandoned working branches when they no longer provide required evidence.
- Never force-push `main`.

Repository settings should require pull requests for `main`, prevent force pushes and deletion, require the complete validation workflow, dismiss stale approvals after new commits, require conversation resolution, and automatically delete merged head branches. These hosted settings remain a Founder-administered control and must be verified before Codex implementation begins.

## Source-of-truth policy

Governed YAML, JSON, schemas, catalogues, fixtures, and release records are authoritative only in their documented hierarchy. Generated files must be reproducible from committed sources and protected by a clean-generation check.

The canonical Phase 1–7 chat-first release remains governed by PCR-01. PCR-02 governs semantic test identity and typed references. PCR-03 governs repository policy files, tracked-file hygiene, and validation-workflow invariants.

## Review and merge accountability

Automation provides evidence, not approval. The person approving a material change must understand:

- what changed and why;
- which requirements and controls are affected;
- which tests ran and what they prove;
- what remains untested or planned;
- whether data, security, cost, legal, rights, or external-action boundaries changed;
- how to roll back.

## Security response

Security reports follow `SECURITY.md`. Material incidents cannot be autonomously closed. Containment may proceed within approved playbooks, but severity, external notification, legal conclusions, production restoration, and final closure remain human-controlled.

## Exceptions

A governance exception must be explicit, time-limited, documented with owner and rationale, and must not bypass law, platform controls, secret handling, real-client-data prohibition, or Founder authority.
