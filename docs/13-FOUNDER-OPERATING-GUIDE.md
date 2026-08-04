# 13 — Founder Operating Guide

## 1. Your role

You are the Founder, product owner and final accountable decision-maker. You are not expected to write or review code.

Your recurring responsibilities are:

- State the business outcome or problem
- Approve phase progression
- Create accounts and subscriptions
- Enter credentials securely
- Complete MFA and OAuth
- Review demonstrations and deliverables
- Decide material product, commercial and risk questions
- Approve external communications and production releases

## 2. What Codex should do for you

Codex should:

- Inspect and prepare the development environment
- Write code and documentation
- Install approved local dependencies
- Run tests
- Open draft pull requests
- Produce screenshots and demonstrations
- Explain failures and decisions in plain English
- Stop when your approval or credentials are required

You should not be asked to run terminal commands unless no safe alternative exists.

## 3. How to start a phase

1. Open the Codex macOS application.
2. Connect or open `rayrayxing/offdata-os`.
3. Paste the relevant prompt from `14-CODEX-KICKOFF.md`.
4. Let Codex inspect the repository and propose its plan.
5. Confirm it is working only on the approved phase.
6. Complete credentials or OAuth only when Codex stops and explains the exact need.
7. Review the completion report and draft pull request.
8. Approve repair, merge or progression.

Do not paste this ChatGPT conversation as the controlling instruction. The repository is the durable specification.

## 4. Safe credential process

When a credential is needed:

1. Codex creates a named placeholder and documents the required permission scope.
2. Codex opens the approved provider screen or gives direct navigation instructions.
3. You create the key or approve OAuth.
4. You enter it directly into the local environment or approved secret manager.
5. Codex verifies access without displaying the secret.
6. Codex records only metadata such as owner, purpose and rotation date.

Never paste a key into:

- Codex chat
- ChatGPT chat
- GitHub issues
- Source code
- Documentation
- Screenshots

## 5. Safe trial and subscription process

Codex may identify trials but may not activate them.

Before you approve a trial, the completion packet should state:

- Service and plan
- Trial end date
- Payment or automatic-renewal behaviour
- Expected value
- Free alternative
- Data processed and region
- Cancellation steps
- Estimated post-trial cost

## 6. Pull-request review for a non-technical Founder

Each draft pull request should include:

- Plain-English summary
- Screenshots or demonstration
- Test results
- Costs
- Risks
- Founder decisions
- Rollback instructions

Your review questions are:

- Does it do the agreed task?
- Can I understand and operate it?
- Are all required tests passing?
- Did it create any cost or external effect?
- Can it be reversed?
- Has Codex moved beyond the approved phase?

You do not need to inspect every line of code.

## 7. When to stop Codex

Stop work if:

- Codex asks for full unrestricted access without a clear reason
- It requests credentials in chat or source code
- It begins purchasing or deploying without approval
- It proposes real client data before the security gate
- It changes the approved architecture without an option analysis
- It disables tests to make them pass
- It merges work without your approval
- It starts sending emails or external messages

## 8. Current cost posture

During foundation and local development:

- Use existing Codex access
- Use private GitHub repository
- Use local containers and databases
- Use synthetic data
- Use free CRM and service tiers only after the relevant phase

No paid infrastructure is required for Phase 0.

## 9. Initial accounts

Already available:

- GitHub account
- Codex access
- GoDaddy account and `offdata.com`

Needed later, not now:

- HubSpot Free
- OpenAI API billing with a low cap
- Managed Singapore database and storage
- Managed deployment platform
- Transactional email
- Monitoring

## 10. Acceptance testing

For each phase, you should receive a short guided script such as:

1. Open this page.
2. Click this button.
3. Confirm you see this result.
4. Enter this synthetic example.
5. Confirm the system produces this output.
6. Try the stop or rollback action.

Codex should automate technical tests and reserve your time for product and output judgement.

## 11. Escalation format

A good Codex question looks like:

> “To complete HubSpot integration, approve one of two options. Option A uses a free private app and is simpler for your single-user prototype. Option B uses OAuth and is more suitable for future external users. I recommend A for the prototype. No cost is incurred. You will need to log in and approve these scopes.”

A poor question looks like:

> “What auth architecture do you want?”

Codex must translate technical ambiguity into decision-ready choices.
