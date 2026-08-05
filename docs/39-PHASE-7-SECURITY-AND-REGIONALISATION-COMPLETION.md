# 39 — Phase 7 Security and Regionalisation Completion

## Status

**Chat-first Phase 7: complete and independently CI-validated.**

Date: 2026-08-05

This release completes the security, privacy and regionalisation intelligence that can be governed and tested before an operating production environment exists. It creates deterministic policy decisions, security evidence requirements, a Singapore-first regional-cell design, configurable retention and deletion controls, provider and processor governance, a threat model, incident playbooks and a default-deny production gate.

Phase 7 does **not** claim that production security infrastructure exists or that real client data is authorised. The controlling configuration remains `real_client_data_enabled: false`.

## 1. Security decision engine

`packages/offdata-core/src/offdata_core/security_regionalisation.py` adds strict immutable contracts and deterministic functions for:

- data classification and minimum handling rules;
- tenant, engagement and regional scope enforcement;
- least-privilege access decisions;
- MFA and support-access expiry checks;
- development-environment real-data prohibition;
- Founder-controlled export, deletion and external action boundaries;
- Singapore-first placement decisions;
- cross-region transfer decisions;
- retention, archival, export and deletion eligibility;
- legal-hold overrides;
- provider and processor use decisions;
- mandatory-control production-gate evaluation;
- incident severity, containment and escalation decisions;
- secret-pattern detection in nested structures;
- deterministic baseline generation and verification.

Every decision returns an explicit disposition and reason set. Ambiguity does not become permission.

## 2. Data classification

The governed classification catalogue contains exactly four levels:

1. `public`;
2. `internal`;
3. `client_confidential`;
4. `highly_restricted`.

The catalogue defines minimum controls for storage, logging, provider routing, regional handling, export, deletion and review. Client-confidential and highly restricted records prohibit raw-payload logging and provider training.

Where multiple classifications apply, the most restrictive classification governs.

## 3. Tenant and engagement isolation

Restricted records carry explicit tenant, engagement and region scope. The access engine denies:

- tenant mismatch;
- engagement mismatch;
- region mismatch;
- missing MFA where required;
- expired time-limited support access;
- unsupported actor capabilities;
- real-client-data use in development;
- unapproved export, deletion or material external action;
- processor use outside its approved data classes, purposes or regions.

Global methodology and global metadata do not create authority to expose engagement content. The regional policy permits only a small controlled global metadata set and explicitly prohibits client names, contact details, evidence text, passages, model inputs, model outputs, recommendations and personal data from that global layer.

## 4. Singapore-first regionalisation

`security/regional-cells.yaml` defines three controlled cells:

- Singapore local development;
- planned Singapore staging;
- planned Singapore production.

The planned production cell remains synthetic-only and does not enable client data. The first managed region remains Singapore.

Future regional-cell expansion requires:

- a documented client, contractual or jurisdictional need;
- approved cell architecture;
- region-specific provider and processor review;
- transfer and backup design;
- isolation and recovery tests;
- incident ownership;
- explicit Founder approval.

Client-data cross-region transfer is denied by default. An approval record cannot substitute for an unavailable or untested destination cell.

## 5. Retention, export and deletion

The release defines four configurable retention-policy defaults. These are product-control defaults and are not represented as legal advice.

The retention engine distinguishes:

- continued retention;
- archive eligibility;
- export eligibility;
- deletion eligibility;
- verified deletion completion.

A soft-delete flag is not verified deletion. Legal hold overrides deletion. Material deletion requires authority, an audit event, execution evidence and verification. Agents may calculate eligibility and prepare a decision packet but may not silently delete governed records.

## 6. Provider and processor governance

`security/provider-processor-register.yaml` defines the governed register schema. It requires, as applicable:

- provider and service identity;
- purpose and owner;
- approved data classes;
- approved regions;
- subprocessors;
- retention and deletion terms;
- training and secondary-use posture;
- transfer basis or restriction;
- security review and evidence dates;
- contract and data-processing status;
- incident contact;
- approval status and expiry;
- rollback or replacement path.

The real register is intentionally empty. No external processor is approved for real client data in Phase 7. Three synthetic processor records exist only for deterministic tests.

