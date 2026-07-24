---
title: "Alerts API"
sidebar_label: "Alerts"
sidebar_position: 7
description: "List, read, acknowledge, assign, and resolve platform alerts over the API."
---

# Alerts API

Alerts are the platform's unified, deduplicated signal stream (from scans,
vulnerabilities, integrations, compliance, threat intel, and system events). Pull
them into your SIEM/on‑call tooling and drive their lifecycle over the API.

> Required permissions: **View Alerts** to read, **Acknowledge Alerts** to
> acknowledge/comment, **Manage Alerts** to assign/resolve.

## List alerts

```
GET /api/alerts
```

**Query parameters**

| Param | Type | Default | Notes |
| --- | --- | --- | --- |
| `page` | int | `1` | Page‑based pagination |
| `limit` | int | `50` | Max `200` |
| `severity` | string | — | `critical` / `high` / `medium` / `low` |
| `source` | string | — | `vulnerability` / `scan` / `integration` / `system` / `threat_intel` / `compliance` |
| `status` | string | — | `new` / `acknowledged` / `investigating` / `escalated` / `resolved` / `false_positive` / `closed` |
| `category` | string | — | Free‑form category filter |
| `assigned_to` | string | — | Owner filter |
| `acknowledged` | bool | — | `true` / `false` |
| `active_only` | bool | `false` | Only open (non‑terminal) alerts |
| `search` | string | — | Case‑insensitive match on title + description |
| `created_after` / `created_before` | datetime | — | ISO‑8601 range |
| `sort_by` | string | `last_seen` | `last_seen` / `created_at` / `severity` / `status` / `occurrence_count` / `sla_due_at` |
| `sort_order` | string | `desc` | `asc` / `desc` |

```bash
curl -s "$OFFLOAD_HOST/api/alerts?severity=critical&active_only=true&limit=25" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

**Response** (returned directly — not wrapped in a `data` envelope):

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
      "sla_due_at": "2026-07-02T12:00:00Z",
      "action_url": "/vulnerabilities/…",
      "first_seen": "2026-07-01T09:00:00Z",
      "last_seen": "2026-07-01T12:00:00Z"
    }
  ],
  "pagination": { "current_page": 1, "total_pages": 4, "total_count": 87, "limit": 25, "has_next": true, "has_prev": false },
  "filters": { "severity": "critical" },
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
  "by_source": { "vulnerability": 25, "scan": 10 },
  "by_status": { "new": 12, "investigating": 8 } }
```

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
| Acknowledge all | `POST /api/alerts/acknowledge-all` | — | Acknowledge Alerts |
| Assign owner | `PUT /api/alerts/{alert_id}/assign` | `{ "assigned_to": "user@…", "note": "…" }` | Manage Alerts |
| Change status | `PUT /api/alerts/{alert_id}/status` | `{ "status": "resolved", "reason": "…" }` | Manage Alerts |
| Comment | `POST /api/alerts/{alert_id}/comment` | `{ "content": "…", "is_internal": true }` | Acknowledge Alerts |

```bash
# Acknowledge
curl -s -X POST "$OFFLOAD_HOST/api/alerts/alert_3f9c2a1b7e4d/acknowledge" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "note": "Triaging in incident #4821" }'

# Resolve (or dismiss as false positive) — same endpoint, different status
curl -s -X PUT "$OFFLOAD_HOST/api/alerts/alert_3f9c2a1b7e4d/status" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "status": "false_positive", "reason": "Accepted risk — compensating control in place" }'
```

Each action returns the **updated alert object**. `acknowledge-all` returns
`{ "acknowledged": <count> }`.

:::note[There is no separate "resolve" or "dismiss" endpoint]
Resolving, dismissing (false positive), closing, and reopening are all done via
`PUT /api/alerts/{alert_id}/status` with the target `status`. Invalid transitions
return **400**.
:::

## Related

- [Alerts (product guide)](../authentication/audit-trail.md)
- [Vulnerabilities](./vulnerabilities.md)
