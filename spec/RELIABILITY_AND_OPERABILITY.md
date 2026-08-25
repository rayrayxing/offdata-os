# Reliability and Operability

## v1 topology

One pinned supervised Hermes host runs gateway, Kanban, profiles, Skills, builders and workspaces. PostgreSQL is authoritative Venture Brain. Off-host backup is mandatory.

Never network-share Kanban SQLite or claim multi-host HA from concurrent dispatchers.

## SLOs

- Work durability: >=99.9% of accepted logical work remains durably represented.
- Workflow integrity: >=99% completes contract or safely enters BLOCKED/FAILED/REVIEW.
- Zero tolerated: authority violation, fabricated authoritative evidence, duplicate financial effect, unaudited capital action, TEST/SIM→authoritative LIVE contamination.

## Monitoring

Gateway/dispatcher, stranded/stale tasks, circuit breakers, worker crashes, model/provider health, DB, backup freshness, disk/RAM, Telegram, audit lag and financial reconciliation.

## Recovery

Use process supervision and Hermes retry/crash reclamation for work. Venture Brain `operation_id` makes external/business effects retry-safe. Test full restore from off-host backup before certification.