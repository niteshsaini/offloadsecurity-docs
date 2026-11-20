---
title: "Vulnerabilities API"
sidebar_label: "Vulnerabilities"
sidebar_position: 8
description: "List and filter normalized vulnerability occurrences across cloud, Kubernetes, container, and application scans, and manage risk exceptions."
---

# Vulnerabilities API

Vulnerabilities are the **normalized, deduplicated** view of findings from every
scanner (cloud, Kubernetes, container, application), each enriched with CVSS,
a risk score, priority and CISA KEV status. Two views:

- **Occurrences**: one row per (vulnerability × asset). Best for triage and SIEM export.
- **Grouped**: one row per CVE or check across all affected assets. Best for reporting.

> Required: an API key with **`vulnerabilities:read`**. Only the endpoints
> marked *Key* below accept an API key; the others need a signed-in session.

## List occurrences

```
GET /api/vulnerabilities/occurrences
```
*Key* (`vulnerabilities:read`).

**Query parameters**

| Param | Type | Default | Notes |
| --- | --- | --- | --- |
| `status` | string | — | `open` / `triaged` / `in_progress` / `resolved` / `verified` / `closed` / `false_positive` / `accepted_risk` / `reopened` |
| `asset_id` | string | — | Only this asset's vulnerabilities |
| `severity_min` | float | — | Minimum base CVSS (for example `7.0`) |
| `priority` | string | — | Platform priority from the triage engine: `P1`–`P4` |
| `priority_rank` | string | — | Legacy CVSS-only rank `P0`–`P4`; prefer `priority` |
| `source` | string | — | `cspm` / `kubernetes` / `container` / `application` |
| `search` | string | — | Substring of title, vulnerability ID or asset ID (1–200 chars) |
| `excepted` | string | see note | `exclude` / `include` / `only`: occurrences under an approved [risk exception](#risk-exceptions) |
| `sort_by` | string | — | `priority`, `triage_risk`, `vpr`, `risk_score`, `severity`, `cvss`, `priority_rank`, `status`, `asset_id`, `scanner`, `sla_due`, `first_seen`, `last_seen`, `created_at`. Unknown values return `400` |
| `sort_dir` | string | `desc` | `asc` / `desc` |
| `skip` | int | `0` | Offset |
| `limit` | int | `50` | `1`–`100` |

Without `sort_by`, results are ranked by the triage engine's risk score, then
VPR score, KEV status and the CVSS-based risk score. Without `excepted`,
excepted occurrences are **excluded** when you filter on an open status and
included (labeled) otherwise.

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
        "lifecycle": { "status": "open", "sla": { "due_at": "2026-11-08T00:00:00Z", "breached": false } },
        "detection": { "scanner": "trivy", "first_seen": "2026-10-28T…", "last_seen": "2026-11-01T…" },
        "remediation": { "recommendation": "Upgrade openssl to 3.0.13" },
        "cisa_kev": true,
        "cisa_kev_details": { },
        "source": "container"
      }
    ],
    "pagination": { "total": 512, "skip": 0, "limit": 50 },
    "exceptions": { }
  }
}
```

Every occurrence with a CVE ID includes **`cisa_kev`** (bool) and
**`cisa_kev_details`** (the KEV entry, or `null`). Occurrence IDs are opaque
(`occur_…`, or `sync_…` for synced sources); do not parse them.

## Get one occurrence

```
GET /api/vulnerabilities/occurrences/{occurrence_id}
```
*Session only* (needs the *vulnerability_view* permission). Returns a single
occurrence under `data`, or `404`.

## Group by CVE

```
GET /api/vulnerabilities/grouped?severity=critical&limit=50
```
*Key* (`vulnerabilities:read`). Filters: `source`, `status`, `severity`
(`critical` / `high` / `medium` / `low`), `search`, `excepted`. Sorting:
`sort_by` (`risk_score`, `severity`, `title`, `source`, `occurrence_count`,
`affected_assets`, `open_count`, `sla_breached`, `assigned`, `first_seen`,
`last_seen`) and `sort_dir`. Paging: `skip`, `limit` (max `200`).

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
        "first_seen": "2026-10-28T…",
        "fix_available": true
      }
    ],
    "pagination": { "total": 73, "skip": 0, "limit": 50 },
    "exceptions": { "mode": "exclude", "hidden": 2 }
  }
}
```

