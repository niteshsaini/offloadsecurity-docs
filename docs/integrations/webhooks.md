---
title: "Webhooks"
sidebar_label: "Webhooks"
sidebar_position: 3
description: "Subscribe your SIEM, SOAR or automation to platform events — scans, findings, SLA, compliance, risk, remediation, evidence, assessments — as signed JSON deliveries with retries and a delivery log, managed over the API."
---

# Webhooks

Webhook subscriptions turn platform events into HTTP calls to an endpoint you control — a SIEM collector, a SOAR playbook trigger, a serverless function that opens a change request. Each delivery is JSON, optionally **HMAC-signed**, retried on failure, and logged so you can see what your endpoint received. Subscriptions are managed over the API; they are per team.

:::note[Two different webhooks]
This page is about **event subscriptions** (`/api/webhooks`) — many endpoints, per-event filtering, a delivery log. The notification **webhook channel** (`channels.webhook` in [Notifications](./notifications.md#preferences)) is a single URL configured through the onboarding API that receives notification payloads. Most integrations want subscriptions.
:::

## Create a subscription

```bash
curl -X POST "$OFFLOAD_HOST/api/webhooks" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "name": "SIEM forwarder",
    "url": "https://collector.example.com/offload",
    "events": ["finding.*", "sla.breached", "compliance.drift_detected"],
    "secret": "a-long-random-string",
    "headers": {"X-Collector-Token": "…"}
  }'
```

| Field | Notes |
| --- | --- |
| `name` | Label shown in listings |
| `url` | HTTPS endpoint. Loopback, link-local, private-network and cloud-metadata addresses are rejected at creation **and** re-checked at connection time (DNS-rebinding defence) |
| `events` | One or more event types; `prefix.*` matches a family, `*` matches everything |
| `secret` | Optional. When set, every delivery carries `X-Webhook-Signature` (below) |
| `headers` | Optional static headers added to every delivery (an auth token for your collector, for example) |

The response carries a `subscription_id` (`whsub_…`). `PUT /api/webhooks/{subscription_id}` changes any field or sets `enabled: false`; `DELETE` removes it. **Manage Integrations** is required for all three; any member can list.

## Event types

`GET /api/webhooks/event-types/list` returns the current list. These are the events the platform publishes:

| Family | Events |
| --- | --- |
| Scans | `scan.started` · `scan.completed` · `scan.failed` |
| Findings | `finding.created` (new **critical / high** findings) · `finding.updated` · `finding.resolved` · `finding.reopened` · `cloud_event.finding_created` |
| Cloud accounts | `cloud_account.added` · `cloud_account.removed` |
| SLA | `sla.warning` · `sla.breached` · `sla.escalated` |
| Compliance | `compliance.score_changed` · `compliance.drift_detected` · `compliance.threshold_breached` |
| Risk | `risk.created` · `risk.updated` · `risk.threshold_breached` |
| Cloud remediation | `remediation.requested` · `approved` · `executed` · `failed` · `rolled_back` |
| Evidence | `evidence.uploaded` · `evidence.approved` · `evidence.expiring_soon` · `evidence.expired` |
| Assessments | `assessment.submitted` · `assessment.completed` |

`finding.created` is published per new critical or high finding — the same events that drive Slack alerts and Jira tickets — not for every medium and low.

## What a delivery looks like

```http
POST /offload HTTP/1.1
Content-Type: application/json
User-Agent: OffloadSecurity-Webhook/1.0
X-Webhook-Event: finding.created
X-Webhook-ID: evt_3f9a1c2b7d
X-Webhook-Signature: sha256=8f1e…

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

`data` is the event's own payload plus `source_module`, `team_id` and `occurred_at`; its keys differ by event family (a `scan.completed` carries `scan_id`, counts and duration; an `sla.breached` carries the finding and its deadline).

### Verify the signature

The signature is HMAC-SHA256 of the **raw request body** with your `secret`:

```python
import hmac, hashlib

def verify(raw_body: bytes, header: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header)
```

Compute it over the bytes exactly as received — do not re-serialise the JSON first.

## Delivery, retries and the log

- A delivery succeeds on any **2xx** within 10 seconds. Anything else is retried up to **3 more times** (after 5 s, 30 s and 120 s), then recorded as failed.
- Every attempt is written to the delivery log: `GET /api/webhooks/{subscription_id}/deliveries?limit=50` returns `event_type`, `status_code`, `success`, `url` and `timestamp`, newest first. The subscription itself carries `delivery_stats` (`total`, `success`, `failed`) and `last_delivery_at`.
- `POST /api/webhooks/{subscription_id}/test` sends a `webhook.test` event immediately — use it to confirm reachability and your signature check before subscribing to real events.

Deliveries are fire-and-forget from the platform's point of view: a slow or failing endpoint never delays the scan or the finding that produced the event.

:::tip[Start with a wildcard in a sandbox]
Subscribe `["*"]` to a request-capture endpoint for a day to see the real shapes and volumes for your tenant, then narrow to the families you will act on. A large cloud scan can produce hundreds of `finding.created` events in a minute.
:::

## Related

- [Notifications](./notifications.md) — human-facing channels and the notification webhook channel.
- [Integrations API](./api.md#webhooks) — the endpoints on this page with parameters.
- [Trust & Security](../trust-and-security.md) — the platform's outbound-request policy.
