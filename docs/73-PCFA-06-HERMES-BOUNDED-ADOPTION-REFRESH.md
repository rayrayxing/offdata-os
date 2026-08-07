# PCFA-06 — Hermes bounded-adoption refresh

## Purpose

PCFA-06 refreshes the earlier PCR-06 Hermes compatibility snapshot against the current public Hermes Agent documentation while preserving offdata's core authority model.

This package is **specification only**. It does not install Hermes, activate a Hermes runtime, enable providers, create credentials, widen Codex Phase 0, or implement any product capability.

The governing machine record is:

- `repository/pcfa06-hermes-bounded-adoption-refresh.json`

The governed source is:

- `configs/pcfa06-hermes-bounded-adoption-refresh.yaml`

## Upstream baseline

The stable Hermes release remains unchanged from PCR-06:

- release: `v0.18.2`
- tag: `v2026.7.7.2`
- commit: `9de9c25`
- release date: 2026-07-07
- assessment date: 2026-08-08

PCR-06 remains retained historical package evidence. PCFA-06 becomes the current offdata authority for how newly documented Hermes surfaces may or may not be adopted.

The current public Hermes documentation is assessed separately from the stable release pin. The documentation can describe features that are newer than the pinned release, so PCFA-06 records a **capability-policy snapshot**, not an assertion that every documented surface exists in `v0.18.2`.

## What changed since the PCR-06 assessment

No stable-version bump is required. The important change is that current Hermes documentation now exposes or documents a richer set of surfaces that need explicit offdata policy:

- persistent `/goal` loops with completion contracts;
- `/subgoal` additions and auto-continuation;
- background top-level `delegate_task` and configurable parallel/nested delegation;
- progressive-disclosure skills, bundles, external directories and large registry surfaces;
- `/learn`, agent-managed skill writes and skill-write approval;
- `/journey` / learning-timeline inspection and editing surfaces;
- persistent memory and background curator behaviour;
- Mixture-of-Agents model fan-out;
- programmatic `execute_code` tool calling;
- MCP, tool gateway, browser and messaging surfaces;
- cron/background sessions and optional Codex app-server runtime surfaces.

These features are potentially useful, but none of them may replace offdata's canonical state, durable workflow, policy engine, evidence model or Founder accountability.

## `/goal` is not workflow authority

Hermes `/goal` can persist an objective across turns and use a completion contract. That is useful as a **future bounded worker-loop pattern**, but raw `/goal` is not authorized.

If a later implementation phase adopts it, the mapping is fixed as follows:

| Hermes completion field | offdata authority |
| --- | --- |
| `outcome` | `WorkerPackage.expected_outputs` |
| `verification` | `WorkerPackage.acceptance` |
| `constraints` | `WorkerPackage.constraints` |
| `boundaries` | `WorkerPackage.workspace_tool_and_data_scope` |
| `stop_when` | `WorkerPackage.escalation_and_stop_conditions` |
| subgoals | additional acceptance criteria recorded by offdata |

The Hermes goal judge is advisory only. `WorkerPackage.acceptance` and offdata test evidence determine completion.

Hermes goal/session persistence is noncanonical. Restart safety must come from the offdata durable workflow checkpoint, not Hermes `SessionDB`. Turn budgets must be bounded, automatic resume after budget exhaustion is denied, and a Founder interrupt must pre-empt the loop.

## Delegation and background work

Current Hermes documentation describes top-level delegation as background execution, with three parallel children by default and optional nested orchestration.

That raw surface is not compatible with the initial offdata safety boundary because:

- child execution is tied to the Hermes process and is not itself the durable consulting workflow;
- parallel children may overlap files, tools, data or side effects;
- only final summaries return to the parent context;
- a child summary is not verified evidence;
- nested delegation can widen orchestration depth and cost.

PCFA-06 therefore keeps:

- raw `delegate_task`: denied;
- top-level background delegation: denied;
- nested delegation: denied;
- parallel fan-out: denied;
- initial adapter concurrency: `1`;
- direct canonical writes: denied;
- offdata verification after child work: required.

