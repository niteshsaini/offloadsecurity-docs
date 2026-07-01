---
title: "Conventions"
sidebar_label: "Conventions"
sidebar_position: 3
description: "Response envelopes, pagination, filtering, error codes, and rate limits for the Offload Security API."
---

# Conventions

## Response envelope

Most endpoints wrap their payload in a standard envelope:

```json
{
  "success": true,
  "message": "Success",
  "timestamp": "2026-07-01T12:00:00.000000+00:00",
  "data": { }
}
```

The meaningful result is always under **`data`**.

:::note Some endpoints return the payload directly
A few list endpoints (notably **Alerts** and **native scan results**) return their
object directly instead of wrapping it — e.g. Alerts returns
`{ "items": […], "pagination": {…} }` at the top level. Each guide shows the
**actual** shape for its endpoints, and you can always confirm in the
[Swagger UI](./index.md#interactive-reference-swagger).
:::

## Pagination

There are two pagination styles depending on the endpoint:

**Offset‑based** (`skip` + `limit`) — vulnerabilities, native scans:

```bash
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?skip=50&limit=50" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```
```json
{ "data": { "occurrences": [ ], "pagination": { "total": 1234, "skip": 50, "limit": 50 } } }
```

**Page‑based** (`page` + `limit`) — alerts:

```bash
curl -s "$OFFLOAD_HOST/api/alerts?page=2&limit=50" -H "X-API-Key: $OFFLOAD_API_KEY"
```
```json
{ "pagination": { "current_page": 2, "total_pages": 25, "total_count": 1234, "limit": 50, "has_next": true, "has_prev": true } }
```

Each list endpoint documents its own `limit` ceiling (commonly 100–500).

## Filtering & sorting

List endpoints take filters as query parameters (e.g. `severity`, `status`,
`source`, `created_after`). Where sorting is supported, use `sort_by` +
`sort_order` (`asc` / `desc`). Unsupported values fall back to a safe default
rather than erroring. See each guide for the exact parameters.

## Errors

Failed requests return a non‑2xx status and a descriptive message. Two shapes
exist depending on the layer that rejected the request:

```json
// FastAPI validation / handler error
{ "detail": "Scan result not found: scan_abc123" }
```
```json
// Enveloped error
{ "success": false, "message": "Query failed: …", "error_code": 500 }
```

| Status | Meaning |
| --- | --- |
| `200 / 201` | Success (201 on resource creation) |
| `400 Bad Request` | Malformed input (e.g. unsafe kubeconfig, bad credentials) |
| `401 Unauthorized` | Missing/invalid/expired API key or session |
| `403 Forbidden` | Insufficient scope or team role |
| `404 Not Found` | Resource doesn't exist **or** belongs to another team |
| `409 Conflict` | Duplicate (e.g. a cluster name already used in your team) |
| `422 Unprocessable Entity` | Request body failed schema validation |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Unexpected server error |

:::tip 404 vs 403
Because every resource is team‑scoped, requesting an ID that belongs to another
team returns **404** (not 403) — the platform never confirms the existence of
resources outside your team.
:::

## Rate limits

Two limits apply:

- **Per‑key** — set at key creation via `rate_limit_per_minute` (default 60, max 600).
- **Per‑endpoint** — sensitive routes have their own request‑per‑window caps.

Exceeding either returns **429**. Back off and retry; for automation, keep a
modest concurrency and honour `429`s with exponential backoff.

## IDs & timestamps

- **IDs** are prefixed and opaque: `osk_…` (API key), `clus_…` (cluster),
  `occur_…` (vulnerability occurrence), `alert_…` (alert), `scan_…` (scan).
- **Timestamps** are ISO‑8601 UTC strings (e.g. `2026-07-01T12:00:00Z`).
