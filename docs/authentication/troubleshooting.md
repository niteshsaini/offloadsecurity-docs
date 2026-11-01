---
title: "Platform Security Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 6
description: "Locked accounts, lost authenticators, forced MFA setup, SSO that refuses sign-in, invitations that never arrive, API keys that return 401 or 403, sessions that end early, audit events you cannot see or verify — and answers to frequent questions."
---

# Platform Security Troubleshooting & FAQ

## Signing in

**"Sign-in temporarily locked after too many failed attempts".**
Five failures from one address lock sign-in to that account from that address for 15 minutes; failing again after the lock doubles it (30, then 60 minutes). Wait, or sign in from your usual network — other addresses are not locked. The platform administrator can see `login_blocked` events in *Login history*. If SSO is enforced on the deployment, passwords are refused for everyone but the platform administrator — use **Sign in with …**.

**Sign-in is slow for one account.**
More than 20 recent failures on that account, from any address, slow every attempt by up to 10 seconds. It clears once the failures stop.

**I lost my authenticator.**
Use one of your backup codes at the MFA prompt, then **Regenerate** codes and re-enrol from **Multi-Factor Auth**. With no codes left you cannot sign in alone: ask the platform administrator to reset your MFA (`POST /api/auth/mfa/admin/reset/{user_id}`, API only). You are signed out and notified, and must enrol again if the deployment enforces MFA. Keep the backup codes somewhere you can reach without the phone.

**After signing in I can only see the MFA setup page.**
The deployment enforces MFA and your account has none. Enrol; the rest of the platform unlocks on that session as soon as MFA is enabled.

**The Disable MFA button is missing.**
The deployment enforces MFA, so it cannot be switched off per user.

**"Forgot your password?" says a link was sent, but nothing arrives.**
The message is the same whether or not the email exists, and sending needs the platform's SMTP (Platform Setup). Without SMTP the platform administrator can issue the link directly from User Activity → **Reset password** (valid 24 hours).

**I was sent to "Change password" straight after signing in.**
The account was created with a temporary password, or an administrator set **Require change**. Set a new password meeting the rules; other sessions of yours are ended.

**I was signed out in the middle of the day.**
Sessions are fixed at 24 hours from sign-in, and five concurrent sessions per user are kept (a sixth evicts the oldest). You are also signed out when a team admin changes your role or removes you from a team, when the platform administrator signs your session out, requires a password change or resets your MFA, and when MFA enforcement is switched on while you have no MFA.

## SSO

**The button is missing.**
`GET /api/auth/sso/status` returns `enabled: false` — `OIDC_ENABLED`, `OIDC_ISSUER`, `OIDC_CLIENT_ID` and `OIDC_CLIENT_SECRET` must all be set and the issuer's discovery document reachable from the backend.

**"SSO sign-in failed" after the provider redirect.**
The login page shows the reason (`sso_error`). The common ones: the email's domain is not in `OIDC_ALLOWED_EMAIL_DOMAINS` (or the deployment's allowed domain); `OIDC_AUTO_PROVISION=false` and the user has no account or invitation yet; the provider sent `email_verified=false` (or, with `OIDC_REQUIRE_EMAIL_VERIFIED=strict`, did not send it — Entra ID never does); the redirect URI registered at the provider is not `<PUBLIC_API_URL or PUBLIC_APP_URL>/api/auth/sso/callback`; clock skew failing the id-token check.

**Roles from my IdP groups are not applied.**
`OIDC_GROUP_ROLE_MAPPING` must be a JSON object of group → role, and every role must exist (`admin`, `security_manager`, `security_analyst`, `compliance_officer`, `auditor`, `viewer`, `integration`). One unknown role disables group sync entirely — deliberately — and the backend log says so. Check also that the provider releases the claim named in `OIDC_GROUPS_CLAIM`: without it, roles are left unchanged. A team membership an admin set by hand is never changed by group sync.

**A user's role dropped to Viewer after SSO sign-in.**
The provider sent the groups claim and none of the user's groups is in the mapping, so the role was reset to `OIDC_DEFAULT_ROLE`. Add the group to the mapping, or grant the role by hand in Team Management.

## Teams and invitations

**"Only team admins can invite members as admin."**
Security Managers can invite and manage members but cannot grant Admin. Ask an Admin.

**Invitations are rejected with "domain not allowed".**
The deployment restricts registration to one email domain (`PUT /api/auth/org-settings/domain`). Invite an address on that domain.

