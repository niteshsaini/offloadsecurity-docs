---
title: "Platform Security API"
sidebar_label: "API"
sidebar_position: 5
description: "Sign-in, MFA and SSO; teams, members and invitations; API key lifecycle and scopes; the audit trail, its hash-chain verification and SIEM export, and the authentication log; the platform-admin console (user activity, teams, security policy, access review, platform admins, step-up) and menu configuration — with the permission each endpoint needs."
---

# Platform Security API

[API Reference](../api-reference/index.md) covers authentication and conventions. Swagger at `https://<your-host>/api/docs` lists every endpoint, but it is **off in production** unless the operator sets `ENABLE_API_DOCS=true`. Requests below use either a session (`Authorization: Bearer <session>`) or an API key (`X-API-Key`); the sign-in endpoints themselves are unauthenticated. Endpoints marked *session only* refuse API keys.

## Sign-in, MFA and SSO

| Task | Endpoint | Notes |
| --- | --- | --- |
| Sign in | `POST /api/auth/login` `{email, password}` → `{session_id, user}` or `{mfa_required: true, mfa_token}` | 5 failures from one address → 15-minute lock (doubling to 60 min) for that address, unless Security Policy is stricter; SSO-enforced deployments refuse non-platform-admin passwords |
| Complete MFA | `POST /api/auth/mfa/verify` `{mfa_token, code}` | TOTP or backup code; challenge valid 5 minutes |
| Who am I · sign out | `GET /api/auth/me` · `POST /api/auth/logout` | |
| MFA management | `POST /api/auth/mfa/setup` → QR + secret · `POST …/mfa/enable` `{secret, code}` → backup codes · `POST …/mfa/disable` `{password}` · `POST …/mfa/backup-codes` (regenerate; no body) · `GET …/mfa/status` | The signed-in user; disable is refused while MFA is enforced |
| MFA enforcement | `GET /api/auth/mfa/enforce` · `POST /api/auth/mfa/enforce` `{enforce}` | GET: any signed-in user. POST: platform administrator, session only, step-up, caller must have MFA |
| MFA reset | `POST /api/auth/mfa/admin/reset/{user_id}` | Platform administrator, session only, step-up; signs the user out and notifies them |
| Passwords | `POST /api/auth/change-password` `{current_password, new_password}` · `POST /api/auth/forgot-password` `{email}` · `POST /api/auth/reset-password` `{token, new_password}` | Reset link valid 30 min |
| SSO | `GET /api/auth/sso/status` → `{enabled, enforced, provider_name}` · `GET /api/auth/sso/login` (redirects to the IdP) · `GET /api/auth/sso/callback` · `POST /api/auth/sso/exchange` `{code}` → session | Configured by environment |
| Registration | `GET /api/auth/invitation-info?token=` · `POST /api/auth/register` `{email, password, name, invitation_token}` | Invitation required after the first account |
| Organization settings | `GET /api/auth/org-settings` · `PUT /api/auth/org-settings/domain` `{domain}` | Allowed registration / SSO domain — org Admin |

## Teams, members and invitations

| Task | Endpoint | Notes |
| --- | --- | --- |
| Teams | `GET /api/teams` · `POST /api/teams` `{name, description?, organization?, risk_appetite_threshold?, compliance_frameworks?}` · `GET` · `PUT` · `DELETE /api/teams/{team_id}` | Create / edit / delete need **Manage Team** |
| Active team | `GET /api/teams/current` · `POST /api/teams/{team_id}/switch` | Switch re-issues the session for that team |
| Members | `GET /api/teams/{team_id}/members` · `PUT …/members/{user_id}` `{role}` · `DELETE …/members/{user_id}` | **Manage Users** (Admin, Security Manager); only an Admin may set `admin`. Role change and removal end the member's sessions; removal also revokes their keys for the team |
| Invitations | `POST /api/teams/{team_id}/members/invite` `{email, role, message?}` · `GET /api/teams/invitations/pending` · `POST …/invitations/{invitation_id}/accept` · `…/reject` | 20 per inviter per hour; 7-day expiry. `pending` lists invitations you received |
| Sent invitations · revoke | `GET /api/teams/{team_id}/invitations` · `DELETE /api/teams/{team_id}/invitations/{invitation_id}` | **Manage Users**; revoke answers 409 if the invitation was already accepted, rejected or revoked |
| Users | `GET /api/auth/users` | Org Admin. Since 1.4.1 it returns only users in the caller's teams; only a platform administrator (inside the admin IP allowlist) gets every user |

