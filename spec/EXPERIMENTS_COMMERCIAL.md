# Experiments, Customer Validation and Commercialization

## ExperimentContract

Required:
- venture/concept revision;
- principal uncertainty;
- hypothesis;
- target user/buyer;
- method/intervention/prototype;
- success and failure signals;
- stopping rule;
- budget and deadline;
- required evidence and attribution;
- disclosure level;
- authority scope;
- deterministic analysis method where applicable.

Optimize **information gained / dollars / time**.

Methods may include interview, workflow observation, outbound-response test, fake door, landing page, concierge, Wizard-of-Oz, prototype, LOI, preorder, paid pilot and real usage.

## Prototype Authorization

Separate pre-G3 decision: `AUTHORIZED | MORE_RESEARCH_REQUIRED | NOT_AUTHORIZED`.

Question: is expected information/commercial learning value greater than cost/opportunity cost? A MATERIAL_EXPERIMENT concern often supports authorization rather than blocking it.

## Prototype acceptance

The prototype must test the principal uncertainty and show the critical workflow/outcome sufficiently to elicit meaningful external reaction. Preserve simulation/limitations. Decorative static HTML is insufficient when interaction is the experiment.

Generated prototypes are untrusted code: separate origin or sandboxed iframe, restrictive CSP/network, no Venture Brain secrets, no parent DOM/storage, narrow bridge.

## Customer stack

Recommended initial integrations:
- business domain + Google Workspace;
- HubSpot or equivalent CRM;
- Apollo **or** Clay initially for prospect/contact enrichment;
- email verification;
- Google Calendar/Meet;
- PostHog;
- Tally/PostHog Surveys/Typeform;
- Stripe;
- Vercel/Cloudflare/equivalent hosting.

Start outbound `DRAFT_ONLY`.

## Contact guard

Before SEND verify opt-out, bounce/reputation, frequency, prior promises, sender identity, disclosure, target/venture and explicit authority.

## Revenue loop

`Interest → problem validation → price → commitment → paid pilot/transaction → delivery → repeat/retention → unit economics`.

Pageviews, likes and internal enthusiasm are not revenue.