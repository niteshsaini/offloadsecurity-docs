---
title: "Getting Started"
sidebar_label: "Getting Started"
sidebar_position: 1
---

# Getting Started

This guide gets you from "I have access" to "I'm reviewing my first findings." It assumes the platform is already deployed and you have an account.

## 1. Sign in

1. Open the platform URL in your browser — e.g. `https://yourdomain.com` (the address your administrator gave you).
2. Enter your **email** and **password** on the login screen and select **Sign in**.
3. On success you land on the **Dashboard**.

:::info First administrator
The first administrator account is created during platform setup. If you're the operator who installed the platform, sign in with the admin email and the password you set (`DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD`). You can then invite teammates and assign roles from **Team Management**.
:::

## 2. Tour the dashboard

The Dashboard is your security command center — a real-time summary of posture, recent activity, and quick actions into the most-used modules.

![Offload Security dashboard overview](/img/screenshots/dashboard.png)

| Area | What it shows |
|---|---|
| **Left navigation** | Every module, grouped into Core Security, Cloud & Infrastructure, Compliance & Risk, Threat & Intelligence, and Management. |
| **Quick-action cards** | One-click entry into AI Governance, Assessments, Container Security, Cloud Security, and Web Application Security. |
| **Security metrics** | Headline numbers — total scans, security score, and vulnerability counts by severity. |
| **Recent Security Activity** | Your latest scans and their status, so you can pick up where you left off. |

## 3. Understand the core concepts

A few ideas appear throughout the platform. Knowing them up front makes everything else click.

### Teams (multi-tenancy)
Every resource — scans, findings, assets, risks, reports — belongs to a **team**. You can be a member of multiple teams and switch between them; you only ever see data for your **active team**. This keeps environments (for example, separate clients or business units) cleanly isolated.

### Roles (RBAC)
Access within a team is governed by role:

| Role | Typical use |
|---|---|
| **Admin** | Full access — manage teams, users, integrations, and all data. |
| **Security Manager** | Manage scans, risks, and remediation across the team. |
| **Security Analyst** | Run scans and work findings day to day. |
| **Compliance Officer** | Drive assessments, compliance, and evidence. |
| **Auditor** | Read-only access to evidence and reports. |
| **Viewer** | Read-only dashboards. |

### The data flow: Scan → Finding → Risk → Report
This is the backbone of how work moves through the platform:

1. **Scan** — you (or a schedule, or your CI pipeline) run a scan against a target: a cloud account, a container image, a web app, a Kubernetes cluster, or source code.
2. **Finding** — results are normalized into findings/vulnerabilities with severity, affected resource, and remediation guidance, then deduplicated.
3. **Risk** — significant findings (and compliance gaps) can be promoted into the **Risk Register** with treatment plans and SLAs.
4. **Compliance & Reports** — findings map to framework controls, and everything can be exported as an audit-ready report.

## 4. Next steps

Now connect something real and run your first scan:

- **[Connect a cloud account](./cloud-security/account-management.md)** — AWS, Azure, or GCP, for continuous posture scanning.
- **[Run and review scans](./security-scanning/native-scans.md)** — web, network, and API testing.
- **[Work your findings](./vulnerability-risk/vulnerability-management.md)** — triage, prioritize, and track to remediation.
- **[Automate in CI/CD](./security-scanning/scan-management.md)** — gate pipelines on scan results.

:::tip Tip
You can change your **active team** at any time from the account menu in the top-right. Make sure you're in the right team before running scans or reviewing data.
:::
