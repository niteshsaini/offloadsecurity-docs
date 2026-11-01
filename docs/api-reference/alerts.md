---
title: "Alerts API"
sidebar_label: "Alerts"
sidebar_position: 7
description: "List, read, acknowledge, assign, and resolve platform alerts over the API, and receive alert events by webhook."
---

# Alerts API

Alerts are the platform's unified, deduplicated signal stream (from
vulnerabilities, scans, integrations such as Wazuh, compliance, threat intel
and system events). Read them and drive their lifecycle over the API, or have
the platform push alert events to you by [webhook](#receive-alert-events-by-webhook).

:::warning[Session only: API keys are refused]
`/api/alerts` is session-only for API keys: a request with `X-API-Key` gets
**403** whatever its scopes. Call these endpoints with a signed-in session
(`Authorization: Bearer <session-token>`), or subscribe to the
[alert webhook events](#receive-alert-events-by-webhook) instead of polling.
:::

> Required team permissions: **View Alerts** to read, **Acknowledge Alerts** to
> acknowledge, comment and run bulk acknowledge, **Manage Alerts** to assign and
> change status. Team-less (platform-wide) system alerts can be changed only by
> the platform admin.

## List alerts

```
GET /api/alerts
```

**Query parameters**

| Param | Type | Default | Notes |
| --- | --- | --- | --- |
| `page` | int | `1` | Page-based pagination |
| `limit` | int | `50` | `1`–`200` |
| `severity` | string | — | `critical` / `high` / `medium` / `low` |
| `source` | string | — | `vulnerability` / `scan` / `integration` / `system` / `threat_intel` / `compliance` / `other` |
| `status` | string | — | `new` / `acknowledged` / `investigating` / `escalated` / `resolved` / `false_positive` / `closed` |
| `category` | string | — | Category filter |
| `assigned_to` | string | — | Owner filter |
| `acknowledged` | bool | — | `true` / `false` |
| `active_only` | bool | `false` | Only open (non-terminal) alerts |
| `search` | string | — | Case-insensitive match on title and description |
| `created_after` / `created_before` | datetime | — | ISO-8601 range |
| `sort_by` | string | `last_seen` | `last_seen` / `created_at` / `severity` / `status` / `occurrence_count` / `sla_due_at`; anything else falls back to `last_seen` |
| `sort_order` | string | `desc` | `asc` / `desc` |

```bash
curl -s "$OFFLOAD_HOST/api/alerts?severity=critical&active_only=true&limit=25" \
  -H "Authorization: Bearer $OFFLOAD_SESSION_TOKEN"
```

**Response** (returned directly, not wrapped in a `data` envelope):

```json
{
  "items": [
    {
      "alert_id": "alert_3f9c2a1b7e4d",
      "source": "vulnerability",
      "severity": "critical",
      "status": "new",
      "priority": "P1",
      "title": "Critical CVE on production API",
      "description": "…",
      "occurrence_count": 3,
      "acknowledged": false,
      "current_assignment": null,
      "sla_due_at": "2026-11-02T12:00:00Z",
      "action_url": "/vulnerabilities/…",
      "first_seen": "2026-11-01T09:00:00Z",
      "last_seen": "2026-11-01T12:00:00Z"
    }
  ],
  "pagination": { "current_page": 1, "total_pages": 4, "total_count": 87, "limit": 25, "has_next": true, "has_prev": false },
  "filters": { "severity": "critical", "source": null, "category": null, "status": null, "assigned_to": null, "acknowledged": null, "search": null },
  "sorting": { "sort_by": "last_seen", "sort_order": "desc" }
}
```

## Summary (for dashboards)

```
GET /api/alerts/summary
```
```json
{ "total": 320, "open": 41, "unacknowledged": 12,
  "by_severity": { "critical": 4, "high": 20, "medium": 17 },
  "by_severity_basis": "open",
  "by_severity_all_status": { "critical": 9, "high": 120, "medium": 191 },
  "by_source": { "vulnerability": 250, "scan": 70 },
  "by_category": { "…": 0 },
  "by_status": { "new": 12, "investigating": 8, "resolved": 279 } }
```

`by_severity` counts **open** alerts only, the same basis as `open` and
`unacknowledged`. The all-status breakdown is `by_severity_all_status`.

## Read one

```
GET /api/alerts/{alert_id}
```
Returns the full alert (with `activity_log`, `comments`, and live
`remediation_progress` when a remediation workflow is linked). `404` if not found
or owned by another team.

## Act on an alert

| Action | Endpoint | Body | Permission |
| --- | --- | --- | --- |
| Acknowledge | `POST /api/alerts/{alert_id}/acknowledge` | `{ "note": "…" }` (optional) | Acknowledge Alerts |
| Acknowledge all matching | `POST /api/alerts/acknowledge-all` | — (same query filters as the list) | Acknowledge Alerts |
| Bulk action | `POST /api/alerts/bulk-action` | `{ "alert_ids": […], "action": "resolved", "note": "…" }` | Acknowledge Alerts; Manage Alerts for any action other than `acknowledge` |
| Assign owner | `PUT /api/alerts/{alert_id}/assign` | `{ "assignee_user_id": "…", "note": "…" }` | Manage Alerts |
| Change status | `PUT /api/alerts/{alert_id}/status` | `{ "status": "resolved", "reason": "…" }` | Manage Alerts |
| Comment | `POST /api/alerts/{alert_id}/comment` | `{ "content": "…", "is_internal": true }` | Acknowledge Alerts |

- **Assign:** `assignee_user_id` is required and must be an active member of
  the alert's team (otherwise `400`). The assignee is notified (in-app and by
  email, per the team's channel settings). `assigned_to` is display-only; the
  server replaces it with the member's email.
- **Bulk action:** `alert_ids` takes 1–500 IDs. `action` is `acknowledge`,
  `investigating`, `escalated`, `resolved`, `false_positive` or `closed`. Alerts
  whose current status doesn't allow the transition are skipped and reported;
  the response is `{ "requested": n, "updated": <count>, "skipped": [{ "alert_id", "reason" }] }`.
- **Acknowledge all** acknowledges every unacknowledged alert matching the
  filters you pass and returns `{ "acknowledged": <count> }`.

```bash
# Acknowledge
curl -s -X POST "$OFFLOAD_HOST/api/alerts/alert_3f9c2a1b7e4d/acknowledge" \
  -H "Authorization: Bearer $OFFLOAD_SESSION_TOKEN" -H "Content-Type: application/json" \
  -d '{ "note": "Triaging in incident #4821" }'

# Dismiss as false positive: same endpoint as resolve, different status
curl -s -X PUT "$OFFLOAD_HOST/api/alerts/alert_3f9c2a1b7e4d/status" \
  -H "Authorization: Bearer $OFFLOAD_SESSION_TOKEN" -H "Content-Type: application/json" \
  -d '{ "status": "false_positive", "reason": "Accepted risk — compensating control in place" }'
```

The single-alert actions return the **updated alert object**.

:::note[There is no separate "resolve" or "dismiss" endpoint]
Resolving, dismissing (false positive), closing and reopening are all done via
`PUT /api/alerts/{alert_id}/status` with the target `status`. Invalid
transitions return **400**. In particular, a `new` alert cannot go straight to
`resolved`: acknowledge it or move it to `investigating` first (it can go
straight to `false_positive` or `closed`). Reopen paths: `resolved` →
`investigating`; `false_positive` or `closed` → `new`.
:::

## Receive alert events by webhook

The platform publishes three alert events to outbound webhook subscriptions:

| Event | When |
| --- | --- |
| `alert.created` | A new unified alert is recorded (a Wazuh rule and agent group is one alert) |
| `alert.updated` | Status, assignee or severity changed |
| `alert.resolved` | Resolved, closed or marked false positive |

Each delivery is a JSON envelope `{ "event_id", "event_type", "timestamp", "data" }`
signed with `X-Offload-Timestamp` and `X-Offload-Signature-V1`. `data` carries
the alert fields plus `changes` (`{ "status": { "from": …, "to": … } }`),
`change_id` and a `deep_link` that opens the alert in the UI.

Subscriptions are managed in **Integrations → Webhooks** or with a session at
`/api/webhooks` (session-only for API keys). `GET /api/webhooks/event-types/list`
returns every event type with an example payload. Setup and signature
verification: [Webhooks](../integrations/webhooks.md).

## Related

- [Alerts (product guide)](../vulnerability-risk/alerts.md)
- [Webhooks](../integrations/webhooks.md)
- [Vulnerabilities](./vulnerabilities.md)
