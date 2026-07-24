---
title: "Vulnerabilities API"
sidebar_label: "Vulnerabilities"
sidebar_position: 8
description: "List and filter normalized vulnerability occurrences across cloud, Kubernetes, container, and application scans."
---

# Vulnerabilities API

Vulnerabilities are the **normalized, deduplicated** view of findings from every
scanner (cloud, Kubernetes, container, application), each enriched with CVSS,
a risk score, priority rank, and CISA KEV status. Two views:

- **Occurrences** — one row per (vulnerability × asset). Best for triage and SIEM export.
- **Grouped** — one row per CVE/check across all affected assets. Best for reporting.

## List occurrences

```
GET /api/vulnerabilities/occurrences
```

**Query parameters**

| Param | Type | Default | Notes |
| --- | --- | --- | --- |
| `status` | string | — | `open` / `triaged` / `in_progress` / `resolved` / `verified` / `closed` / `false_positive` / `accepted_risk` / `reopened` |
| `asset_id` | string | — | Only this asset's vulnerabilities |
| `severity_min` | float | — | Minimum base CVSS (e.g. `7.0`) |
| `priority_rank` | string | — | `P0`–`P4` |
| `source` | string | — | `cspm` / `kubernetes` / `container` / `application` |
| `skip` | int | `0` | Offset |
| `limit` | int | `50` | Max `100` |

Results are sorted by risk score (highest first).

```bash
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?severity_min=7&status=open&limit=50" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

**Response**

```json
{
  "success": true,
  "data": {
    "occurrences": [
      {
        "occurrence_id": "occur_5a1f…",
        "vulnerability_id": "CVE-2024-1234",
        "asset_id": "i-0abc…",
        "component": { "name": "openssl", "version": "3.0.11", "fixed_version": "3.0.13" },
        "risk_assessment": { "base_cvss": 8.1, "risk_score": 86, "priority_rank": "P1" },
        "lifecycle": { "status": "open", "sla": { "due_at": "2026-07-08T00:00:00Z", "breached": false } },
        "detection": { "scanner": "trivy", "first_seen": "2026-06-28T…", "last_seen": "2026-07-01T…" },
        "remediation": { "recommendation": "Upgrade openssl to 3.0.13" },
        "cisa_kev": true,
        "source": "container"
      }
    ],
    "pagination": { "total": 512, "skip": 0, "limit": 50 }
  }
}
```

Every occurrence includes **`cisa_kev`** (bool) and **`cisa_kev_details`** —
whether the CVE is on CISA's Known Exploited Vulnerabilities list.

## Get one occurrence

```
GET /api/vulnerabilities/occurrences/{occurrence_id}
```
Returns a single occurrence (same shape) under `data`, or `404`.

## Group by CVE

```
GET /api/vulnerabilities/grouped?severity=critical&limit=50
```
`severity` = `critical` / `high` / `medium` / `low`; `limit` max `200`.

```json
{
  "data": {
    "grouped_vulnerabilities": [
      {
        "vulnerability_id": "CVE-2024-1234",
        "title": "OpenSSL …",
        "severity": "critical",
        "risk_score": 86,
        "occurrence_count": 14,
        "affected_asset_count": 9,
        "open_count": 11,
        "resolved_count": 3,
        "sla_breached_count": 2,
        "first_seen": "2026-06-28T…",
        "fix_available": true
      }
    ],
    "pagination": { "total": 73, "skip": 0, "limit": 50 }
  }
}
```

## Other reads

| Endpoint | Purpose |
| --- | --- |
| `GET /api/vulnerabilities/stats` | Aggregate counts by severity/status/source |
| `GET /api/vulnerabilities/catalog` | CVE definition entries |
| `GET /api/vulnerabilities/assets/{asset_id}` | Per‑asset vulnerability summary |

## Related finding types

The endpoints above are for **CVE‑style vulnerabilities**. Two adjacent surfaces:

- **`GET /api/cspm/findings`** — cloud **misconfiguration** findings (Prowler/CSPM).
- **`GET /api/risk-management/…`** — the unified **risk register**.

## Errors

| Status | Cause |
| --- | --- |
| `403` | Insufficient permission (single‑occurrence read requires *vulnerability_view*) |
| `500` | `Query failed: …` |

## Related

- [Scans & Results](./scans-and-results.md) — raw per‑scan findings
- [Vulnerabilities & Risk (product guide)](../vulnerability-risk/index.md)
