---
title: "Platform Administration"
sidebar_label: "Platform Administration"
sidebar_position: 4
description: "The platform-administrator account — what makes it different from a team or org Admin, how more than one can exist — and what only it can do: Platform Setup, modules and tiers, Client Menu Visibility, the platform-admin console, scanner image overrides; plus the deployment security settings an operator controls."
---

# Platform Administration

Each deployment of Offload Security — a SaaS tenant or an on-premises install — has at least one **platform administrator**. The first account created when the platform was set up is one. Since 1.4.1 a platform administrator can grant the role to other accounts (see [Platform admins](./platform-admin-console.md#platform-admins)). It is not a team role. A team Admin governs one team; the platform administrator governs the deployment, sees across every team, and is the break-glass account when single sign-on is enforced.

**Where:** account menu → **Platform Setup**; left navigation → *Management* → **Client Menu Visibility**, **User Activity**, **Teams & Users**, **Audit Log**, **System Health**, **Access Review**, **Security Policy**. All of these are shown to platform administrators only. The pages are described in [Platform-Admin Console](./platform-admin-console.md).

## What the platform administrator can do

| Capability | Team Admin | Platform administrator |
| --- | :-: | :-: |
| Everything inside their own teams | ✓ | ✓ |
| Manage every team, its members and roles (**Teams & Users**) | — | ✓ |
| Read the audit trail across all teams; export all of it; the **Audit Log** page | — | ✓ |
| Read and verify the authentication event chain (`/api/auth/audit-log`, `?store=auth`) | — | ✓ |
| See every account, live session and login attempt; sign users out; unlock, deactivate and reactivate accounts; issue password resets; require a password change | — | ✓ |
| Turn deployment-wide MFA enforcement on or off; reset a user's MFA | — | ✓ |
| Set the password, lockout and session policy and the platform-admin IP allowlist (**Security Policy**) | — | ✓ |
| Run access reviews and dormant-user deactivation (**Access Review**); view **System Health** | — | ✓ |
| Grant, revoke and transfer the platform-admin role | — | ✓ |
| Choose which menu sections the deployment's users see | — | ✓ |
| Enable modules, change subscription tiers and client configuration | — | ✓ |
| Override a scanner's image (API) | — | ✓ |
| API key scope report and migration across the deployment (API) | — | ✓ |
| Read platform metrics (`/api/platform/metrics`) when no `METRICS_TOKEN` is set | — | ✓ |
| Reopen Platform Setup (connectivity, keys, storage, platform URL, SMTP) | — | ✓ |
| Sign in with a password while SSO is enforced | — | ✓ |
| List users (`/api/auth/users`) | Users in their own teams (org Admin) | Every user |

The flag (`is_platform_admin`) is set on the first registration and by a grant from another platform administrator. No invitation, registration or SSO path can set it. Protect these accounts accordingly: strong password, MFA, a recorded owner, and at least two platform admins so the deployment does not depend on one person.

### Org Admin is not platform administrator

Someone invited to a team as **Admin** becomes an Admin of the deployment as well (org Admin, `users.role: admin`). An org Admin can manage org settings such as the allowed email domain and can list the users of their own teams. An org Admin is **never** a platform administrator. Only a platform administrator can enable modules, change tiers, reopen Platform Setup or use the platform-admin console. An Admin invitation can only be issued, and is only honored, while the person who sent it is an active Admin of that team.

An existing account that accepts an Admin invitation keeps its current deployment-level role.

## Platform Setup

![Platform Setup: Reconfigure Platform Settings — what you can reconfigure (MongoDB and Redis connectivity, cryptographic keys, object storage, platform name / URL / environment, email / SMTP); Launch Setup Wizard](/img/screenshots/platform-security/platform-setup.webp)

The setup wizard that ran on first boot can be relaunched at any time by a **platform administrator**; the **Platform Setup** item appears in the account menu for platform administrators only. Since 1.4.1 an org Admin can no longer reopen it, and the wizard's writes after a reopen need the platform administrator too. Setup on a fresh install still needs no sign-in, and a completed setup stays locked until it is reopened. Its steps: **Welcome → Service Connectivity** (MongoDB, Redis) → **Security Keys** (generated secrets for sessions, credential encryption, webhooks) → **Storage** (object storage for evidence and reports) → **Platform Settings** (name, public URL, environment) → **Email / SMTP** → **Admin Account** (first run only) → **Complete**. Each step validates before saving — the SMTP step authenticates to the server, the storage step writes and reads a test object.

Keys the wizard generates should not stay in the platform database: copy them into the deployment's `.env` (see [Deployment security settings](#deployment-security-settings) below). To recover lost keys without the wizard, restore them in the host `.env` and recreate the services.

SMTP set here is the **platform** mail server: it sends invitations, password-reset links and platform notifications, and is the fallback when a team has not connected its own under [Integrations](../integrations/notifications.md#email-smtp). The deployment environment (`SMTP_HOST`) still overrides both.

## Client Menu Visibility

![Client Menu Visibility: per-section checkboxes grouped by Core Security, Cloud & Infrastructure, …; applies to every user except the platform administrator](/img/screenshots/platform-security/menu-settings.webp)

Choose which sections of the left navigation the deployment's users see. Untick a module a customer has not licensed or a team is not ready for and it disappears from the menu for everyone — except the platform administrator, who always sees the full menu. Hiding asks for confirmation; opening a hidden section by link shows *not enabled for your organisation*; the page shows who last changed the setting and when. There is one setting for the whole deployment.

:::warning[Not an access control]
This hides menus and pages only. The data stays, scheduled jobs keep running, and the API behind a hidden section still answers anyone whose role allows it — for example with an API key. Use [roles](./rbac-team-management.md#the-role-catalog) to restrict what people may do. Settings are stored per deployment (`PUT /api/admin/menu-config`; the sidebar reads `GET /api/menu-config`).
:::

## User Activity

Accounts, presence, live sessions and login history for the whole deployment, with **Sign out**, **Reset password** and **Require change** per user — described on [Audit Trail & User Activity](./audit-trail.md#user-activity-platform-administrator). The account actions added in 1.4.1 (MFA reset and enforcement, sign out everywhere, unlock, deactivate, platform admins) are on [Platform-Admin Console](./platform-admin-console.md#user-activity).

## Scanner image overrides

A platform administrator can pin a scanner to a different build of its image with `PUT /api/scan-tools/versions/{tool}` `{image, reason}` and roll back with `DELETE /api/scan-tools/versions/{tool}`. This is API only. The override applies to every team's scans, so since 1.4.1:

- Only a platform administrator can set it. Before 1.4.1 any team Admin could.
- The image must come from the tool's own repository and be pinned by digest (`<repo>@sha256:…`).
- The override is checked again when a scan runs. An override that does not meet these rules is ignored, and the pinned image runs instead.

Each change is written to the authentication event log.

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
| `TRUSTED_PROXIES` | empty (no proxy trusted) | The exact address(es) of the reverse proxy in front of the backend. Only then is `X-Forwarded-For` used to find the client address. API key IP allowlists and the platform-admin IP allowlist depend on it behind nginx. Never trust a whole Docker range |
| `AUTH_PASSWORD_MIN_LENGTH` · `AUTH_LOCKOUT_THRESHOLD` · `AUTH_LOCKOUT_DURATION_SECONDS` · `AUTH_SESSION_LIFETIME_SECONDS` · `AUTH_MAX_SESSIONS_PER_USER` | built-in values | Floors under the [Security Policy](./platform-admin-console.md#security-policy) page. An env value can only make a setting stricter |
| `ADMIN_IP_ALLOWLIST_ENFORCE` | `true` | Set `false` and restart the backend to stop enforcing the platform-admin IP allowlist (break-glass) |
| `STEP_UP_WINDOW_MINUTES` | `15` | How long a [step-up re-authentication](./platform-admin-console.md#step-up-re-authentication) lasts (1–60) |

Procedures — moving keys out of the database, rotating the credential key, setting up the head witness — are in [Deployment & Operations](../on-premises/deployment.md#encryption-keys).

:::note[Response headers in 1.4.1]
The nginx front end and the backend no longer send `X-XSS-Protection`, which browsers have deprecated. Both now send `Cross-Origin-Resource-Policy: same-origin`, and nginx no longer reports its version in the `Server` header.
:::

## Related

- [Platform-Admin Console](./platform-admin-console.md) — the platform administrator's pages.
- [Signing In & Sessions](./session-management.md) — the SSO-enforced break-glass rule, MFA enforcement and the registration bootstrap.
- [Production configuration](../adoption/production-configuration.md) — environment variables an operator sets outside the wizard.
- [On-Premises](../on-premises/index.mdx) — where the deployment itself lives.
