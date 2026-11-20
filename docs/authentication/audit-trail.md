---
title: "Audit Trail & User Activity"
sidebar_label: "Audit Trail & User Activity"
sidebar_position: 3
description: "What the platform records about every change — actor, team, action, outcome, timing, redacted context — in a hash-chained, tamper-evident trail; who can read, verify and export it (CSV or a SIEM feed); the authentication event log; per-feature logs; and the platform administrator's User Activity view of accounts, live sessions and login history."
---

# Audit Trail & User Activity

An auditor's first question about a security tool is who did what in it. The platform answers from three records: the **audit trail** written for every change made through the API, the **authentication event log** written by the sign-in system itself, and the per-feature logs that some modules keep (API keys, Auto-Fix actions, DPDP). The platform administrator additionally gets a live **User Activity** view.

## The audit trail

Every write request to the API — every `POST`, `PUT`, `PATCH` and `DELETE`, which covers every change made in the UI — and every report or export download is written to the audit trail as one event. Plain reads (`GET` requests other than report and export downloads) are not recorded.

| Field | Content |
| --- | --- |
| **Who** | User id, email, role, active team; or the API key's owner |
| **What** | HTTP method and path, and a classified **action** — `user.login`, `user.logout`, `user.sso_login`, `mfa.setup` / `enable` / `disable` / `verify`, `scan.start`, `report.generate` / `report.download`, `assessment.create` / `update`, `team.modify`, `user.modify`, `integration.*`, `api_key.*`, and a generic `<resource>.<verb>` for the rest |
| **When** | Timestamp and how long the request took |
| **Outcome** | HTTP status and success / failure |
| **Context** | A summary of the request body for writes (first 500 characters) with sensitive fields — passwords, secrets, tokens, session ids, API keys and anything named like them — replaced by `***REDACTED***`; sign-in, registration, MFA and SSO exchanges log no body at all |

Health checks, live-event streams, documentation endpoints and, since 1.4.1, CORS preflight (`OPTIONS`) requests are not recorded. Audit trail entries are **not pruned automatically**; they are kept until an operator removes them.

### Who can read what

