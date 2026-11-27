---
title: "After Your First Scan: Tickets, Alerts and Automation"
sidebar_label: "Tickets, Alerts & Automation"
sidebar_position: 1.5
description: "Send findings to Jira, deliver alerts to Slack, Teams, Google Chat or a webhook, and gate CI/CD pipelines on scan results, with the third-party access each step needs."
---

# After Your First Scan: Tickets, Alerts and Automation

Once the **[Quickstart](../getting-started.md)** has produced findings, this guide connects them to the tools your team already works in: a ticket for each finding that needs fixing, a channel post when something important appears, and a pipeline gate so the scan runs on every build. Each step is independent; do them in any order, or skip the ones you don't use.

Unlike the quickstart, these steps reach outside the platform. Allow time to get third-party credentials and any approvals your organization needs before you start.

## Before you begin

- **A completed scan with findings** in your active team (see the [Quickstart](../getting-started.md)).
- **The Manage Integrations permission** (the **Admin** or **Security Manager** role) to connect Jira, chat channels and webhooks, and to change alert delivery settings. See [RBAC & Team Management](../authentication/rbac-team-management.md).
- **Third-party access**, listed under each step below. Requests for a service account, an API token or a new chat webhook often need an administrator on the other side to approve them.

## Steps

### Step 1 — Create remediation tickets

**You need:**

- In Jira Cloud: a dedicated account that can create and transition issues in the target project, an **API token** for it, and the **project key** tickets go into (for example `SEC`). Creating the account or token may need approval from your Jira administrator.
- In Offload Security: **Manage Integrations** to connect Jira; the **Vulnerability Management** permission to create tickets on request.

1. **Connect Jira.** Open **Integrations → Jira → Connect** and enter your Jira site URL, the account email and API token, and the **default project key**. A connection without a project key creates no tickets. See [Jira](../integrations/jira.md).
2. **Create tickets.** Critical findings get a ticket automatically once Jira is connected. For others, select the occurrences under **Vulnerability Management → All Occurrences** and create Jira tickets for them.

GitHub Issues and GitLab Issues can also be connected as ticketing targets; see [GitHub & GitLab Issues](../integrations/git-issues.md).

- **Expected result:** a Jira issue is created and linked to the finding.
- **Verify:** the finding shows its ticket key, and the **Jira** tab in Vulnerability Management lists it; when the ticket is closed in Jira the finding resolves within 15 minutes.

### Step 2 — Configure an alert channel

**You need:**

- On the chat side, permission to add an incoming webhook to the channel or space: the *Incoming Webhooks* app in **Slack**, a channel **Workflow** in **Microsoft Teams**, or **Apps & integrations → Webhooks** in a **Google Chat** space. Some workspaces only let administrators add these.
- For a SIEM or other system, an **HTTPS** endpoint the platform server can reach.
- In Offload Security: **Manage Integrations**.

1. **Connect a channel.** Connect **Slack**, **Microsoft Teams** or **Google Chat** under **Integrations** — the connection test posts a message to the channel — or set up a [webhook subscription](../integrations/webhooks.md) for your SIEM.
2. **Choose what is delivered.** Choose the minimum severity and channels under **Alerts → Delivery settings**. See [Notifications](../integrations/notifications.md).

- **Expected result:** new or reopened alerts at or above the delivery severity (high by default) reach the channel; every alert appears in the bell and in **Alerts** regardless. Email is sent as a daily digest, not per alert.
- **Verify:** the wizard's test message arrived; the next high or critical finding produces a channel post.

### Step 3 — Then automate it

**You need:**

- An Offload Security **API key** (creating one needs **Manage Integrations**). See [Roles, Teams & API Keys](../authentication/rbac-team-management.md).
- Permission to edit the pipeline in your CI system (for example, to add a workflow step and a secret in GitHub), which may need approval from the repository owner.

Once the manual path works, **[gate your CI/CD pipelines](../cli-and-cicd.md)** on scan results so the scan runs on every build. The pipeline uses plain `curl` against the REST API, or the GitHub Action; there is no CLI or agent to install.

## Check that it worked

- [ ] A finding is linked to a Jira ticket (or you've consciously skipped ticketing for now).
- [ ] A notification channel (Slack, Teams, Google Chat, or webhook) received a test message.
- [ ] A pipeline run shows the scan result, and fails when the severity threshold is breached.

## If something goes wrong

- **The Jira connection saves but no tickets appear** — the connection has no default project key. **Reconfigure** it and enter one.
- **No Slack test message arrives** — the webhook URL is wrong; the connection test shows the HTTP error. Copy the URL again from Slack.
- For more, see [Integrations troubleshooting](../integrations/troubleshooting.md).

## Next steps

- **[First 7 Days](./first-7-days.md)** — turn your first scan into an operating program.
- **[Recommended Production Configuration](./production-configuration.md)** — starting points for alerting, ticketing and schedules.
