---
title: "Security & Access Control"
sidebar_label: "Overview"
sidebar_position: 0
---

# Security & Access Control

Offload Security is built for teams that handle sensitive security data, so controlling **who can sign in**, **what they can do**, and **keeping each team's data separate** is core to the platform. This page is your overview of how access works and how your data is protected. Deeper, task-focused guides are linked at the bottom.

## What it does

- **Sign-in and sessions** — email-and-password sign-in with optional multi-factor authentication (MFA), plus sessions that keep you signed in securely and end cleanly when you log out.
- **Role-based access control (RBAC)** — six built-in roles that decide what each member can see and do, from full administration down to read-only viewing.
- **Team-based multi-tenancy** — every scan, finding, asset, risk, and report belongs to a **team**, and you only ever see data for your **active team**, so environments (clients, business units, regions) stay cleanly isolated.
- **API keys** — scoped, revocable keys for CI/CD pipelines and integrations, so automation never needs a person's password.
- **Audit logging** — an immutable record of who did what, when, and with what result, ready for compliance and investigations.

## Signing in

1. Open your platform URL and enter your **email** and **password**.
2. If your account has **MFA** enabled, you'll be prompted for a 6-digit code from your authenticator app to complete sign-in.
3. On success you land on the **Dashboard**, and your session keeps you signed in across the app.
4. Selecting **Log out** ends your session immediately so the token can't be reused.

:::tip Turn on MFA
For an extra layer of protection, enable MFA from your account settings. You scan a QR code with an authenticator app and are issued one-time backup codes to store safely.
:::

## Roles and what they can do

Access within a team is governed by role. Every member is assigned one of these six roles:

| Role | Typical use |
|---|---|
| **Admin** | Full access — manage teams, members, integrations, and all data. |
| **Security Manager** | Manage scans, risks, remediation, and team membership. |
| **Security Analyst** | Run scans and work findings and risks day to day. |
| **Compliance Officer** | Drive assessments and compliance, view executive dashboards, and export reports. |
| **Auditor** | Read-only access to scans, reports, and evidence. |
| **Viewer** | Read-only dashboards and basic visibility. |

Permissions are enforced consistently across the platform — both in what appears in the interface and on every action you take — so a member can't reach data or controls outside their role.

## Teams and data isolation

The platform is **multi-tenant**: each team's data is fully separated from every other team's.

- You can belong to **multiple teams** and switch your **active team** from the account menu in the top-right.
- You only ever see data for your active team — scans, findings, assets, risks, and reports are all scoped to it.
- New members join a team by **invitation**. Admins send an invite to a specific email address, and the invitee must register with that address. Only team admins can invite someone as an admin, and invitations can be rate-limited.
- When access is revoked, it takes effect immediately.

:::note Pick the right team first
Before you run scans or review data, confirm your active team in the top-right account menu. Everything you create is recorded under that team.
:::

## API keys for automation

API keys give your pipelines and integrations programmatic access without using a person's credentials.

- Keys are easy to spot by their **`osk_`** prefix.
- You assign each key a **scope** (for example, the ability to trigger scans or read vulnerabilities) so it can do only what you intend.
- You can restrict a key to specific **IP addresses** and **rotate** it with a short grace period, so automation keeps working while the old key retires.
- Send the key in the **`X-API-Key`** request header. The full key value is shown only once when you create it, so copy it somewhere safe.

For setup details and CI/CD examples, see **[RBAC, API Keys & Team Management](./rbac-team-management.md)**.

## Audit logging

Significant actions are captured in an **immutable audit trail** that records who performed an action, what it was, when it happened, and the outcome — useful for compliance reviews and investigations.

- Sensitive values such as passwords, secrets, tokens, and API keys are **automatically redacted** before anything is stored, so credentials never land in the log.
- Routine, high-volume requests (like health checks) are excluded to keep the record focused and readable.

## How your data is protected

:::tip Your credentials and data are protected
- **Encrypted credentials at rest** — cloud account credentials (AWS, Azure, GCP keys and service principals) are **encrypted before they're stored**, and the platform uses **read-only** access to your environments.
- **Passwords are never stored in plain text** — they're protected with strong, industry-standard hashing.
- **Tokens and keys are never stored in the clear** — session identifiers, API keys, and invitation tokens are stored only as one-way hashes, so a database copy can't be used to impersonate you.
- **Team isolation** — your data is scoped to your team and never visible to other tenants.
:::

## Related

- **[Authentication & Session Management](./session-management.md)** — sign-in, MFA, and how sessions work.
- **[RBAC, API Keys & Team Management](./rbac-team-management.md)** — roles, permissions, API keys, and team setup.
- **[Audit Trail & Webhook Events](./audit-trail.md)** — the audit log and event notifications.
- **[Getting Started](../getting-started.md)** — sign in and learn the core concepts.
- **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)** — how read-only, encrypted cloud credentials are set up.
