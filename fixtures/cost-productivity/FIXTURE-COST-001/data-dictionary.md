# Data dictionary — FIXTURE-COST-001

All values are synthetic. Currency fields ending `_sgd` are Singapore dollars. Percent fields are percentage points.

- `site-cost-baseline.csv`: annual site demand and cost. Allocated corporate overhead is not automatically avoidable.
- `activity-capacity.csv`: time-driven activity inputs, practical capacity and failure-demand share.
- `service-performance.csv`: service, repeat-visit, peak-utilisation, safety and data-quality measures.
- `initiative-options.csv`: management options with cash, capacity, cost-avoidance, implementation-cost and risk fields. Options sharing an `overlap_group` require de-duplication.

Known defects are intentional: inconsistent closure codes, standby hours embedded in contractor cost, overhead allocation and overlapping route/dispatch benefit estimates.