`UT-PROCESSOR-REGISTER-001` is converted from planned to executable evidence. Physical provider configuration and contractual approval remain later gates.

## 7. Threat model and abuse cases

The governed threat model contains twenty threats covering:

- credential exposure;
- cross-tenant and cross-engagement leakage;
- regional-placement and cross-border errors;
- prompt injection and malicious documents;
- excessive agent or integration permissions;
- unsafe external actions;
- processor scope expansion;
- sensitive logging and telemetry;
- retention and deletion failure;
- backup and restoration failure;
- supply-chain compromise;
- monitoring failure;
- incident concealment or premature closure;
- release-gate bypass;
- insecure support access;
- uncontrolled global metadata;
- recovery that duplicates external actions.

Each threat has prevention, detection, response, evidence and residual-risk expectations.

## 8. Security control catalogue

The release contains forty-eight security controls. Eighteen are mandatory before real client data can be enabled:

- strong authentication and MFA;
- least privilege;
- environment separation;
- encryption in transit;
- encryption at rest;
- tenant isolation;
- engagement isolation;
- region pinning;
- secret scanning;
- supply-chain review;
- prompt-injection testing;
- backup restoration testing;
- kill-switch testing;
- observability and alerts;
- incident playbook readiness;
- retention and deletion controls;
- processor register completeness;
- audit export capability.

Evidence must be current and match the exact environment and region. A passing policy unit test cannot stand in for encryption, restoration, isolation or operational-monitoring evidence.

## 9. Production security gate

The production gate is default-deny.

A request to enable real client data passes the machine gate only when the exact target cell has current passing evidence for every mandatory control. Even then, the result is not autonomous activation: explicit Founder approval remains required.

The gate rejects:

- missing evidence;
- failed evidence;
- expired evidence;
- evidence for a different environment;
- evidence for a different region;
- incomplete mandatory-control coverage;
- a cell that is not approved for client data;
- self-approval by an agent or service actor.

An empty evidence set produces a complete report of all eighteen missing mandatory controls.

## 10. Incident response

Twelve incident playbooks cover security, privacy, regional, provider, availability, integrity and external-action incidents.

The deterministic incident assessment can recommend:

- kill-switch activation;
- integration revocation;
- credential rotation;
- tenant or engagement quarantine;
- preservation of audit evidence;
- backup isolation;
- provider escalation;
- Founder notification;
- client-notification decision support;
- corrective-action and regression-test requirements.

Agents may assist with analysis and containment preparation. They may not conceal, minimise or autonomously close a material incident. High and critical incidents require Founder notification.

## 11. Security test catalogue

The governed catalogue contains thirty-six security tests across:

- chat-first unit and policy tests;
- security and adversarial tests;
- integration tests;
- recovery tests;
- Founder-acceptance tests.

Phase 7 adds thirty-seven executable runtime tests and mapped requirement evidence. Mutation tests cover permissive classification drift, scope bypass, regional drift, unsafe transfer, retention bypass, processor overreach, missing controls, stale evidence, secret leakage and incident under-classification.

The following operating-environment tests correctly remain planned:

- `IT-ENV-SEPARATION-001`;
- `SEC-ENCRYPTION-001`;
- `SEC-REGION-ISOLATION-001`;
- `IT-BACKUP-RESTORE-001`;
- `SEC-SUPPLY-CHAIN-001`;
- `IT-OBSERVABILITY-001`;
- `IT-RETENTION-001`;
- `IT-ROLLBACK-001`;
- `FA-PRODUCTION-GATE-001`.

`SEC-P7-DOCUMENT-001` also remains planned for operating document-ingestion security evidence.

## 12. Deterministic baseline

`security/security-regionalisation-baseline.json` is generated from the governed YAML records. Its validated scope is:

- four data classes;
- three regional cells;
- four retention policies;
- zero approved real processors;
- three synthetic processor fixtures;
- twenty threats;
- forty-eight controls;
- thirty-six security tests;
- twelve incident playbooks;
- eighteen mandatory real-client controls;
- first managed region Singapore;
- real-client-data enablement false.

