# 31 — Founder Setup and Credential Readiness

## Status

Plain-English readiness guide v1.0 for the Founder’s macOS environment.

## 1. What to do now

Only a small number of actions are useful before Codex begins integration.

### 1.1 Confirm account security

- GitHub multifactor authentication is enabled.
- The GitHub recovery method is current.
- The email account associated with offdata is protected by MFA.
- A password manager is installed and used.
- Do not store API keys in notes, email drafts or chat.

### 1.2 Install or confirm the Codex application

- Install the current Codex app for macOS.
- Sign in using the account with Codex access.
- Connect the GitHub account when prompted.
- Do not grant unrestricted access to unrelated folders.
- Use `rayrayxing/offdata-os` as the working repository.

### 1.3 Confirm Microsoft Office availability

PowerPoint, Word and Excel are strongly recommended for final rendering tests.

Record whether each is installed and opens correctly:

- Microsoft PowerPoint.
- Microsoft Word.
- Microsoft Excel.

A Microsoft 365 subscription is not required for the earliest source-code work, but it becomes highly valuable before the deliverable studio is accepted.

### 1.4 Prepare the methodology source folder

Create one local folder, for example:

`~/Documents/offdata-source-library/`

Place the original methodology and domain-pack files there unchanged. Do not rename, edit or convert them. Codex will later copy them into the controlled import process and calculate checksums.

### 1.5 Confirm available storage

Keep at least 30 GB of free disk space for:

- containers;
- databases;
- model and package caches;
- Office and browser render outputs;
- fixture datasets;
- backups.

### 1.6 Allow uninterrupted local execution

For long Codex runs:

- connect the Mac to power;
- use a stable internet connection;
- prevent automatic sleep during the approved run window;
- leave enough time to review permission prompts.

## 2. What Codex can install later

Codex can inspect the machine and install or configure the following after your approval:

- Homebrew if absent.
- Git and GitHub CLI.
- Docker Desktop or an approved container alternative.
- Python and `uv`.
- Node.js and `pnpm`.
- PostgreSQL client tools.
- local S3-compatible object storage.
- browser testing dependencies.
- PowerPoint, Word and Excel test helpers.
- code formatters, linters and test runners.
- secret and dependency scanners.

You do not need to install these manually unless you prefer to do so.

## 3. Recommended optional installation now

### Docker Desktop

This is the only development tool that may be worthwhile installing before Codex begins because it requires a normal macOS application installation and security approval.

It can also be left for Codex to guide you through. No account or paid plan should be necessary for local personal development under normal use, but the applicable licence should be reviewed before commercial team use.

### Microsoft 365

Install before the deliverable-rendering phase if it is not already available.

### Password manager

Recommended immediately if none is in use.

## 4. Accounts to create only when requested by a phase

Do not create or pay for all services now.

### Phase 0–2

No new paid cloud account is required.

### Staging phase

Codex may request:

- Supabase or another managed PostgreSQL and storage provider.
- Vercel or another application hosting provider.
- OpenAI API billing with a small spending cap.
- email and monitoring free tiers.

Use Singapore region where available.

### CRM phase

Create HubSpot Free only when the synthetic adapter and field mapping are ready. No paid HubSpot plan is required initially.

### Design phase

A Figma account may be useful when visual concepts and editable diagrams are being reviewed. It is not needed for core engineering.

### Later worker trials

OpenClaw, Hermes, Buzz, Conductor, Reasonix, Claude APIs and other providers should be created only for a defined benchmark or capability gap.

## 5. Services not to install yet

Do not install or subscribe to these before the core foundation and tests exist:

- OpenClaw.
- Hermes Agent.
- Buzz.xyz infrastructure.
- Reasonix.
- Conductor cloud workspaces.
- paid HubSpot tiers.
- paid enrichment or contact databases.
- production monitoring plans.
- multiple model-provider subscriptions.
- paid research databases.

Premature installation creates cost, permissions and integration complexity before the system can evaluate the benefit.

## 6. Credential process

When an integration is ready:

1. Codex creates the empty secret name and configuration location.
2. Codex explains in plain English why the credential is required and what permissions it needs.
3. You create the key or authorise OAuth in the provider interface.
4. You enter the value directly into the approved local or managed secret store.
5. The value is never pasted into chat, GitHub, code or documentation.
6. Codex performs a minimal connection test.
7. Codex records provider, scope, owner, rotation date and revocation method without recording the secret value.
8. You revoke unused test keys after the phase is complete.

## 7. OAuth process

For OAuth integrations:

- Codex may navigate to the consent point and prepare required settings.
- You verify the provider, requested scopes and redirect address.
- You complete sign-in, MFA and consent.
- Codex validates the connection with a non-destructive test.
- Write scopes should be deferred until read-only behaviour is proven where the provider permits it.

## 8. Spending controls

For every paid or usage-based provider:

- start on a free trial or smallest suitable plan;
- set a hard spending limit where supported;
- set alert thresholds below the limit;
- use synthetic data first;
- record the cancellation method and trial end date;
- review cost by engagement and agent;
- do not prepay annual plans before commercial demand is proven.

## 9. Data-safety rules during development

Until production readiness passes:

- use only synthetic or deliberately sanitised data;
- do not upload client documents;
- do not connect a live client mailbox or drive;
- do not provide real prospect lists;
- do not expose the local service publicly;
- do not send external email;
- do not use offdata.com DNS for a live application;
- do not record screens containing passwords or API keys.

## 10. Mac permission expectations

Codex or installed tools may request permission for:

- repository-folder access;
- terminal execution;
- Docker networking and storage;
- browser automation;
- screen recording or accessibility for Computer Use;
- Office application automation;
- notifications.

Approve only the permission required for the current phase. Avoid full-disk access unless a specific need is explained and approved.

## 11. Founder readiness checklist

Before Codex integration begins, confirm:

- [ ] GitHub MFA is enabled.
- [ ] Codex app is installed and signed in.
- [ ] `rayrayxing/offdata-os` is visible in Codex.
- [ ] A password manager is available.
- [ ] Original methodology files are collected unchanged.
- [ ] At least 30 GB disk space is free.
- [ ] PowerPoint, Word and Excel availability is known.
- [ ] No real client data will be used.
- [ ] No API keys have been pasted into GitHub or chat.
- [ ] You can review macOS permission and MFA prompts during the run.

## 12. Information Codex should report before installing anything

- tool and version;
- why it is required;
- installation source;
- expected disk and permission impact;
- whether it creates an account or cost;
- data it can access;
- rollback or uninstall method;
- safer alternatives if available.

## 13. Recommended immediate Founder action

At this stage, the only actions worth completing are:

1. Install and sign into the Codex macOS app.
2. Confirm GitHub MFA.
3. Confirm whether Microsoft 365 desktop applications are installed.
4. Gather the original methodology files unchanged in one local folder.
5. Confirm sufficient free disk space.

Everything else can wait until the relevant integration is implementation-ready.