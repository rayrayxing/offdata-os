# Workstream 4 Readiness Evidence

Date: 2026-08-06  
Baseline integrated `main`: `617e4fe59a9f712d75da29f88508819c0296fc84`

## Repository evidence retained

- PCR-10 exact tested merge reference: `6abc4785422e878c160aeb33065e98967c0e3b89`
- PCR-10 run/job: `31069304377` / `92513690720`
- PCR-10 artifact: `8955036460`
- PCR-10 artifact SHA-256: `9e5425bae029a7a383632767b213e3a1114fb88e44d4c634e5261bf94e322511`
- Complete release run/artifact: `31069304330` / `8955039054`
- Complete release artifact SHA-256: `64c6a71c7bbb961c689cdf89a7a9c0ed2c8a670f5c9e29f44d5f28b3306452bd`
- Canonical issue-body SHA-256: `01871803444487ef3e808f155a85cc13ac6fc2350eb11a401e6b5c14fc4a79ad`
- Runtime: 247 tests passed
- Coverage: 93.14 percent across 4,604 statements
- Referential integrity: 245 executable nodes, 99 semantic tests, 604 edges, zero unresolved references

## Action runtime maintenance

Every permanent workflow is migrated to immutable Node 24-native releases:

- `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (`v7.0.1`)
- `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97` (`v7.0.0`)
- `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` (`v7.0.1`)

The Workstream 4 validator rejects legacy pins, floating tags and unknown action SHAs.

## Pending authoritative evidence

The following are intentionally not claimed from repository evidence:

- GitHub MFA;
- branch-protection and ruleset settings;
- automatic branch deletion;
- completion of historical branch cleanup;
- clean macOS machine readiness;
- Founder environment attestation;
- explicit Founder Phase 0 approval.

These remain false in the machine contract until separate evidence is recorded. `codex_start_authorized=false`.
