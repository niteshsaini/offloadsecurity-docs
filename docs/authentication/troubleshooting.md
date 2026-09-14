---
title: "Platform Security Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 6
description: "Locked accounts, lost authenticators, SSO that refuses sign-in, invitations that never arrive, API keys that return 401 or 403, sessions that end at 24 hours, audit events you cannot see — and answers to frequent questions."
---

# Platform Security Troubleshooting & FAQ

## Signing in

**"Invalid email or password" although both are right.**
Five failures lock the account for 15 minutes and every attempt during the lock gets the same message. Wait, or ask the platform administrator to check *Login history* for `login_blocked`. If SSO is enforced on the deployment, passwords are refused for everyone but the platform administrator — use **Sign in with …**.

**I lost my authenticator.**
Use one of your backup codes at the MFA prompt, then **Regenerate** codes and re-enrol from **Multi-Factor Auth**. With no codes left you cannot sign in, and there is no admin bypass in the UI (disabling MFA needs a signed-in session plus your password), so the operator has to clear the enrolment on the account record. Keep the backup codes somewhere you can reach without the phone.

**"Forgot your password?" says a link was sent, but nothing arrives.**
The message is the same whether or not the email exists, and sending needs the platform's SMTP (Platform Setup). Without SMTP the platform administrator can issue the link directly from User Activity → **Reset password** (valid 24 hours).

**I was sent to "Change password" straight after signing in.**
The account was created with a temporary password, or an administrator set **Require change**. Set a new password meeting the rules; other sessions of yours are ended.

**My session ends after a day even while I am working.**
Sessions are fixed at 24 hours from sign-in; there is no sliding extension. Sign in again. Five concurrent sessions per user are kept; a sixth evicts the oldest.

## SSO

**The button is missing.**
`GET /api/auth/sso/status` returns `enabled: false` — `OIDC_ENABLED`, `OIDC_ISSUER`, `OIDC_CLIENT_ID` and `OIDC_CLIENT_SECRET` must all be set and the issuer's discovery document reachable from the backend.

**"SSO sign-in failed" after the provider redirect.**
The login page shows the reason (`sso_error`). The common ones: the email's domain is not in `OIDC_ALLOWED_EMAIL_DOMAINS` (or the deployment's allowed domain); `OIDC_AUTO_PROVISION=false` and the user has no account yet; the redirect URI registered at the provider is not `<PUBLIC_APP_URL>/api/auth/sso/callback`; clock skew failing the id-token check.

**Roles from my IdP groups are not applied.**
`OIDC_GROUP_ROLE_MAPPING` must be a JSON object of group → role, and every role must exist (`admin`, `security_manager`, `security_analyst`, `compliance_officer`, `auditor`, `viewer`). One unknown role disables group sync entirely — deliberately — and the backend log says so.

## Teams and invitations

**"Only team admins can invite members as admin."**
Security Managers can invite and manage members but cannot grant Admin. Ask an Admin.

**Invitations are rejected with "domain not allowed".**
The deployment restricts registration to one email domain (set at bootstrap, `PUT /api/auth/org-settings/domain`). Invite an address on that domain.

**"Rate limit exceeded" while inviting.**
20 invitations per inviter per rolling hour (`INVITE_RATE_LIMIT_COUNT`). Bulk onboarding is easier through SSO auto-provisioning.

**The invitee never got the email.**
Invitation mail needs SMTP; without it, share the link from the response. Links expire after 7 days — send a new one.

**I switched teams and my API script broke.**
API keys are bound to the team that was active when they were created; switching your own active team does not move them. Create a key per team.

## API keys

**401 with a valid-looking key.**
Expired (`expires_in_days`), revoked, or past its rotation grace period. `GET /api/api-keys` shows status and expiry; rotated keys list the successor.

**403 on an endpoint that works in the browser.**
Sessions carry every scope; keys carry only theirs. Add the scope (`scans:manage`, `vulnerabilities:manage`, …) or choose a wider preset — and check the IP allowlist if the request comes from a new runner.

**429 from the key's own limit.**
`rate_limit_per_minute` (60 by default) is per key and separate from the platform's rate limits; raise it on the key or spread calls.

**I need to see keys a former colleague created.**
Team Admins: `GET /api/api-keys/admin/team-keys` lists every key in the team with its owner; revoke what should not outlive them.

## Audit trail

**I only see my own events.**
By design for non-Admin roles. A team Admin sees the whole team; the platform administrator sees every team.

**Login attempts are not in the audit trail export.**
Sign-in requests are recorded without bodies, and the detailed authentication events (`login_failed`, `login_blocked`, `session_expired`, …) live in the separate authentication log — User Activity → *Login history*, or `GET /api/auth/audit-log` for the platform administrator.

**Client Menu Settings hid a module, but the API still answers.**
Intended: menu settings are presentation only. Permissions are what stop an action; use roles for that.

## Frequently asked questions

**Can I create a custom role?**
Not in the current release: six fixed roles per team, plus scoped API keys for narrower automation access.

**Is there a session-timeout setting?**
No — 24 hours fixed. Use MFA, SSO enforcement and the platform administrator's *Sign out* for stricter control.

**Do API keys expire?**
By default after 90 days; `0` creates a non-expiring key (not recommended). Rotation keeps the old key alive for 48 hours by default.

**Where do I set SSO for a SaaS tenant?**
SSO is configured per deployment by the operator; on SaaS, ask Offload Security to enable it for your tenant with your provider's details.

**How long is the audit trail kept?**
365 days by default (`AUDIT_TRAIL_RETENTION_DAYS`). Export CSV to keep longer.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login page errors, workers and deployment. When contacting support include the email, the time and IP of the attempt (from Login history if you are the platform administrator), and for API keys the key prefix — never the key itself.
