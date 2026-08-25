# System Architecture

## Layers

1. **Hermes Core** — profiles, models, Skills, Kanban, cron, gateway, MCP, browser, terminal, plugins, dashboard.
2. **Venture Brain** — canonical state, evidence/claims/concerns, experiments, gates, finance/capital, authority/audit, calibration/learning.
3. **Specialist Company** — innovation, research, critique, product, commercial, finance, governance and learning roles.
4. **External World** — web/social/research, CRM/email/calendar, GitHub/cloud/hosting, analytics/ads/support, payment/accounting.

## Memory separation

- Profile memory: procedural/role learning only.
- Kanban task context: current objective, parents, artifacts, attempts, blockers and required Skills/model.
- Venture Brain: canonical venture truth. Venture Brain wins on conflict.

## Environments

Every root and descendant is one of `TEST`, `SIMULATION`, `LIVE` and carries `is_provisional` where applicable. Environment/provisional state may not be silently promoted. Mock providers cannot write authoritative LIVE records.

## Board topology

- `portfolio`: discovery, Skill/capability work, cross-venture research, capital allocation and learning.
- `venture-<slug>`: one board per serious venture.
- dynamic profile `venture-gm-<slug>` coordinates each venture but cannot bypass policy.

## Idempotency

Every consequential Venture Brain mutation/external effect requires `operation_id` and `correlation_id`.

- same operation + same normalized input → return existing result;
- same operation + different normalized input → `IDEMPOTENCY_CONFLICT`.

## Single-host v1

Hermes/Kanban runs on one pinned supervised host. PostgreSQL is authoritative venture state. Off-host backups and tested restore are required. Multi-host coordination is a future explicit broker boundary.