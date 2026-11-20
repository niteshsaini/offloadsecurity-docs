---
title: "Platform-Admin Console"
sidebar_label: "Platform-Admin Console"
sidebar_position: 4.5
new_in: 1.4.1
description: "The platform administrator's pages: User Activity account actions, Teams & Users across every team, the Audit Log, System Health, Security Policy with the admin IP allowlist, Access Review, and managing several platform admins with step-up re-authentication."
---

# Platform-Admin Console

Since 1.4.1 the platform administrator manages the deployment from a set of pages under *Management* in the left navigation. Team Admins never see these pages, and the APIs behind them refuse everyone else. This page describes each page. [Platform Administration](./platform-administration.md) explains what the platform-admin account is.

**Where:** left navigation → *Management* → **Client Menu Visibility**, **User Activity**, **Teams & Users**, **Audit Log**, **System Health**, **Access Review**, **Security Policy**. Each one is marked *Platform-admin only*.

## Before you begin

- You are signed in **with a session** as a platform administrator. API keys never reach platform-admin endpoints.
- For the actions marked *step-up* below, you need your local password, plus your authenticator code if you use MFA. See [Step-up re-authentication](#step-up-re-authentication).
- If a [platform-admin IP allowlist](#platform-admin-ip-allowlist) is set, connect from an allowed address.

## User Activity

User Activity lists every account on the deployment, live sessions, and login history. The tiles, tabs and password actions are described in [Audit Trail & User Activity](./audit-trail.md#user-activity-platform-administrator). In 1.4.1 the **Users** tab adds a search box (**Search email or name**) and a status filter (**Active**, **Deactivated**, **Locked**). It also adds **MFA** and **Access** columns and these actions:

| Action | What it does | Step-up |
| --- | --- | :-: |
| **Enforce MFA for everyone** / **Stop enforcing MFA** | Deployment-wide MFA enforcement (see [Enforcing MFA for everyone](./session-management.md#enforcing-mfa-for-everyone)). You must enable MFA on your own account first | ✓ |
| **Reset MFA** | Clears the user's MFA, signs them out everywhere and notifies them | ✓ |
| **Sign out everywhere** | Ends every session of the user. Their API keys keep working. On your own account it signs you out too | ✓ |
| **Unlock** | Clears the failed-login backoff for the account. A deactivated account stays deactivated | ✓ |
| **Deactivate** | Sets the account inactive, signs it out and revokes its API keys. Refused for yourself, a platform admin, the last admin, or a team's only admin. Nothing is deleted, so the audit trail is kept | ✓ |
| **Reactivate** | Lets the user sign in again. API keys revoked at deactivation stay revoked | — |
| **Reset password** · **Require change** | Described in [Changing and resetting passwords](./session-management.md#changing-and-resetting-passwords) | ✓ |
| **Make platform admin** | See [Platform admins](#platform-admins) | ✓ |

Every action is written to the authentication event log.

## Teams & Users

**Teams & Users** lists every team on the deployment with its member and admin counts. From here the platform administrator can manage any team, including teams they are not a member of. A team Admin still manages only their own teams from **Team Management**.

| Task | Notes | Step-up |
| --- | --- | :-: |
| Create a team | Its first admin is a user you choose, or you. A team never starts without an admin. Names are unique among active teams | ✓ |
| Rename or re-describe a team | | — |
| Add an existing user to a team, with a role | The deployment's allowed email domain applies, as for invitations | ✓ |
| **Create user** directly in a team | Same password rules and domain rule as registration. The user must change the password you set at first sign-in | ✓ |
| Change a member's role · remove a member | Removing or demoting a team's only admin is refused. The member is signed out everywhere, and removal revokes their API keys for that team | ✓ |
| Delete a team | Shows what would be removed first. A team with members or data needs its exact name typed to confirm. The default team cannot be deleted | ✓ |

:::warning[Deleting a team deletes its data]
Deleting a team permanently removes that team's module data: findings, scans, cloud accounts and their credentials, evidence, risks and schedules. Export anything you need first.
:::

Every change is written to the authentication event log.

## Audit Log

**Audit Log** is the screen for the [audit trail](./audit-trail.md). It has three tabs:

| Tab | Shows |
| --- | --- |
| **API trail** | The request trail for every team. Filter by **Team**, **Actor (user ID)**, **Action**, **Resource (path contains)**, **Outcome** and a date range. **Export CSV** downloads up to 10,000 matching entries |
| **Auth events** | The separate authentication event store, filtered by **Event**, **Email (exact)** and a date range |
| **Integrity & SIEM export** | **Verify chain** for the API, compliance or auth store, with an optional sequence range. It also pulls a SIEM page as JSON lines or CEF |

If a CSV export reaches the 10,000-entry limit, the page warns that the export is partial. Use the SIEM export to page through everything.

## System Health

**System Health** shows one card per health source, each marked **OK**, **Warning**, **Error** or **Unknown**:

- **Backups**
- **Subsystem integrity**
- **Scan failures** (unacknowledged)
- **Data-sync watchdog**
- **Scan queue**
- **Dead letters**
- **Prometheus metrics (summary)**

The page reads the platform's existing health endpoints. A failed or refused request shows as **Error** or **Unknown**, never as healthy.

## Security Policy

**Security Policy** shows each password, lockout and session setting with its effective value, its floor and the source of that value (**Policy page**, **Environment** or **Built-in**). You can make a setting stricter than its floor, but never looser.

| Setting | Built-in floor | Stricter direction | Allowed range | Floor variable |
| --- | --- | --- | --- | --- |
| Minimum password length | 12 characters | higher | 8–128 | `AUTH_PASSWORD_MIN_LENGTH` |
| Failed sign-ins before backoff | 5 attempts | lower | 3–20 | `AUTH_LOCKOUT_THRESHOLD` |
| First backoff duration | 900 seconds | higher | 60–3,600 seconds | `AUTH_LOCKOUT_DURATION_SECONDS` |
| Absolute session lifetime | 86,400 seconds (24 h) | lower | 900 seconds–7 days | `AUTH_SESSION_LIFETIME_SECONDS` |
| Concurrent sessions per user | 5 | lower | 1–50 | `AUTH_MAX_SESSIONS_PER_USER` |

The operator can raise a floor by setting a stricter value in `.env`. A looser or out-of-range value there is ignored, and the backend logs a warning. The page enters values in minutes where a setting is a duration.

Saving needs step-up and is written to the audit trail with the before and after values. Saving never signs anyone out and never expires a password:

- A new minimum length applies at the next password change.
- Session settings apply to new sign-ins.

Every backend worker picks up a change within 30 seconds.

### Platform-admin IP allowlist

On the same page you can list up to 100 IP addresses or CIDR ranges allowed to use platform-admin powers. An empty list turns the allowlist off. When the allowlist is on and the request comes from outside it:

- Platform-admin pages and APIs answer *Platform-admin access is not allowed from this network address* (403, `ADMIN_IP_NOT_ALLOWED`).
- Shared pages that show more to a platform admin (the audit trail, alerts, the scan queue, `GET /api/auth/users` and others) show only what your own team role allows.
- When SSO is enforced, the platform administrator's password sign-in only works from inside the allowlist.
- Other users are not affected. Signing in still works from anywhere, so you can reach the page to fix the list. The metrics scrape token is not covered.

Saving refuses a list that does not include your current address. It also refuses when the request reached the backend through a proxy that the backend does not trust. Behind nginx or a load balancer, the operator must set `TRUSTED_PROXIES` first (see [Deployment security settings](./platform-administration.md#deployment-security-settings)).

:::warning[Break-glass for a lockout]
If the allowlist locks every platform administrator out, the operator can set `ADMIN_IP_ALLOWLIST_ENFORCE=false` in `.env` and restart the backend. The stored list is kept but not enforced.
:::

Password history, password expiry, idle timeout and the lockout counter window are not configurable.

## Access Review

**Access Review** supports periodic access reviews and dormant-account cleanup.

- **Entitlements**: every user with status, org role, each team and team role, MFA, sign-in method, last login, creation date and who created or invited them. **Export** as CSV or JSON returns every user, with no row cap. Each export is written to the audit trail with its row count and a SHA-256 of the snapshot.
- **Record review**: write a note, mark the users removed as a result, and record the review. The platform stores a frozen snapshot of the entitlements and its SHA-256. **Past reviews** re-checks each stored snapshot against its hash. A banner appears when no review has been recorded within the reminder period (90 days by default).
- **Dormant users**: deactivate accounts with no sign-in for a set number of days (90 by default, at least 30). This is **off by default**. Turning it on needs step-up. A daily job then deactivates the users the preview shows, and **Deactivate now** runs it at once (step-up). Platform admins, service accounts (Integration role), accounts holding a live API key and a team's last active admin are never deactivated. Accounts created within the period that have never signed in are not dormant. No warning email is sent before a dormant account is deactivated.

Dormant users are deactivated the same way as on User Activity. Reactivate them from User Activity or from **Recent runs**.

## Platform admins

A deployment can have more than one platform administrator. The **Platform admins** panel on User Activity lists each one, whether they can sign in with a local password, and whether they have MFA. It warns when only one platform admin is active, or when none has MFA.

1. **Grant.** Click **Make platform admin** on an active user in the Users table (step-up). Their team role does not change. The grant takes effect at their next sign-in.
2. **Revoke.** Click **Revoke** in the panel and type the user's email to confirm (step-up). Every session of that account is signed out.
3. **Transfer.** Make the new person a platform admin, then click **Step down** on your own row.

The platform always keeps a **break-glass** pair: at least one active platform admin, and at least one who can sign in with a local password, so someone can get in when SSO is down. A revoke that would break either rule is refused. MFA is not required for a platform admin. A platform admin cannot be deactivated: revoke platform admin first.

### Step-up re-authentication

Before a sensitive action, the console asks for your password again, plus your authenticator code if you use MFA. The confirmation is bound to that browser session and lasts **15 minutes** by default (`STEP_UP_WINDOW_MINUTES`, 1–60).

- Failed attempts count toward the sign-in lockout.
- Accounts that sign in only through SSO cannot step up yet. A platform admin with a local password must perform these actions.
- Over the API, a gated call without a fresh step-up answers 403 with `detail.code` `step_up_required`. Re-authenticate with `POST /api/auth/step-up` and retry.

## Related

- [Platform Administration](./platform-administration.md): the account, Platform Setup, Client Menu Visibility and deployment settings.
- [Audit Trail & User Activity](./audit-trail.md): what the trail records and how verification works.
- [Platform Security API](./api.md#platform-admin-console): the endpoints behind these pages.
