# 17 — Third-Party Tool and Skill Registry

## 1. Purpose

Prevent tool accumulation, unmanaged hooks, hidden data exposure and unnecessary subscription cost. Every external agent harness, framework, skill, connector, model provider or SaaS service must be registered before installation or production use.

## 2. Status definitions

- `approved-foundation` — approved for the current build foundation.
- `approved-later` — approved in principle but deferred until its dependency phase.
- `trial` — may be tested with synthetic data under bounded permissions.
- `watch` — monitor; do not install yet.
- `rejected` — not justified or incompatible.
- `retired` — previously used but removed.

## 3. Adoption rules

Every candidate must record:

- Purpose and architectural layer.
- Version or commit.
- Licence and attribution requirements.
- Installation scope: project, user, local service or cloud.
- Scripts, hooks and permissions.
- Data exposed and residency implications.
- Credentials required.
- Expected benefit and benchmark.
- Acceptance tests and rollback.
- Cost, trial and cancellation route.
- Review owner and review date.

Project-scoped installation is preferred. Global installation requires a clear reason. Unreviewed hooks and skills must not be trusted automatically.

## 4. Current registry decisions

| Tool | Role | Status | Initial decision |
|---|---|---|---|
| GitHub | Canonical code, issues, pull requests and CI | approved-foundation | Controlling engineering repository |
| Codex | Primary engineering agent and macOS build operator | approved-foundation | Execute phase-gated implementation and tests |
| Pydantic | Typed records and validation | approved-foundation | Used by `offdata-core` and future APIs |
| Playwright | Browser and visual regression | approved-foundation | Scaffold in Phase 0; expand in deliverable phase |
| Promptfoo | Prompt, agent and red-team evaluations | approved-foundation | Scaffold early; populate from Phase 4 |
| Agent Skills format | Portable method and capability packaging | approved-foundation | Use for domain capability packs |
| PostgreSQL | Canonical relational state | approved-foundation | Local in Phase 0; managed Singapore later |
| S3-compatible storage | Source and artefact object storage | approved-foundation | Local emulator first |
| FastAPI | Python service API | approved-foundation | Phase 0 backend shell |
| Next.js | Founder cockpit and web interface | approved-foundation | Phase 0 frontend shell |
| Restate | Durable workflow execution | approved-later | Primary Phase 3 candidate; benchmark before commitment |
| LangGraph | Explicit graph-oriented alternative | watch | Retain as alternative if graph complexity demands it |
| Pydantic AI | Typed agent framework | approved-later | Phase 4 candidate after deterministic kernel |
| OpenTelemetry | Vendor-neutral traces and metrics | approved-later | Add foundational instrumentation during integration |
| Langfuse | LLM traces, prompts and evaluations | trial | Compare with lower-cost alternatives before production |
| HubSpot Free | CRM and relationship continuity | approved-later | Phase 8; no paid tier initially |
| OpenClaw | Agent gateway and operator shell | trial | Synthetic-data trial after engagement kernel works |
| Hermes Agent | Persistent personal Partner agent | watch | Introduce only if it materially improves Partner workflow |
| Buzz.xyz | Human-agent collaboration workspace | watch | Young platform; pilot separately, never canonical truth |
| Conductor.build | Coding-agent supervision workspace | trial | Compare with Codex app using synthetic data only |
| Reasonix | Lower-cost coding worker | watch | Benchmark only after deterministic tests exist |
| Pi | Lightweight embeddable coding worker | watch | Potential bounded worker, not control plane |
| Claude Code | Alternative engineering and document worker | watch | Add only through task benchmarks |
| Super Simple Software Factory | Deterministic software-factory reference | watch | Adopt design principles; do not stamp implementation yet |
| Impeccable | Frontend design guidance and deterministic UI checks | approved-later | Install project-scoped after frontend shell exists |
| Taste Skill | Brand and visual exploration | trial | Use only in isolated design workflow; avoid conflicting governance |
| Figma MCP | Editable design and infographic canvas | approved-later | Add when design system and visual grammar are ready |
| Supabase | Managed Singapore PostgreSQL/auth/storage candidate | trial | Free synthetic staging, Pro before real client data |
| Vercel | Web deployment candidate | trial | Use trial for staging; commercial plan before client use |
| n8n | Deterministic integration automation | watch | Use only for bounded integration tasks, not consulting judgement |

## 5. Required benchmark template

```yaml
tool:
version_or_commit:
problem_being_solved:
existing_alternative:
installation_scope:
permissions:
data_exposure:
residency:
secrets:
licence:
cost:
trial_end:
benchmark_tasks:
acceptance_thresholds:
security_tests:
rollback:
owner:
decision:
review_date:
```

## 6. Current principle

The minimum initial stack remains GitHub, Codex, deterministic Python, Next.js, FastAPI, PostgreSQL, local object storage, Playwright, Promptfoo scaffolding and portable Agent Skills. New products must solve an observed problem rather than a hypothetical preference.
