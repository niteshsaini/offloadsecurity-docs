---
title: "Notifications"
sidebar_label: "Notifications"
sidebar_position: 2
description: "Where alerts go — the in-app notification center, Slack, Microsoft Teams, email (SMTP) and PagerDuty — how each channel is configured, which events fire out of the box, Slack routing rules, and the per-team preferences that decide channels, muted categories and the minimum severity that leaves the platform."
---

# Notifications

A finding nobody hears about is a finding nobody fixes. Offload Security raises notifications for the events that need a human — new critical and high findings, SLA warnings and breaches, compliance drift, scan and integration failures — and delivers them to the **in-app notification center** always, and to **Slack, Microsoft Teams, email and PagerDuty** when a team connects them. What leaves the platform, and where, is decided per team.

## Channels at a glance

| Channel | Configured where | Receives |
| --- | --- | --- |
| **In-app** (bell) | Nothing to configure | Every notification for the team; per-user read / dismiss state |
| **Slack** | Integrations → **Slack** (incoming webhook) · optional routing rules over the API | Security alerts, scan failures and platform events; per-rule channels by category, severity and source |
| **Microsoft Teams** | Integrations → **Microsoft Teams** (incoming webhook) | Security alerts as cards |
| **Email (SMTP)** | Integrations → **Email (SMTP)**, or the deployment's `SMTP_*` environment | Alerts to team members' addresses, scheduled reports, invitations, assessment reminders |
| **PagerDuty** | Integrations → **PagerDuty** (Events API v2 integration key) | Incidents for alerts, once the team has connected it |
| **Webhooks** | API — see [Webhooks](./webhooks.md) | Signed JSON for every platform event you subscribe to |

All channels are **team-scoped**: a webhook or mail server connected by one team is never used for another team's notifications, and a notification without a team context (platform housekeeping) can only use the deployment's environment-level channels.

:::note[Who can configure this]
Connecting channels and changing team preferences require **Manage Integrations**. Every member can read their notifications and set their own opt-out.
:::

## What fires out of the box

Without any rule or preference, a team receives:

| Event | Condition | Channels |
| --- | --- | --- |
| **Security alert** (new or reopened) | Severity **high or above** — the threshold is `alerts.min_severity` in the team's preferences, `ALERT_NOTIFY_MIN_SEVERITY` for the deployment | In-app, Slack, Teams — and PagerDuty / webhook when the team has enabled them |
| **New critical / high finding** | From cloud scans and real-time cloud events | In-app and email to the team's members; a Slack `security_alert`; for **critical**, a Jira ticket when Jira is connected |
| **SLA warning / breach** | From [SLA Management](../vulnerability-risk/sla-management.md) | In-app, email |
| **Compliance drift / threshold breached** | From [Drift Detection](../compliance/drift-detection.md) | In-app, email |
| **Scan failed** | Failure classified (connectivity, credentials, tool error, timeout, permission) with a remediation hint | In-app, email, Slack |
| **Platform event** — integration unhealthy, certificate expiring, worker down | Raised by the health checks and monitors | In-app always; Slack as `system_error` (critical / high) or `system_notification`; email to `ADMIN_EMAIL` for critical / high |

Two things follow from the table. **Teams receives the alert stream** (findings, SLA, drift all surface as alerts), not the platform-event stream — use Slack or a webhook for operational noise. And email respects each member's opt-out; the bell is the place everyone sees everything.

## The in-app notification center

**Where:** the bell in the top bar; the badge is the unread count.

Every notification for the team is listed newest first with its priority, title, message and — when there is somewhere to go — an action link. **Mark read**, **mark all read** and **dismiss** are per user, so one analyst clearing the list does not clear it for the team. Notifications expire after their retention window; the API (`GET /api/notifications?unread_only=true`) returns the same list for scripts and dashboards.

## Slack

