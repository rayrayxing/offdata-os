# WS6.8 — Issue and backlog normalization

WS6.8 closes `WS6-CONSIST-005` and `WS6-CODEXPREP-007`.

Issues #3, #4 and #5 were ambiguous open implementation assignments. They are normalized as closed, superseded and non-actionable provenance records. Their remaining scope is mapped into repository-only blocked drafts for `IMP-P1` through `IMP-P12` under `handoff/future-implementation-issue-pack/`.

The future issue pack is generated from `docs/11-BUILD-BACKLOG.md`. It preserves exact phase order, task identities and dependencies while keeping every future phase marked `draft_only=true`, `live_issue_created=false` and `implementation_authorized=false`.

After normalization:

- issue #1 is the only actionable implementation assignment, limited to permit-gated `IMP-P0`;
- issue #19 is the only manual pre-launch gate;
- issue #2 remains closed as a duplicate;
- issues #3–#5 remain closed as `not_planned` and must not be reopened to bypass phase gates;
- no live issue exists for `IMP-P1` through `IMP-P12`.

This package does not authorize Codex. `WS6-BLOCK-006` remains open; `codex_start_authorized=false`; IMP-P0 merge, IMP-P1+, runtime activation, production and external actions remain unauthorized.

Next permitted work package: `WS6.9`.
