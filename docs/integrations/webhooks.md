---
title: "Webhooks"
sidebar_label: "Webhooks"
sidebar_position: 3
description: "Subscribe your SIEM, SOAR or automation to platform events — alerts, scans, findings, SLA, compliance, risk, remediation, evidence, assessments — as signed JSON deliveries with retries and a delivery log, managed on the Integrations page or over the API."
---

# Webhooks

Webhook subscriptions turn platform events into HTTPS calls to an endpoint you control — a SIEM collector, a SOAR playbook trigger, a serverless function that opens a change request. Each delivery is JSON, **HMAC-signed with a timestamp**, retried on failure, and logged so you can see what your endpoint received. Subscriptions are per team.

**Where:** **Integrations** → **Webhooks** section (above the catalog). Everything on the screen is also available over the API (`/api/webhooks`).

:::note[Two different webhooks]
This page is about **event subscriptions** — many endpoints, per-event filtering, a delivery log. The notification **webhook channel** (`channels.webhook` in [Notifications](./notifications.md#preferences)) is a single URL configured through the onboarding API that receives notification payloads. Most integrations want subscriptions. For Splunk or a syslog SIEM, [SIEM Forwarding](./siem-forwarding.md) adds a queue, backoff and delivery health that webhooks do not have.
:::

## Before you begin

- **View Integrations** to see webhooks and their delivery log; **Manage Integrations** to add, edit, enable / disable, test, rotate and delete.
- An **HTTPS** endpoint the platform server can reach. `http://` URLs are refused.
- The platform encryption key (`CLOUD_ENCRYPTION_KEY`) must be configured: signing secrets and custom header values are stored encrypted only, so without it a webhook cannot be created (*Webhook signing is unavailable …*).

## Add a webhook

1. **Integrations → Webhooks → Add webhook.**
2. **Name and endpoint URL** (`https://…`).
3. **Event types.** Tick single types, a whole group (for example `alert.*`), or **All events** (`*`). **Payload examples** shows what each alert event contains.
4. **Custom headers** (optional) — for example an `Authorization` header your receiver expects. Values are stored encrypted and never shown again; renaming a header keeps its value.
5. **Create webhook.** Copy the **signing secret** that appears and store it on your receiver — it is shown **only once**.
6. **Send test event.** A real, signed `webhook.test` event is posted; the result says whether your endpoint accepted it (HTTP 2xx), with the status code and time taken.

Over the API:

```bash
curl -X POST "$OFFLOAD_HOST/api/webhooks" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "name": "SIEM forwarder",
    "url": "https://collector.example.com/offload",
    "events": ["alert.*", "finding.created", "sla.breached"],
    "headers": {"X-Collector-Token": "…"}
  }'
```

| Field | Notes |
| --- | --- |
| `name` | Label shown in listings |
| `url` | HTTPS only. Loopback and cloud-metadata addresses are always refused; private-network addresses are refused unless the deployment sets `ALLOW_PRIVATE_WEBHOOK_TARGETS=true`. Checked when saved **and** again at every send; redirects are never followed |
| `events` | One or more event types; `prefix.*` matches a family, `*` matches everything. Unknown types are refused (*Unknown event type(s)*) |
| `secret` | Optional. Omit it and a signing secret is generated and returned once as `signing_secret` |
| `headers` | Optional static headers added to every delivery |

The response carries a `subscription_id` (`whsub_…`). `PUT /api/webhooks/{subscription_id}` changes any field or sets `enabled: false`; `POST …/{subscription_id}/rotate-secret` issues a new secret (shown once — update your receiver straight away); `DELETE` removes it. A team can have at most **100** webhooks.

## Event types

`GET /api/webhooks/event-types/list` returns the current list, with a payload example for the alert events. These are the events the platform publishes:

| Family | Events |
| --- | --- |
| Alerts | `alert.created` · `alert.updated` · `alert.resolved` |
| Scans | `scan.started` · `scan.completed` |
| Findings | `finding.created` (new **critical / high** findings) · `cloud_event.finding_created` |
| Cloud accounts | `cloud_account.added` · `cloud_account.removed` |
| SLA | `sla.warning` · `sla.breached` · `sla.escalated` |
| Compliance | `compliance.score_changed` · `compliance.drift_detected` · `compliance.threshold_breached` |
| Risk | `risk.created` · `risk.updated` · `risk.threshold_breached` |
| Cloud remediation | `remediation.requested` · `approved` · `executed` · `simulated` (dry run, no cloud change) · `failed` · `rolled_back` |
| Evidence | `evidence.uploaded` · `evidence.approved` · `evidence.expiring_soon` · `evidence.expired` |
| Assessments | `assessment.submitted` · `assessment.completed` |

The list also carries every other type the platform's event bus defines, with a description derived from its name.

:::warning[Listed but not published]
`scan.failed`, `scan.progress`, `finding.updated`, `finding.resolved` and `finding.reopened` are subscribable, but **nothing publishes them in 1.4.0** — a subscription to them receives nothing. For finding lifecycle changes, use [SIEM Forwarding](./siem-forwarding.md); for alert lifecycle changes, use the `alert.*` events.
:::

`finding.created` is published per new critical or high finding — the same events that drive Slack alerts and Jira tickets — not for every medium and low.

### Alert events

`alert.created`, `alert.updated` and `alert.resolved` follow the alerts on the [Alerts](../vulnerability-risk/alerts.md) page — one event per alert, never per raw source event.

| Event | When |
| --- | --- |
| `alert.created` | A new alert was recorded. A Wazuh rule firing repeatedly on the same agent is **one** alert (an alert group); its repeats raise the occurrence count and send nothing more |
| `alert.updated` | The status changed (acknowledged, investigating, escalated, reopened, resolved → closed), the assignee changed, or a recurrence changed the severity. `changes` lists each field from → to; `changed_by` says who |
| `alert.resolved` | An open alert was resolved, closed or marked false positive — by an analyst or automatically when its source condition cleared |

Every alert event's `data` carries `alert_id`, `title`, `description`, `severity`, `priority`, `status`, `source`, `source_event_type`, `source_id`, `category`, `occurrence_count`, `first_seen`, `last_seen`, `created_at`, `updated_at`, `acknowledged`, `assigned_to`, `sla_due_at`, `sla_breached`, `changes`, `changed_by`, `change_id` and `deep_link`, plus `team_id`, `source_module` and `occurred_at`. Wazuh alert groups add `group` (rule id, rule level, agent id, agent name). `deep_link` opens the alert in the platform and is empty unless the platform's public URL is configured.

- The payload includes the alert title and description and the email addresses in `assigned_to` and `changed_by`; comments, notes, raw log lines and other source details are never sent. Point the webhook only at a receiver allowed to hold that data.
- `change_id` identifies one change; de-duplicate on it as well as on the event id.
- Bulk changes (*Acknowledge all*, automatic resolution) send one event per alert at no more than 50 per second, so a large change arrives over a few minutes.

## What a delivery looks like

```http
POST /offload HTTP/1.1
Content-Type: application/json
User-Agent: OffloadSecurity-Webhook/1.0
X-Webhook-Event: finding.created
X-Webhook-ID: evt_3f9a1c2b7d
X-Offload-Timestamp: 1789295131
X-Offload-Signature-V1: v1=8f1e…

{
  "event_id": "evt_3f9a1c2b7d",
  "event_type": "finding.created",
  "timestamp": "2026-09-13T10:42:11.503Z",
  "data": {
    "source_module": "cspm",
    "team_id": "team-…",
    "occurred_at": "2026-09-13T10:42:11.480Z",
    "finding_id": "…", "severity": "critical", "title": "S3 bucket allows public read",
    "resource_id": "arn:aws:s3:::…", "service": "s3", "region": "ap-south-1",
    "provider": "aws", "account_id": "…", "scan_run_id": "…"
  }
}
```

`data` is the event's own payload plus `source_module`, `team_id` and `occurred_at`; its keys differ by event family (a `scan.completed` carries `scan_id`, counts and duration; an `sla.breached` carries the finding and its deadline). The same signature value is also sent as `X-Offload-Signature` and `X-Webhook-Signature`.

### Verify the signature

`X-Offload-Signature-V1` is `v1=` followed by the hex HMAC-SHA256, keyed with your signing secret, of the `X-Offload-Timestamp` value, a `.`, and the **raw request body**. Reject a request whose timestamp is more than 5 minutes old — that is what stops a captured delivery from being replayed.

```python
import hmac, hashlib, time

def verify(raw_body: bytes, timestamp: str, signature: str, secret: str) -> bool:
    if abs(time.time() - int(timestamp)) > 300:
        return False
    msg = timestamp.encode() + b"." + raw_body
    expected = "v1=" + hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected.encode(), signature.strip().encode())
```

Compute it over the bytes exactly as received — do not re-serialize the JSON first. Subscriptions created before 1.4.0 that never had a secret are signed with the team's webhook signing secret instead.

:::warning[Legacy signature (deprecated)]
Before 1.4.0, subscriptions with a secret were signed with an untimestamped `X-Webhook-Signature: sha256=HMAC(secret, body)`, which a captured request could replay forever. It is **off by default**. Setting `NOTIFICATION_WEBHOOK_LEGACY_SIGNATURE=true` on the backend restores it in `X-Webhook-Signature` (the V1 header is always sent) while you move a receiver to `X-Offload-Signature-V1`. The legacy header will be removed in a future release.
:::

## Delivery, retries and the log

- A delivery succeeds on any **2xx** within 10 seconds. Anything else is retried up to **3 more times** (after 5 s, 30 s and 120 s) — four attempts in all. A refused URL or a missing encryption key is not retried. The test send is a single attempt.
- **Deliveries** on a webhook opens its delivery log: time, event type, delivered / failed, HTTP code (— when no answer came back), latency, attempt *n of 4* with the next retry, and the error (cut at 500 characters, and marked). Filter by Delivered / Failed and page through it; entries are kept **30 days**. Over the API: `GET /api/webhooks/{subscription_id}/deliveries?limit=50&offset=0&outcome=failed`.
- Each webhook shows Enabled / Disabled, its event types, the last delivery and HTTP code, attempt counts, failures in a row and the last error. Test sends are shown separately (*Last test …*) and do not change those counts.
- **Auto-disable.** A webhook whose endpoint has failed every attempt for at least **24 hours** (50 or more attempts in a row) is disabled automatically — it reads *Disabled automatically* with the reason and last error, and an alert is raised. Fix the receiver, then click **Enable**; the failure count starts again from zero.
- A retried delivery carries the same `X-Webhook-ID`; de-duplicate on it. Deliveries run concurrently and can arrive out of order — order one alert's events by `data.updated_at`, other events by `data.occurred_at`.

Deliveries never delay the scan or the finding that produced the event. They are also **best effort, not a queue**: events are not stored for replay, so an event raised while the platform is restarting can be lost. Treat the platform pages or API as the source of truth.

:::tip[Start with a wildcard in a sandbox]
Subscribe `["*"]` to a request-capture endpoint for a day to see the real shapes and volumes for your tenant, then narrow to the families you will act on. A large cloud scan can produce hundreds of `finding.created` events in a minute.
:::

## Related

- [Notifications](./notifications.md) — human-facing channels and the notification webhook channel.
- [SIEM Forwarding](./siem-forwarding.md) — queued delivery to Splunk and syslog SIEMs.
- [Integrations API](./api.md#webhooks) — the endpoints on this page with parameters.
- [Trust & Security](../trust-and-security.md) — the platform's outbound-request policy.
