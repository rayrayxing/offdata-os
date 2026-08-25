# DeepSeek Harness Builder Lane

DeepSeek Harness is treated as a **replaceable builder**, not canonical venture/task lifecycle authority.

## V1

Hermes profile `builder-deepseek` receives a BuildContract and runs a pinned DeepSeek Harness subprocess/worktree. Capture exact Harness version/SHA, repo/base SHA, workspace, commands, files changed, tests and artifacts. Post result/receipts back to Hermes Kanban. DeepSeek cannot mark independent certification PASS.

BuildContract: repo, base SHA, worktree, requirements, non-goals, architecture/security constraints, acceptance tests, runtime/retry budget.

## Future native lane

If V1 proves useful, implement a Hermes external CLI worker-lane adapter against the current pinned Hermes worker-lane lifecycle. Hermes remains canonical claim/review/completion state.

Harness is developer preview: pin it and do not auto-track head.