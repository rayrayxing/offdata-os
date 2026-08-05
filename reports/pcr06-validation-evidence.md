# PCR-06 Validation Evidence

Date: 2026-08-05

## Scope

PCR-06 governs Hermes Agent adoption compatibility without installing or activating the runtime. It covers the assessed upstream release pin, skills and procedural-memory controls, worker-harness mapping, tool and gateway restrictions, memory boundaries, deterministic generation, schema validation, mutation rejection and regression compatibility with PCR-04 and PCR-05.

## Upstream assessment

- Repository: `NousResearch/hermes-agent`
- Assessed release: `v0.18.2`
- Assessed tag: `v2026.7.7.2`
- Assessed commit: `9de9c25`
- Assessment date: 2026-08-05
- Update policy: pinned review required

## Contract evidence

- Compatibility surfaces: 4
- Capability mappings: 5
- Repository skills expected: 11
- Controlled mutations: 16
- PCR-05 adapter: `hermes-worker-harness`
- Worker mode: foreground, concurrency 1, isolated branch
- Canonical writes: commands only
- Hermes memory canonical: false
- Runtime activation authorised: false
- Hermes activation authorised: false

## Boundaries

No installation, production use, provider gateway, OAuth, messaging channel, background delegation, autonomous skill write, autonomous memory write, `/yolo`, real client data, external action or autonomous merge is authorised.

## Final evidence

Exact branch head, pull-request merge reference, workflow runs, jobs, test counts, coverage and retained artifacts will be recorded after the complete exact-head gates pass.
