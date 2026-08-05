# Security and regionalisation control pack

This directory is the governed chat-first security, privacy and regionalisation package for offdata.

It defines policy and evidence requirements. It does not represent an operating production security stack and does not authorise real client data.

## Governing records

- `data-classification.yaml` — four handling classes and their minimum controls.
- `regional-cells.yaml` — Singapore-first cell definitions and the future regional-cell template.
- `retention-policies.yaml` — configurable retention, archival, export, hold and deletion defaults.
- `provider-processor-register.yaml` — the governed register schema and current empty approval state.
- `provider-processor-fixtures.yaml` — synthetic records used only for deterministic tests.
- `threat-model.yaml` — twenty threat and abuse cases.
- `security-control-catalogue.yaml` — mandatory and supporting controls with required evidence.
- `security-test-catalogue.yaml` — chat-first, integration, recovery, security and Founder-acceptance tests.
- `incident-playbooks.yaml` — containment, assessment, Founder-decision and closure-evidence requirements.
- `security-regionalisation-baseline.json` — deterministic generated baseline; do not edit manually.

## Non-negotiable boundary

`configs/security-regionalisation.yaml` keeps `real_client_data_enabled: false`.

Real client data may be enabled only after the exact production cell has current passing evidence for every mandatory control and an explicit Founder approval record. Chat-first policy tests cannot substitute for infrastructure, recovery, encryption, region-isolation or Founder-acceptance evidence.
