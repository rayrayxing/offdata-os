# 45 — PCR-06 Hermes Adoption and Compatibility Pack

## Status

PCR-06 is complete as a chat-first compatibility contract. It does not install or activate Hermes Agent. The assessed upstream baseline is Hermes Agent `v0.18.2` (`v2026.7.7.2`, commit `9de9c25`) as reviewed on 2026-08-05.

## Adoption decision

Hermes is accepted only as a future bounded worker-harness candidate behind the PCR-05 `WorkerPackage` and `WorkerResult` contracts. `runtime_activation_authorized=false` and `hermes_activation_authorized=false` remain binding.

The compatibility pack governs four surfaces:

1. skills and external skill directories;
2. worker execution and completion contracts;
3. tools, MCP and provider gateways;
4. memory, curator and background review.

## Skills

Offdata repository skills remain canonical under `agents/*/SKILL.md`. A Hermes local skill copy is non-canonical and must be read-only or checksum-verified. Progressive disclosure and the agentskills-compatible structure are usable, but `skill_manage`, `/learn`, curator and background review may not write canonical skills without Founder review.

Every skill remains prohibited from direct canonical writes, autonomous approval, external sending, credential collection, production deployment and real-client-data use.

## Worker compatibility

The governed Hermes worker mode is foreground, single-worker, isolated-branch execution. It consumes a PCR-05 `WorkerPackage` and returns a `WorkerResult`. Offdata acceptance tests—not Hermes self-assessment—control completion.

`background_fanout`, autonomous merge, direct canonical writes, external sends, `/yolo`, unreviewed skill writes and unreviewed memory writes are prohibited. Completion-contract and `pre_verify` concepts are compatible only through an explicit allowlist of repository validation commands.

## Tools and gateways

Hermes terminal and web extraction capabilities may only map to declared PCR-05 tool classes and workspace/network scopes. MCP, provider tool gateways, browser automation, OAuth, messaging channels and credential-bearing integrations remain denied until separate processor, security, paid-service and Founder approvals are complete.

## Memory boundary

Hermes memory is not compatible with canonical offdata state. Session memory may be ephemeral for synthetic work, but curator, journey persistence, autonomous memory writes and client-data retention remain disabled. The offdata command/event model remains the only canonical state path.

## Activation conditions

All conditions are mandatory before any Hermes sandbox activation:

- PCR-03, PCR-04, PCR-05 and PCR-06 merged through their governed sequence;
- issue #19 hosted controls verified;
- explicit Founder Phase 0 approval;
- clean macOS environment;
- pinned Hermes version and checksum verified;
- isolated synthetic-data sandbox conformance passed.

No paid service is required by PCR-06. Real client data, production deployment, external actions, provider gateways, OAuth and autonomous merge remain prohibited.

## Validation

Run from repository root:

```bash
python scripts/build_pcr06_hermes_compatibility.py
python scripts/validate_pcr06_hermes_compatibility.py
python scripts/validate_pcr05_runtime_adapters.py
python scripts/validate_pcr04_codex_handoff.py
```

The validator checks schema validity, deterministic generation, PCR-05 adapter compatibility, PCR-04 start denial, repository skill presence, exact activation blockers and sixteen controlled mutations.