## API keys

| Task | Endpoint | Notes |
| --- | --- | --- |
| Create | `POST /api/api-keys` `{name, description?, scopes[] \| scope_preset, expires_in_days (90; 0 = never; ≤ 365), ip_allowlist[]? (≤ 50), environment (production\|staging\|development\|ci), rate_limit_per_minute (60; 1–600)}` | **Manage Integrations**; returns the key **once**. `rate_limit_per_minute` is enforced (429 with `Retry-After`) |
| List · detail · scopes | `GET /api/api-keys` · `GET /api/api-keys/{key_id}` · `GET /api/api-keys/scopes` | Own keys |
| Update · rotate · revoke | `PATCH /api/api-keys/{key_id}` `{name?, description?, scopes?, ip_allowlist?, environment?, rate_limit_per_minute?}` · `POST …/{key_id}/rotate` `{grace_period_hours (48; 0–168)}` · `DELETE /api/api-keys/{key_id}` · `POST /api/api-keys/bulk-revoke` `{key_ids[]? , environment?}` | **Manage Integrations** |
| Usage | `GET /api/api-keys/analytics?days=30` · `GET /api/api-keys/audit-log?limit=` | |
| Team-wide (admin) | `GET /api/api-keys/admin/team-keys` · `DELETE /api/api-keys/admin/{key_id}` | Team **Admin** |
| Scope review | `GET /api/api-keys/admin/scope-report` · `POST /api/api-keys/admin/scope-migration` | Platform administrator |

## Audit trail and user activity

| Task | Endpoint | Notes |
| --- | --- | --- |
| Query | `GET /api/audit-trail?user_id=&action=&start_date=&end_date=&success_only=&team_id=&resource=&limit=&skip=` · `GET /api/audit-trail/user/{user_id}` · `GET /api/audit-trail/actions` · `GET /api/audit-trail/teams` | Members: own events; team Admin: the team; platform administrator: everything |
| Export | `GET /api/audit-trail/export` (CSV, ≤ 10,000 events; `X-Audit-Truncated` says if more matched) | Team Admin or platform administrator |
| Authentication events | `GET /api/audit-trail/auth-events?event=&email=&start_date=&end_date=&limit=(≤ 500)&skip=` | Platform administrator |
| Verify a chain | `GET /api/audit-trail/verify?store=api\|compliance\|auth&from_seq=&to_seq=` · `POST /api/audit-trail/verify/jobs` · `GET /api/audit-trail/verify/jobs/{job_id}` | Team Admin (own team) or platform administrator; `auth` is platform administrator only. Session or a key with `admin:audit` |
| SIEM export | `GET /api/audit-trail/export/siem?after_seq=&limit=&format=jsonl\|cef&store=` | As verify; ≤ 5,000 entries per call, cursor in `X-Audit-Next-After-Seq` |
| Authentication log | `GET /api/auth/audit-log?limit=` | Platform administrator |
| Menu configuration | `GET /api/menu-config` (any signed-in user — drives the sidebar) · `PUT /api/admin/menu-config` `{menu_visibility: {section_id: bool}}` | PUT: platform administrator |
| Platform setup | `GET /api/platform-setup/status` · `POST /api/platform-setup/reopen` · `…/validate-service` · `…/validate-smtp` · `…/validate-storage` · `…/save-config` · `…/complete` | No sign-in on a fresh install; reopening, and every write after a reopen, needs the platform administrator |
| Scanner image override | `PUT /api/scan-tools/versions/{tool}` `{image, reason}` · `DELETE /api/scan-tools/versions/{tool}` (roll back) | Platform administrator; image must be the tool's own repository, pinned by digest |

