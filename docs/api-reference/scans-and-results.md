---
title: "Scans & Results API"
sidebar_label: "Scans & Results"
sidebar_position: 6
description: "Trigger scans, poll their status, fetch results and raw evidence, compare runs, and verify exported reports over the API."
---

# Scans & Results API

The scanning API follows a simple pattern: **trigger → poll → fetch**. Triggers
return immediately with a scan ID and `status: "running"`; you poll until the
scan reaches a terminal status, then read the results and findings.

> Required: an API key with **`scans:trigger`** to start scans and
> **`scans:read`** to read them; the key's owner needs the **Run Scans** and
> **View Scans** team permissions respectively.

## 1. Trigger a scan

**Cloud posture**: re-scan a connected account (see [Cloud Accounts](./cloud-accounts.md#trigger-a-scan-on-demand)):

```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/{account_id}/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

**Native security scans**: target a URL or host directly. Each tool has its
own endpoint under `/api/native-scans`:

| Scan | Endpoint | Key body fields |
| --- | --- | --- |
| Web vulnerability (ZAP) | `POST /api/native-scans/web-vulnerability` | `target_url`, `scan_type` (`quick` / `standard` / `comprehensive`), `auth_config`, `exclude_paths`, `engagement` |
| Network and ports (nmap) | `POST /api/native-scans/network-discovery` | `target`, `scan_type` (`port_scan` default, `ping_sweep`, `service_detection`, `comprehensive`, `vulnerability_scan`), `exclude_hosts`, `timing`, `engagement` |
| SSL/TLS (testssl.sh) | `POST /api/native-scans/ssl-security` | `target`, `port` (`443`), `scan_type`, `engagement` |
| API security | `POST /api/native-scans/api-security-testing` | `target_url`, `test_type` (`basic` / `standard` / `comprehensive`) |
| Security headers | `POST /api/native-scans/security-headers` | `target_url`, `port`, `use_get` |
| Nuclei | `POST /api/native-scans/nuclei/url-scan` | `target_url`, `scan_type` (`quick` / `standard` / `comprehensive` / `cve-focused`), `engagement` |
| Run all | `POST /api/native-scans/run-all` | `target`, `tools[]`, `scan_intensity`, `ssl_port`, `engagement` |

```bash
curl -s -X POST "$OFFLOAD_HOST/api/native-scans/web-vulnerability" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "target_url": "https://app.example.com", "scan_type": "standard",
        "engagement": { "attested": true, "reference": "PT-2026-114", "environment": "staging" } }'
```

**Response**, a scan handle:

```json
{
  "success": true,
  "scan_id": "zap_20261101120000_1a2b3c4d",
  "target": "https://app.example.com",
  "scan_type": "standard",
  "status": "running",
  "findings_count": 0
}
```

For CI pipelines, the dedicated `POST /api/cicd/scans/trigger` endpoint adds a
pass/fail gate; see [CLI & CI/CD](../cli-and-cicd.md).

### Engagement record

*New in 1.4.0.* ZAP, nmap, testssl.sh, Nuclei, run-all, App Scan, Kubernetes,
cloud and container scans accept an `engagement` object that records who
authorized testing the target:

| Field | Notes |
| --- | --- |
| `attested` | `true` confirms the caller is authorized to test these targets |
| `reference` | Engagement, rules-of-engagement or ticket ID (up to 200 chars) |
| `environment` | `production` / `staging` / `development` / `test` / `unspecified` (default) |
| `valid_until` | `YYYY-MM-DD`, end of the authorized window. A past date is refused (`400`) |
| `notes` | Up to 500 chars |

Who attested and when are taken from the authenticated caller, never from the
body. A rescan carries the original attestation and is refused once its window
has ended. Reports show "Not recorded" for scans without an attestation.

The attestation is **optional by default**. Set `SCAN_REQUIRE_AUTHORIZATION=true`
in the backend environment to make it mandatory; scans without
`"attested": true` are then refused with `400`.

## 2. Poll for completion

Fetch the scan by ID and check `status` (`running` → `completed`, `partial` or
`failed`):

```bash
curl -s "$OFFLOAD_HOST/api/native-scans/results/zap_20261101120000_1a2b3c4d" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

Poll every few seconds with an overall timeout, and stop on any terminal
status, not only `completed`.

## 3. Fetch results and findings

```
GET /api/native-scans/results/{scan_id}
```
```json
{
  "success": true,
  "scan_result": {
    "scan_id": "zap_20261101120000_1a2b3c4d",
    "status": "completed",
    "tool_type": "zap",
    "target": "https://app.example.com",
    "findings_count": 12,
    "findings": [
      { "name": "…", "severity": "high", "description": "…", "solution": "…" }
    ],
    "raw_output": { },
    "started_at": "2026-11-01T12:00:02+00:00",
    "completed_at": "2026-11-01T12:03:10+00:00",
    "duration_seconds": 188.0,
    "metadata": { "provenance": { }, "scan_config": { }, "artifacts": [ ], "engagement": { } },
    "created_at": "2026-11-01T12:00:00+00:00"
  }
}
```

`raw_output` holds the parsed scanner output; the list endpoint omits it.
Credentials in `auth_config` and in recorded command lines are masked on every
read and export.

### Provenance and raw evidence

*New in 1.4.0.* Each nmap, Nuclei, testssl.sh and ZAP run records how it was
produced in `metadata.provenance`: tool, engine (container image, local binary,
or the built-in fallback when ZAP did not run), pinned version, Nuclei
templates version, profile settings, the redacted command line (not recorded
for ZAP), exit code and UTC start and end times.

The tool's own output is kept in object storage and listed in
`metadata.artifacts` (name, SHA-256, size). Download one with:

```
GET /api/native-scans/results/{scan_id}/artifacts/{name}
```

The response is the file (nmap XML, Nuclei JSONL, testssl JSON or ZAP report),
with credential header values masked and the SHA-256 recorded at storage time
in the `X-Content-SHA256` header. Files over 50 MB (`SCAN_ARTIFACT_MAX_BYTES`)
are recorded as not kept, with the reason. `410` means the file is no longer
in storage. The scan results page in the UI also offers these downloads.

## List scans

```
GET /api/native-scans/results?tool_type=zap&status=completed&limit=50&skip=0
```

Filters: `tool_type`, `status`, `scan_type`, `search` (target or scan ID
substring), `exclude_tool_type` (repeatable), `exclude_app_scan_children`.
Sorting: `sort_by` (`created_at`, `tool_type`, `target`, `scan_type`,
`findings_count`, `status`) and `sort_dir`. `limit` max `500`.

```json
{ "success": true, "count": 50, "total": 212, "scan_types": ["standard", "quick"],
  "results": [ { "scan_id": "…", "status": "completed", "findings_count": 12 } ], "limit": 50, "skip": 0 }
```

`count` is the size of the returned page; `total` is the number of matching
scans, so you can page through all of them.

**Aggregate history** across scan types (cloud, container, native), scoped to
the calling user:

```
GET /api/scan-management/history?scan_type=cloud&limit=50
```
```json
{ "data": { "total_scans": 50, "by_type": { "cloud": 50 }, "recent_scans": [ ] } }
```

`limit` max `200`; `total_scans` counts the returned rows.

## Compare with an earlier run

*New in 1.4.0.* Each scanning module can compare two runs finding by finding.
Every comparison says what it cannot claim: a finding missing from a partial
run is listed as not seen or not re-evaluated, never as fixed.

| Module | Endpoint | Baseline parameter (default) | In the UI |
| --- | --- | --- | --- |
| Native scans | `GET /api/native-scans/results/{scan_id}/compare` | `baseline` (latest earlier completed or partial run of the same tool on the same target) | ✓ (previous run) |
| Cloud posture | `GET /api/cloud-scans/{run_id}/compare` | `baseline` (previous run of the account with a frozen snapshot) | ✓ (previous run) |
| Code scans | `GET /api/code/reports/{scan_id}/compare` | `base` (previous completed scan of the same repository and branch) | — API-only |
| Kubernetes | `GET /api/k8s/scans/{scan_id}/compare` | `base` (previous completed scan of the cluster) | — API-only |
| Container images | `GET /api/container-registries/scans/{scan_id}/compare` | `baseline` (the image's previous completed scan) | — API-only |

All need `scans:read`. Choosing a non-default baseline is API-only for every module.

**Native scans.** The response (not enveloped) has `current` and `baseline` run
summaries, `counts` and lists for `new`, `fixed`, `not_seen`, `unchanged` and
`severity_changed` (with `previous_severity`), plus `caveats`. Finding identity
is (rule, location, parameter). If this run is `partial`, findings it did not
report go to `not_seen`, not `fixed`. A run that is not `completed` or
`partial` returns `409`; a baseline of a different tool or target returns
`400`. With no earlier run, the response has `"baseline": null` and a `detail`.

```json
{
  "current":  { "scan_id": "nuclei_20261101…", "status": "completed", "scan_type": "standard", "findings_count": 9 },
  "baseline": { "scan_id": "nuclei_20261015…", "status": "completed", "scan_type": "standard", "findings_count": 14 },
  "counts": { "new": 1, "fixed": 6, "not_seen": 0, "unchanged": 8, "severity_changed": 1 },
  "new": [ { "title": "…", "severity": "high", "rule": "…", "location": "https://app.example.com/login", "param": null } ],
  "fixed": [ ], "not_seen": [ ], "unchanged": [ ], "severity_changed": [ ],
  "caveats": [ ]
}
```

**Cloud posture.** See [Cloud Accounts → Compare two runs](./cloud-accounts.md#compare-two-runs)
(`new_failing`, `fixed`, `still_failing`, `not_reevaluated`).

**Code scans and Kubernetes.** Enveloped under `data`, with `counts` (`new`,
`fixed`, `triaged`, `not_reevaluated`, `persisting`) and complete lists.
`triaged` means gone because it was suppressed, risk-accepted or marked false
positive. Code `fixed` requires that the later scan re-evaluated the finding
(its tool ran completely and its file was assessed). `404` when a scan is not
found; `409` when the scans cannot be compared. See also
[Kubernetes → Compare two scans](./kubernetes.md#compare-two-scans).

**Container images.** Enveloped under `data`, keyed per (CVE, package,
version), digest-aware: `new`, `fixed` (gone, same image digest),
`not_in_new_image` (gone because the tag now points to a different digest; the
old image may still run), `unchanged`, `severity_changed` and `caveats`. A
baseline of a different image returns `400`.

## Download a report

```
GET /api/native-scans/results/{scan_id}/download?format=pdf
```
`format` = `json` \| `csv` \| `html` \| `pdf` \| `docx`. Returns a file stream,
not JSON. HTML, PDF and DOCX use the consolidated report layout;
`include_screenshots=true` adds browser screenshots of affected URLs (slower).

Every download carries an **`X-Content-SHA256`** header, is recorded on the
scan's export log and kept byte for byte (*new in 1.4.0*):

| Action | Endpoint |
| --- | --- |
| List the exports issued for a scan (format, SHA-256, size, who, when, `kept`) | `GET /api/native-scans/results/{scan_id}/exports` |
| Re-download an issued report exactly as issued, not regenerated | `GET /api/native-scans/results/{scan_id}/exports/{sha256}` |

### Verify an exported report

*New in 1.4.0 · API-only.* Check whether a file someone sends you is an
unmodified report issued to your team:

```
GET /api/native-scans/exports/verify?sha256={64-hex-digest}
```

```bash
curl -s "$OFFLOAD_HOST/api/native-scans/exports/verify?sha256=$(shasum -a 256 report.pdf | cut -d' ' -f1)" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```
```json
{ "verified": true, "sha256": "9f2c…", "match": { "kind": "scan_export", "scan_id": "zap_…", "tool": "zap", "target": "https://app.example.com", "export": { } } }
```

One check covers native scan exports, consolidated reports, container scan
exports (JSON, CSV, CycloneDX) and Cloud Security Posture reports. A file that
was altered, or did not come from this platform, returns `"verified": false`
with an explanation. A Cloud Security Posture report can be re-downloaded
exactly as issued with `GET /api/export/issued/{sha256}` (`reports:read`).

## Delete a scan

```
DELETE /api/native-scans/results/{scan_id}?reason=…
```

*Changed in 1.4.0:* the scan is moved to a tombstone recording who, when and
why, and purged with its artifacts and kept exports after
`SCAN_TOMBSTONE_DAYS` (default 30). Needs `scans:trigger` and *Run Scans*.

## Statistics

```
GET /api/native-scans/statistics
```

## Errors

| Status | Cause |
| --- | --- |
| `400` | Invalid engagement (expired window, bad environment) or, with `SCAN_REQUIRE_AUTHORIZATION=true`, a missing attestation; a comparison baseline of another tool, target or image |
| `403` | Key lacks `scans:trigger` / `scans:read`, or owner lacks *Run Scans* / *View Scans* |
| `404` | `Scan result not found: {scan_id}`: wrong ID, or the scan belongs to another team |
| `409` | Comparing a run that is not completed or partial |
| `410` | Raw artifact or issued copy no longer in storage |

:::note[Two scan stores]
Native scans (`/api/native-scans/*`) are team-scoped. The aggregate history
(`/api/scan-management/*`) is user-scoped and reads from a different
collection. To fetch a single native scan's findings, use
`GET /api/native-scans/results/{scan_id}`.
:::

## Related

- [Vulnerabilities](./vulnerabilities.md): the normalized, deduplicated view of findings across all scans
- [App & Infrastructure Scanning](../security-scanning/index.md)
