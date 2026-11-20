---
title: "Notifications"
sidebar_label: "Notifications"
sidebar_position: 2
description: "Where alerts go — the in-app notification center, Slack, Microsoft Teams, Google Chat, email (SMTP) and PagerDuty — how each channel is configured, which events fire out of the box, Slack routing rules, and the per-team preferences that decide channels, muted categories and the minimum severity that leaves the platform."
---

# Notifications

A finding nobody hears about is a finding nobody fixes. Offload Security raises notifications for the events that need a human — new critical and high findings, SLA warnings and breaches, compliance drift, scan and integration failures — and delivers them to the **in-app notification center** always, and to **Slack, Microsoft Teams, Google Chat, email and PagerDuty** when a team connects them. What leaves the platform, and where, is decided per team.

## Channels at a glance

| Channel | Configured where | Receives |
| --- | --- | --- |
| **In-app** (bell) | Nothing to configure | Every notification for the team; per-user read / dismiss state |
| **Slack** | Integrations → **Slack** (incoming webhook) · optional routing rules | Security alerts, scan failures and platform events; per-rule channels by category, severity and source |
| **Microsoft Teams** | Integrations → **Microsoft Teams** (Workflows webhook, or a legacy Office 365 connector URL) | Alerts and notifications as cards |
| **Google Chat** | Integrations → **Google Chat** (space incoming webhook) | Every notification that goes to Slack or Teams, as cards |
| **Email (SMTP)** | Integrations → **SMTP Email**, or the deployment's `SMTP_*` environment | Notification email to team members, scheduled reports, invitations, assessment reminders, the daily SOC digest |
| **PagerDuty** | Integrations → **PagerDuty** (Events API v2 integration key) | Incidents for alerts, once the team has connected it |
| **Webhooks** | Integrations → **Webhooks** — see [Webhooks](./webhooks.md) | Signed JSON for every platform event you subscribe to |

All channels are **team-scoped**: a webhook or mail server connected by one team is never used for another team's notifications. A team's notification never falls back to the deployment's environment-level channels either — those serve only platform events that have no team (see [Operator channels](#operator-channels)).

:::note[Who can configure this]
Connecting channels and changing team preferences require **Manage Integrations**. Every member can read their notifications and set their own opt-out.
:::

## What fires out of the box

Without any rule or preference, a team receives:

| Event | Condition | Channels |
| --- | --- | --- |
| **Security alert** (new or reopened) | Severity **high or above** — the threshold is `alerts.min_severity` in the team's preferences, `ALERT_NOTIFY_MIN_SEVERITY` for the deployment | In-app, Slack, Teams, Google Chat — and PagerDuty / webhook when the team has enabled them |
| **New critical / high finding** | From cloud scans and real-time cloud events; collapsed to at most one notification per team and severity per window, so a scan does not produce one message per finding | In-app; a Slack `security_alert`; for **critical**, a Jira ticket when Jira is connected |
| **SLA warning / breach** | From [SLA Management](../vulnerability-risk/sla-management.md) | In-app, email, Slack, Teams, Google Chat |
| **Compliance drift / threshold breached** | From [Drift Detection](../compliance/drift-detection.md) | In-app, email |
| **Scan failed** | Failure classified (connectivity, credentials, tool error, timeout, permission) with a remediation hint | In-app, email, Slack |
| **Platform event** — integration unhealthy, certificate expiring, worker down | Raised by the health checks and monitors | In-app always; Slack as `system_error` (critical / high) or `system_notification`; email to `ADMIN_EMAIL` for critical / high |

Email respects each member's opt-out; the bell is the place everyone sees everything. Individual alerts are not emailed one by one — email carries digests, invitations and system notifications.

## The in-app notification center

**Where:** the bell in the top bar; the badge is the unread count.

Every notification for the team is listed newest first with its priority, title, message and — when there is somewhere to go — an action link. **Mark read**, **mark all read** and **dismiss** are per user, so one analyst clearing the list does not clear it for the team. Notifications expire after their retention window; the API (`GET /api/notifications?unread_only=true`) returns the same list for scripts and dashboards.

## Slack

