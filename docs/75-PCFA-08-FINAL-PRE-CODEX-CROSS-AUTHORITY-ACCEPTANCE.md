# PCFA-08 — Final pre-Codex cross-authority acceptance

## Purpose

PCFA-08 is the final repository-side chat-first acceptance package before the manual Codex Phase 0 launch gates. It reconciles the current operational projection with PCFA-01 through PCFA-07, the permanent WS6 release, the existing IMP backlog, the launch permit semantics, current issue bodies and the remaining hosted/manual evidence requirements.

PCFA-08 does **not** create `codex/phase-0-foundation`, issue a permit, authorize implementation, merge any pull request or claim manual evidence that has not been produced.

Canonical machine authority: `repository/pcfa08-final-pre-codex-cross-authority-acceptance.json`.

## Repository-side acceptance

PCFA-08 accepts **18** cross-authority invariants. The resulting repository-side conclusion is:

- PCFA-01 launch-SHA semantics remain repaired;
- PCFA-02 remains the sole live readiness projection;
- PCFA-03 requires private/internal development with no public licence grant;
- PCFA-04 product-scope requirements remain planned, not implemented;
- PCFA-05 MVCL obligations and Founder interrupts remain mandatory and planned;
- PCFA-06 Hermes remains bounded and inactive;
- PCFA-07 remains exactly **93 obligations / 93 planned tests** with zero IMP-P0 widening;
- the Codex launch target remains exactly P0.1–P0.4;
- a valid local single-use permit remains mandatory before implementation;
- all implementation/runtime/distribution/external-action boundaries remain false.

## Manual launch gates remain pending

Repository-side cross-authority acceptance does not satisfy the eight remaining launch gates:

1. live repository visibility is private;
2. GitHub hosted controls are verified;
3. historical/corrective branch cleanup is complete;
4. clean supported macOS evidence is complete;
5. live Issue #1 and Issue #19 bodies are synchronized after integration;
6. the Founder explicitly approves exactly P0.1–P0.4;
7. all evidence binds one exact then-current `main` SHA;
8. the real launch verifier issues the local single-use permit.

Until all eight pass, `codex_start_authorized=false`.

## Exact branch-cleanup acceptance

PCFA-08 records an exact post-integration cleanup allowlist of **65** non-`main` branches: the 64 non-`main` refs observed before the PCFA-08 branch was created, plus `pcfa/08-final-pre-codex-cross-authority-acceptance` itself.

Cleanup rules are fail-closed:

- delete exact branch names only; no wildcard or prefix deletion;
- preserve each branch's final **40-hex SHA** before deleting the ref;
- classify each deleted branch as merged, obsolete or superseded with the required ancestry/disposition evidence;
- do not include `main` in the deletion set;
- `codex/phase-0-foundation` must still be absent;
- the hosted-controls attestation must contain one `deleted_branches` evidence item for every one of the 65 governed cleanup refs;
- the launch verifier independently queries GitHub and requires the live branch inventory to contain **only `main`** immediately before Codex branch creation.

Any unexpected branch requires explicit reconciliation before permit issuance.

## Integration boundary

PCFA-08 is intentionally stacked on PCFA-07. The PCFA chain must be integrated in dependency order with explicit Founder merge approval for each material merge. Only after PCFA-08 is integrated should the live Issue #1 and Issue #19 bodies be synchronized and the hosted/manual launch evidence be completed.

A successful PCFA-08 PR proves the repository is internally ready for those manual gates. It does not itself make the live GitHub repository private, delete branches, validate the Founder's macOS environment, bind the final `main` SHA or issue a launch permit.
