---
title: "Integrations Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 14
description: "Fix the common problems with integrations and notifications — a connection test that fails on a private address, a card that says Connected while nothing arrives, Slack that goes to the wrong channel, email that ignores the team's SMTP, webhooks that never fire, SIEM forwarding that falls behind — and answers to frequent questions."
---

# Integrations Troubleshooting & FAQ

## Connecting

**The connection test says "Server URL is not allowed … (SSRF protection)".**
The address is loopback, link-local or cloud-metadata — those are never allowed; use the tool's real host name or IP — or it is a private address on a deployment that set `ALLOW_PRIVATE_INTEGRATION_TARGETS=false`. Private ranges (`10/8`, `172.16/12`, `192.168/16`) are allowed by default because on-premises tools live on the LAN; ask your administrator whether the setting was turned off.

**"… is a catalog entry only: no connection test or data exchange is implemented yet. Nothing was stored."**
The tool is *Planned* (PentestGPT, CodeQL, Datadog, Grafana, ServiceNow). It cannot be connected; see the [Integration Catalog](./third-party.md).

**"INTEGRATION_ENCRYPTION_KEY is required to encrypt integration credentials …"**
The deployment has no credential encryption key, so nothing can be saved safely. The administrator must set it. If the key is lost or replaced, saved integration credentials can no longer be read and every integration must be reconfigured (Git tokens use a separate key and are not affected).

**"Invalid session ID" during setup.**
The setup was left open for more than two hours, so its session — and the values typed into it — were deleted. Close the wizard and start again.

**"Connection Not Verified" after Complete Setup.**
The configuration was saved, but the server-side re-test failed (fields can change between the wizard's test and completion). Use **Reconfigure** with corrected values.

**Wazuh: "Partially Connected" — Manager connected, Indexer unreachable.**
Agents will sync; alerts and vulnerabilities will not. On a single-node deployment leave the indexer fields blank (Manager host on `9200` with the API credentials is assumed); on a split deployment fill `indexer_host` and its own credentials. Accept the warning only if you knowingly run Manager-only.

**Greenbone OpenVAS: connection refused or timeout.**
The integration speaks GMP over TLS on port **9390**, not the web UI on 9392. Check that gvmd's GMP is exposed on that host and port — the bundled `docker-compose.openvas.yml` provides the TLS bridge — and that firewalls allow it. See [OpenVAS](./openvas.md).

**Jira: "default_project_key is required" or "Jira not configured or ticket creation failed".**
The project key is required. A Jira connection saved before it became required may have none: **Reconfigure** and enter a project the Jira user can create issues in.

**Microsoft Teams: "Teams webhook returned HTTP 404 … older *.logic.azure.com Workflows URL".**
Microsoft moved Workflows webhooks to new URLs. Open the workflow in Teams, copy the current URL from its webhook trigger, and **Reconfigure**.

**Microsoft Teams: test says "accepted" but no card appears.**
A Workflows webhook accepts the request before the workflow runs. Open the workflow's run history in Teams or Power Automate; the *Post card* step shows why it failed (for example, the workflow's owner left the channel).

**Google Chat: "Google Chat webhook URL rejected: …".**
Copy the whole webhook URL from the space's Webhooks settings, including its `key` and `token`.

**PagerDuty: "PagerDuty rejected the test event (HTTP 400)".**
The integration key is wrong or belongs to a service without an Events API v2 integration. Copy it from the service's Integrations tab. *"Test event accepted … but resolving it failed"* means the key works — resolve the *connection test* incident by hand.

**SMTP test fails with "STARTTLS extension not supported" or "535 authentication failed".**
The first means the relay has no STARTTLS — set `use_tls` to `false`. The second is the credential: Gmail and Microsoft 365 need an **app password**, not the account password.

## Connected, but nothing happens

**The card says Connected, but Slack / Teams / Google Chat / PagerDuty never receive anything.**
Check in this order: the team's [preferences](./notifications.md#preferences) and **Alerts → Delivery settings** (channel switched off? category muted?), the alert threshold (`alerts.min_severity`, high by default — a medium alert never leaves the platform), then the Slack routing rules (a rule with the wrong webhook captures the alert). The card of a delivery-tested tool shows the last real delivery and its error.

**Slack messages arrive in the default channel, not the one my rule names.**
A rule matches on `category` first. Security findings are `security_alert`; scan failures and integration problems are `system_error` / `system_notification`. Check the rule's `enabled`, `severities` and `sources` — an empty list matches all, a non-empty list must contain the alert's value exactly (`cspm`, not `aws`).

**A chat message ends with "… (truncated — open in Offload for the full text)".**
Slack, Teams and Google Chat messages are limited to 2,000 characters. Open the item in the platform; the button to it appears only when `PUBLIC_APP_URL` is set.

**Team SMTP is configured but mail goes through a different server (or none).**
The deployment's `SMTP_HOST` / `SMTP_SERVER` wins over any team configuration and the log says `environment sets SMTP_HOST … which takes precedence`. Unset it on multi-team installs.

**Jira connected, no tickets appear.**
Tickets are automatic for **critical** findings only (at most 50 new tickets per sync); others are created on request. Check that the account can create issues in `default_project_key`, then `GET /api/integrations/jira/tickets`.

