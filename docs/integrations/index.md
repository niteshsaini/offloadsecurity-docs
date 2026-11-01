---
title: "Integrations & Notifications"
sidebar_label: "Overview"
sidebar_position: 0
description: "Connect the tools around your security program — chat, email and paging for alerts, Jira and GitHub / GitLab Issues for tickets, Splunk and syslog SIEMs for events, Wazuh and Greenbone OpenVAS for data — from one catalog with a five-step wizard, and know exactly what each connection does once it is green."
---

# Integrations & Notifications

Offload Security is the system of record for posture, findings, risk and compliance; integrations are how that record reaches the tools your team already lives in — and how a few outside tools feed data back in. Every catalog connection is made from one place, follows the same five-step wizard, and is labelled with what actually happens after it turns green.

**Where:** left navigation → *Management* → **Integrations**.

![Integrations hub: available integrations, connected tools, open-source and category counts; the eight integration categories; search](/img/screenshots/integrations/integrations-hub.webp)

## What an integration does

Not every connection means the same thing. Each card in the catalog carries a **capability badge**, and it is worth reading before you connect:

| Badge | Meaning | Tools |
| --- | --- | --- |
| **pulls data in** | The platform syncs data *from* the tool into its own views | Wazuh (agents → assets, host CVEs → vulnerability occurrences, alerts → Alerts), Greenbone OpenVAS (scan results → vulnerability occurrences), SonarQube (project and open-issue snapshot), Jenkins (job summary) |
| **two-way** | Data flows both directions | Jira — tickets are created from findings, and ticket status closes or reopens the finding |
| **sends out** | The platform pushes alerts, events or documents *to* the tool | Slack, Microsoft Teams, Google Chat, SMTP Email, PagerDuty, Confluence, Splunk, Syslog / CEF, GitHub Actions (pipeline configuration) |
| **connection test only** | The connection is verified and recorded; no data flows | OWASP ZAP, Burp Suite, Nuclei, Snyk, CloudMapper, AWS Security Hub, Prowler |
| **catalog only** *(shown as Planned)* | Listed for roadmap visibility; no Connect | PentestGPT, CodeQL, Datadog, Grafana, ServiceNow |

Scanners in the *connection test only* group that the platform already **runs natively** — ZAP, Nuclei and Prowler — are built-in scan engines; the catalog entry only verifies a remote instance you may run elsewhere. Snyk, Burp Suite, CloudMapper and Security Hub are verified, but their findings are not imported.

Planned tools are hidden by default; the note above the cards counts them and **Show planned** lists them.

![Catalog cards with capability badges: OWASP ZAP and Nuclei "connection test only", Wazuh "pulls data in", PentestGPT "catalog only · Planned"](/img/screenshots/integrations/integrations-catalog.webp)

## Categories

The category cards filter the catalog; the count on each is the number of tools it holds.

| Category | Tools |
| --- | --- |
| Security Testing | OWASP ZAP, Burp Suite, Nuclei, PentestGPT, Wazuh, Greenbone OpenVAS |
| Code Security | SonarQube, Snyk, CodeQL |
| Cloud Security | AWS Security Hub, Prowler, CloudMapper |
| DevOps & CI/CD | Jenkins, GitHub Actions |
| Monitoring & Analytics | Datadog, Grafana, PagerDuty |
| Ticketing & ITSM | Jira, ServiceNow |
| Collaboration & Notifications | Slack, SMTP Email, Microsoft Teams, Google Chat, Confluence |
| SIEM & SOAR | Splunk, Syslog / CEF |

## The rest of the Integrations page

Above the catalog, three panels are not tied to a single card:

| Panel | What it is |
| --- | --- |
| **Data collection health** | Every connected source — cloud accounts, clusters, registries, threat feeds, integrations, the GitHub App — with whether it is still delivering data, why it stopped, and how to restore it. See [Data Collection Health](./capability-health.md). |
| **Webhooks** | Signed event subscriptions to your own HTTPS endpoints, with a delivery log. See [Webhooks](./webhooks.md). |
| **GitHub & GitLab Issues** | Issues from findings and Wazuh alert groups on your existing Git connections, with two-way status. See [GitHub & GitLab Issues](./git-issues.md). |

