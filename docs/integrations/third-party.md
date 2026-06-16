---
title: "Third-Party Integrations"
sidebar_label: "Third-Party Integrations"
sidebar_position: 2
---

# Third-Party Integrations

Offload Security connects to the tools your team already uses, so security findings turn into tracked work, alerts reach the right people, and your audit evidence lands where reviewers can see it. You connect each tool once from the **Integrations** area; credentials are stored **encrypted at rest** and isolated to your **active team**.

This page focuses on the integrations that close the loop on a finding: **ticketing**, **SIEM**, **incident response**, and **evidence/audit** systems. (For built-in Email, Slack, and Microsoft Teams alerting, see **[Notifications](./notifications.md)**.)

## What it does

Once connected, third-party tools let you:

- **Open tickets from findings.** Push a vulnerability, misconfiguration, or compliance gap into your tracker as a ticket — with severity, affected resource, and remediation guidance attached.
- **Keep an audit trail.** Two-way status sync records who fixed what and when, so remediation is provable, not just claimed.
- **Forward an immutable log.** Stream audit events and findings to your SIEM as a retained, tamper-evident record for compliance.
- **Page on what matters.** Trigger incidents on critical findings or SLA breaches and route them through your on-call escalation policy.
- **Publish evidence for auditors.** Auto-publish policies, evidence, and audit reports to a documentation space your reviewers can access.

:::note Complementary, not competing
Offload Security integrates with the tooling that *surrounds* a compliance program — ticketing, SIEM, incident response, team chat, and evidence docs. It is itself the audit and compliance system of record, so it does not require a separate compliance-automation platform.
:::

## Available integrations

Browse the full catalog in the **Integrations** area, filtered by category. The systems most relevant to closing out findings and audits are:

| Category | Tools | Typical use |
|---|---|---|
| **Ticketing** | Jira, ServiceNow | Auto-create incident/change tickets from findings; two-way status sync; custom field and project mapping. |
| **SIEM & SOAR** | Splunk, IBM QRadar, Microsoft Sentinel, Splunk Phantom, Wazuh | Forward audit events and findings; correlation/alerting; compliance dashboards. |
| **Incident response** | PagerDuty | Page on critical findings or SLA breaches with an auditable response timeline. |
| **Collaboration & evidence** | Slack, Microsoft Teams, Confluence, SMTP Email | Channel alerts, reviewer sign-off prompts, and published evidence/audit-report pages. |

:::tip There's more in the catalog
The Integrations area also lists vulnerability scanners (Qualys, Tenable, Rapid7), code security (Snyk, SonarQube, Checkmarx, Veracode, GitHub CodeQL), container/cloud security (Aqua, Prisma Cloud, Sysdig, Prowler, AWS Security Hub), DevOps/CI/CD (Jenkins, GitHub Actions), and monitoring (Datadog, Grafana). Each tile shows what the tool does, its setup requirements, and a link to the vendor's documentation.
:::

## How to connect a tool

Connecting any integration follows the same guided, five-step wizard.

1. **Open Integrations** and select **Add Integration** (or pick a tool tile from the catalog).
2. **Select the tool** — for example, Jira, ServiceNow, or Splunk.
3. **Enter credentials.** Each tool asks only for the fields it needs, such as:
   - **Jira** — site URL, account email, and an API token (plus an optional default project key).
   - **ServiceNow** — your instance URL and an OAuth client or API user.
   - **Splunk** — the HTTP Event Collector (HEC) URL and HEC token.
   - **PagerDuty** — an integration (routing) key.
   - **Confluence** — your site URL and an API token.
4. **Test the connection.** The platform makes a live call to the tool to confirm the credentials and reachability before going further. Fix any reported error and re-test.
5. **Configure settings**, then **Complete**. The integration is saved (credentials encrypted), marked active, and begins routing data per your settings.

After setup, the platform runs **periodic health checks** on each active integration and shows its current status, so a broken token or expired credential surfaces before you rely on it.

:::note You need the right role
Adding, editing, or removing integrations requires the **Manage Integrations** permission — typically held by **Admin** and **Security Manager** roles. Other roles can view connected tools and their status.
:::

## Tips & prerequisites

:::tip Use least-privilege credentials
Create a dedicated service account or scoped API token for each tool, with only the access Offload Security needs (for example, permission to create issues in a single Jira project). Rotate tokens on your normal schedule — the integration's health status will flag a credential that has stopped working.
:::

:::warning Integrations are team-scoped
An integration you connect belongs to your **active team** and is not visible to other teams. Confirm you're in the correct team (top-right account menu) before connecting a tool, and connect it again in each team that needs it.
:::

:::note Credential security
All integration credentials are encrypted at rest. The connection test never stores credentials until the integration is saved, and tokens are never shown back to you in plain text after setup.
:::

## Related

- **[Integrations & Notifications](./index.md)** — overview of the connectivity layer.
- **[Notifications](./notifications.md)** — built-in Email, Slack, and Microsoft Teams alerting and routing.
- **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)** — connect AWS, Azure, and GCP for posture scanning.
- **[Getting Started](../getting-started.md)** — teams, roles, and the Scan → Finding → Risk → Report flow.
