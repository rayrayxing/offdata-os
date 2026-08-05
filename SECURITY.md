# Security Policy

## Current security boundary

offdata OS is in a synthetic-data, pre-production build stage. Real client data is prohibited until the governed production-security evidence packet and explicit Founder approval are complete.

## Reporting a vulnerability

Do not open a public issue or pull request containing vulnerability details, credentials, private data, restricted evaluation material, or exploit steps.

Use GitHub's private vulnerability reporting or a private repository security advisory when available. If that interface is unavailable, contact the Founder through an existing private channel and provide only the minimum information needed to establish a secure reporting path.

Include:

- affected component and commit;
- impact and realistic preconditions;
- reproduction steps using synthetic data;
- suggested containment;
- whether secrets or private data may be exposed.

Do not access data beyond what is necessary to demonstrate the issue. Do not perform denial-of-service testing, social engineering, credential attacks, destructive actions, or testing against third parties.

## Supported versions

Before the first production release, only the current `main` branch and active approved pull request are supported for security fixes. Historical branches and superseded pull requests are not supported releases.

## Response and disclosure

The Founder controls severity, remediation priority, external notification, production restoration, and disclosure. Automated agents may triage, reproduce with synthetic fixtures, propose patches, and run tests, but may not autonomously disclose or close a material incident.

## Secrets and private material

Never commit or paste:

- API keys, tokens, passwords, certificates, or private keys;
- real client data or client-identifying metadata;
- original private methodology source files;
- restricted answer keys or evaluation oracles;
- provider credentials, processor contracts, or confidential incident evidence.

If a secret is committed, treat it as compromised: stop use, revoke or rotate it through the provider, remove it from active code, assess exposure, and preserve an incident record. Rewriting Git history alone is not sufficient remediation.