**Connect:** Integrations → **Slack** → **Connect** → paste the **incoming webhook URL** (from Slack's *Incoming Webhooks* app) and optionally a default channel name. The connection test **posts a message to the channel** — if it does not arrive, the webhook is wrong, and the test says so (`Webhook returned HTTP 404: no_service`). Webhook URLs must be `https://hooks.slack.com/…` (or a host you allow with `SLACK_WEBHOOK_ALLOWED_HOSTS`).

That webhook is the **default channel**: every Slack-bound notification for the team goes there unless a routing rule claims it.

### Routing rules

Routing rules send different classes of notification to different Slack channels. They are managed over the API today (`/api/notifications/slack/routing`); the fields:

| Field | Values |
| --- | --- |
| `name` | Label for the rule |
| `category` | `security_alert` (findings from cloud, Kubernetes, registry and code scanning) · `system_notification` (scan completions, scheduled-job results, configuration changes) · `system_error` (service degradation, task failures, connectivity) |
| `severities` | Optional list — `critical`, `high`, `medium`, `low`, `info`; empty matches all |
| `sources` | Optional list of modules — `cspm`, `kubernetes`, `container_security`, `registry`, `code_scan`, `iac_scan`, `compliance`, `sla`, `threat_intelligence`, `vulnerability`, `integration`, `system`, … (`GET /api/notifications/slack/categories` lists them) |
| `webhook_url` · `channel_name` | The target channel's incoming webhook and display name |

```bash
curl -X POST "$OFFLOAD_HOST/api/notifications/slack/routing" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"name":"Critical security","category":"security_alert",
       "severities":["critical","high"],
       "webhook_url":"https://hooks.slack.com/services/T000/B000/XXXX",
       "channel_name":"#security-critical"}'
```

A notification is matched against the team's enabled rules — the most specific rule wins (category + severity + source over category + severity over category + source over category alone) — and anything unmatched falls back to the default channel. `POST …/slack/test` `{webhook_url, channel_name}` posts a test message; `GET …/slack/status` reports whether a default webhook is configured, the rule count and the channels in use. Rules show the webhook **masked**.

:::tip[A three-channel starting point]
`security_alert` + `critical, high` → `#security-critical`; `system_error` → `#ops-alerts`; everything else falls through to the default `#security-alerts`. Add a `sources: ["kubernetes"]` rule when the platform team wants its own feed.
:::

## Microsoft Teams

**Connect:** Integrations → **Microsoft Teams** → **Connect** → paste the channel's **incoming webhook URL**. The test posts a message to the channel. Alerts arrive as cards with a *View Details* link back to the platform. There is one Teams channel per team; use Slack routing rules or webhooks when you need fan-out.

## Email (SMTP)

The platform sends mail through **your** SMTP server. Settings are resolved in this order for each send: the deployment's environment (`SMTP_HOST`/`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`), then the **team's** SMTP connection, then the platform setup wizard's.

**Connect per team:** Integrations → **Email (SMTP)** → **Connect**:

| Field | What to enter |
| --- | --- |
| `smtp_host` · `smtp_port` | Your mail host and port (`587` for STARTTLS) |
| `smtp_username` · `smtp_password` | The sending account — an **app password** for Gmail / Microsoft 365, which refuse plain account passwords |
| `from_email` | Sender shown to recipients (defaults to the username) |
| `use_tls` | STARTTLS on the connection (`true` by default; `false` only for an internal relay that has none) |

The connection test connects, negotiates STARTTLS and authenticates; nothing is sent. Recipients are the team's members (per-user opt-out respected); scheduled-report recipients are set on the schedule.

:::warning[Environment wins]
If the deployment sets `SMTP_HOST`, that server is used for every team and a team's own SMTP connection is ignored — the log says so when it happens. Single-tenant installs usually set the environment; multi-team installs should leave it unset and let each team connect its own.
:::

## PagerDuty

**Connect:** Integrations → **PagerDuty** → **Connect** → the service's **Events API v2 integration key** and an optional service name. Connecting is the opt-in: from then on the team's alerts are raised as PagerDuty incidents (`critical` → critical, `high` → error, `medium` → warning, `low` → info; de-duplicated per notification). Turn the channel off without removing the connection by setting `channels.pagerduty=false` in the preferences below. The key is not probed on connect — validating an Events API key means triggering an incident — so the first real alert is the first delivery.

## Preferences

Preferences are per team and per user, managed over the API (`/api/notifications/preferences`, **Manage Integrations** for the team scope):

```json
{
  "channels": {"email": true, "slack": true, "teams": true, "in_app": true,
               "webhook": false, "pagerduty": true},
  "muted_categories": ["scan_failure"],
  "alerts": {"enabled": true, "min_severity": "high",
             "channels": {"in_app": true, "slack": true, "teams": true}}
}
```

- **`channels`** — switches a delivery channel on or off for the whole team. Email, Slack, Teams and in-app default on (they simply skip when unconfigured); webhook and PagerDuty default off unless connected.
- **`muted_categories`** — notification categories the team does not want at all (the `category` of the notification, e.g. `scan_failure`, `sync_health`, `sla_warning`).
- **`alerts`** — the security-alert stream: `enabled`, `min_severity` (`critical` · `high` · `medium` · `low` · `info`) and which of in-app / Slack / Teams it uses.
- **Per user** — `PUT /api/notifications/preferences/me` `{opted_out, muted_categories}` lets an individual stop receiving email and in-app notifications, or mute categories, without affecting the team.

Absent preferences mean *deliver everywhere that is configured*, so nothing changes until someone writes them.

## Verify a channel

- **Slack / Teams** — the wizard's connection test posts a real message; `POST /api/notifications/slack/test` re-sends one to any webhook.
- **Email** — `POST /api/integration-config/notifications/test` `{channel: "email" | "slack" | "teams" | "all"}` sends a test notification through the configured channels; `GET …/notifications/status` shows which are configured.
- **Everything** — the bell always receives; if a notification is in the bell but not in Slack, the channel, a routing rule, a preference or the severity threshold is the reason, in that order.

## Related

- [Webhooks](./webhooks.md) — signed event delivery to your own endpoints.
- [Alerts](../vulnerability-risk/alerts.md) — the alert stream these notifications announce.
- [Scheduled Reports](../reports-and-ai/scheduled-reports.md) — the other big consumer of SMTP.
- [Integrations API](./api.md#notifications) — every endpoint on this page.