## Connect, then verify

1. **Connect** on a card opens the five-step wizard — overview, credentials, a **real** connection test, health-check frequency, review. The test contacts the tool: a Slack, Teams or Google Chat webhook receives a test message, PagerDuty receives a test event that is resolved straight away, a Jira token is checked against `/myself`, an SMTP server is authenticated to. See [Connecting Tools](./connecting-tools.md).
2. A connected card shows **Configured**, its sync status and last sync, and three actions: **Sync now**, **Reconfigure**, **Remove**.
3. **Health checks** re-run the connection test on the cadence you chose in the wizard (hourly by default); a rotated token turns the card from *Connected & healthy* to *disconnected* with the error, and raises an in-app notification. Tools whose only real test is a delivery (Slack, Teams, Google Chat, PagerDuty, Splunk, Syslog / CEF) are not re-tested in the background; their card shows the last real delivery instead.
4. For *pulls data in* tools a **global sync** runs every 30 minutes; **Sync now** starts one immediately as a background job.

![A connected GitHub Actions card: "sends out", Configured, "Connected & healthy — last sync", Sync now / Reconfigure / Remove](/img/screenshots/integrations/integrations-connected-card.webp)

:::note[Team-scoped, encrypted, permissioned]
A connection belongs to the **active team**; another team never sees it and must connect its own. Credentials are encrypted at rest with a key that never leaves the backend (`INTEGRATION_ENCRYPTION_KEY`), and are not shown back after setup. Connecting, testing, reconfiguring and removing need the **Manage Integrations** permission (Admin and Security Manager by default); any team member can see the catalog and the connected state. See [Roles, Teams & API Keys](../authentication/rbac-team-management.md).
:::

## Where notifications come from

Alerts do not need a connected tool to exist — they land in the **in-app notification center** (the bell) for every team member. Connecting Slack, Microsoft Teams, Google Chat, Email or PagerDuty adds a delivery channel; per-team **preferences** decide which channels are on, which categories are muted and the minimum alert severity that leaves the platform (high, by default). Slack additionally supports **routing rules** — critical security alerts to one channel, operational errors to another. All of this is on [Notifications](./notifications.md). For machines rather than people: [Webhooks](./webhooks.md) for your own endpoints, and [SIEM Forwarding](./siem-forwarding.md) for Splunk and syslog SIEMs.

## In this section

| Page | Read it for |
| --- | --- |
| [Connecting Tools](./connecting-tools.md) | The wizard step by step, what each step verifies, managing a connected tool |
| [Notifications](./notifications.md) | Slack, Teams, Google Chat, Email, PagerDuty, the in-app center, routing rules and preferences |
| [Webhooks](./webhooks.md) | Event subscriptions, signature verification, delivery log |
| [SIEM Forwarding](./siem-forwarding.md) | Splunk HEC and Syslog / CEF; the audit-trail export |
| [Jira](./jira.md) · [GitHub & GitLab Issues](./git-issues.md) | Tickets from findings, two-way status sync |
| [Wazuh](./wazuh.md) · [Greenbone OpenVAS](./openvas.md) · [Wazuh + OpenVAS](./wazuh-openvas.md) · [SonarQube](./sonarqube.md) | The data integrations and what each one brings in |
| [Data Collection Health](./capability-health.md) | Which sources stopped delivering data, and how to restore them |
| [Integration Catalog](./third-party.md) | Every tool, its capability, and the credentials it asks for |
| [API](./api.md) · [Troubleshooting & FAQ](./troubleshooting.md) | Endpoints and permissions; common problems |

CI/CD is not an integration card: pipeline gates use the CLI and the GitHub Action — see [CLI & CI/CD](../cli-and-cicd.md). The GitHub App for pull-request scanning is set up under DevSecOps — see [Pull request scanning](../security-scanning/code/pull-request-scanning.md). Cloud accounts and Kubernetes clusters are connected in their own modules — [Connecting Cloud Accounts](../cloud-security/connecting-accounts.md), [Kubernetes onboarding](../security-scanning/kubernetes/onboarding-clusters.md).