| Reader | Sees |
| --- | --- |
| Any member | Their **own** events in the active team |
| Team **Admin** | Every event in the active team, filterable by user; verify and SIEM export for the team |
| **Platform administrator** | Every event on the deployment, across teams (from inside the [platform-admin IP allowlist](./platform-admin-console.md#platform-admin-ip-allowlist) when one is set) |

`GET /api/audit-trail?user_id=&action=&start_date=&end_date=&success_only=&team_id=&resource=&limit=&skip=` queries it (wildcards such as `user.*` work on `action`; `resource` matches part of the request path; `team_id` is for the platform administrator; up to 1,000 events per page); `GET /api/audit-trail/user/{user_id}` narrows to a person; `GET /api/audit-trail/actions` lists the action vocabulary; `GET /api/audit-trail/export` returns **CSV** (up to 10,000 events — team Admin or platform administrator). The `X-Audit-Total`, `X-Audit-Exported` and `X-Audit-Truncated` response headers say whether the export is complete.

:::note[The Audit Log screen is for the platform administrator]
Since 1.4.1 the platform administrator has an **Audit Log** page with filters, CSV export, chain verification and SIEM export. See [Platform-Admin Console](./platform-admin-console.md#audit-log). Team Admins and members still read the trail through the API and the exports.
:::

## Integrity and SIEM export

Since 1.4.0 the audit trail is **tamper-evident**. Each team's entries form a hash chain: every entry stores a sequence number, the previous entry's hash and its own HMAC-SHA256 hash, and each chain has a signed start (anchor) and a signed end (head). Writes are durable — acknowledged by the database majority and retried — and a write that is still lost is logged and counted on the platform's metrics rather than dropped silently.

Three stores are chained, chosen with `?store=`:

| Store | What it holds | Who can read it |
| --- | --- | --- |
| `api` (default) | The audit trail above, one chain per team | Team Admin (own team), platform administrator |
| `compliance` | Compliance control-status history, one chain per team | Team Admin (own team), platform administrator |
| `auth` | Sign-in, lockout, MFA, password and session events, one chain for the deployment | Platform administrator |

**Verify a chain** — `GET /api/audit-trail/verify` walks every entry and reports `ok`, `broken` (an entry was edited or forged) or `truncated` (entries were deleted from the start or the end), the first broken link, and `disclosures` such as since when the chain exists and how many older entries predate it. A chain longer than 100,000 entries is verified as a background job: the response carries a `job_id` to poll at `GET /api/audit-trail/verify/jobs/{job_id}`.

**Export to a SIEM** — `GET /api/audit-trail/export/siem?after_seq=<cursor>&format=jsonl|cef` returns up to 5,000 chained entries per call as JSON lines or ArcSight CEF; the `X-Audit-Next-After-Seq` and `X-Audit-Has-More` headers drive the next pull. A SIEM can pull on a schedule with an API key holding the `admin:audit` scope whose owner is a team Admin.

Entries written before 1.4.0 are left as they were and reported as unchained. What the operator sets up — the chain key, its rotation, and the optional **external head witness** that also catches someone with database access deleting the newest entries — is in [Deployment & Operations](../on-premises/deployment.md#audit-trail-integrity). Without a witness, verify says so in its disclosures.

## Authentication events

Independently of the request trail, the sign-in system records `login_success`, `login_failed`, `login_blocked` (lockout), `login_throttled`, `account_auto_unlocked`, `session_created`, `session_destroyed`, `session_expired`, `session_revoked`, `user_registered`, password changes, administrator-issued resets and *Require change* flags, with the IP address and user agent. These events are hash-chained too (the `auth` store above). Since 1.4.1 the store also records the platform administrator's account actions: unlocks, deactivations, MFA resets, sign-outs, platform-admin grants and revocations, step-up attempts, team and member changes made from Teams & Users, Security Policy changes, access-review exports and scanner image overrides. They feed the platform administrator's **Login history** below, the **Auth events** tab of the Audit Log, `GET /api/audit-trail/auth-events?event=&email=&start_date=&end_date=&limit=&skip=` and `GET /api/auth/audit-log` (all platform administrator).

## Per-feature logs

- **API keys** — `GET /api/api-keys/audit-log`: creation, rotation, revocation and requests blocked by scope, IP allowlist, expiry or rate limit; `GET /api/api-keys/analytics` for usage over 30 days.
- **Auto-Fix actions** — approve / deny / execute / rollback with approver and reason, on each action — see [Security Command Center](../ai-threat-intelligence/ai-soc-agents.md#auto-fix-engine).
- **Compliance overrides and remediation** — the remediation audit trail exported by [Audit Reports](../compliance/audit-reports.md).
- **DPDP** — the sealed audit pack in [DPDP Compliance](../compliance/dpdp-privacy.md#audit--export).
- **AI agent decisions** — the Command Center's [Activity Log](../ai-threat-intelligence/ai-soc-agents.md#activity-log).

## User Activity (platform administrator)

**Where:** left navigation → *Management* → **User Activity** (visible to the platform administrator only).

![User Activity: users, online now, live sessions, signed in 24 h, logins 24 h, failed logins; Users tab with role, status, presence, sessions, last login, from, via, teams, password actions](/img/screenshots/platform-security/user-activity.webp)

Every account on the deployment in one place — who is signed in right now, from where, and every login attempt. The tiles count users (and how many never signed in), online now, live sessions, users signed in over 24 hours / 7 / 30 days, and successful and failed sign-ins in the last 24 hours.

| Tab | Shows |
| --- | --- |
| **Users** | Each account: role, status, presence (online = active in the last 15 minutes), open sessions, last login, source IP, sign-in method (password or SSO), teams, and the password actions below |
| **Live sessions** | Every open session — user, presence, IP, client, method, signed in, expires — with **Sign out** per session |
| **Login history** | Successful, failed and blocked sign-ins with IP and reason, filtered by email, event and window (24 hours to 90 days in the UI; up to 365 days over the API) |

![Live sessions: user, presence, IP, client, via, signed in, expires; Sign out](/img/screenshots/platform-security/user-activity-sessions.webp)

In 1.4.1 the Users tab adds search, a status filter and more account actions (MFA reset and enforcement, sign out everywhere, unlock, deactivate and reactivate, and platform-admin grants). These are described on [Platform-Admin Console](./platform-admin-console.md#user-activity).

Two account actions live here because they are the administrator's answer when email is not configured: **Reset password** shows a single-use reset link (valid 24 hours by default) to hand to the user directly — it is also emailed when SMTP is set — and **Require change** signs the user out of every session and forces a new password at the next sign-in. Neither works on SSO-only accounts. The page says so itself when SMTP is missing.

Listing sessions here is read-only by design: opening the page does not refresh anyone's session or make them look active. **Reset password** and **Require change** ask for your password again first ([step-up](./platform-admin-console.md#step-up-re-authentication)).

## Related

- [Signing In & Sessions](./session-management.md) — the events that produce the login history.
- [Roles, Teams & API Keys](./rbac-team-management.md) — who is a team Admin, and the `admin:audit` scope.
- [Platform Administration](./platform-administration.md) — the account that sees across teams.
- [Platform-Admin Console](./platform-admin-console.md) — the Audit Log page and the other platform-admin pages.
- [Platform Security API](./api.md#audit-trail-and-user-activity) — the endpoints on this page.