## Other reads

| Endpoint | Purpose | Auth |
| --- | --- | --- |
| `GET /api/vulnerabilities/findings` | Unified, cross-tool findings with triage filters (`priority`, `kev`, `sla_breached`, `module`, `cve`, …); `limit` max `200` | Key |
| `GET /api/vulnerabilities/findings/{fingerprint}` | One unified finding | Key |
| `GET /api/vulnerabilities/stats` | Aggregate counts by severity, status and source | Session only |
| `GET /api/vulnerabilities/catalog` | CVE definition entries | Session only |
| `GET /api/vulnerabilities/assets/{asset_id}` | Per-asset vulnerability summary | Session only |

Status changes and assignment (`PUT /api/vulnerabilities/occurrences/{occurrence_id}/status`,
`…/assign`, `POST …/bulk-status`, `…/bulk-assign`) also need a session.

## Risk exceptions

*New in 1.4.0 (Vulnerability Management → Risk exceptions in the UI).* Request,
approve, reject and revoke an exception for a single finding. Approved
exceptions hide the finding from open lists and counts (see `excepted` above).
Key access uses the `risks:read` / `risks:manage` scopes; writes need the
owner's **Manage Risks** permission.

| Action | Endpoint | Auth |
| --- | --- | --- |
| Request | `POST /api/risk-exceptions` | `risks:manage` + Manage Risks |
| List (`status`, `finding_id`, `limit` up to 500, default 100) | `GET /api/risk-exceptions` | `risks:read` |
| Is a finding excepted? | `GET /api/risk-exceptions/check/{finding_id}` | `risks:read` |
| What the caller may do | `GET /api/risk-exceptions/capabilities` | `risks:read` + View Risks |
| Approve / reject (body `{ "comment": "…" }`) | `POST /api/risk-exceptions/{exception_id}/approve`, `…/reject` | `risks:manage` + Manage Risks |
| Revoke an approved exception (body `{ "reason": "…" }`) | `POST /api/risk-exceptions/{exception_id}/revoke` | `risks:manage` + Manage Risks |

**Request body**

| Field | Notes |
| --- | --- |
| `finding_id` | **Required.** A Vulnerability Management occurrence ID, a triage finding fingerprint, or a Cloud Security / Kubernetes finding ID in your team; anything else returns `400` |
| `justification` | **Required**, 10–2,000 chars |
| `exception_type` | `accept` (default), `suppress` or `defer` |
| `expires_at` | ISO-8601 date or date-time (for example `2026-12-31`) |
| `compensating_controls`, `finding_title`, `finding_severity`, `finding_source` | Optional context |

A new exception is `pending` (statuses: `pending`, `approved`, `rejected`,
`expired`, `revoked`). **Separation of duties:** the requester cannot approve
their own exception. Product guide:
[Risk exceptions](../vulnerability-risk/vulnerability-management/risk-exceptions.md).

## Related finding types

The endpoints above are for **CVE-style vulnerabilities**. Two adjacent surfaces:

- **`GET /api/cspm/findings`**: cloud **misconfiguration** findings (`cloud:read`).
- **`GET /api/risk-management/risks`**: the unified **risk register** (session only).

## Errors

| Status | Cause |
| --- | --- |
| `400` | Unknown `sort_by` value; unknown `finding_id` on an exception request |
| `401` | A session-only endpoint called with an API key |
| `403` | Key lacks `vulnerabilities:read` / `risks:*`, or the owner's role lacks the permission |
| `500` | Server error; the message is generic and carries a `request_id` |

## Related

- [Scans & Results](./scans-and-results.md): raw per-scan findings
- [Vulnerabilities & Risk (product guide)](../vulnerability-risk/index.md)
