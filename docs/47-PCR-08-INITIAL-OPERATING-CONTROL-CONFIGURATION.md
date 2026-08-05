# PCR-08 — Initial operating-control configuration

## Purpose

PCR-08 converts the existing governance, security, runtime, incident, retention, approval and cost rules into one deterministic initial operating-control configuration. It is a configuration and reconciliation phase only. It does not start Codex, activate a runtime, install Hermes, implement the Northstar blueprint, enable a provider, approve a processor, permit real client data or authorise production use.

The initial posture is deliberately narrow: **Founder-only** operation, local synthetic work, Singapore as the first managed region, public and internal data only, commands-only canonical writes, deny-by-default networking, and no external or billable execution.

## Delivered control model

The source configuration is `configs/initial-operating-controls.yaml`. The generated machine contract is `contracts/initial-operating-controls.json`, validated against Draft 2020-12 JSON Schema by `scripts/validate_pcr08_initial_operating_controls.py`.

The configuration reconciles all **forty-eight security controls** into ten accountable operating domains:

1. identity, access and credentials;
2. data classification, tenancy and regionalisation;
3. secret safety, supply chain and document quarantine;
4. runtime, agent, tool and usage control;
5. canonical state, audit and durable workflow integrity;
6. decision, assurance and release authority;
7. backup, recovery, retention and verified deletion;
8. providers and processors;
9. monitoring, kill switches and incident response;
10. environment, encryption and change control.

Every catalogue control is assigned exactly once. Eighteen controls remain mandatory for any future real-client-data gate. The configuration does not claim infrastructure evidence for controls that are only specified at chat-first stage.

## Authority and operating gates

The six decision classes remain aligned to `configs/policy.yaml`. Routine internal actions may execute only within the policy, tool, data, budget and phase boundaries. Material, external, commercial, legal or regulatory, and irreversible decisions retain human accountability. Legal or regulatory conclusions require qualified specialist review.

Eight gates are configured and all begin unauthorised:

- Codex Phase 0 start;
- runtime activation;
- Hermes activation;
- Northstar implementation;
- real client data;
- external action execution;
- paid service or trial activation;
- production deployment.

The external-action gate requires the global switch to be enabled, an exact scoped unexpired approval, an idempotency key and correlated audit evidence. The real-client-data gate requires current evidence for every mandatory control in the exact environment and region, an approved processor register and explicit Founder approval.

## Switches, cost and provider posture

Six control switches cover agent execution, tool invocation, external actions, provider and gateway networking, workflow classes and production deployment. Every switch starts in `deny`, fails closed, requires a correlated audit event and can be reset only by the Founder.

The initial configuration sets a **paid-provider hard cap of zero**. Purchases and trials remain unauthorised. Per-invocation limits continue to come from the six governed agent budget profiles, adapters may not raise those limits, actual usage must be recorded, and any billable usage must alert.

The processor register remains empty for real client data. Unregistered processors deny by default. OAuth, provider gateways, provider training, credential values and paid-service activation remain disabled.

## Incident, recovery, retention and exceptions

All twelve incident playbooks are reconciled. Agents may assist but may not close material incidents. Critical and high incidents require immediate Founder notification, evidence preservation and fail-closed containment. An implicated actor cannot be the sole reviewer.

All four retention policies remain mapped. Legal hold overrides deletion. Deletion is never autonomous, requires Founder approval and verification, and must propagate to derived indexes and caches. Backup and restore evidence remains pending the operating environment, and recovery objectives remain unset until measured rather than being asserted without evidence.

Exceptions cannot be silent. They require exact scope, expiry, compensating controls, independent review and Founder approval. Secret values in source or chat, cross-tenant access, real client data before the production gate, self-approval of material work, autonomous merge and unregistered processors are non-waivable.

## Evidence and cadence boundary

Per-change and per-release controls are active for repository work: deterministic generation, complete CI, independent review, rollback records, exact-version approval and retained evidence. Daily, weekly, monthly, quarterly and annual operating cadences are configured but remain disabled until the relevant runtime or environment is activated.

Chat-first configuration evidence is current. Hosted-control evidence, operating-environment evidence and production evidence remain incomplete. In other words, **operating evidence remains pending** and a green repository gate must not be represented as proof of production readiness.

## Activation boundary

The following remain binding:

- `initial_operating_controls_activation_authorized=false`;
- `codex_start_authorized=false`;
- `runtime_activation_authorized=false`;
- `hermes_activation_authorized=false`;
- `northstar_implementation_authorized=false`;
- real client data remains disabled;
- external actions remain disabled;
- paid services remain disabled;
- production deployment remains disabled;
- autonomous merge remains disabled.

PCR-03 through PCR-08 must merge in governed sequence, GitHub-hosted controls in issue #19 must be verified, a clean macOS environment must be available and the Founder must explicitly approve Phase 0 before Codex may begin.

## Validation

Run:

```bash
python scripts/build_pcr08_initial_operating_controls.py
python scripts/build_pcr04_codex_handoff.py
python scripts/validate_pcr08_initial_operating_controls.py
python scripts/validate_pcr04_codex_handoff.py
```

The PCR-08 validator enforces deterministic generation, schema validity, exact cross-contract control coverage, authority and activation boundaries, evidence honesty and controlled negative mutations.
