---
title: "Getting Started"
sidebar_label: "Getting Started"
sidebar_position: 1
---

# Getting Started

This guide gets you from "I have access" to "I'm reviewing my first findings." It assumes the platform is already deployed and you have an account.

:::info[Before you begin]
A quick checklist so your first scan goes smoothly:

- **A platform account.** Your administrator provides your login. What you can do depends on your role — viewing findings needs *view* access, while connecting accounts and starting scans needs *management* access. See [RBAC & Team Management](./authentication/rbac-team-management.md).
- **Permission to connect your first cloud account** — the main setup step:
  - **AWS** — the ability to create a **read-only IAM role** in the target account (the role Offload assumes is read-only; you need IAM access to create it). Ready-to-use Terraform is provided.
  - **GCP** — a role that can create a service account and grant read-only access (Project IAM Admin or Owner); organization onboarding needs organization-level access.
  - **Azure** — the ability to register an application and assign the **Reader** role on the subscription.

  See [Connecting Cloud Accounts](./cloud-security/connecting-accounts.md) for the exact permissions and copy-paste setup.
- **Nothing to install.** There is no CLI or agent to download — everyday use is the web app, and CI/CD integration uses plain `curl` / the REST API or the [GitHub Action](./cli-and-cicd.md). (Deploying the platform itself is a separate operator task — see [On-Premises](./on-premises/index.mdx).)
- **Time to value:** connecting your first cloud account takes about **3 minutes**; the first scan then runs in the background.
:::

:::tip[Scans are read-only — you won't touch production]
Every scan uses **read-only** credentials and only ever *reads* your environment; Offload never changes anything in your cloud. There's no separate sandbox to configure — but if you'd rather start small, scope your first scan to a single non-production account or region.
:::

## 1. Sign in

1. Open the platform URL in your browser — e.g. `https://yourdomain.com` (the address your administrator gave you).
2. Enter your **email** and **password** on the login screen and select **Sign in**.
3. On success you land on the **Dashboard**.

:::info[First administrator]
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

## 4. Your first scan — a guided walkthrough

Follow this end-to-end path to go from a connected environment to a tracked, alerted finding. Each step notes **what success looks like** and **how to confirm it** in the product.

### Step 1 — Connect a cloud account
In **Cloud Security → Cloud Accounts**, select **Add Cloud Account** and follow **[Connecting Cloud Accounts](./cloud-security/connecting-accounts.md)** for your provider (read-only, with copy-paste Terraform).
- **Expected result:** the account appears with a **Connected / Active** status, and a first scan starts automatically.
- **Verify:** the account is listed as Connected, and you can see a scan in progress with a scan run ID.

### Step 2 — Run and watch a scan
The first scan runs on connect; you can also start one at any time, or run a **[native web / API / network scan](./security-scanning/native-scans.md)** against a target you own.
- **Expected result:** the scan reaches **Completed** (or **Partial**, if some checks couldn't run), and findings appear.
- **Verify:** on the **Scans** page the status shows Completed with a finding count — open it to see the results.

### Step 3 — Understand a finding
Open **[Vulnerability Management](./vulnerability-risk/vulnerability-management.mdx)** and select a finding.
- **Expected result:** the finding shows its severity, the affected resource, remediation guidance, and exploit context (CISA KEV / EPSS where applicable).
- **Verify:** you can see the affected asset and a concrete remediation step — and the same issue found by two scanners appears as **one** deduplicated record.

### Step 4 — Create a remediation ticket
With **[Jira connected](./integrations/third-party.md)**, push a finding to your tracker.
- **Expected result:** a Jira issue is created and linked to the finding.
- **Verify:** the finding shows a linked ticket, and its status stays in sync as the ticket moves.

### Step 5 — Configure an alert
Set up **[notifications](./integrations/notifications.md)** to Slack, Microsoft Teams, email, or a webhook.
- **Expected result:** new or reopened high-severity findings notify your channel.
- **Verify:** send a test (or trigger a finding) and confirm the message arrives — the alert also appears in **Alerts**.

### Then automate it
Once the manual path works, **[gate your CI/CD pipelines](./cli-and-cicd.md)** on scan results so this runs on every build.

:::tip[Tip]
You can change your **active team** at any time from the account menu in the top-right. Make sure you're in the right team before running scans or reviewing data.
:::