The permanent CI gate regenerates this baseline and fails on byte drift.

## 13. Requirement and test traceability

The combined registry records:

- 215 implemented test nodes;
- 55 remaining planned tests;
- 19 completed planned-test IDs;
- all 123 catalogue requirements mapped to implemented or planned evidence.

Phase 7 converts only `UT-PROCESSOR-REGISTER-001` to executable evidence. Infrastructure and Founder-acceptance tests remain planned rather than being represented as complete.

## 14. Independent validation evidence

GitHub Actions run `30975868412`, job `92209612760`, validated branch head `79b61615185ac4da99c81fa2a6e95b694a9ca35a` and pull-request merge reference `644e3c4311637511ad5753f968a5c57f8c3bd520` on Ubuntu 24.04 and Python 3.11.15.

### Phase 7 validator

```text
PHASE 7 SECURITY AND REGIONALISATION VALIDATION PASSED
- data_classes=4
- regional_cells=3
- retention_policies=4
- processor_records=0
- processor_fixtures=3
- threats=20
- controls=48
- security_tests=36
- incident_playbooks=12
- mandatory_real_client_controls=18
- first_managed_region=singapore
- real_client_data_enabled=false
- production_gate_default=deny
- founder_approval_boundary=preserved
```

### Complete Phase 1–7 quality gate

- Phase 1 contract validator: passed;
- Phase 2 agent-system validator: passed;
- Phase 3 analytical-oracle validator: passed;
- Phase 4 deliverable-semantic validator: passed;
- Phase 5 additional-fixture validator: passed;
- Phase 6 knowledge-ingestion validator: passed;
- Phase 7 security and regionalisation validator: passed;
- read-only clean generation of all governed Phase 1–7 records: passed;
- runtime tests: 217 passed;
- total coverage: 93.34 percent;
- mandatory coverage floor: 90 percent;
- Python compilation: passed;
- Ruff: passed;
- strict MyPy: passed with no issues across 30 source files.

### Retained release artefact

- files: 65;
- artefact ID: `8918232404`;
- compressed size: 157,193 bytes;
- SHA-256: `e3a87d3a23f1adce313985a79300447de1cd548986dd81abcf4c8b240c0aa263`;
- retention: 30 days.

## 15. Explicitly deferred evidence

Phase 7 does not establish:

- production identity-provider configuration;
- operating MFA enforcement;
- physical development, staging and production isolation;
- deployed encryption in transit or at rest;
- cloud-region and backup-region isolation;
- real database or object-store tenant isolation;
- backup restoration against operating stores;
- container, dependency and runtime supply-chain scanning;
- production telemetry and alert delivery;
- operating retention jobs, exports or verified deletion;
- infrastructure rollback;
- provider contracts or processor approval;
- real-client incident exercises;
- Founder acceptance of a production cell;
- legal or regulatory compliance certification.

These require Codex execution, provider and contract evidence, and Founder decisions. They must not be inferred from the chat-first policy package.

## 16. Phase-gate conclusion

Phase 7 is complete as the governed chat-first security and regionalisation intelligence. It makes the future production gate explicit, testable and default-deny while preserving operational autonomy and Founder accountability.

Real client data remains prohibited.

## 17. PCR-01 canonical evidence reconciliation

PCR-01 establishes the final exact-head release evidence as authoritative:

- final run: `30976222896`;
- final job: `92210649514`;
- pull-request head: `8da0f1167d9b6f4da792770b0d564379aa46c3fe`;
- pull-request merge reference: `264459045ce75d7d7c60cbc980a50193f08a6f16`;
- controlling `main` commit: `7dc5531e641158e5a84fbbb9fdf07cefefd4782b`;
- final artifact: `8918355687`;
- final artifact SHA-256: `3b9f14c520d31ce5f73fbecc726b032a3134042769ee84176e85d642fe2ea852`.

The earlier successful runs `30975868412` and `30976088173`, and their artifacts `8918232404` and `8918307764`, are preserved as **superseded validation snapshots**. Their evidence remains historical, but they are not the controlling Phase 7 release. This section supersedes the earlier run and artifact metadata in Section 14 without deleting that audit history.
