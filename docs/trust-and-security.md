---
title: "Trust & Security"
description: "How Offload Security protects the platform itself: tenant isolation, platform-admin controls, a tamper-evident audit trail, credential and secret handling, API and web security, AI data handling, usage analytics, data residency, retention and responsible disclosure."
sidebar_label: "Trust & Security"
sidebar_position: 12
---

# Trust & Security

How Offload Security protects the platform itself — the questions security reviewers and procurement teams ask, answered in one place. For deeper due-diligence material (detailed architecture, data-flow diagrams, assessment reports), contact us for the NDA trust pack.

## Tenant isolation

Every record on the platform is scoped to your **team**. All queries filter on that scope server-side — API keys and user sessions both resolve to a team before any data is read. Role-based access control ([Roles, Teams & API Keys](./authentication/rbac-team-management.md)) governs what members of a team can see and do. The user list (`GET /api/auth/users`) is scoped to the caller's own teams.

## Platform-admin controls

Since 1.4.1 the deployment's **platform admin** has a set of pages that team admins do not see: **User Activity**, **Teams & Users**, **Audit Log**, **System Health**, **Access Review**, **Security Policy** and **Client Menu Visibility**. The first account on the deployment is a platform admin; someone invited as **Admin** is an admin of the organization, not a platform admin.

- **More than one platform admin.** A platform admin can grant, revoke and hand over the role. The platform always keeps at least one active platform admin and at least one who can sign in with a local password, so someone can get in if SSO is down (break-glass). A revoke that would break either rule is refused.
- **Step-up re-authentication.** Sensitive actions (granting or revoking platform admin, deactivating a user, password and MFA resets, signing a user out everywhere, unlocking, enforcing MFA, team and role changes on Teams & Users, and Security Policy changes) ask for the admin's password again, plus the authenticator code when MFA is on. The confirmation lasts 15 minutes by default (`STEP_UP_WINDOW_MINUTES`, at most 60). Accounts that sign in only through SSO cannot re-authenticate for these actions yet.
- **Account controls.** Reset a user's MFA, enforce MFA for the whole deployment, sign a user out everywhere, unlock a locked account, and deactivate an account (sessions ended, API keys revoked; no hard delete).
- **Security Policy.** Password length, sign-in lockout and session settings are stored in the database and can only be made stricter than the built-in floor (or a stricter floor the operator sets in `.env`). An optional **admin IP allowlist** restricts every platform-admin power to listed addresses or CIDR ranges. Behind nginx it needs `TRUSTED_PROXIES`; `ADMIN_IP_ALLOWLIST_ENFORCE=false` is the operator's break-glass if the list locks every admin out.
- **Access Review.** Export every user's entitlements (CSV or JSON, each export audited), record a signed-off review against a hashed snapshot, and optionally deactivate dormant accounts daily (off by default, at least 30 days).
- **Scanner image overrides** can be set only by a platform admin, must stay in the tool's own repository and be pinned by digest, and are re-checked when a scan runs.

## Audit trail

The platform [audit trail](./authentication/audit-trail.md) records every authenticated change (POST, PUT, PATCH, DELETE) and every report download or export, with actor, team, IP address, action and outcome; request bodies are summarized with sensitive fields redacted, and the bodies of sign-in, registration, MFA and SSO requests are never logged. Since 1.4.0 the trail is **tamper-evident**: each entry is appended to a per-team hash chain (HMAC-SHA256 over the entry and the previous hash), and writes are retried rather than dropped. The platform admin's **Audit Log** page shows the API trail and the separate authentication-event chain, with filters, CSV export and a **verify** action that reports whether the chain is intact, broken or truncated and which signing key it was checked with. Two admin-only endpoints, also reachable with an API key that holds the `admin:audit` scope, serve it to your own tooling:

| Action | Endpoint |
| --- | --- |
| Check the chain and report the first broken link | `GET /api/audit-trail/verify` |
| Pull entries for a SIEM (cursor by sequence; JSON lines or CEF) | `GET /api/audit-trail/export/siem` |