## Platform-admin console

Every endpoint here is platform administrator only, session only (API keys are refused), and subject to the platform-admin IP allowlist. Endpoints marked *step-up* answer 403 `step_up_required` without a recent `POST /api/auth/step-up`.

| Task | Endpoint | Notes |
| --- | --- | --- |
| Step-up | `POST /api/auth/step-up` `{password, otp_code?}` · `GET /api/platform-admin/admins/step-up-status` | Valid for `STEP_UP_WINDOW_MINUTES` (15) on this session; failures count toward the login lockout; SSO-only accounts are refused |
| User activity | `GET /api/platform-admin/activity/summary` · `…/users` · `…/sessions` · `DELETE …/sessions/{session_id}` · `GET …/login-history?email=&event=&days=` | `days` 1–365 |
| Account actions | `POST /api/platform-admin/activity/users/{user_id}/reset-password` · `…/require-password-change` `{required}` · `…/sign-out-all` · `…/unlock` · `…/deactivate` · `…/reactivate` | All step-up except reactivate |
| Platform admins | `GET /api/platform-admin/admins` · `POST …/admins/{user_id}/grant` · `POST …/admins/{user_id}/revoke` `{confirm_email}` | Grant and revoke: step-up. Revoke is refused (409) if it would leave no active platform admin, or none with a local password |
| Teams & Users | `GET /api/platform-admin/teams` · `POST /api/platform-admin/teams` · `PUT …/teams/{team_id}` · `GET …/teams/{team_id}/delete-impact` · `DELETE …/teams/{team_id}?confirm=<name>` | Create and delete: step-up |
| Team members | `GET …/teams/{team_id}/members` · `POST …/members` `{user_id, role}` · `PUT …/members/{user_id}` `{role}` · `DELETE …/members/{user_id}` · `POST …/teams/{team_id}/users` (create a user) · `GET …/teams/directory/users` | Writes: step-up |
| Security policy | `GET /api/platform-admin/security-policy` · `PUT /api/platform-admin/security-policy` | PUT: step-up; values can only be stricter than the floor |
| Access review | `GET /api/platform-admin/access-review/entitlements` · `…/entitlements/export?format=csv\|json` · `GET …/status` · `GET`/`POST …/reviews` · `GET …/reviews/{review_id}` · `…/reviews/{review_id}/snapshot` · `GET`/`PUT …/settings` · `GET …/dormant/preview` · `POST …/dormant/run` · `GET …/dormant/runs` | Turning dormant deactivation on and `dormant/run`: step-up |

## Permissions

| Action | Permission |
| --- | --- |
| Own sessions, MFA, password, list own API keys, own audit events | any authenticated user |
| Create / edit / rotate / revoke API keys | **Manage Integrations** (`manage_integrations`) — Admin, Security Manager |
| Create / edit / delete teams | **Manage Team** (`manage_team`) — Admin, Security Manager |
| Invite, change roles, remove members | **Manage Users** (`manage_users`) — Admin, Security Manager; assigning **Admin** needs an Admin |
| Team-wide audit trail, CSV export, chain verify and SIEM export; team-wide API keys | **Admin** role in the team |
| Org settings (allowed domain); list the users of your own teams | org **Admin** (`users.role: admin`) |
| Cross-team audit, authentication log and chain, the platform-admin console, MFA enforcement and MFA reset, API key scope report, menu configuration, reopening Platform Setup, modules and tiers, scanner image overrides | platform administrator (`is_platform_admin`) |

See [Authentication](../api-reference/authentication.md) for key scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
