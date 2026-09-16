---
title: "Integrations Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 11
description: "Fix the common problems with integrations and notifications — a connection test that fails on a private address, a card that says Connected while nothing arrives, Slack that goes to the wrong channel, email that ignores the team's SMTP, webhooks that never fire — and answers to frequent questions."
---

# Integrations Troubleshooting & FAQ

## Connecting

**The connection test says "Server URL is not allowed … (SSRF protection)".**
The address is loopback, link-local, cloud-metadata, or a private range. The first three are never allowed. Private ranges (`10/8`, `172.16/12`, `192.168/16`) are allowed only when the deployment sets `ALLOW_PRIVATE_SCAN_TARGETS=true` — the normal setting for an on-premises install whose Wazuh, Jenkins or SonarQube lives on the LAN. Set it on the backend and retry; nothing else changes.

**Connect on Microsoft Teams or PagerDuty fails immediately.**
Fixed in the current release — earlier builds had no wizard template for either (the error read "Unknown tool", reported as a 500). Upgrade; both connect through the normal wizard now.

**The ZAP / Burp / Security Hub test fails whatever I enter.**
Older builds read `server_url` for ZAP and Burp (defaulting to localhost, which the SSRF guard then blocked) and the wrong key names for Security Hub. Fixed in the current release; the wizard's own fields are used.

**The Slack, Teams or SMTP test passed but the webhook / mail server was wrong.**
An older build reported success for these three without contacting anything ("configuration saved"). The current release posts a real test message (Slack, Teams) or authenticates to the server (SMTP); re-run **Reconfigure** and the test will tell you.

**Wazuh: "Manager connected, Indexer unreachable" warning.**
Agents will sync; alerts and vulnerabilities will not. On a single-node deployment leave the indexer fields blank (Manager host on `9200` with the API credentials is assumed); on a split deployment fill `indexer_host` and its own credentials. Accept the warning only if you knowingly run Manager-only.

**SMTP test fails with "STARTTLS extension not supported" or "535 authentication failed".**
The first means the relay has no STARTTLS — set `use_tls` to `false` (older builds ignored that value; fixed). The second is the credential: Gmail and Microsoft 365 need an **app password**, not the account password.

## Connected, but nothing happens

**The card says Connected & healthy, but Slack / Teams / PagerDuty / Jira / SMTP never receive anything.**
In older builds several senders read only the configuration written by the `/integration-config` API and never the hub's wizard store, so a tool connected in the hub was inert. Fixed in the current release: every sender falls back to the hub connection. If you are current, check in this order: the team's [preferences](./notifications.md#preferences) (channel switched off? category muted?), the alert threshold (`alerts.min_severity`, high by default — a medium alert never leaves the platform), then the Slack routing rules (a rule with the wrong webhook captures the alert).

**Slack messages arrive in the default channel, not the one my rule names.**
A rule matches on `category` first. Security findings are `security_alert`; scan failures and integration problems are `system_error` / `system_notification`. Check `GET /api/notifications/slack/routing` for the rule's `enabled`, `severities` and `sources` — an empty list matches all, a non-empty list must contain the alert's value exactly (`cspm`, not `aws`).

**Slack posts a test message every 30 minutes.**
An older build re-ran the delivery test as part of the global sync. Fixed: Slack and Teams keep their last real test result and are not re-posted by background checks.

**Team SMTP is configured but mail goes through a different server (or none).**
The deployment's `SMTP_HOST` / `SMTP_SERVER` wins over any team configuration and the log says `environment sets SMTP_HOST … which takes precedence`. Unset it on multi-team installs.

**Jira connected in the hub, no tickets appear.**
Tickets are automatic for **critical** findings only (high ones are created on request from Raw Findings). Check the account can create issues in `default_project_key`, then `GET /api/integrations/jira/tickets`. Older builds only read a Jira configured through `/integration-config/jira`; fixed.

**Resolving a finding does not close the Jira ticket.**
The platform tries the transitions `Done`, `Resolve`, `Close` in that order; a custom workflow needs `JIRA_RESOLVED_TRANSITION="Fixed,Closed"` (and `JIRA_REOPENED_TRANSITION`) on the backend. The log lists the names tried.

**My webhook subscription never receives events (only the test works).**
Older builds never connected subscriptions to the platform's event bus — only the test button delivered. Fixed in the current release; every team-scoped event fans out. Also check that your `events` list contains types the platform publishes (`GET /api/webhooks/event-types/list`); `finding.excepted` and `user.login` were never emitted and have been removed from the catalogue.

**A webhook delivery shows `success: false` with status 0.**
The endpoint did not answer within 10 seconds, or its address failed the connection-time safety check (DNS rebinding to a private IP). The delivery is retried after 5 s, 30 s and 120 s; check `deliveries` for the final status.

**The Integrations hub shows "1 planned" while six cards say Planned, or a category with 0 tools.**
Both fixed in the current release — stats and categories are derived from the catalog. Cosmetic; nothing to change on your side.

## Sync and health

**"Sync status: disconnected" with an empty reason after it was healthy.**
The stored credentials no longer work (rotated token, revoked API user) or the host is unreachable from the platform; the next health check writes the tool's error. **Reconfigure** with the new credential.

**Sync now returns a job id and the card does not change.**
Syncs run as background jobs; the card refreshes when the job finishes (Wazuh with many agents can take a minute). `GET /api/jobs/{job_id}` shows progress; a failed job carries the reason.

**The health check frequency I chose is not what I see in the logs.**
Two schedules exist: the frequency from the wizard drives the per-connection health check; the 30-minute global sync additionally re-tests every *pulls data in* connection. Both write the same status fields, so a failure surfaces at whichever runs first.

## Frequently asked questions

**Does a connection test store my credentials?**
No. Credentials are saved — encrypted — only on **Complete Setup**, and the completion re-runs the test server-side. A test that fails saves nothing.

**Can two teams share one Slack webhook or Jira project?**
Each team connects its own; nothing is shared across teams by design. The same webhook URL may be entered in both.

**Which integrations import findings?**
Wazuh (host vulnerability state → occurrences) is the only one that creates findings today. SonarQube and Jenkins keep snapshots; the *connection test only* tools import nothing. Use [webhook subscriptions](./webhooks.md) to export, and the [Vulnerabilities API](../vulnerability-risk/api.md) to import from a tool that is not in the catalog.

**Where is the CI/CD integration?**
Pipeline gating uses the CLI and the GitHub Action, not a catalog card — see [CLI & CI/CD](../cli-and-cicd.md). The GitHub Actions card only records that you use it.

**How do I send everything to my SIEM?**
A webhook subscription with `events: ["*"]` and a signing secret — see [Webhooks](./webhooks.md). Splunk, Sentinel and QRadar all accept HTTP JSON collectors.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment. When contacting support include the tool id, the exact connection-test message, the `integration_id` from `GET /api/integrations/user-integrations`, and — for webhooks — the `subscription_id` and a delivery `event_id`.
