---
title: "Scans & Results API"
sidebar_label: "Scans & Results"
sidebar_position: 6
description: "Trigger scans, poll their status, and fetch results and findings over the API."
---

# Scans & Results API

The scanning API follows a simple pattern: **trigger → poll → fetch**. Triggers
return immediately with a `scan_id` and `status: "running"`; you poll until the
scan completes, then read the results and findings.

> Required permission: **Run Scans** to trigger, **View Scans** to read.

## 1. Trigger a scan

**Cloud posture** — re‑scan a connected account (see [Cloud Accounts](./cloud-accounts.md)):

```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/{account_id}/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

**Native security scans** — target a URL/host directly. Each tool has its own endpoint under `/api/native-scans`:

| Scan | Endpoint | Key body fields |
| --- | --- | --- |
| Web vulnerability (ZAP) | `POST /api/native-scans/web-vulnerability` | `target_url`, `scan_type` (`quick`/`standard`/`comprehensive`) |
| Network / ports (nmap) | `POST /api/native-scans/network-discovery` | `target`, `scan_type` |
| SSL/TLS (testssl) | `POST /api/native-scans/ssl-security` | `target`, `port` (443) |
| API security | `POST /api/native-scans/api-security-testing` | `target_url`, `test_type` |
| Security headers | `POST /api/native-scans/security-headers` | `target_url` |
| Nuclei | `POST /api/native-scans/nuclei/url-scan` | `target_url`, `scan_type` |
| Run all | `POST /api/native-scans/run-all` | `target`, `tools[]`, `scan_intensity` |

```bash
curl -s -X POST "$OFFLOAD_HOST/api/native-scans/web-vulnerability" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "target_url": "https://app.example.com", "scan_type": "standard" }'
```

**Response** — a scan handle:

```json
{
  "success": true,
  "scan_id": "scan_7b1c…",
  "target": "https://app.example.com",
  "scan_type": "standard",
  "status": "running",
  "findings_count": 0
}
```

## 2. Poll for completion

Fetch the scan by id and check `status` (`running` → `completed` / `failed`):

```bash
curl -s "$OFFLOAD_HOST/api/native-scans/results/scan_7b1c" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

Poll every few seconds with a sensible cap. When `status` is `completed`, the
same response carries the findings.

## 3. Fetch results & findings

```
GET /api/native-scans/results/{scan_id}
```
```json
{
  "success": true,
  "scan_result": {
    "scan_id": "scan_7b1c",
    "status": "completed",
    "tool_type": "zap",
    "target": "https://app.example.com",
    "findings_count": 12,
    "findings": [
      { "name": "…", "severity": "high", "description": "…", "solution": "…" }
    ],
    "raw_output": { },
    "metadata": { "completed_at": "2026-07-01T12:03:00Z" },
    "created_at": "2026-07-01T12:00:00Z"
  }
}
```

`raw_output` holds the full scanner output; the list endpoint omits it for speed.

## List scans

```
GET /api/native-scans/results?tool_type=zap&status=completed&limit=50&skip=0
```
```json
{ "success": true, "count": 50, "results": [ { "scan_id": "…", "status": "completed", "findings_count": 12 } ], "limit": 50, "skip": 0 }
```

`count` is the size of the returned page (not a grand total).

**Aggregate history** across scan types (cloud, container, native) — user‑scoped, API‑key friendly:

```
GET /api/scan-management/history?scan_type=cloud&limit=50
```
```json
{ "data": { "total_scans": 87, "by_type": { "cloud": 40, "container": 47 }, "recent_scans": [ ] } }
```

## Download a report

```
GET /api/native-scans/results/{scan_id}/download?format=pdf
```
`format` = `json` \| `csv` \| `html` \| `pdf` \| `docx`. Returns a file stream, not JSON.

## Statistics

```
GET /api/native-scans/statistics
```

## Errors

| Status | Cause |
| --- | --- |
| `403` | Missing *Run Scans* (trigger) or *View Scans* (read) |
| `404` | `Scan result not found: {scan_id}` — wrong id, or the scan belongs to another team |

:::note Two scan stores
Native scans (`/api/native-scans/*`, team‑scoped) and the aggregate history
(`/api/scan-management/*`, user‑scoped) read from **different** collections. To
fetch a single native scan's findings, use `GET /api/native-scans/results/{scan_id}`.
:::

## Related

- [Vulnerabilities](./vulnerabilities.md) — the normalized, deduplicated view of findings across all scans
- [Security Scanning](../security-scanning/index.md)
