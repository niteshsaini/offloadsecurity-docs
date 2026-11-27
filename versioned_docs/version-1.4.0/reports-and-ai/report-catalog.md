---
title: "Report Catalog"
sidebar_label: "Report Catalog"
sidebar_position: 3
description: "Every export the platform produces, by module — what it contains, the formats, where to click and the API route — plus the branded PDF / HTML / DOCX report family, how issued reports are frozen and verified, and the retention rules."
---

# Report Catalog

Before building a report, check whether it already exists. This page is the complete list, grouped by who usually asks for it.

## Scanning

![Consolidated Security Report dialog on Scanning → Targeted runs: 1 scan, 1 target, 1 tool (security headers on http://juice-shop:3000); report title, HTML / PDF / DOCX format and optional evidence screenshots](/img/screenshots/reports-and-ai/scan-results-report.webp)

| Report | Content | Formats | Where |
| --- | --- | --- | --- |
| **Per-scan report** | One web / API / network / TLS scan with findings, evidence and remediation | HTML · PDF · DOCX | Scanning → *Completed* → **View / HTML / PDF** per row · `GET /api/native-scans/results/{scan_id}/download?format=` |
| **Consolidated security report** | Selected scans (or all completed scans of a target) merged into one executive document: risk matrix, findings by tool, optional **evidence screenshots** of affected URLs, remediation roadmap | HTML · PDF · DOCX | Scanning → **Consolidated Report** (tick scans first, or it takes all completed) · `POST /api/reports/consolidated` · `POST /api/reports/target` → job, then `GET /api/reports/{job_id}/download`; history at `GET /api/reports/history` |
| **App Scan report** | The all-tools application assessment with standards mapping | HTML · PDF | App Scan → run → **Report** · `GET /api/app-scan/{app_scan_id}/report` |
| **Network VAPT report** | Network / infrastructure assessment from the latest Greenbone OpenVAS and nmap results: scope and methodology, executive summary, risk-rated findings with affected hosts, evidence, remediation and retest status, annexures, integrity statement | PDF · DOCX · HTML | Audit Reports → **Network VAPT report** · `GET /api/export/network-vapt` · `.docx` · `.html` — see [below](#network-vapt-report) |
| **Code report** | Per-repository / per-scan SAST, secrets, SCA, IaC findings with tool breakdown; rendered from the copy frozen when the scan completed (`live=true` for the current state) | PDF (+ raw artifacts per tool) | Code Command Center → Reports → **Export** · `GET /api/code/reports/{scan_id}/export?format=pdf` · `…/artifact/{kind}` |
| **SBOM** | Components, licences, vulnerabilities for a code scan or image | CycloneDX / SPDX JSON · CSV · vulnerabilities CSV · licence notices | Code → SBOM & Licences → **Download / Export** · `GET /api/code/sbom/{scan_id}/download` · `…/export?format=csv\|csv-vulns\|json` · `…/report` |
| **Container scan export** | Image vulnerabilities from a full analysis | JSON · CSV · CycloneDX | Container Security → scan → **Export** · `GET /api/container/scans/{scan_id}/export?format=json\|csv\|cyclonedx` |
| **Container compliance report** | Image / registry / account against CIS Docker, NIST, PCI DSS or SOC 2, with a manifest of every scan it used; `scan_id` reports on one past scan | JSON · HTML · PDF | Container Security → Compliance → **Generate** · `POST /api/container-security/compliance-report` · issued copies: `GET …/compliance-report/history` · `…/compliance-report/{report_id}` |
| **Kubernetes compliance report** | Cluster against CIS, NIST, PCI DSS, SOC 2 or HIPAA; each completed scan also freezes its CIS / NIST / PCI / SOC 2 reports as a point-in-time record | JSON · HTML · PDF | Kubernetes Security → Compliance → **Generate report** · `POST /api/k8s/compliance/report` · frozen: `GET /api/k8s/compliance/history/{cluster_id}` · `…/compliance/reports/{report_id}` |

## Cloud, vulnerabilities and risk

| Report | Content | Formats | Where |
| --- | --- | --- | --- |
| **Cloud findings export** | Filtered CSPM findings | CSV · XLSX | Cloud Security → Findings → **Export** · `GET /api/cspm/findings/export?format=csv\|xlsx` (session only) |
| **Vulnerability occurrences / findings** | The unified lake, filterable | JSON over the API | `GET /api/vulnerabilities/occurrences` · `GET /api/vulnerabilities/findings` |
| **Risk register export** | Risks with treatment plans and controls | CSV (selection) · JSON / CSV (full) | Risk Management → **Export CSV** on a selection · Reports → **Full Risk Export** · `GET /api/risk-management/reports/export?format=json\|csv` |
| **Risk executive summary** | Register posture for a board pack | JSON (+ PDF data) | `GET /api/risk-management/reports/executive-summary` · `…/executive-pdf-data` |
| **Heat map export** | 5 × 5 matrix data | JSON | Risk Management → Heat Map → **Heat Map Export** |
| **SLA breaches** | Current breach list | JSON | `GET /api/sla/breaches` |

## Compliance and audit

| Report | Content | Formats | Where |
| --- | --- | --- | --- |
| **Audit reports** | Controls (with overrides and evidence counts), findings, drift history, remediation audit trail, compliance-score history | Attestable PDF (content SHA-256 on every page) + CSV per section, or CSV only | Audit Reports · `POST /api/compliance-engine/reports/generate` → `…/download/{section}` — see [Audit Reports](../compliance/audit-reports.md) |
| **Auditor package** | Per framework, per control, evidence in four layers | ZIP | Evidence Hub → **Download audit package** · `GET /api/evidence-completion/auditor-package/{framework}` |
| **Statement of Applicability** | Requirement → controls → status | JSON | `GET /api/common-controls/soa/{framework}` |
| **Assessment PDF** | A completed questionnaire with answers, evidence and score | PDF | `GET /api/assessments/{assessment_id}/export-pdf` |
| **DPDP audit pack** | Event log slice + module state, SHA-256 sealed | JSON · PDF | DPDP Compliance → Audit & Export · `POST /api/dpdp/audit/pack` → `…/pack/{pack_id}/pdf` |
| **DPDP breach reports** | Rule 7(2) Board report and CERT-In report text | Text (for filing) | Breach → **Report text** · `GET /api/dpdp/breach/{incident_id}/dpb-report-text` · `…/cert-in-report-text` |
| **Executive compliance PDF** | Executive summary, framework status with chart, trend, readiness, strengths, open control gaps | PDF | Executive Dashboard → **Export PDF** · `GET /api/executive-dashboard/export-pdf` — see [Executive Dashboard](./executive-dashboard.md#executive-reports) |

## Executive

| Report | Content | Formats | Where |
| --- | --- | --- | --- |
| **Board report** · **Trend analysis** · **Certification plan** | See [Executive Dashboard](./executive-dashboard.md#executive-reports) | On screen · PDF | Executive Dashboard → Executive Reports |
| **Gap analysis** · **Remediation roadmap** | Generated documents from the current gaps | On screen · PDF · email | Executive Dashboard → Gap Analysis / Remediation Roadmap |
| **Scheduled reports** | Any of the above on a cadence | PDF by email, history | [Scheduled Reports](./scheduled-reports.md) |

## Branded report family (API)

A set of branded, team-scoped documents that share one design system (cover page, document control table, charts, header/footer) and are rendered server-side. They are available over the API today and are what integrations and scripts should call for a finished document:

| Route | Formats | Content |
| --- | --- | --- |
| `GET /api/export/executive-dashboard` | PDF | Executive dashboard summary |
| `GET /api/export/compliance-posture` | PDF | Compliance posture (same as the dashboard's Export PDF) |
| `GET /api/export/cloud-posture` · `.html` · `.docx` | PDF · HTML · DOCX | Cloud posture across connected accounts |
| `GET /api/export/web-app` · `.html` · `.docx` | PDF · HTML · DOCX | Web-application security findings |
| `GET /api/export/network` · `.html` · `.docx` | PDF · HTML · DOCX | Network security findings |
| `GET /api/export/network-vapt` · `.html` · `.docx` | PDF · HTML · DOCX | Network / infrastructure VAPT report (see below) |
| `GET /api/export/app-sec` · `.html` · `.docx` | PDF · HTML · DOCX | Application security (code + dependencies) |
| `GET /api/export/consolidated-exec` · `.html` · `.docx` | PDF · HTML · DOCX | Consolidated executive report across modules |
| `GET /api/export/scan-results?scan_type=` | PDF | Scan results by type |
| `GET /api/export/ai-decisions` | PDF | AI SOC agent decisions audit |

All of them stream the file with a `Content-Disposition` attachment header; authenticate with `X-API-Key`.

## Network VAPT report

The report an empanelled auditor can use for a network / infrastructure VAPT engagement, built from your Greenbone OpenVAS and nmap results. It is generated when you download it, from the latest OpenVAS report per task and the latest nmap scan per target.

**Where:** **Audit Reports** → *Network VAPT report* → **VAPT report (PDF)** or **VAPT report (Word)**. The section is shown to users with **Vulnerability View**, **View Scans** or **View Assessments**.

| Part | Contents |
| --- | --- |
| **Scope & methodology** | Targets and windows; tools with versions (OpenVAS's own version is printed as *not recorded*); the Greenbone result filter; authenticated coverage per host, or *not recorded* |
| **Summary** | Executive summary, severity breakdown, KEV / EPSS view, top findings |
| **Findings** | Risk-rated, grouped per check with every affected host, CVSS, evidence, remediation, retest status and — for users who can view integrations — the Wazuh agent's verdict for the host |
| **Retest** | Findings closed on retest, removed tasks, and analyst decisions in the last 90 days (older closures counted) |
| **Annexures** | Host inventory, open ports and services, host-side correlation |
| **Integrity** | Last section: whether every source was read. A source that could not be read marks the report as degraded; it never says *Complete* |

Failed nmap targets are listed, not dropped. The Word version is rendered from the same sections as the PDF, so it carries every row.

## Point-in-time and verifiable reports

A report handed to an auditor must stay the same document. Where noted below, the platform freezes the data a report was built from, prints what the report is made of, and keeps a fingerprint of the issued file.

| Report | What is kept |
| --- | --- |
| **Cloud Security posture** (`/api/export/cloud-posture`, PDF / HTML) | Each scan run's findings are frozen on completion; a run-scoped report reads that frozen copy (hash-checked) and states its basis. The report prints the engine version, the scan identity (no secrets) and per-region evidence digests. Every issued file is fingerprinted (SHA-256), recorded and kept |
| **Code report** | Frozen at scan completion, including the triage state at that moment; the PDF renders from the frozen copy by default |
| **Kubernetes compliance** | Frozen per scan with a scan manifest (scanners, versions, image digests, cluster identity, credential type) and a coverage statement |
| **Container compliance** | The findings used are frozen with a manifest of every scan (image, digest, tools, scanner DB age) and a coverage statement naming unreadable, tag-only or degraded scans and caps |
| **Native scan reports** and **consolidated reports** | Each export's SHA-256 is recorded; raw tool output (nmap XML, Nuclei JSONL, testssl / ZAP JSON) and run provenance are kept |
| **Audit reports** | PDF carries the report ID and content SHA-256 in the footer of every page |

Reports built on the shared reporting layer (container and Kubernetes compliance, Network VAPT) end with an **integrity** section, and any table they truncate states the true total and where the full list is — nothing is cut silently.

**Verify a file.** `GET /api/native-scans/exports/verify?sha256=<digest>` answers whether your team was issued exactly that file, across scan exports, consolidated reports and the issued-report ledger (cloud posture, code, Kubernetes compliance, container exports). `GET /api/export/issued/{sha256}` re-downloads a ledgered report byte for byte; a kept copy that no longer matches its digest is refused. Audit reports are verified on the Audit Reports page (*Verify a report*) — see [Audit Reports](../compliance/audit-reports.md).

:::note[Narrative text is templated]
Executive summaries and narratives in these reports are generated from your data by templates, not by an AI model. An LLM-written remediation narrative in the branded cloud-posture and consolidated executive reports is **opt-in per team** (`llm_narrative_enabled` in the team's branding record, off by default, no screen to set it) and is limited to the top findings.
:::

## Retention and scope

- Generated reports (consolidated, executive, scheduled, audit) are kept **180 days** by default (`REPORT_RETENTION_DAYS`); per-scan reports follow the scan retention policy in [Scan Management](../security-scanning/scan-management.md#result-retention).
- Every report contains **only the active team's data**; API keys are scoped to their team.
- Branding (name, logo, colors, classification banner, legal footer) comes from the platform's `PLATFORM_BRAND_*` settings, optionally overridden per team, and applies to every server-rendered document. Issued-report copies follow the same `REPORT_RETENTION_DAYS` window.

## Related

- [Executive Dashboard](./executive-dashboard.md) · [Scheduled Reports](./scheduled-reports.md)
- [Reports & AI API](./api.md) — the routes above with parameters.
