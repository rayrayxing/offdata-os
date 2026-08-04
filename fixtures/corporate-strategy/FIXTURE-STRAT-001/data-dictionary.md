# Data dictionary — FIXTURE-STRAT-001

All values are synthetic. Currency fields ending `_sgd_m` are SGD millions. Percent fields are percentage points, not fractions.

- `business-unit-performance.csv`: controlled historical business-unit economics. `allocated_corporate_overhead_sgd_m` is an allocation and is not automatically avoidable.
- `market-position.csv`: synthetic market and ownership-position evidence. `evidence_quality` records confidence in the estimate.
- `capital-options.csv`: mutually exclusive action options by business unit. Net capital commitment equals incremental investment less divestiture proceeds.
- `scenario-assumptions.csv`: scenario inputs used to test robustness, not forecasts represented as facts.

Known defects are intentional: incomplete digital churn history, uncertain environmental provision, a management-sponsored growth estimate and non-causal overhead allocation.
