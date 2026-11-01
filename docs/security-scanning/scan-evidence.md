---
title: "Engagement & Evidence"
sidebar_label: "Engagement & Evidence"
sidebar_position: 3.5
description: "How every Scanning run records who authorized it, exactly what ran, the tool's raw output and every report it issued — so a point-in-time test can be defended afterwards."
new_in: 1.4.0
---

# Engagement & Evidence

A security test is only useful to an auditor or a client if you can show, later, that it was authorized, what it covered, what produced each result and that the report you hand over is the one the platform issued. From 1.4.0 every Scanning run records that evidence. This page explains what is kept and where to find it.

## The engagement record

App Scan and targeted ZAP, Nuclei, Nmap and testssl.sh runs carry an engagement record:

| Field | Source |
| --- | --- |
| Attested | The **I am authorized to test this target** checkbox |
| Attested by / at | Your user and the time (UTC), taken from your session, never from the request |
| Reference | Optional engagement, rules-of-engagement or ticket ID (up to 200 characters) |
| Environment | Production, staging, development, test or unspecified |
| Valid until | Optional end of the authorized window; a past date is refused |
| Scope | Requested targets, plus excluded paths (ZAP, App Scan) and excluded hosts (Nmap) |

How it is enforced:

- **In the launcher**, **Submit** stays disabled for those scan types until you attest.
- **Over the API**, attestation is optional by default so existing CI callers keep working; their scans are recorded and reported as **authorization not recorded**, never as authorized. Set `SCAN_REQUIRE_AUTHORIZATION=true` on the deployment to refuse any scan without an attestation (HTTP 400).
- **Rescan** carries the attestation (noting who re-ran it) and the exclusions, and is refused once the authorized window has ended.
- **Scheduled scans** store an engagement on the schedule. At each run the platform checks it again: if the authorization is missing (when required) or past its end date, the run fails and nothing is scanned. The Unified Scheduler flags such schedules and offers **Re-attest** ([Scan Management](./scan-management.md#authorization-on-scheduled-scans)).

**In the report**, the scope table shows an Authorization row (who, when, reference, window — or "Not recorded" and how many scans lack one), the Environment you chose ("Not specified" otherwise), the network type derived from the targets (IP addresses are classified; hostnames are not resolved at report time, and the report says so) and the excluded paths and hosts. It no longer asserts "Production" or "External scan" by default.

## Provenance: what exactly ran

Each Nmap, Nuclei (single and bulk), testssl.sh and ZAP run — including the tool runs inside an App Scan and scheduled runs — records:

- the tool and the **engine**: the pinned Docker image, a local binary, or the built-in fallback;
- the **version** (pinned image tag or the binary's reported version) and, for Nuclei, the **templates release**;
- the profile and settings, and the command line with credentials redacted (ZAP's command line is deliberately not recorded, because its configuration can carry authentication values);
- the exit code and the UTC start and end times.

The run detail shows this as **Ran: …**, and any depth that did not happen — for example OS detection on an unprivileged engine — as **Not done: …**. The report's configuration appendix prints the recorded values; a setting that was not recorded is printed as "not recorded", never guessed.

## Raw evidence kept with the run

The tool's own output is kept in object storage after parsing:

| Tool | Kept |
| --- | --- |
| Nmap | XML and normal output |
| Nuclei | JSONL results (and the target list for bulk runs) |
| testssl.sh | JSON |
| ZAP | JSON report |

Credential header values are masked in the stored text, and the SHA-256 and size of each file are recorded. A file larger than `SCAN_ARTIFACT_MAX_BYTES` (default 50 MB) is not kept, and the run says so with the reason. Download a file from the run detail (**Raw output**) or with `GET /api/native-scans/results/{scan_id}/artifacts/{name}`, which returns the digest in `X-Content-SHA256`.

## Completeness

A run that did not fully happen is never presented as clean:

- A run where a tool stopped part-way, timed out or fell back to built-in checks is **partial**, with the reason. ZAP's fallback is labeled "Built-in HTTP checks (OWASP ZAP did not run)", never "OWASP ZAP".
- Reports include partial runs and list failed, missing or still-running runs as **NOT TESTED** with their reason in a **Coverage & Completeness** section.
- An App Scan where no tool completed is **failed** with no grade; a partial App Scan's grade is **provisional**.

## Fingerprinted, frozen exports

Every report you download for a targeted run (HTML, PDF, DOCX, JSON or CSV):

1. carries its SHA-256 in the `X-Content-SHA256` response header;
2. is recorded on the scan's export log (format, digest, size, who, when — the most recent 500 exports per scan are kept);
3. is stored byte-for-byte, so the exact report a client received can be downloaded again later, whatever triage changed since. Copies over 50 MB are logged but not stored.

| Task | Endpoint |
| --- | --- |
| List the exports issued for a scan | `GET /api/native-scans/results/{scan_id}/exports` |
| Re-download an issued report exactly | `GET /api/native-scans/results/{scan_id}/exports/{sha256}` |
| Check whether the platform issued a file | `GET /api/native-scans/exports/verify?sha256=<digest>` |

Verification matches the digest against your team's scan exports and generated consolidated reports.

:::note[API only]
Export history, exact re-download and verification are available over the API in 1.4.0; the run detail does not list issued exports.
:::

## Deleted scans are tombstoned

**Delete** moves a run to a tombstone record (who, when, why) instead of erasing it. Tombstones, with their raw output and issued copies, are purged by the daily retention cycle after `SCAN_TOMBSTONE_DAYS` (default 30). A deleted run disappears from the Scanning lists immediately.

:::warning[After the tombstone window]
Once a tombstone is purged, the run, its raw evidence and its issued report copies are gone. Keep downloaded reports and their digests if you must retain them longer.
:::

## Related

- [Scan Results](./scan-results.md) — run detail, comparison and reports.
- [Scan Management](./scan-management.md#result-retention) — how long runs are kept.
- [Scanning API](./api.md#evidence-and-integrity) — every endpoint on this page.
