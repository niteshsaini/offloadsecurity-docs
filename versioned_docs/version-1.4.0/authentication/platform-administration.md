---
title: "Platform Administration"
sidebar_label: "Platform Administration"
sidebar_position: 4
description: "The platform-administrator account — what makes it different from a team Admin — and what only it can do: choose which menu sections the deployment's users see, watch every account and session in User Activity, enforce MFA deployment-wide; plus Platform Setup and the deployment security settings an operator controls."
---

# Platform Administration

Each deployment of Offload Security — a SaaS tenant or an on-premises install — has one **platform administrator**: the first account created when the platform was set up. It is not a team role. A team Admin governs one team; the platform administrator governs the deployment, sees across every team, and is the break-glass account when single sign-on is enforced.

**Where:** account menu → **Platform Setup** (any Admin); left navigation → *Management* → **Client Menu Visibility**, **User Activity** (platform administrator only).

## What the platform administrator can do

| Capability | Team Admin | Platform administrator |
| --- | :-: | :-: |
| Everything inside their own teams | ✓ | ✓ |
| Read the audit trail across all teams; export all of it | — | ✓ |
| Read and verify the authentication event chain (`/api/auth/audit-log`, `?store=auth`) | — | ✓ |
| See every account, live session and login attempt; sign sessions out; issue password resets; require a password change | — | ✓ |
| Turn deployment-wide MFA enforcement on or off; reset a user's MFA (API) | — | ✓ |
| Choose which menu sections the deployment's users see | — | ✓ |
| API key scope report and migration across the deployment (API) | — | ✓ |
| Read platform metrics (`/api/platform/metrics`) when no `METRICS_TOKEN` is set | — | ✓ |
| Rerun Platform Setup (connectivity, keys, storage, platform URL, SMTP) | ✓ (Admin role) | ✓ |
| Sign in with a password while SSO is enforced | — | ✓ |
| List users of the deployment (`/api/auth/users`) | ✓ (Admin role) | ✓ |

The flag (`is_platform_admin`) is set once, on the first registration; it is not assignable from the UI. Protect this account accordingly: strong password, MFA, and a recorded owner.

## Platform Setup

![Platform Setup: Reconfigure Platform Settings — what you can reconfigure (MongoDB and Redis connectivity, cryptographic keys, object storage, platform name / URL / environment, email / SMTP); Launch Setup Wizard](/img/screenshots/platform-security/platform-setup.webp)

The setup wizard that ran on first boot can be relaunched at any time by an account with the **Admin** role. Its steps: **Welcome → Service Connectivity** (MongoDB, Redis) → **Security Keys** (generated secrets for sessions, credential encryption, webhooks) → **Storage** (object storage for evidence and reports) → **Platform Settings** (name, public URL, environment) → **Email / SMTP** → **Admin Account** (first run only) → **Complete**. Each step validates before saving — the SMTP step authenticates to the server, the storage step writes and reads a test object.

Keys the wizard generates should not stay in the platform database: copy them into the deployment's `.env` (see [Deployment security settings](#deployment-security-settings) below).

SMTP set here is the **platform** mail server: it sends invitations, password-reset links and platform notifications, and is the fallback when a team has not connected its own under [Integrations](../integrations/notifications.md#email-smtp). The deployment environment (`SMTP_HOST`) still overrides both.

## Client Menu Visibility

![Client Menu Visibility: per-section checkboxes grouped by Core Security, Cloud & Infrastructure, …; applies to every user except the platform administrator](/img/screenshots/platform-security/menu-settings.webp)

Choose which sections of the left navigation the deployment's users see. Untick a module a customer has not licensed or a team is not ready for and it disappears from the menu for everyone — except the platform administrator, who always sees the full menu. Hiding asks for confirmation; opening a hidden section by link shows *not enabled for your organisation*; the page shows who last changed the setting and when. There is one setting for the whole deployment.

:::warning[Not an access control]
This hides menus and pages only. The data stays, scheduled jobs keep running, and the API behind a hidden section still answers anyone whose role allows it — for example with an API key. Use [roles](./rbac-team-management.md#the-role-catalog) to restrict what people may do. Settings are stored per deployment (`PUT /api/admin/menu-config`; the sidebar reads `GET /api/menu-config`).
:::

## User Activity

Accounts, presence, live sessions and login history for the whole deployment, with **Sign out**, **Reset password** and **Require change** per user — described on [Audit Trail & User Activity](./audit-trail.md#user-activity-platform-administrator).

## Deployment security settings

These are set by the operator in the deployment's `.env`, not in the UI. They are listed here so the platform administrator knows what governs the deployment.

| Setting | Default | Effect |
| --- | --- | --- |
| `ENABLE_API_DOCS` | On outside production; **off** when `ENVIRONMENT=production` | Serves the OpenAPI schema, Swagger UI (`/api/docs`) and ReDoc. Set `true` to expose them in production |
| `API_KEY_SCOPE_MODE` | `enforce` | API keys are limited to their scopes; `warn` / `off` are opt-outs — see [What a key can reach](./rbac-team-management.md#what-a-key-can-reach) |
| `METRICS_TOKEN` | unset | Bearer token for Prometheus `/metrics`; when unset, `/api/platform/metrics` needs the platform administrator's session |
| `REQUIRE_EXTERNALIZED_SECRETS` | `auto` | Whether the platform may still read encryption keys from its database. `auto` is strict for new installs; `true` refuses to start while a key exists only in the database |
| `CLOUD_ENCRYPTION_KEY` · `CLOUD_ENCRYPTION_KEY_PREVIOUS` | — | The key that encrypts stored credentials; during a rotation the previous value(s) decrypt while credentials are re-encrypted |
| `AUDIT_CHAIN_HMAC_KEY` · `AUDIT_CHAIN_HMAC_KEY_PREVIOUS` | derived from `SECRET_KEY` | Signs the [audit hash chains](./audit-trail.md#integrity-and-siem-export); set a dedicated value |
| `AUDIT_HEAD_WITNESS_DIR` · `AUDIT_HEAD_WITNESS_SYSLOG` | off | Opt-in copy of each audit chain's signed head outside the database |
| `OIDC_*` | SSO off | Single sign-on, enforcement and group-to-role mapping — see [Signing In & Sessions](./session-management.md#single-sign-on-oidc) |

Procedures — moving keys out of the database, rotating the credential key, setting up the head witness — are in [Deployment & Operations](../on-premises/deployment.md#encryption-keys).

## Related

- [Signing In & Sessions](./session-management.md) — the SSO-enforced break-glass rule, MFA enforcement and the registration bootstrap.
- [Production configuration](../adoption/production-configuration.md) — environment variables an operator sets outside the wizard.
- [On-Premises](../on-premises/index.mdx) — where the deployment itself lives.
