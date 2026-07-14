---
title: "Trust & Security"
sidebar_label: "Trust & Security"
sidebar_position: 12
---

# Trust & Security

How Offload Security protects the platform itself — the questions security reviewers and procurement teams ask, answered in one place. For deeper due-diligence material (detailed architecture, data-flow diagrams, assessment reports), contact us for the NDA trust pack.

## Tenant isolation

Every record on the platform is scoped to your **team**. All queries filter on that scope server-side — API keys and user sessions both resolve to a team before any data is read. Role-based access control ([RBAC & team management](./authentication/rbac-team-management.md)) governs what members of a team can see and do, and an [audit trail](./authentication/audit-trail.md) records administrative and security-relevant actions.

## Credentials & secrets handling

Cloud credentials, registry credentials, integration tokens, and API keys you store on the platform are **encrypted at rest with envelope encryption**: data keys are derived from a key-encryption key held in a managed secrets service, not in application code or configuration files. Secrets are decrypted only at the moment of use (for example, when a scan authenticates to your cloud account) and are never returned by the API once saved.

For scanning, the platform asks only for **read-only roles** wherever the provider supports it — see [cloud permissions](./cloud-security/permissions.md) for the exact policies per cloud.

## API security

- **Authentication** — short-lived user sessions, plus scoped **API keys** for automation (including a CI/CD-scoped preset). See [API & Automation](./api-automation/index.md).
- **Rate limiting** — the public API enforces per-client rate limits and returns standard `X-RateLimit-*` headers with `429` responses when exceeded.
- **Signed webhooks** — outbound [webhook deliveries](./integrations/notifications.md#how-to-set-up-webhook-subscriptions) are signed with **HMAC-SHA256** so your receivers can verify authenticity, with retries and a delivery log. Webhook destinations are validated to block private, internal, and cloud-metadata addresses.

## How AI features handle your data

The platform's AI features (summaries, remediation suggestions, questionnaire auto-fill, the assistant) are designed so that AI is a consumer of your data under the same controls as everything else:

- **Scoped retrieval.** AI answers are generated from data your team already has access to — the same tenant scoping applies to AI context as to API queries.
- **Configurable model providers.** AI calls route through a central provider layer to leading LLM APIs. On-premises and enterprise deployments can configure their own provider keys, so inference happens under your own agreements.
- **A cache that never crosses tenants.** Frequently asked *generic platform questions* are answered from a curated knowledge cache without any model call. Only tenant-neutral content is ever cached — answers derived from your data are not stored in the shared cache.
- **No training on your data.** Your data is sent to model providers only to serve the specific request, under API terms that do not use it for model training.
- **AI is advisory.** Suggestions (remediation guidance, auto-fill drafts) are drafts for human review — they never change your configuration or accept a risk on their own.

## Deployment options & data residency

- **SaaS** — the managed platform.
- **On-premises / private deployment** — the full platform inside your own environment, where **scan data, findings, evidence, and reports never leave your network**. This is the deployment regulated customers (banks, entities with data-localization obligations) typically choose. See [On-Premises](./on-premises/index.md) and [India regulatory readiness](./industries/india-regulatory-readiness.md).

## Data retention & deletion

Retention is enforced platform-wide: operational data (scan results, events, alerts) ages out on schedules, audit-log retention is configurable where regulations require specific periods (for example, [DPDP audit records](./compliance/dpdp-privacy.md)), and deleting a team or account cascades through the platform's data stores rather than orphaning records. On request, customer data is deleted at contract end.

## Secure development

The platform is built with the same controls it sells: static analysis, dependency and secret scanning, container image scanning, and CI/CD release gates run on the platform's own codebase, and findings are triaged through the same workflow customers use.

## Responsible disclosure

If you believe you've found a security vulnerability in Offload Security, email **security@offloadsecurity.com**. We acknowledge reports promptly, keep you informed through remediation, and credit reporters who wish to be named. Please don't test against other customers' data — on request we can provide a test tenant.

:::note Certifications
Formal third-party certifications for the platform are in progress. Ask us for the current status and available attestation documents as part of your vendor review.
:::

## Related

- [Authentication & Access Control](./authentication/index.md)
- [API & Automation](./api-automation/index.md)
- [On-Premises deployment](./on-premises/index.md)
- [DPDP Act (India) Privacy](./compliance/dpdp-privacy.md)