**Connect:** Integrations → **Slack** → **Connect** → paste the **incoming webhook URL** (from Slack's *Incoming Webhooks* app) and optionally a bot token and a default channel name. The connection test **posts a message to the channel** — if it does not arrive, the webhook is wrong, and the test says so (`Webhook returned HTTP 404: no_service`). Webhook URLs must be `https://hooks.slack.com/…` (or a host you allow with `SLACK_WEBHOOK_ALLOWED_HOSTS`).

That webhook is the **default channel**: every Slack-bound notification for the team goes there unless a routing rule claims it.

### Routing rules

Routing rules send different classes of notification to different Slack channels.

**Where:** **Alerts** → **Delivery settings** → *Slack routing rules* (add and delete rules; changing them needs Manage Integrations). The same rules are available over the API at `/api/notifications/slack/routing`. The fields:

| Field | Values |
| --- | --- |
| `name` | Label for the rule |
| `category` | `security_alert` (findings from cloud, Kubernetes, registry and code scanning) · `system_notification` (scan completions, scheduled-job results, configuration changes) · `system_error` (service degradation, task failures, connectivity) |
| `severities` | Optional list — `critical`, `high`, `medium`, `low`, `info`; empty matches all |
| `sources` | Optional list of modules — `cspm`, `kubernetes`, `container_security`, `registry`, `code_scan`, `iac_scan`, `compliance`, `sla`, `threat_intelligence`, `vulnerability`, `integration`, `system`, … (`GET /api/notifications/slack/categories` lists them) |
| `webhook_url` · `channel_name` | The target channel's incoming webhook and display name |
| `priority` | Optional number, default `100`; lower wins ties |

```bash
curl -X POST "$OFFLOAD_HOST/api/notifications/slack/routing" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"name":"Critical security","category":"security_alert",
       "severities":["critical","high"],
       "webhook_url":"https://hooks.slack.com/services/T000/B000/XXXX",
       "channel_name":"#security-critical"}'
```

A notification is matched against the team's enabled rules only — never another team's or a global rule. The most specific rule wins: category + severity + source first, then category + severity or category + source (equally specific; the lower `priority` number wins), then category alone. Anything unmatched falls back to the team's default channel. `POST …/slack/test` `{webhook_url, channel_name}` posts a test message; `GET …/slack/status` reports whether a default webhook is configured, the rule count and the channels in use. Rules show the webhook **masked**.

Routing rules apply to Slack only; Teams and Google Chat always use the one webhook connected in Integrations.

:::tip[A three-channel starting point]
`security_alert` + `critical, high` → `#security-critical`; `system_error` → `#ops-alerts`; everything else falls through to the default `#security-alerts`. Add a `sources: ["kubernetes"]` rule when the platform team wants its own feed.
:::

## Microsoft Teams

**Connect:** in Teams, open the channel's **Workflows** and create one from the *Post to a channel when a webhook request is received* template; copy its URL. Then Integrations → **Microsoft Teams** → **Connect** → paste it as the webhook URL. The test posts a card titled *Offload Security — connection test for Microsoft Teams*.

- **Workflows URLs** receive an **Adaptive Card** with the title, message, severity, source and context.
- **Legacy Office 365 connector URLs** (`…webhook.office.com/…/IncomingWebhook/…`) keep working and receive the older MessageCard, with a note that Microsoft is retiring these connectors. Replace the URL with a Workflows one when you can.
- A Workflows webhook accepts the request before the workflow runs, so *accepted* does not prove the card was posted. If no card appears, open the workflow's run history in Teams or Power Automate.

There is one Teams channel per team; use Slack routing rules or webhooks when you need fan-out.

## Google Chat

**Connect:** in the Google Chat space, open **Apps & integrations → Webhooks**, add a webhook and copy its URL (`https://chat.googleapis.com/v1/spaces/…/messages?key=…&token=…`). Then Integrations → **Google Chat** → **Connect** → paste it. The URL is checked when you save — it must be a `chat.googleapis.com` space URL with its key and token — and the test posts a card to the space.

Google Chat receives every notification that goes to Slack or Teams: new and reopened alerts, SLA breaches, scan failures, compliance drift and the other platform notifications sent to chat. Turn it off with the Google Chat switch in the team's preferences or in **Alerts → Delivery settings**.

### What chat messages look like

- Teams and Google Chat cards carry an **Open in Offload** button only when the platform's public address is set (`PUBLIC_APP_URL`); without it there is no button, because the link could not be opened from the chat.
- Text from findings is shown as plain text in Teams and Google Chat — formatting and links inside a finding title are not rendered. In Slack, link markup and mentions in finding text are escaped.
- A Slack, Teams or Google Chat message longer than **2,000 characters** is shortened and ends with *… (truncated — open in Offload for the full text)*. Nothing is cut silently.

## Email (SMTP)

The platform sends mail through **your** SMTP server. Settings are resolved in this order for each send: the deployment's environment (`SMTP_HOST`/`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`), then the **team's** SMTP connection, then the platform setup wizard's.

**Connect per team:** Integrations → **SMTP Email** → **Connect**:

| Field | What to enter |
| --- | --- |
| `smtp_host` · `smtp_port` | Your mail host and port (`587` for STARTTLS) |
| `smtp_username` · `smtp_password` | The sending account — an **app password** for Gmail / Microsoft 365, which refuse plain account passwords |
| `from_email` | Sender shown to recipients (defaults to the username) |
| `use_tls` | STARTTLS on the connection (`true` by default; `false` only for an internal relay that has none) |

The connection test connects, negotiates STARTTLS and authenticates; nothing is sent. Recipients are the team's members (per-user opt-out respected); scheduled-report recipients are set on the schedule. The **daily SOC digest** is configured in **Alerts → Delivery settings**.

:::warning[Environment wins]
If the deployment sets `SMTP_HOST`, that server is used for every team and a team's own SMTP connection is ignored — the log says so when it happens. Single-tenant installs usually set the environment; multi-team installs should leave it unset and let each team connect its own.
:::

## PagerDuty

**Connect:** Integrations → **PagerDuty** → **Connect** → the service's **Events API v2 integration key** and an optional service name. The connection test sends an `info` test event to the service and **resolves it straight away**; depending on the service's rules, on-call may still be notified. If the trigger works but the resolve fails, resolve the *connection test* incident in PagerDuty by hand.

Connecting is the opt-in: from then on the team's alerts are raised as PagerDuty incidents (`critical` → critical, `high` → error, `medium` → warning, `low` → info; de-duplicated per notification). Turn the channel off without removing the connection by setting `channels.pagerduty=false` in the preferences below. Health checks never re-send to PagerDuty.

## Operator channels

The deployment's `.env` can name channels for **platform events that have no team** (housekeeping, worker health). They are never used for — or as a fallback for — a team's notifications.

| Variable | Channel |
| --- | --- |
| `SLACK_WEBHOOK_URL` · `TEAMS_WEBHOOK_URL` | Slack / Teams webhook for system events |
| `ALERT_WEBHOOK_URL` | Generic outbound webhook for system events, signed with `WEBHOOK_SECRET` |
| `PAGERDUTY_ROUTING_KEY` | PagerDuty routing key for system events |
| `ADMIN_EMAIL` | Recipient of critical / high platform events by email |

## Preferences

Preferences are per team and per user. The alert part — on/off, minimum severity and the in-app / Slack / Teams / Google Chat switches — is edited in **Alerts → Delivery settings**; the rest is over the API (`/api/notifications/preferences`, **Manage Integrations** for the team scope):

```json
{
  "channels": {"email": true, "slack": true, "teams": true, "google_chat": true,
               "in_app": true, "webhook": false, "pagerduty": true},
  "muted_categories": ["scan_failure"],
  "alerts": {"enabled": true, "min_severity": "high",
             "channels": {"in_app": true, "slack": true, "teams": true, "google_chat": true}}
}
```

- **`channels`** — switches a delivery channel on or off for the whole team. Email, Slack, Teams, Google Chat and in-app default on (they simply skip when unconfigured); webhook and PagerDuty default off unless connected.
- **`muted_categories`** — notification categories the team does not want at all (the `category` of the notification, e.g. `scan_failure`, `sync_health`, `sla_warning`).
- **`alerts`** — the security-alert stream: `enabled`, `min_severity` (`critical` · `high` · `medium` · `low` · `info`) and which of in-app / Slack / Teams / Google Chat it uses.
- **Per user** — `PUT /api/notifications/preferences/me` `{opted_out, muted_categories}` lets an individual stop receiving email and in-app notifications, or mute categories, without affecting the team.

Absent preferences mean *deliver everywhere that is configured*, so nothing changes until someone writes them.

## Verify a channel

- **Slack / Teams / Google Chat / PagerDuty** — verified when you connect; background health checks never re-send. The card says *Verified at &lt;time&gt; — not re-checked automatically* and shows the last real delivery, with its error if it failed. `POST /api/notifications/slack/test` re-sends a Slack test to any webhook.
- **Email** — `POST /api/integration-config/notifications/test` `{channel: "email" | "slack" | "teams" | "all"}` sends a test notification through the configured channels; `GET …/notifications/status` shows which are configured.
- **Everything** — the bell always receives; if a notification is in the bell but not in Slack, the channel, a routing rule, a preference or the severity threshold is the reason, in that order.

## Related

- [Webhooks](./webhooks.md) — signed event delivery to your own endpoints.
- [SIEM Forwarding](./siem-forwarding.md) — alerts, finding changes and the audit trail to Splunk or a syslog SIEM.
- [Alerts](../vulnerability-risk/alerts.md) — the alert stream these notifications announce.
- [Scheduled Reports](../reports-and-ai/scheduled-reports.md) — the other big consumer of SMTP.
- [Integrations API](./api.md#notifications) — every endpoint on this page.
