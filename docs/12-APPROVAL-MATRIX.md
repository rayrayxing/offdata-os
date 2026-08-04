# 12 — Founder Approval Matrix

## 1. Purpose

Translate the principle of operational autonomy without accountability autonomy into executable approval rules.

## 2. General rule

Agents may prepare any permitted internal analysis. They may execute only actions allowed by their decision class and current policy.

## 3. Approval matrix

| Action | Default class | Agent may prepare | Agent may execute | Founder approval |
|---|---:|---:|---:|---:|
| Draft internal mandate | D1 | Yes | Yes | No |
| Create synthetic fixture | D1 | Yes | Yes | No |
| Search approved public sources | D1 | Yes | Yes | No |
| Run local tests | D1 | Yes | Yes | No |
| Create local branch and commits | D1 | Yes | Yes | No |
| Open draft pull request | D1 | Yes | Yes | No |
| Add a free dependency | D2 | Yes | Yes with notice | Notify |
| Change a material architecture decision | D2 | Yes | No | Yes |
| Accept a material evidence gap | D2 | Yes | No | Yes |
| Waive a medium defect | D2 | Yes | No | Yes or delegated policy |
| Waive a high or critical defect | D3/D4 | Yes | No | High: explicit Founder; Critical: normally prohibited |
| Create a billable cloud resource | D3 | Yes | No | Yes |
| Start a paid trial | D3 | Yes | No | Yes |
| Enter API credentials | D3 | No value handling | No | Founder enters securely |
| Approve OAuth consent | D3 | Prepare setup | No | Founder |
| Change DNS or domain settings | D3 | Prepare exact records | No | Founder |
| Deploy synthetic staging | D2/D3 | Yes | Only after approved plan | Yes before first deployment |
| Deploy real client data | D3 | Yes | No | Yes after security gate |
| Send prospect outreach | D3 | Yes | No initially | Yes |
| Send client deliverable | D3 | Yes | No | Yes |
| Make pricing or scope commitment | D3 | Yes | No | Yes |
| Publish methodology release | D3 | Yes | No | Yes |
| Give specialist regulated opinion | D4 | Assist qualified reviewer | No | Qualified authority required |
| Bypass access controls or suppression | D4 | No | No | Prohibited |
| Copy proprietary or confidential material | D4 | No | No | Prohibited |

## 4. Approval packet schema

```yaml
approval_request:
  id:
  engagement_id:
  requested_action:
  decision_class:
  why_now:
  recommended_option:
  alternatives:
  evidence:
  risks:
  cost:
  timing:
  reversibility:
  conditions:
  expiry:
  preview_of_external_effect:
  rollback_or_compensation:
```

## 5. Standing approvals

The Founder may later create standing policies for narrowly defined actions, such as:

- Approved model spend below a threshold
- Approved public-source monitoring
- Approved synthetic staging deployments
- Approved CRM field synchronisation
- Approved campaign follow-ups within a reviewed sequence

Standing approvals require:

- Scope
- Conditions
- Limits
- Start and expiry date
- Audit requirements
- Revocation mechanism

## 6. Emergency stop

The Founder must be able to:

- Stop all agents
- Stop one engagement
- Disable external sending
- Disable one integration
- Revoke model access
- Quarantine an engagement
- Roll back a release where supported

Emergency stop actions must take precedence over queued or scheduled work.

## 7. Approval usability

Founder decisions must be presented in plain English. Avoid asking the Founder to inspect code or logs. Include technical detail only as supporting evidence or an expandable appendix.
