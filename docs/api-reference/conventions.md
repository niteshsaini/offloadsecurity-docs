---
title: "Conventions"
sidebar_label: "Conventions"
sidebar_position: 3
description: "Response envelopes, pagination, filtering, error format, and rate limits for the Offload Security API."
---

# Conventions

## Response envelope

Most endpoints wrap their payload in a standard envelope:

```json
{
  "success": true,
  "message": "Success",
  "timestamp": "2026-11-01T12:00:00.000000+00:00",
  "data": { }
}
```

The result is under **`data`**.

:::note[Some endpoints return the payload directly]
Several endpoints return their object without the envelope: the Alerts list
(`{ "items": […], "pagination": {…} }`), native scan results
(`{ "success": true, "scan_result": {…} }`), cloud accounts, Kubernetes
clusters, and the native and cloud scan comparisons. Each guide shows the
actual shape for its endpoints.
:::

## Pagination

The style depends on the endpoint:

| Style | Parameters | Used by |
| --- | --- | --- |
| Offset | `skip` + `limit` | Vulnerabilities, native scan results, cloud scan runs |
| Page | `page` + `limit` | Alerts |
| Page | `page` + `page_size` | Kubernetes clusters |
| Cursor | `after_seq` + `limit` | Audit-trail SIEM export |

**Offset example:**

```bash
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?skip=50&limit=50" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```
```json
{ "data": { "occurrences": [ ], "pagination": { "total": 1234, "skip": 50, "limit": 50 } } }
```

**Page example** (Alerts, session only):

```json
{ "pagination": { "current_page": 2, "total_pages": 25, "total_count": 1234, "limit": 50, "has_next": true, "has_prev": true } }
```

Each list endpoint has its own `limit` ceiling (for example 100 for
vulnerability occurrences, 200 for alerts, 500 for native scan results). A
value above the ceiling is rejected with `422`, not clamped.

## Filtering and sorting

List endpoints take filters as query parameters (for example `severity`,
`status`, `source`, `search`). Sorting parameters differ by endpoint:

- Vulnerabilities and native scan results use `sort_by` + `sort_dir`
  (`asc` / `desc`). An unknown `sort_by` value returns **`400`** listing the
  allowed fields.
- Alerts use `sort_by` + `sort_order`. An unknown `sort_by` falls back to
  `last_seen`.

See each guide for the exact parameters.

## Errors

Failed requests return a non-2xx status and a JSON body in one shape:

```json
{ "success": false, "error": { "code": "HTTP_404", "message": "Scan result not found: zap_20261101120000_1a2b3c4d" } }
```

| Case | `error.code` | Notes |
| --- | --- | --- |
| Handler-raised 4xx | `HTTP_<status>` or a specific code | `message` is the handler's reason; some add `details` |
| Request validation | `VALIDATION_ERROR` | `details.validation_errors` lists each `field`, `message` and `type` |
| Rate limit | `RATE_LIMIT_EXCEEDED` | `details` gives `limit`, `window_seconds`, `retry_after_seconds` |
| Any 5xx | `HTTP_<status>` | Generic message plus a `request_id`; internal details are logged, not returned |

| Status | Meaning |
| --- | --- |
| `200 / 201 / 202` | Success (`201` on creation, `202` when work is queued, such as a K8s scan) |
| `400 Bad Request` | Invalid input (unsafe kubeconfig, unknown sort field, expired engagement window) |
| `401 Unauthorized` | Missing, invalid or expired API key or session, or a session-only endpoint called with a key |
| `403 Forbidden` | Key lacks the scope, route is session-only for keys, or team role lacks the permission |
| `404 Not Found` | Resource doesn't exist **or** belongs to another team |
| `409 Conflict` | Duplicate (a cluster name already used in your team) or a state that blocks the action (comparing a running scan) |
| `410 Gone` | A kept file (raw artifact, issued report copy) is no longer in storage |
| `422 Unprocessable Entity` | Request failed schema validation |
| `429 Too Many Requests` | Rate limit exceeded |
| `5xx` | Server error; quote the `request_id` to support |

:::tip[404 vs 403]
Every resource is team-scoped, so requesting an ID that belongs to another
team returns **404**, not 403. The platform never confirms that a resource
outside your team exists.
:::

## Rate limits

The API applies **per-client-IP** limits by path prefix, in a sliding
one-minute window shared across workers (when Redis is configured):

| Path prefix | Requests per minute |
| --- | --- |
| `/api/auth/login` | 5 |
| `/api/scans/trigger`, `/api/cloud-scan/trigger` | 10 |
| `/api/vulnerability…` (includes `/api/vulnerabilities`), `/api/cspm/findings`, `/api/risks`, `/api/assessments`, `/api/evidence`, `/api/threat-intelligence` | 60 |
| Any other `/api/` path | 100 |

Exceeding a limit returns **429** with `Retry-After` and `X-RateLimit-*`
headers. Your reverse proxy may apply its own limits as well.

:::note[Per-key rate limit is not enforced in 1.4.0]
API keys carry a `rate_limit_per_minute` value (default 60, max 600), but
release 1.4.0 stores it without enforcing it. The per-IP limits above are what
apply. Keep a modest concurrency and honor `429` with exponential backoff.
:::

## IDs and timestamps

- **IDs** are opaque strings. Do not parse them. Formats you will see:
  `osk_…` (API key value), UUIDs (API `key_id`, cloud account `id`, cloud scan
  `run_id`, CI/CD `scan_id`), `clus_…` (cluster), `alert_…` (alert),
  `<tool>_<timestamp>_<hex>` (native scan, for example `zap_20261101120000_1a2b3c4d`).
- **Timestamps** are ISO-8601 strings in UTC (for example `2026-11-01T12:00:00+00:00`).