A later adapter may use Hermes as a replaceable bounded worker only after PCFA-07 maps the exact obligations and an implementation phase supplies durability, isolation, idempotency, permissions, cost limits and tests.

## Skills, `/learn`, `/journey` and curator

The repository remains the canonical home for offdata skills: `agents/*/SKILL.md`.

Hermes skill mechanisms are treated as follows:

- bundled Hermes skills: candidate-only;
- Skills Hub or third-party skills: quarantined candidate-only;
- skill bundles: candidate task profiles only;
- `/learn`: suggestion-only candidate drafting;
- `skill_manage`: noncanonical staging with review;
- `/journey`: read-only observability only;
- `/journey edit` and `/journey delete`: not governance actions;
- curator: disabled;
- automatic skill promotion: denied;
- automatic methodology promotion: denied.

A Hermes-generated procedure can become an offdata skill only through independent review, provenance checking, tests and the normal Founder-controlled promotion path.

## Memory remains noncanonical

Hermes persistent memory may be useful for local convenience context, but it cannot hold canonical engagement truth, approvals, evidence decisions or methodology authority.

Client truth belongs in the offdata system of record. Cross-engagement memory is prohibited. Any later use must respect data classification, retention, isolation and audit requirements. Real client data remains disabled.

## Mixture-of-Agents

Mixture-of-Agents is a potentially useful model-routing pattern, but it remains a candidate behind the offdata model router.

Required future controls include:

- offdata owns model/provider selection;
- explicit provider allowlists;
- explicit cost budgets before fan-out;
- evaluation thresholds before activation;
- reference-model outputs are advisory inputs;
- the acting aggregator must still satisfy offdata typed contracts and evidence rules;
- MoA does **not** count by itself as independent quality review.

The offdata independent-QA requirement still requires a sufficiently separate run, context, rubric or model configuration and cannot be discharged merely because several reference models participated in one MoA call.

## External tools and runtime surfaces

The following remain denied or deferred pending their own tool, processor, credential, data, durability and external-action reviews:

- MCP servers;
- Nous/tool gateway;
- unrestricted browser or terminal access;
- external skill registries without quarantine/review;
- messaging channels;
- scheduled external actions;
- background sessions as workflow authority;
- optional Hermes Codex app-server runtime;
- provider or OAuth activation.

`execute_code` is only a future bounded tool candidate. Deterministic calculations and transformations remain governed offdata services, and any Hermes execution would require declared inputs, sandboxing, reproducibility and captured outputs.

## Existing IMP ownership only

PCFA-06 creates no new implementation phase and adds no product scope to `IMP-P0`.

The 11 capability assessments map only to existing `IMP-P1` through `IMP-P11` tasks. Every capability is `planned_not_implemented`.

The launch target therefore remains exactly:

- `P0.1`
- `P0.2`
- `P0.3`
- `P0.4`

No Hermes installation or activation is part of Codex Phase 0.

## PCFA-07 handoff

PCFA-07 must reconcile every PCFA-06 capability to:

- requirement IDs;
- existing IMP task ownership;
- planned test IDs;
- evidence type;
- phase gate;
- dependencies;
- `planned_not_implemented` status;
- preserved upstream-evidence classification.

PCFA-08 remains the final cross-authority acceptance package after that reconciliation.

## Fail-closed boundaries

PCFA-06 leaves all of the following false:

- implementation authorization;
- Hermes installation authorization;
- runtime activation;
- Hermes activation;
- background execution;
- model fan-out;
- autonomous skill promotion;
- autonomous memory authority;
- external actions;
- real client data;
- paid services;
- OAuth;
- production deployment;
- autonomous merge;
- `codex_start_authorized`.

Machine boundary: `codex_start_authorized=false`.

Founder accountability remains preserved.

## Validation

The package is validated by:

```text
python scripts/validate_pcfa06_hermes_refresh.py
python scripts/validate_pcr06_hermes_compatibility.py
python scripts/validate_pcr05_runtime_adapters.py
python scripts/prepare_codex_phase0_launch.py --self-test
bash scripts/run_ws62_ci.sh
```

PCFA-06 is complete only when those checks and the full inherited GitHub workflow matrix pass on the exact candidate head/merge reference.
