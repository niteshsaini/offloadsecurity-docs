---
title: "Platform Security API"
sidebar_label: "API"
sidebar_position: 5
description: "Sign-in, MFA and SSO; teams, members and invitations; API key lifecycle; the audit trail and authentication log; platform-administrator activity and menu configuration — with the permission each endpoint needs."
---

# Platform Security API

[API Reference](../api-reference/index.md) covers authentication and conventions; Swagger at `https://<your-host>/api/docs` is exhaustive. Requests below use either a session (`Authorization: Bearer <session>`) or an API key (`X-API-Key`); the sign-in endpoints themselves are unauthenticated.

## Sign-in, MFA and SSO

| Task | Endpoint | Notes |
| --- | --- | --- |
| Sign in | `POST /api/auth/login` `{email, password}` → `{session_id, user}` or `{mfa_required: true, mfa_token}` | 5 failures → 15-minute lock; SSO-enforced deployments refuse non-platform-admin passwords |
| Complete MFA | `POST /api/auth/mfa/verify` `{mfa_token, code}` | TOTP or backup code; challenge valid 5 minutes |
| Who am I · sign out | `GET /api/auth/me` · `POST /api/auth/logout` | |
| MFA management | `POST /api/auth/mfa/setup` → QR + secret · `POST …/mfa/enable` `{code}` → backup codes · `POST …/mfa/disable` `{code}` · `POST …/mfa/backup-codes` `{code}` (regenerate) · `GET …/mfa/status` | The signed-in user |
| MFA enforcement | `GET` · `POST /api/auth/mfa/enforce` `{enforce}` | **Manage Team** |
| Passwords | `POST /api/auth/change-password` `{current_password, new_password}` · `POST /api/auth/forgot-password` `{email}` · `POST /api/auth/reset-password` `{token, new_password}` | Reset link valid 30 min |
| SSO | `GET /api/auth/sso/status` → `{enabled, enforced, provider_name}` · `GET /api/auth/sso/login` (redirects to the IdP) · `GET /api/auth/sso/callback` · `POST /api/auth/sso/exchange` `{code}` → session | Configured by environment |
| Registration | `GET /api/auth/invitation-info?token=` · `POST /api/auth/register` `{email, password, name, invitation_token}` | Invitation required after the first account |
| Organisation settings | `GET /api/auth/org-settings` · `PUT /api/auth/org-settings/domain` `{domain}` | Allowed registration / SSO domain — Admin |

## Teams, members and invitations

| Task | Endpoint | Notes |
| --- | --- | --- |
| Teams | `GET /api/teams` · `POST /api/teams` `{name, description?, organization?, risk_appetite_threshold?, compliance_frameworks?}` · `GET` · `PUT` · `DELETE /api/teams/{team_id}` | Create / edit / delete need **Manage Team** |
| Active team | `GET /api/teams/current` · `POST /api/teams/{team_id}/switch` | Switch re-issues the session for that team |
| Members | `GET /api/teams/{team_id}/members` · `PUT …/members/{user_id}` `{role}` · `DELETE …/members/{user_id}` | **Manage Users** (Admin, Security Manager); only an Admin may set `admin` |
| Invitations | `POST /api/teams/{team_id}/members/invite` `{email, role, message?}` · `GET /api/teams/invitations/pending` · `POST …/invitations/{invitation_id}/accept` · `…/reject` | 20 per inviter per hour; 7-day expiry |
| Users on the deployment | `GET /api/auth/users` | Admin |

## API keys

| Task | Endpoint | Notes |
| --- | --- | --- |
| Create | `POST /api/api-keys` `{name, description?, scopes[] \| scope_preset, expires_in_days (90; 0 = never; ≤ 365), ip_allowlist[]? (≤ 50), environment (production\|staging\|development\|ci), rate_limit_per_minute (60; 1–600)}` | Returns the key **once** |
| List · detail · scopes | `GET /api/api-keys` · `GET /api/api-keys/{key_id}` · `GET /api/api-keys/scopes` | Own keys |
| Update · rotate · revoke | `PUT /api/api-keys/{key_id}` `{name?, description?, ip_allowlist?, environment?, rate_limit_per_minute?}` · `POST …/{key_id}/rotate` `{grace_period_hours (48; 0–168)}` · `DELETE /api/api-keys/{key_id}` · `POST /api/api-keys/bulk-revoke` `{key_ids[]? , environment?}` | |
| Usage | `GET /api/api-keys/analytics?days=30` · `GET /api/api-keys/audit-log?limit=` | |
| Team-wide (admin) | `GET /api/api-keys/admin/team-keys` · `DELETE /api/api-keys/admin/{key_id}` | Team **Admin** |

## Audit trail and user activity

| Task | Endpoint | Notes |
| --- | --- | --- |
| Query | `GET /api/audit-trail?user_id=&action=&start_date=&end_date=&success_only=&limit=&skip=` · `GET /api/audit-trail/user/{user_id}` · `GET /api/audit-trail/actions` | Members: own events; team Admin: the team; platform administrator: everything |
| Export | `GET /api/audit-trail/export` (CSV, ≤ 10,000 events) | Team Admin or platform administrator |
| Authentication log | `GET /api/auth/audit-log?limit=` | Platform administrator |
| User activity | `GET /api/platform-admin/activity/summary` · `…/users` · `…/sessions` · `DELETE …/sessions/{session_id}` · `GET …/login-history` · `POST …/users/{user_id}/reset-password` · `POST …/users/{user_id}/require-password-change` | Platform administrator |
| Menu configuration | `GET` · `PUT /api/admin/menu-config` `{menu_visibility: {section_id: bool}}` | Platform administrator |
| Platform setup | `GET /api/platform-setup/status` · `POST /api/platform-setup/reopen` · `…/validate-service` · `…/validate-smtp` · `…/validate-storage` · `…/save-config` · `…/complete` | Admin |

## Permissions

| Action | Permission |
| --- | --- |
| Own sessions, MFA, password, own API keys, own audit events | any authenticated user |
| Create / edit / delete teams, MFA enforcement | **Manage Team** (`manage_team`) — Admin, Security Manager |
| Invite, change roles, remove members | **Manage Users** (`manage_users`) — Admin, Security Manager; assigning **Admin** needs an Admin |
| Team-wide audit trail and export, team-wide API keys, list deployment users, Platform Setup | **Admin** role |
| Cross-team audit, authentication log, User Activity, session revocation, password resets, menu configuration | platform administrator (`is_platform_admin`) |

See [Authentication](../api-reference/authentication.md) for key scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