**Resolving a finding does not close the Jira ticket.**
The platform tries the transitions `Done`, `Resolve`, `Close` in that order; a custom workflow needs `JIRA_RESOLVED_TRANSITION="Fixed,Closed"` (and `JIRA_REOPENED_TRANSITION`) on the backend. The log lists the names tried.

**A GitHub or GitLab issue was closed but the finding is still open.**
An issue closed as *not planned* never resolves its finding; a person decides in the platform. Otherwise status is read every 15 minutes (200 issues per provider per run) — click **Refresh statuses**. See [GitHub & GitLab Issues](./git-issues.md).

**My webhook subscription receives nothing for some event types.**
`scan.failed`, `scan.progress`, `finding.updated`, `finding.resolved` and `finding.reopened` are listed but not published in 1.4.0. Use `alert.*` events, or [SIEM Forwarding](./siem-forwarding.md) for finding lifecycle changes.

**A webhook reads "Disabled automatically".**
Its endpoint failed every delivery for at least 24 hours (50 or more attempts in a row). Fix the receiver, then click **Enable**; send a test event to check.

**"Webhook URL not allowed: …" or "webhook URL must use https://".**
Webhooks are HTTPS only. Loopback and cloud-metadata are always refused; a private-network endpoint needs `ALLOW_PRIVATE_WEBHOOK_TARGETS=true` on the backend (off by default — separate from the integration setting).

**My receiver rejects every signature after the upgrade to 1.4.0.**
Deliveries are signed with `X-Offload-Signature-V1` over the timestamp and body — see [Verify the signature](./webhooks.md#verify-the-signature). While you update the receiver, `NOTIFICATION_WEBHOOK_LEGACY_SIGNATURE=true` restores the old untimestamped header (deprecated).

**A webhook delivery fails with no HTTP code.**
The endpoint did not answer within 10 seconds, could not be reached, or redirected (redirects are never followed). The delivery is retried after 5 s, 30 s and 120 s; the delivery log shows each attempt and its error.

**Splunk / Syslog card shows a red "event(s) were not forwarded" box.**
Finding events were dropped from a full queue (10,000 per destination), rejected by the receiver, or belonged to an older configuration. Fix the receiver; new events flow again. See [SIEM Forwarding](./siem-forwarding.md#if-something-goes-wrong).

**GitHub App shows Connected, but pull requests are not scanned.**
Open DevSecOps → **GitHub App** → **Webhook deliveries**: it reads GitHub's own delivery results and names the cause — a 401 is a webhook secret mismatch, a 404 a wrong URL path, no response a firewall, DNS or timeout problem. See [Pull request scanning](../security-scanning/code/pull-request-scanning.md).

## Sync and health

**"Sync status: disconnected" after it was healthy.**
The stored credentials no longer work (rotated token, revoked API user) or the host is unreachable from the platform; the health check writes the tool's error. **Reconfigure** with the new credential. [Data Collection Health](./capability-health.md) lists every source in this state with restore steps.

**"Some data could not be fetched" on a card.**
Part of the sync failed; the named dataset and its error say which. For Wazuh this is usually the Indexer; for OpenVAS a *partial* dataset means not every report was read, and nothing was resolved on its basis.

**Sync now returns a job id and the card does not change.**
Syncs run as background jobs; the card refreshes when the job finishes (Wazuh with many agents can take a minute). `GET /api/jobs/{job_id}` shows progress; a failed job carries the reason.

**The health check frequency I chose is not what I see in the logs.**
Two schedules exist: the frequency from the wizard drives the per-connection health check; the 30-minute global sync additionally re-tests every *pulls data in* connection. Both write the same status fields, so a failure surfaces at whichever runs first.

## Frequently asked questions

**Does a connection test store my credentials?**
No. The wizard's test and `POST /api/integrations/test-connection` store nothing. Credentials are saved — encrypted — only on **Complete Setup**.

**Can two teams share one Slack webhook or Jira project?**
Each team connects its own; nothing is shared across teams by design. The same webhook URL may be entered in both.

**Which integrations import findings?**
Wazuh (host vulnerability state) and Greenbone OpenVAS (scan results) create vulnerability occurrences. SonarQube and Jenkins keep snapshots; the *connection test only* tools import nothing. Use the [Vulnerabilities API](../vulnerability-risk/api.md) to import from a tool that is not in the catalog.

**Where is the CI/CD integration?**
Pipeline gating uses the CLI and the GitHub Action, not a catalog card — see [CLI & CI/CD](../cli-and-cicd.md). The GitHub Actions card only records that you use it.

**How do I send everything to my SIEM?**
For Splunk or any syslog / CEF receiver (QRadar, ArcSight, …), connect it under *SIEM & SOAR* — see [SIEM Forwarding](./siem-forwarding.md). For anything that accepts HTTPS JSON, use a [webhook subscription](./webhooks.md). To pull the audit trail, use `GET /api/audit-trail/export/siem`.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment. When contacting support include the tool id, the exact connection-test message, the `integration_id` from `GET /api/integrations/user-integrations`, and — for webhooks — the `subscription_id` and a delivery `event_id`.