CORS preflight requests are not written to the trail. Splunk (HTTP Event Collector) and syslog / CEF integrations can also forward the trail. Because the chain must stay verifiable, audit-trail entries are no longer deleted by a time-to-live; the operator can additionally write the chain head to an external witness (`AUDIT_HEAD_WITNESS_DIR`, `AUDIT_HEAD_WITNESS_SYSLOG`).

## Credentials & secrets handling

Cloud credentials, registry credentials, integration tokens and Knowledge Base provider keys you store on the platform are **encrypted at rest** with authenticated symmetric encryption (Fernet: AES-128-CBC with HMAC-SHA256) under keys that live in the deployment's secret store or environment (`CLOUD_ENCRYPTION_KEY` for cloud credentials, `INTEGRATION_ENCRYPTION_KEY` for integration credentials) — generated by the setup wizard, never in application code. Secrets are decrypted only at the moment of use (when a scan authenticates to your cloud account, when an alert is posted to your webhook) and are never returned by the API once saved. User passwords are hashed (PBKDF2-SHA256, 600,000 iterations, per-user salt); session tokens, API keys and invitation tokens are stored only as SHA-256 hashes.

For scanning, the platform asks only for **read-only roles** wherever the provider supports it — see [cloud permissions](./cloud-security/permissions.md) for the exact policies per cloud.

## API security

