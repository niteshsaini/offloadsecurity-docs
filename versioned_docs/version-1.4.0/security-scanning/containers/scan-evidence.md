---
title: "Container Scan Records & Evidence"
sidebar_label: "Scan Records & Evidence"
sidebar_position: 5
new_in: 1.4.0
description: "What every container scan records — engines, vulnerability database and its age, registry login, raw output, authorization — and how to compare two scans and verify an exported file."
---

# Container Scan Records & Evidence

From 1.4.0 each container scan is a point-in-time record you can defend later: it says exactly what ran, against which image digest and vulnerability database, who authorized it, and what it could not assess. Exports and reports are fingerprinted so a file can be checked against what the platform issued.

Most of what this page describes is stored on the scan record and returned by the API; the UI shows the result, its banners and the reuse source.

## What each run records {#run-provenance}

| Recorded | Detail |
| --- | --- |
| **Image identity** | The resolved digest, whether the scan was digest-pinned, and for multi-arch images the platform scanned. See [One digest, every tool](./image-scanning.md#digest-pinning). |
| **Engines** | Each tool's version. Trivy: its report schema and time and the arguments used. Grype: its version. |
| **Vulnerability database** | Trivy's database version and update time; Grype's database build time and schema. Each database's **age in days**, and **stale** when older than `CONTAINER_VULN_DB_MAX_AGE_DAYS` (default 7). |
| **Registry login** | The registry host and whether a login was used or not required — never a credential. |
| **Raw output** | For registry scans, each tool's original output is kept in object storage with its SHA-256. |
| **Outcome per image** | Completed, partial or failed, from what Trivy and Grype actually returned. |
| **What the scanners said** | Findings keep the scanner's own severity and fields; secrets and base-OS end-of-support are recorded on the scan. |
| **Reuse source** | When results were reused or re-matched from an earlier scan of the same digest, which scan and when. See [Results reused by image digest](./image-scanning.md#digest-reuse). |

:::note[Why the database age matters]
Scanner images ship with their vulnerability database and automatic updates off. A stale database finds fewer CVEs without failing, so the age is recorded on every scan and called out in compliance reports.
:::

## Who authorized the scan {#who-authorized-the-scan}

Every container scan — single image, bulk, scan job or registry sweep — records its **authorization**:

- An attestation sent with the scan (`engagement` in the request body: `attested`, optional `reference`, `environment`, `valid_until`) is recorded on the scan and kept as the registry's **standing authorization** for later scans, until `valid_until`.
- Without one, the registry's standing authorization applies. A registry sweep uses the cloud account's.
- With none, the scan is recorded as *authorization not recorded* — never as authorized.

When an administrator sets `SCAN_REQUIRE_AUTHORIZATION=true`, a scan without a current authorization is refused (HTTP 400), and webhook or polling auto-scans are skipped and logged. In 1.4.0 the container screens do not have authorization fields: record the first authorization for a registry by sending `engagement` with a scan over the API (for example `POST /api/container-registries/saved/{registry_id}/scan-existing`).

## Compare two scans of an image {#compare-two-scans}

```
GET /api/container-registries/scans/{scan_id}/compare?baseline={scan_id}
```

Compares a registry image scan with a baseline — by default the image's previous completed scan — and lists vulnerabilities (CVE × package × version), not just counts:

| List | Meaning |
| --- | --- |
| `new` | In this scan, not in the baseline. |
| `fixed` | In the baseline, not in this scan, **same image digest**. |
| `not_in_new_image` | In the baseline, not in this scan, and the tag now names a **different digest**. The old image had it; it is not "fixed", because that image may still run. |
| `unchanged` / `severity_changed` | Present in both. |

The response also carries caveats when either scan was degraded, the scans used different tools, or a scan was by tag rather than digest. The comparison is API-only in 1.4.0.

## Verifiable exports {#verifiable-exports}

Every container scan export — **JSON**, **CSV** and **SBOM** (CycloneDX) from the scan detail — is fingerprinted when issued:

1. The download carries its SHA-256 in the `X-Content-SHA256` response header, and the platform keeps a byte-for-byte copy.
2. To check a file later, compute its SHA-256 and call:
   ```
   GET /api/native-scans/exports/verify?sha256={hex}
   ```
   A match names the export; no match means the file was altered or did not come from this platform.
3. An issued file can be downloaded again exactly as issued: `GET /api/export/issued/{sha256}`.

If a scan's findings cannot be loaded from storage, the export fails with an error (HTTP 502) instead of returning an empty or partial file.

Container compliance reports are frozen in the same spirit — see [Frozen when issued](./governance.md#frozen-reports).

## Audited purges

When retention removes old container scan data, the purge is recorded (collection, number of records, cutoff, time) in the platform's retention audit, so a missing record can be told apart from one that never existed. Retention periods are set by your administrator; see [Scan Management — Result retention](../scan-management.md#result-retention).

## Related

- [Engagement & Evidence](../scan-evidence.md) — the same model for Scanning-module runs.
- [Image Scanning](./image-scanning.md) — digest pinning, reuse and superseded findings.
- [Policies, Webhooks, SBOM & Compliance](./governance.md) — frozen compliance reports.
- [Registries — sweep coverage](./registries.md#sweep-coverage) — what a registry sweep did and did not scan.
