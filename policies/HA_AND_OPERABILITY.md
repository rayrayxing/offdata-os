# HA and Operability

Hermes Kanban is treated as single-host in v1. Do not place `kanban.db` on NFS/SMB/network-shared storage and do not pretend multiple dispatchers form a cluster.

## v1 topology

- one pinned supervised Hermes host;
- durable local disk for Hermes/Kanban/workspaces;
- PostgreSQL as authoritative Venture Brain;
- off-host backups for Postgres, Kanban, profiles, Skills/certifications and critical artifacts;
- process supervisor/watchdog;
- Telegram exception alerts;
- operation-level idempotency protects authoritative effects when reasoning is retried.

## Recovery

Test restore. A backup never restored is not certification evidence.

## Future scale-out boundary

If multiple hosts are needed, introduce an explicit distributed broker/API or replacement work-queue substrate while retaining Venture Brain operation contracts. Do not network-share SQLite.
