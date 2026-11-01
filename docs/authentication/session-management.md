---
title: "Signing In & Sessions"
sidebar_label: "Signing In & Sessions"
sidebar_position: 1
description: "Password rules and lockout, TOTP multi-factor authentication with backup codes and deployment-wide enforcement, OIDC single sign-on with just-in-time provisioning and group-to-role mapping, how sessions are issued, revoked and expire, and how passwords are changed or reset."
---

# Signing In & Sessions

Two ways in — a password (with MFA on top) or your identity provider — and one kind of session behind both. This page is what a user needs to sign in and stay safe, and what an administrator needs to set the deployment's policy.

## Password sign-in

![Sign In: email, password, Sign In, Forgot your password?; "This platform is invite-only"](/img/screenshots/platform-security/login.webp)

| Rule | Value |
| --- | --- |
| Password | At least **12 characters** with an uppercase letter, a lowercase letter, a digit and a special character, and not on the built-in list of common passwords |
| Storage | PBKDF2-SHA256, 600,000 iterations, a unique salt per user — never reversible |
| Lockout | **5** failed attempts from one address lock sign-in to that account **from that address** for **15 minutes**; further failures from the same address double the lock (30, then 60 minutes, the cap). Other addresses are not locked, so a third party cannot lock a user out |
| Account-wide brake | After 20 recent failures on one account across all addresses, every attempt on it is slowed (1 s, rising to 10 s). This is a delay, never a lock |
| Enumeration | A wrong email and a wrong password take the same time and give the same answer |
| First sign-in | An account created by an administrator with a temporary password is sent to **Change password** before anything else |

IPv6 addresses are grouped by /64 for the lockout. Failure counters are forgotten an hour after the lock they caused would have ended.

## Multi-factor authentication

**Where:** account menu → **Multi-Factor Auth**.

![Multi-Factor Authentication: status Disabled, method not configured, backup codes 0 remaining, Enable MFA; how it works](/img/screenshots/platform-security/mfa-settings.webp)

1. **Enable MFA** shows a QR code (and the key, for manual entry) for any TOTP app — Google Authenticator, Authy, 1Password, Microsoft Authenticator.
2. Enter the 6-digit code from the app to confirm. MFA is on from the next sign-in.
3. Save the **10 backup codes** shown once; each works exactly once in place of a code. **Regenerate** replaces the set.

![Step 1: scan QR code; Step 2: enter verification code](/img/screenshots/platform-security/mfa-setup.webp)

With MFA on, a correct password returns an MFA challenge rather than a session; the code (or a backup code) completes the sign-in within five minutes. **Disable** asks for your password, not a code. TOTP secrets are stored encrypted; if the deployment's encryption key is missing, enrolment is refused rather than storing a secret in plain text.

### Enforcing MFA for everyone

MFA enforcement is a **deployment-wide** setting that only the [platform administrator](./platform-administration.md) can change, from a signed-in session (not an API key), and only after enabling MFA on their own account. There is no switch in the UI; it is set over the API:

```
POST /api/auth/mfa/enforce
```

While enforcement is on:

- Turning it on signs out every account that has no MFA.
- An account without MFA that signs in — by password or SSO — gets a **restricted session** that can only reach MFA setup; the browser goes straight to the MFA page. Enrolling lifts the restriction on that session.
- Users cannot disable their own MFA; the **Disable** button is hidden and the API refuses it.

When SSO is used and the identity provider already performs MFA, the operator can set `OIDC_TRUST_IDP_MFA=true` so SSO users are not asked twice. With it left at `false` (the default), an account that has platform MFA enabled gets the same MFA challenge after SSO as after a password.

A user who has lost both the authenticator and the backup codes cannot recover alone. The platform administrator can reset that user's MFA with `POST /api/auth/mfa/admin/reset/{user_id}` (API only): MFA is cleared, the user is signed out everywhere and notified (in-app, and by email when SMTP is configured), and the reset is audited. Under enforcement their next sign-in is the restricted, enrol-only session.

## Single sign-on (OIDC)

The platform is an OpenID Connect relying party (authorization code + PKCE) for any compliant provider — Okta, Microsoft Entra ID, Google Workspace, Keycloak, Auth0. SAML-only providers are supported through an OIDC broker such as Keycloak. The operator configures it in the deployment environment; there is no SSO settings screen:

