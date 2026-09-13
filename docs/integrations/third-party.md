---
title: "Integration Catalog"
sidebar_label: "Integration Catalog"
sidebar_position: 9
description: "Every tool in the Integrations catalog — its category, what actually happens once it is connected (pulls data in, two-way, sends out, connection test only, or catalog only), and the exact fields its wizard asks for."
---

# Integration Catalog

Twenty-four tools, eight categories, five kinds of connection. This page is the catalog as the platform ships it, with the one thing a card cannot fit: the exact fields each wizard asks for. For how the wizard works, see [Connecting Tools](./connecting-tools.md); for what the capability words mean, see the [Overview](./index.md#what-an-integration-does).

## Data integrations — *pulls data in* / *two-way*

| Tool | Category | After connecting | Fields |
| --- | --- | --- | --- |
| **Wazuh** | Security Testing | Agents → Asset Inventory and the security graph; alerts → Alerts; host CVEs → vulnerability occurrences; Endpoint Security dashboard. 30-minute sync. [Details](./wazuh.md) | `api_username`\* `api_password`\* `wazuh_host`\* · `wazuh_port` (55000) `verify_ssl` `ca_cert` `indexer_host` `indexer_port` (9200) `indexer_username` `indexer_password` |
| **SonarQube** | Code Security | Snapshot of projects and open vulnerability issues (`GET /api/integrations/data/sonarqube`); issues are not imported as findings. [Details](./sonarqube.md) | `token`\* `server_url`\* · `project_key` `verify_ssl` `ca_cert` |
| **Jenkins** | DevOps & CI/CD | Job summary snapshot on each sync (`GET /api/integrations/data/jenkins`) | `username`\* `api_token`\* `jenkins_url`\* · `verify_ssl` `ca_cert` |
| **Jira** | Ticketing & ITSM | Tickets from critical findings automatically and from high findings on request; status synced both ways every 15 minutes; Jira tab. [Details](./jira.md) | `base_url`\* `auth_email`\* `auth_token`\* · `default_project_key` |

## Outbound integrations — *sends out*

| Tool | Category | After connecting | Fields |
| --- | --- | --- | --- |
| **Slack** | Collaboration & Notifications | Security alerts, scan failures and platform events to the default channel; [routing rules](./notifications.md#routing-rules) per category / severity / source | `webhook_url` (`https://hooks.slack.com/…`) · `default_channel` |
| **Microsoft Teams** | Collaboration & Notifications | Security alerts as cards | `webhook_url`\* |
| **Email (SMTP)** | Collaboration & Notifications | Alert and event email to team members, scheduled reports, invitations — unless the deployment sets `SMTP_HOST` | `smtp_host`\* `smtp_port`\* `smtp_username`\* `smtp_password`\* · `from_email` `use_tls` (true) |
| **PagerDuty** | Monitoring & Analytics | Incidents for the team's alerts (opt-in by connecting; `channels.pagerduty=false` to pause) | `integration_key`\* · `service_name` |
| **Confluence** | Collaboration & Notifications | Compliance summary page published to a space on request (`POST /api/integration-config/confluence/publish-compliance-summary`) | `base_url`\* `auth_email`\* `auth_token`\* · `default_space_key` |
| **GitHub Actions** | DevOps & CI/CD | Records the connection; pipeline scanning itself is configured with the workflow in [CLI & CI/CD](../cli-and-cicd.md) | `github_token`\* · `repository` `workflow_id` |

## Verified connections — *connection test only*

The connection is tested for real and re-checked on the health schedule; **no data is imported**. ZAP, Nuclei and Prowler are engines the platform already runs natively — these entries verify a *separate* instance you operate.

| Tool | Category | The test | Fields |
| --- | --- | --- | --- |
| **OWASP ZAP** | Security Testing | ZAP API version call with the API key | `api_key`\* `zap_host`\* · `zap_port` (8080) `target_url` `verify_ssl` `ca_cert` |
| **Burp Suite** | Security Testing | Burp REST API call with the API key | `api_key`\* `burp_host`\* · `burp_port` (1337) `license_key` `verify_ssl` `ca_cert` |
| **Nuclei** | Security Testing | Confirms the Nuclei engine is available to the platform (Docker image or binary) | `target_url`\* · `template_path` `severity` |
| **Greenbone OpenVAS** | Security Testing | GMP authentication. Results stay in Greenbone. [Details](./openvas.md) | `username`\* `password`\* `gmp_host`\* · `gmp_port` (9390) `verify_ssl` `ca_cert` |
| **Snyk** | Code Security | Snyk REST API `/self` with the token | `api_token`\* · `organization_id` |
| **AWS Security Hub** | Cloud Security | `securityhub:DescribeHub` with the keys | `aws_access_key_id`\* `aws_secret_access_key`\* `region`\* · `aws_session_token` |
| **Prowler** | Cloud Security | `sts:GetCallerIdentity` with the keys — the built-in cloud scanner does not need this; connect real accounts in [Cloud Security](../cloud-security/connecting-accounts.md) | `aws_access_key_id`\* `aws_secret_access_key`\* · `aws_region` `aws_session_token` |
| **CloudMapper** | Cloud Security | `sts:GetCallerIdentity` with the keys | `aws_access_key_id`\* `aws_secret_access_key`\* · `account_id` |

## Catalog only — shown as *Planned*

Listed so you can see the direction; the card has no Connect button.

| Tool | Category |
| --- | --- |
| PentestGPT | Security Testing |
| CodeQL | Code Security |
| Datadog · Grafana | Monitoring & Analytics |
| ServiceNow | Ticketing & ITSM |
| Splunk | SIEM & SOAR |

For a SIEM today, use [webhook subscriptions](./webhooks.md) — signed JSON for every platform event — rather than waiting for a vendor card. **Request Integration** at the bottom of the catalog sends your ask to the product team.

:::note[Fields marked \* are required]
Optional fields show their default in parentheses. `verify_ssl` / `ca_cert` appear on every tool the platform connects to over TLS that might sit behind a private CA; see [Connecting Tools](./connecting-tools.md#step-2--authentication-configuration).
:::

## Related

- [Overview](./index.md) — capability legend and categories.
- [Connecting Tools](./connecting-tools.md) — the wizard and what a connected card shows.
- [Integrations API](./api.md) — list the catalog, connect, sync and remove over the API.