- **Authentication** — 24-hour user sessions (at most five per user by default; the platform admin can tighten both on **Security Policy**, and can sign a user out everywhere), optional TOTP MFA with deployment-wide enforcement, OIDC single sign-on, and scoped **API keys** for automation with expiry, IP allowlists, per-key rate limits and rotation. See [Platform Security](./authentication/index.md) and [API & Automation](./api-automation/index.md).
- **Rate limiting** — the public API enforces per-client rate limits (IPv6 clients are counted per /64) and each API key's own per-minute limit, and returns standard `X-RateLimit-*` and `Retry-After` headers with `429` responses when exceeded.
- **Response headers** — the web app and API send `Strict-Transport-Security`, a `Content-Security-Policy` with no inline scripts, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy` and `Cross-Origin-Resource-Policy: same-origin`. The deprecated `X-XSS-Protection` header is not sent, and nginx does not reveal its version.
- **Signed webhooks** — outbound [webhook deliveries](./integrations/webhooks.md) are signed with **HMAC-SHA256** so your receivers can verify authenticity, with retries and a delivery log. Webhook destinations are validated to block private, internal, and cloud-metadata addresses.

## How AI features handle your data

The platform's AI features (summaries, remediation suggestions, questionnaire auto-fill, the assistant) are designed so that AI is a consumer of your data under the same controls as everything else:

- **Scoped retrieval.** AI answers are generated from data your team already has access to — the same tenant scoping applies to AI context as to API queries.
- **What the model receives.** Depending on the feature: finding and asset details, scan summaries and compliance status for the page you are on, code snippets around a code finding (explanations, fix suggestions, and the fix agent when enabled), and the text of documents you upload to the Knowledge Base (questionnaire answers and policy Q&A). Page context is validated and passed to the model as delimited data, not instructions.
- **Configurable model providers.** AI calls route through a central provider layer to Anthropic, OpenAI or Google. A team can configure its own provider and key; otherwise the deployment-wide key the operator set is used. With neither, AI features are off and everything else works.
- **A cache that never crosses tenants.** Frequently asked *generic platform questions* are answered from a curated knowledge cache without any model call. Only tenant-neutral content is ever cached — answers derived from your data are not stored in the shared cache.
- **No training on your data.** Your data is sent to model providers only to serve the specific request, under API terms that do not use it for model training.
- **AI is advisory.** Suggestions (remediation guidance, auto-fill drafts) are drafts for human review — they never change your configuration or accept a risk on their own. The agentic fix feature, which can open a pull request with a code change, is off by default (`AGENTIC_FIX_ENABLED`), must also be switched on per team, and never merges.

## Usage analytics

The web app loads the PostHog analytics library with a project key built into the image, and sends product usage analytics from each user's browser to PostHog's US cloud (`us.i.posthog.com`; the library itself loads from `us-assets.i.posthog.com`). The events are what PostHog's default settings capture, such as page views and clicks. The app does not identify users to PostHog. This applies to on-premises installs too, and in this release there is no setting to turn it off. The platform's Content Security Policy allows these hosts. To stop it, block those hosts at your network egress or browser proxy. The backend does not send usage analytics to PostHog.

## Deployment options & data residency

- **SaaS** — the managed platform.
- **On-premises / private deployment** — the full platform inside your own environment, where **scan data, findings, evidence and reports are stored on your infrastructure**. Data that does go out, each item optional or blockable: browser usage analytics (see [Usage analytics](#usage-analytics)), prompts to the LLM provider when AI features are enabled, leaked secrets sent to their own issuer for live validation (on by default; `SECRET_VALIDATION_ENABLED=false`), package and CVE identifiers for vulnerability enrichment, and whatever notification, ticketing, SIEM or backup destinations you configure. The full list, with ports, data categories and how to disable or host each one internally, is in [What needs outbound access](./on-premises/deployment.md#what-needs-outbound-access). What the platform can change in your environment is listed in [What Offload Reads, Tests and Changes](./what-offload-changes.md). This is the deployment regulated customers (banks, entities with data-localization obligations) typically choose. See [On-Premises](./on-premises/index.mdx) and [India regulatory readiness](./industries/india-regulatory-readiness.md).

## Data retention & deletion

Retention is enforced platform-wide by time-to-live indexes and a daily retention sweep. Since 1.4.1 the nightly cycle works through its summarize and archive backlog in batches, records each cycle, and reports missing backups. The defaults (unchanged since 1.4.0; each is an environment variable the operator can change):

| Data | Default | Variable |
| --- | --- | --- |
| Scans, scan runs, container scans | 730 days (24 months) | `SCAN_RETENTION_DAYS`, `SCAN_RUN_RETENTION_DAYS`, `CONTAINER_SCAN_RETENTION_DAYS` |
| Cloud and Kubernetes findings | 730 days | `FINDING_RETENTION_DAYS` |
| Native web / API / network scan records | 365 days | `NATIVE_SCAN_RETENTION_DAYS` |
| Generated reports | 180 days | `REPORT_RETENTION_DAYS` |
| Alerts | 90 days | `ALERT_RETENTION_DAYS` |
| Compliance records (frozen Kubernetes compliance reports, drift reports, control-state history) | 1,825 days (5 years) | `COMPLIANCE_RETENTION_DAYS`, `COMPLIANCE_DRIFT_TTL_DAYS`, `COMPLIANCE_AUDIT_LOG_RETENTION_DAYS` |
| Compliance evidence | 7 years | `EVIDENCE_RETENTION_YEARS` |
| Platform audit trail | Not deleted automatically (hash-chained) | — |

Regulated records keep the periods their regulation requires (for example, [DPDP audit records](./compliance/dpdp-privacy.md), never less than 365 days). A deleted native scan is kept as a tombstone (who, when, why) until its grace period ends, then purged with its raw artifacts. Deleting a team or account cascades through the platform's data stores rather than orphaning records. On request, customer data is deleted at contract end.

:::note[Upgrading from an older `.env`]
An `.env` copied from an earlier `.env.example` pins the older, shorter windows (90 / 180 / 365 days). Raise or delete those lines to get the current defaults.
:::

## Secure development

The platform is built with the same controls it sells: static analysis, dependency and secret scanning, container image scanning, and CI/CD release gates run on the platform's own codebase, and findings are triaged through the same workflow customers use.

## Responsible disclosure

If you believe you've found a security vulnerability in Offload Security, email **security@offloadsecurity.com**. We acknowledge reports promptly, keep you informed through remediation, and credit reporters who wish to be named. Please don't test against other customers' data — on request we can provide a test tenant.

:::note[Certifications]
Formal third-party certifications for the platform are in progress. Ask us for the current status and available attestation documents as part of your vendor review.
:::

## Related

- [Platform Security](./authentication/index.md)
- [API & Automation](./api-automation/index.md)
- [On-Premises deployment](./on-premises/index.mdx)
- [DPDP Act (India) Privacy](./compliance/dpdp-privacy.md)