| Variable | Purpose |
| --- | --- |
| `OIDC_ENABLED` · `OIDC_ISSUER` · `OIDC_CLIENT_ID` · `OIDC_CLIENT_SECRET` | Turn SSO on and point it at the provider (discovery from the issuer URL) |
| `OIDC_PROVIDER_NAME` | The label on the **Sign in with …** button |
| `OIDC_SCOPES` | `openid email profile` by default |
| `OIDC_ENFORCED` | Refuse password sign-in for everyone except the platform administrator (the break-glass account); the login page hides the password form |
| `OIDC_AUTO_PROVISION` · `OIDC_DEFAULT_ROLE` | Create an account on first SSO sign-in (on by default) with this role (`viewer` by default) |
| `OIDC_ALLOWED_EMAIL_DOMAINS` | Only provision users from these domains; empty falls back to the deployment's registration domain. An address invited explicitly by a team admin is admitted even outside the list |
| `OIDC_REQUIRE_EMAIL_VERIFIED` | `true` (default) rejects only an explicit `email_verified=false`; `strict` requires `email_verified=true` (Entra ID never sends the claim, so `strict` blocks it); `false` never checks |
| `OIDC_GROUPS_CLAIM` · `OIDC_GROUP_ROLE_MAPPING` | Map identity-provider groups to platform roles on every sign-in — see below |
| `OIDC_TRUST_IDP_MFA` | Accept the provider's MFA instead of the platform's |
| `PUBLIC_APP_URL` · `PUBLIC_API_URL` · `OIDC_REDIRECT_URI` | The redirect base (`PUBLIC_API_URL` if set, else `PUBLIC_APP_URL`); the callback is `/api/auth/sso/callback`. `OIDC_REDIRECT_URI` overrides the computed value |

The flow ends on the platform: after the provider's callback the platform mints an ordinary session and hands it to the browser through a single-use code in the URL fragment (never a query string, so it never reaches proxies or logs). SSO sign-ins are audited as `user.sso_login`. `GET /api/auth/sso/status` tells the login page whether SSO is enabled, enforced and what to call it.

### Group-to-role mapping

Group mapping is configured **only in the environment** — there is no UI for it. `OIDC_GROUP_ROLE_MAPPING` is a JSON object, for example `{"sec-admins":"admin","sec-analysts":"security_analyst"}`; the first entry whose group the user holds wins.

- A **new** SSO user gets the mapped role; with no match, the role from their invitation, else `OIDC_DEFAULT_ROLE`.
- An **existing** user's role is re-synced on every sign-in. If the provider sends the groups claim and none of the mapped groups is in it, the user drops to `OIDC_DEFAULT_ROLE`. If the claim is missing altogether, nothing changes (that is treated as a provider misconfiguration, not a revocation).
- Sync changes only team memberships that SSO itself created. A membership an admin granted or changed by hand is never overwritten.
- A mapping that names an unknown role disables group sync entirely rather than mass-demoting; the backend log says so.

## Sessions

- A session is an opaque random token stored **hashed** server-side (Redis, with MongoDB as fallback); the browser holds the token and sends it as `Authorization: Bearer`.
- Sessions last **24 hours** from sign-in. There is no silent extension — sign in again after a day.
- A user may hold **5** sessions at once (laptop, phone, a second browser); the oldest is evicted when a sixth is created.
- **Sign Out** deletes the session server-side. Switching teams re-issues the session bound to the new team.
- Sessions are also ended for you when a team admin **changes your role** or **removes you** from a team, when the platform administrator signs a session out from [User Activity](./audit-trail.md#user-activity-platform-administrator), sets **Require change** or resets your MFA, and when MFA enforcement is turned on while you have no MFA.

## Changing and resetting passwords

![Change password: current password, new password, confirm; the five rules; "Changing your password signs you out everywhere else"](/img/screenshots/platform-security/change-password.webp)

- **Change password** (account menu) needs the current password and a new one meeting the rules; every other session of yours is ended.
- **Forgot your password?** on the login page emails a single-use link valid for **30 minutes** (`PASSWORD_RESET_TTL_MINUTES`) — always with the same "if an account exists…" answer. It needs the deployment's SMTP to be configured.
- Without SMTP, or for a locked-out colleague, the platform administrator issues a reset link from User Activity (**Reset password**, valid **24 hours** by default, `PASSWORD_RESET_ADMIN_TTL_MINUTES`) or flags the account with **Require change**, which signs the user out and sends the next sign-in straight to *Change password*. Neither applies to SSO-only accounts — reset those at the identity provider.

There is no password expiry or password-history rule; use SSO if your policy requires them.

## Registration and invitations

The **first account** on a new deployment registers itself and becomes the platform administrator; from then on registration is **invitation-only**. An invitation carries the team and role, is bound to the invited email, expires after **7 days** (`INVITATION_EXPIRY_DAYS`) and is stored hashed. A team admin may send **20 invitations an hour** (`INVITE_RATE_LIMIT_COUNT` / `…_WINDOW_SECONDS`). Where the deployment set an **allowed email domain**, invitations outside it are refused. See [Roles, Teams & API Keys](./rbac-team-management.md#invite-a-teammate-and-assign-a-role).

## Related

- [Roles, Teams & API Keys](./rbac-team-management.md) — what a signed-in user can do.
- [Audit Trail & User Activity](./audit-trail.md) — every sign-in, MFA change and session in the record.
- [Platform Security API](./api.md#sign-in-mfa-and-sso) — the endpoints behind this page.
