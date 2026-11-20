---
title: "Quickstart: Your First Scan"
sidebar_label: "Quickstart"
sidebar_position: 1
description: "Sign in, run your first scan against one cloud account or one website, and read your first finding in about 15 minutes."
---

# Quickstart — your first scan in about 15 minutes

This guide takes you from "I have access" to "I'm reading my first finding" in one short sitting. Apart from the platform, you need only one target to scan: a cloud account you can connect read-only, or a website you are authorized to test.

:::tip[Self-hosting? Install first]
This quickstart starts from a running platform. If you are installing Offload Security on your own server, run the **[one-file installer](./on-premises/deployment.md#one-file-installer-recommended)** first, then come back when you have:

- **The platform running** — the installer ends by printing the service status, and the UI answers at `https://<your domain>`.
- **The admin sign-in the installer prints** — the login and its generated password (also kept as `DEFAULT_ADMIN_PASSWORD` in the install directory's `.env`). See [First sign-in](./on-premises/deployment.md#first-sign-in).
:::

In about 15 minutes you will:

1. Sign in and get oriented (about 3 minutes).
2. Run your first scan on **one** of two paths (about 5–10 minutes):
   - **Path A — connect one cloud account** (AWS, GCP or Azure, read-only); or
   - **Path B — scan one website** you are authorized to test, if you don't have a cloud account to hand.
3. Open and understand a real finding (about 2 minutes).

Tickets, alert channels and CI/CD gates need access to other systems, so they have their own guide: **[After Your First Scan: Tickets, Alerts and Automation](./adoption/connect-integrations.md)**.

## Before you begin

- **A platform account.** Your administrator provides your login. Viewing findings needs *view* access; starting scans needs the **Security Analyst** role or higher; connecting a cloud account needs **Security Manager** or **Admin**. See [RBAC & Team Management](./authentication/rbac-team-management.md).
- **One scan target**, either:
  - **Path A:** permission to create read-only access in one cloud account:
    - **AWS** — the ability to create a **read-only IAM role** in the target account (the role Offload assumes is read-only; you need IAM access to create it). Ready-to-use Terraform is provided.
    - **GCP** — a role that can create a service account and grant read-only access (Project IAM Admin or Owner).
    - **Azure** — the ability to register an application and assign the **Reader** role on the subscription.

    See [Connecting Cloud Accounts](./cloud-security/connecting-accounts.md) for the exact permissions.
  - **Path B:** the URL of a website or web app **you own or are authorized to test**.
- **Nothing to install** on your workstation. Everyday use is the web app.

:::note[Cloud scans are read-only]
The cloud scan in this guide uses the **read-only** role you create and only *reads* your environment; it creates, changes and deletes nothing. Capabilities that can write, such as cloud remediation, fix pull requests and ticketing, are separate, and each is off by default or waits for an approval. Web, API and network scans send test traffic to their targets. See [What Offload Reads, Tests and Changes](./what-offload-changes.md). If you'd rather start small, scope your first scan to a single non-production account or region.
:::

## 1. Sign in

1. Open the platform URL in your browser — e.g. `https://yourdomain.com` (the address your administrator gave you, or the domain you installed on).
2. Enter your **email** and **password** on the login screen and select **Sign in** — or **Sign in with …** if your organization uses single sign-on. If MFA is enabled on your account, enter the code from your authenticator app.
3. On success you land on the **Dashboard**.

:::note[First administrator]
The first administrator account is created during platform setup, and it is the deployment's **platform admin**. If you installed the platform with the [one-file installer](./on-premises/deployment.md), its first run generates the admin password and prints the login and password when it finishes; both are kept in the install directory's `.env` (`DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD`). Change the password after your first sign-in. You can then invite teammates and assign roles from **Team Management**. Someone you invite as **Admin** becomes an admin of your organization, not a platform admin; see [RBAC & Team Management](./authentication/rbac-team-management.md).
:::

## 2. Tour the dashboard

The Dashboard is a stitched summary of posture across every module, with two tabs: **Security Overview** and **Executive Dashboard**. On a new platform most tiles show **—** or **Not assessed**: the number is unknown because nothing has been scanned yet, never zero. The overview refreshes about every 15 minutes, so a scan that just finished can take a few minutes to appear here; the module pages themselves are live.

![Dashboard, Security Overview tab: overall risk score (unknown until assets are inventoried), active alerts, vulnerabilities, implementation score and assets monitored tiles; Since yesterday counts (new, reopened, newly overdue, resolved, back for review, P1 open); Cloud IAM & Network Posture; risk posture by domain and top risk findings below](/img/screenshots/dashboard.webp)

Three things to know before you scan:

- **Left navigation** groups every module into Core Security, Cloud & Infrastructure, Compliance & Risk, Threat & Intelligence, and Management. Dashboard tiles and coverage cards drill down: clicking one opens the filtered list behind the number.
- **Help on every module.** Each module page has a **Help** button in its header that opens task guides ("How do I…") with prerequisites, steps and common errors.
- **Your active team.** Everything you scan and see belongs to your **active team**; switch it from the account menu in the top-right. Check it before you start a scan.

## 3. Understand the core concepts

Work moves through the platform in one direction:

1. **Scan** — you (or a schedule, or your CI pipeline) run a scan against a target: a cloud account, a container image, a web app, a Kubernetes cluster, or source code.
2. **Finding** — results are normalized into findings with severity, affected resource and remediation guidance, then deduplicated.
3. **Risk** — significant findings (and compliance gaps) can be promoted into the **Risk Register** with treatment plans and SLAs.
4. **Compliance & Reports** — findings map to framework controls, and everything can be exported as an audit-ready report.

Every resource belongs to a **team**, and your **role** in that team decides what you can do there. The full permission matrix is in [Roles, Teams & API Keys](./authentication/rbac-team-management.md).

## 4. Your first scan — a guided walkthrough

Pick **one** path. Each step notes what success looks like and how to confirm it.

### Step 1 — Start a scan

#### Path A: connect a cloud account

1. In **Cloud Security → Cloud Accounts**, select **Add Cloud Account** and follow **[Connecting Cloud Accounts](./cloud-security/connecting-accounts.md)** for your provider (read-only, with copy-paste Terraform). Setup takes about 3 minutes once you have the permissions above.
2. Connecting starts a first posture scan automatically. If it doesn't, start one from the account card in **Cloud Security**, and follow it on the **Cloud Scans** tab.

**Expected result:** the account appears with a **Connected / Active** status and a scan in progress. Within a few minutes findings start to appear, and the scan reaches **Completed** (or **Partial**, if some checks couldn't run). A large account can take longer; the scan runs in the background, so you can carry on.

#### Path B: scan a website you are authorized to test

1. Open **Core Security → Scanning → New scan**.
2. In **Assessment Type**, choose **Security Headers Check (shcheck)**. It needs only a URL and finishes in seconds.
3. Enter the **Target URL**, for example `https://app.example.com`, and launch the scan.
4. The run opens under **Targeted runs**, where it shows as running and then completed.

For a broader first look, choose **Nuclei Vulnerability Scan** with the **Quick** profile instead (1–2 minutes, critical and high templates). Nuclei actively probes the target, so the form asks you to tick **I am authorized to test this target** and keeps the launch button disabled until you do; the attestation is recorded with your name and the time. A full **App Scan** takes longer and is covered in [App Scan](./security-scanning/app-scan.md).

**Expected result:** the run reaches **Completed** with a finding count. Open it from **Targeted runs** to see what ran (tool, version, settings) and its findings — see [Reading a result](./security-scanning/native-scans.md#reading-a-result).

### Step 2 — Understand a finding

- **Path A:** open **[Vulnerability Management](./vulnerability-risk/vulnerability-management/index.mdx)** and select a finding. It shows its severity, the affected resource, remediation guidance, and exploit context (CISA KEV / EPSS where applicable). The same issue found by two scanners appears as **one** deduplicated record.
- **Path B:** select a finding in the run detail. It shows a severity, what was observed, the tool's own proof and the **fix**.

**Expected result:** you can name the affected resource (or URL) and one concrete remediation step.

## You're done when…

- [ ] One scan — a cloud scan or a targeted run — has reached **Completed** and produced findings.
- [ ] You've opened a finding and can name its affected resource and remediation step.

If either box won't check, see [Troubleshooting](./troubleshooting.md).

## Where to next

- **[After Your First Scan: Tickets, Alerts and Automation](./adoption/connect-integrations.md)** — send findings to Jira, post alerts to Slack, Teams or Google Chat, and gate your CI/CD pipelines. Each step lists the third-party access and approvals it needs.
- **[First 7 Days](./adoption/first-7-days.md)** — a day-by-day plan that takes this first scan to an operating program: baseline, prioritization, SLAs, compliance, shift-left, and executive reporting.
- **[Recommended Production Configuration](./adoption/production-configuration.md)** — opinionated starting points for schedules, alerting, and coverage.
- **Role guides:** the [Security Engineer journey](./adoption/security-engineer-journey.md) or the [Compliance Officer journey](./adoption/compliance-officer-journey.md), depending on what you're here to do.
