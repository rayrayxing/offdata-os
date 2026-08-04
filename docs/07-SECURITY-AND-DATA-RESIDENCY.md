# 07 — Security, Privacy and Data Residency

## 1. Security objective

Protect client confidentiality, engagement integrity, credentials, commercial information and methodology assets while preserving recoverability and auditability.

The first implementation uses synthetic data only. Real client data is prohibited until the production security gate is approved.

## 2. Initial deployment assumptions

- Founder based in Singapore
- Initial user count: one
- Initial preferred data region: Singapore
- Local development on macOS
- Future expansion through regional deployment cells where residency or client policy requires it

## 3. Data classes

### Public

Information intended for public use.

### Internal

Business and product information not intended for public release.

### Client confidential

Client-provided or client-derived information restricted to the engagement and authorised users.

### Highly restricted

Credentials, regulated information, sensitive personal data, transaction clean-team content, privileged material or information subject to special contractual controls.

Data class determines storage, logging, model routing, retrieval, export and retention rules.

## 4. Core controls

- Strong authentication and MFA
- Least-privilege roles
- Separate development, staging and production
- Encryption in transit and at rest
- Approved secret management
- Tenant and engagement isolation
- Explicit regional storage configuration
- Versioned and auditable material records
- Immutable or tamper-evident material action logs
- Backup and tested restoration
- Configurable retention, export and deletion
- Kill switches and integration revocation
- Dependency, container and code scanning
- Prompt-injection and malicious-document controls

## 5. Secrets

Secrets include API keys, OAuth tokens, passwords, signing keys, database credentials and webhook secrets.

Rules:

- Never place secrets in prompts, source files, issues, screenshots or documentation.
- Commit only `.env.example` placeholders.
- Use local secret files excluded by `.gitignore` for development.
- Use a managed secret store for staging and production.
- Rotate exposed or uncertain credentials immediately.
- Limit secrets by environment and purpose.
- Record credential owner, scope, creation date and rotation status without storing the value.

## 6. Client isolation

- Every client-scoped record requires tenant and engagement identifiers.
- Database access must enforce row-level or equivalent application controls.
- Object-storage paths and encryption boundaries must be engagement-aware.
- Retrieval indexes must not leak records across engagements.
- Global methodology retrieval must exclude confidential client content.
- Support and debugging access must be logged and time-limited.
- Cross-engagement reuse requires explicit authority and sanitisation.

## 7. Model and agent controls

- Send only minimum necessary context.
- Route highly restricted data only to approved providers and regions.
- Disable provider training or retention where contractually required and supported.
- Record provider, model, region and policy for material calls.
- Test for prompt injection, indirect prompt injection, data exfiltration and unsafe tool use.
- Treat model output as untrusted until validated.
- Do not place raw secrets in agent context.

## 8. Document ingestion

Uploaded documents may contain malicious instructions or embedded content.

The ingestion pipeline must:

- Preserve the original file and checksum.
- Scan file type and content.
- Extract text in a sandbox.
- Separate document content from agent instructions.
- Detect suspicious links, macros or embedded objects.
- Quarantine unsupported or high-risk files.
- Record extraction method and errors.
- Prevent document text from overriding system or repository policy.

## 9. External actions

External actions include email, CRM updates, file sharing, deployments, purchases, DNS changes and client communications.

Every material external action requires:

- Authorised actor or approval
- Policy check
- Idempotency key
- Target and payload preview
- Audit record
- Failure and compensation plan
- Rate and frequency limits

## 10. Data residency architecture

### Singapore cell

Initial production cell should host:

- Application compute
- PostgreSQL
- Object storage
- Search index
- Backups where available
- Logs subject to data-class policy

### Future regional cells

Each cell should have:

- Region-specific storage and compute
- Separate encryption and access policies
- Controlled global metadata only where permitted
- Explicit cross-border transfer rules
- Region-aware model routing
- Documented disaster-recovery arrangements

Methodology records that contain no client-confidential information may be distributed globally. Client data remains in the authorised cell unless a documented transfer basis exists.

## 11. CRM boundary

HubSpot initially stores relationship and opportunity information only.

Do not send to CRM by default:

- Detailed evidence
- Client datasets
- Internal hypotheses
- Sensitive model outputs
- Highly restricted records
- Full engagement work products

Synchronise only approved summaries and identifiers.

## 12. Logging and privacy

- Avoid logging raw sensitive prompts or files when metadata is sufficient.
- Redact secrets and sensitive identifiers.
- Define log retention separately from client-record retention.
- Record all privileged access and external actions.
- Provide an audit export for an engagement.

## 13. Backups and recovery

Before real client use:

- Automated backups must exist.
- Restore must be tested, not assumed.
- Recovery time and recovery point objectives must be documented.
- Object and database versions must reconcile.
- Workflow recovery must not duplicate external actions.

## 14. Production security gate

Real client data may be enabled only after:

- Threat model review
- Authentication and authorisation tests
- Engagement-isolation tests
- Secret scanning
- Dependency and container scanning
- Prompt-injection tests
- Backup restoration test
- Kill-switch test
- Incident response procedure
- Data-processing and retention register
- Founder approval

## 15. Incident handling

The system must support:

- Immediate disablement of agents and integrations
- Credential revocation
- Engagement quarantine
- Preservation of audit evidence
- Impact assessment
- Client-notification decision support
- Corrective action and regression tests

Agents may assist with incident analysis but may not conceal, minimise or unilaterally close a material incident.
