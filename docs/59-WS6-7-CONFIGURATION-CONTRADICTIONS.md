# WS6.7 — Configuration contradictions

WS6.7 closes `WS6-CONSIST-004`.

The committed environment example previously advertised a USD 25 monthly model budget even though the controlling initial operating controls prohibit purchases, hard-cap paid-provider spend at zero, and keep paid services unauthorized.

The repair sets `OFFDATA_MONTHLY_MODEL_BUDGET_USD=0`, keeps all paid-provider API keys blank, and adds a deterministic cross-file gate that reads `.env.example` and `contracts/initial-operating-controls.json` together. The gate rejects any non-zero committed budget, configured provider key, authorized purchase, non-zero hard cap, paid-service authorization, or launch-boundary promotion.

This package does not authorize Codex. `WS6-BLOCK-006` remains open; `codex_start_authorized=false`; IMP-P0, merge, runtime activation, production and IMP-P1 remain unauthorized.

Next permitted work package: `WS6.8`.
