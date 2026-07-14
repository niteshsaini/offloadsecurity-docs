---
title: "Roles, Teams & API Keys"
sidebar_label: "Roles, Teams & API Keys"
sidebar_position: 1
---

# Roles, Teams & API Keys

Offload Security is multi-tenant: every scan, finding, asset, risk, and report belongs to a **team**, and what each person can do inside a team is governed by their **role**. This page explains the role catalog, how to invite teammates and assign roles, how to switch your active team, and how to create and manage API keys for automation.

![Team management with member roles and invitations](/img/screenshots/team-management.png)

You manage all of this from **Team Management** (under the **Management** section of the left navigation). API keys are managed alongside it.

## What it does

- **Isolates data by team.** You only ever see data for your **active team**, so separate clients, environments, or business units stay cleanly separated.
- **Controls access by role.** Each member holds one role per team, and that role determines which modules and actions they can use.
- **Lets people belong to multiple teams.** You can switch your active team at any time without signing out.
- **Secures automation with scoped API keys.** Keys let CI/CD pipelines and integrations call the platform with only the permissions they need.

## The role catalog

Each team member is assigned exactly one of six roles. Roles are additive — higher roles include the abilities of the ones below them.

| Role | What they can do |
|---|---|
| **Admin** | Full control of the team: manage members and their roles, integrations, cloud accounts, and every other module and its data. |
| **Security Manager** | Run and manage scans, cloud accounts, risks, assessments, threat intelligence, container security, and remediations; approve remediations; use AI assistants. Can also invite and manage members. |
| **Security Analyst** | The day-to-day operator: run scans, create and manage risks, work assessments, view findings and reports, and use AI assistants. |
| **Compliance Officer** | GRC-focused: manage assessments, view the executive dashboard, export reports, and use the compliance copilot. |
| **Auditor** | Read-only across security data and reports, with the ability to **export** reports for evidence. |
| **Viewer** | Basic read-only visibility into dashboards, scans, risks, and reports. |

:::note[Inviting and managing members]
The ability to invite teammates and change their roles belongs to **Admins** and **Security Managers** (both hold the "manage users" permission). As a safeguard, only an **Admin** can invite or promote someone to the **Admin** role.
:::

## Invite a teammate and assign a role

1. Open **Team Management**. Your active team and your role are shown at the top.
2. Find the team you want to add someone to and select **Invite Member** (or **Invite Members**). This option appears only if you're an Admin (or Security Manager) of that team.
3. In the **Invite Member** dialog, enter the person's **email address**, choose a **role**, and optionally add a personal message.
4. Select **Send Invitation**. The invitee receives an email with a link to accept and set up their account; once they accept, they join the team with the role you chose.

:::tip[Prerequisites and limits]
- If your organization has restricted invitations to a specific email domain, you can only invite addresses on that domain — others are rejected.
- Invitations are rate-limited per inviter (by default, up to 20 in a rolling hour) to prevent accidental floods.
- Invitation links expire after a set window (7 days by default). If a link expires, simply send a new invitation.
:::

### Change someone's role

In the member list for your active team, Admins can change a member's role from the role dropdown next to their name. The change takes effect immediately the next time that member's access is checked.

## Switch your active team

If you belong to more than one team, you can switch which one is active:

1. Open **Team Management**.
2. In the list of your teams, select the team you want to work in. Your current team is marked as the active one.
3. The platform switches your context and refreshes so that scans, findings, and reports all reflect the team you just selected.

:::tip[Always confirm your active team first]
Before you run a scan, connect an account, or review data, make sure the correct team is active — the action and its results are scoped to whatever team you're currently in. You can also switch teams from the account menu in the top-right.
:::

## API keys for automation

API keys give CI/CD pipelines, scripts, and integrations programmatic access to the platform — for example, to trigger scans from a pipeline or pull findings into another tool. Each key carries its own **scopes** (a focused set of permissions), so you can grant automation exactly what it needs and nothing more.

### Create a key

1. Open the **API Keys** screen and select **Create API Key**.
2. Give the key a **name** (and an optional description of what it's for).
3. Choose a **scope preset** that matches the job:

   | Preset | Grants |
   |---|---|
   | **CI/CD Pipeline (Basic)** | Trigger scans and read results. |
   | **CI/CD Pipeline (Full)** | Trigger, read, and manage scans, plus read vulnerabilities. |
   | **Read Only** | Read scans, vulnerabilities, assessments, cloud posture, risks, and reports. |
   | **Security Automation** | Trigger/read/manage scans, read and update vulnerabilities, read cloud posture, and read/generate reports. |
   | **Full Access** | All available scopes. |

4. Optionally set an **expiry** (default 90 days, up to 365), an **environment** label, and a per-minute rate limit.
5. Select **Create Key**.

:::warning[Copy your key immediately]
The full key is shown **only once**, right after you create it — use the **Copy** button and store it somewhere secure (a secrets manager or your CI/CD secret store). The platform keeps only a hashed version and can never show you the full key again. Keys begin with the `osk_` prefix so they're easy to recognize.
:::

### Use a key

Send the key in the `X-API-Key` request header. Endpoints accept either a signed-in session **or** a valid API key, and each request is allowed only if the key's scopes cover the action.

### Rotate, revoke, and monitor keys

From the key list you can:

- **Rotate** a key when you want to replace it. The old key keeps working for a **48-hour grace period** so you can update your pipelines without downtime.
- **Revoke** a key to disable it immediately. This can't be undone — issue a new key if you need one again.
- **Monitor** each key's usage count, last-used time, and environment to spot keys that are unused or behaving unexpectedly.

:::note[Key limits and hardening]
- Each user can hold up to **25** active keys at a time; revoke unused keys before creating more.
- For extra protection you can restrict a key to a set of allowed IP addresses (up to 50), so it can only be used from your pipeline's network.
:::

## Related

- **[Getting Started](../getting-started.md)** — sign in and learn the core concepts, including teams and roles.
- **[Authentication & Session Management](./session-management.md)** — how sign-in, sessions, and MFA work.
- **[Audit Trail & Webhook Events](./audit-trail.md)** — see who did what across your team.
- **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)** — add the accounts your team will scan.