**"Rate limit exceeded" while inviting.**
20 invitations per inviter per rolling hour (`INVITE_RATE_LIMIT_COUNT`). Bulk onboarding is easier through SSO auto-provisioning.

**The invitee never got the email.**
Invitation mail needs SMTP; without it, share the link from the response. Links expire after 7 days — send a new one.

**I switched teams and my API script broke.**
API keys are bound to the team that was active when they were created; switching your own active team does not move them. Create a key per team.

## API keys

**I cannot create an API key.**
Creating, editing, rotating and revoking keys needs **Manage Integrations** — the Admin or Security Manager role.

**401 with a valid-looking key.**
Expired (`expires_in_days`), revoked, past its rotation grace period, or its owner's account is disabled. `GET /api/api-keys` shows status and expiry; rotated keys list the successor.

**403 on an endpoint that works in the browser.**
Sessions carry every scope; keys carry only theirs. The 403 names the missing scope — add it (`scans:manage`, `vulnerabilities:manage`, …) or choose a wider preset. If the message says the route is **session-only** or has **no scope mapping**, no key can call it; use a signed-in session. Also check the IP allowlist if the request comes from a new runner, and that the key's owner is still a member of the team (a key acts with its owner's *current* role).

**A key shows "review scopes" or "Will be refused".**
It was created before scopes were enforced and was given scopes automatically on upgrade. Check them in the scope editor on the API Keys page; "Will be refused" lists calls the key made before that its scopes now block.

**429 from the key's own limit.**
`rate_limit_per_minute` (60 by default) is per key and separate from the platform's rate limits; raise it on the key or spread calls.

**I need to see keys a former colleague created.**
Removing a member from a team revokes their keys for that team. For other keys, team Admins can use `GET /api/api-keys/admin/team-keys`, which lists every key in the team with its owner.

## Audit trail

**I only see my own events.**
By design for non-Admin roles. A team Admin sees the whole team; the platform administrator sees every team.

**Page views and searches are not in the audit trail.**
By design: only write requests (and report and export downloads) are recorded.

**Login attempts are not in the audit trail export.**
Sign-in requests are recorded without bodies, and the detailed authentication events (`login_failed`, `login_blocked`, `session_expired`, …) live in the separate authentication log — User Activity → *Login history*, or `GET /api/auth/audit-log` for the platform administrator.

**Verify returns `truncated` or `broken`.**
`broken` means an entry, anchor or head no longer matches its signature — an edit. `truncated` means entries are missing from the start or the end. Both are logged at ERROR on the backend; treat them as a security event. An `unknown_key` result usually means the chain key was rotated without keeping the old value in `AUDIT_CHAIN_HMAC_KEY_PREVIOUS` (or `SECRET_KEY` changed while the chain key was derived from it) — see [Deployment & Operations](../on-premises/deployment.md#audit-trail-integrity).

**Verify returns a `job_id` instead of a result.**
The chain has more than 100,000 entries; poll `GET /api/audit-trail/verify/jobs/{job_id}`.

**Client Menu Visibility hid a module, but the API still answers.**
Intended: menu visibility is presentation only. Permissions are what stop an action; use roles for that.

**`/api/docs` returns 404.**
Swagger and ReDoc are off when `ENVIRONMENT=production`; the operator enables them with `ENABLE_API_DOCS=true`.

## Frequently asked questions

**Can I create a custom role?**
Not in the current release: six fixed roles per team, plus scoped API keys for narrower automation access.

**Is there a session-timeout setting?**
No — 24 hours fixed. Use MFA, SSO enforcement and the platform administrator's *Sign out* for stricter control.

**Can I set password expiry or history rules?**
No. Use SSO and set them at your identity provider.

**Do API keys expire?**
By default after 90 days; `0` creates a non-expiring key (not recommended). Rotation keeps the old key alive for 48 hours by default.

**Where do I set SSO for a SaaS tenant?**
SSO, including group-to-role mapping, is configured per deployment by the operator in the environment; on SaaS, ask Offload Security to enable it for your tenant with your provider's details.

**How long is the audit trail kept?**
It is not pruned automatically. Export CSV, or stream it to your SIEM, if you also need a copy outside the platform.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login page errors, workers and deployment. When contacting support include the email, the time and IP of the attempt (from Login history if you are the platform administrator), and for API keys the key prefix — never the key itself.
