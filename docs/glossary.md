---
title: "Glossary"
sidebar_position: 14
description: "The terms Offload Security uses across its screens and documentation — findings and occurrences, fingerprints, provenance and frozen reports, risk exceptions, SCF controls, drift, KEV and EPSS, teams and roles, API-key scopes, AIBOM."
---

# Glossary

Terms as the product uses them, in the order you are likely to meet them.

## Scanning and findings

| Term | Meaning |
| --- | --- |
| **Scan** | One run of an engine against one target — a cloud account, a cluster, an image, a repository, a URL, a host. Scans are triggered by hand, by schedule or by a pipeline. |
| **App Scan** | The Scanning module's graded assessment of a web application or API: one run of every selected tool (up to 13), with a verified login, standards mapping (ASVS, OWASP, NIST SSDF), an A–F grade and one report. Listed on the **Assessments** tab. |
| **Targeted run** | A single-tool scan in the Scanning module — ZAP, Nuclei, Nmap, testssl.sh, security headers, API discovery, API deep scan, domain recon. Not graded and no login check. Listed on the **Targeted runs** tab. |
| **Assessment Type** | The first choice on **Scanning → New scan**: App Scan (the default) or one of the targeted runs. |
| **Engagement record** | What a web, API or network scan records about its authorization: who attested they are authorized to test the target and when, an optional reference, environment and "authorized until" date, and excluded paths or hosts. Rescans carry it forward and are refused after the window ends. Mandatory only when the operator sets `SCAN_REQUIRE_AUTHORIZATION=true`. |
| **Provenance** | The record of what produced a run: tool, engine, pinned version, settings, redacted command line, exit code, UTC start and end. Printed in reports; "not recorded" when a run predates it. |
| **Raw evidence (artifacts)** | The tool's own output for a web, API or network run (for example nmap XML or the ZAP JSON report), kept with its SHA-256 alongside the parsed findings. |
| **Compare (runs)** | A finding-by-finding diff of a run with the previous run of the same target (or a chosen baseline): new, fixed, unchanged. A partial run lists missing findings as *not seen*, never *fixed*. Available for web / API / network, cloud, container, Kubernetes and code scans. |
| **Frozen report** | A report or snapshot fixed when the scan or report was issued, so later scans and triage do not change it; re-downloads return the issued bytes. |
| **Export fingerprint** | The SHA-256 digest of an issued report, sent with the download and printed in the report; a verify endpoint checks a file against what the platform issued. |
| **Finding** | One issue observed by one scan on one resource — severity, description, resource, remediation. Cloud, code, container, Kubernetes and web / API / network findings all normalize into the same shape. |
| **Occurrence** | One instance of a *vulnerability* (a CVE, a weakness) on one asset. The same CVE on three images is three occurrences of one vulnerability. |
| **Fingerprint** | The stable identity of a finding, built from what the issue is and where it is rather than which tool found it. A re-scan updates the fingerprinted finding rather than creating a duplicate; a fingerprint that stops appearing is reconciled as resolved. Not to be confused with an *export fingerprint* or the App Scan *technology fingerprint* (detected tech stack). |
| **Reconciliation** | The step after a scan that resolves findings the scanner no longer sees — and reopens ones that come back. |
| **Severity** | Critical · High · Medium · Low · Info, normalized across sources. |
| **KEV** | CISA's Known Exploited Vulnerabilities catalog — CVEs confirmed exploited in the wild. A KEV flag raises priority everywhere: triage, threat-intel scoring, the Command Center's *Critical* verdict. |
| **EPSS** | Exploit Prediction Scoring System — the probability (0–1) a CVE is exploited in the next 30 days. |
| **SBOM** | Software bill of materials for a repository or image (CycloneDX / SPDX); the source of license compliance and the AIBOM. |
| **Raw findings** | The per-scanner view in Vulnerability Management, before triage groups and ranks them. |
| **SARIF import** | Uploading a SARIF 2.1.0 log from another scanner (CodeQL, Semgrep, Snyk Code…) in Code Command Center or from CI; its results become findings beside the platform's own. |

## Triage, risk and SLAs

| Term | Meaning |
| --- | --- |
| **Triage** | The engine that ranks open findings into an action queue from severity, KEV, EPSS, exposure, environment and age; also the Security Command Center's agent that assigns a verdict per finding. |
| **Verdict** | The Command Center's decision on a finding: Critical · Investigate · Monitor · False positive · Auto-resolved, with a confidence and a reason. |
| **Work item** | One check across many resources (for example *S3 bucket public access* on 14 buckets) — the unit of a bulk triage decision. |
| **Disposition** | The human decision on a triaged finding: fix · defer · dedup · suppress. |
| **SLA** | A policy giving matched findings a respond-by and resolve-by time (the default production policies: critical 1 day, high 7, medium 30), with warnings before and escalation after breach. |
| **Alert** | A record in the unified alert stream — from a new or reopened critical / high finding, an SLA event, compliance drift, a scan or integration failure, or a Wazuh detection — routed to the bell and to connected channels. |
| **Risk** | An entry in the Risk Register: likelihood × impact, owner, treatment plan, linked controls and findings, review date. Findings promote into risks; risks can also be imported. |
| **Risk appetite** · **KRI** | The tolerated risk level per category, and the key risk indicators tracked against it. |
| **Exception** | A documented, time-boxed decision not to fix a finding or apply a control, with an approver. |
| **Risk exception** | In Vulnerability Management → Risk exceptions: a formally requested, time-limited exception for one finding (accept risk, suppress or defer), approved by someone other than the requester. While approved it is left out of open, overdue, SLA and severity counts and hidden from the Cloud Security and Kubernetes findings views; it can be revoked. |
| **Investigation record (case file)** | The **Case file** on a triaged finding: priority evidence, owner (or why there is none), the next action, closure proof (fix PRs, rescan verification) and a timeline across handoffs. Read-only. |
| **Fix first** | In Infra Command Center → Endpoint Security, Wazuh host vulnerabilities ranked by triage priority, with a roll-up of which package upgrades fix the most. |

## Compliance

| Term | Meaning |
| --- | --- |
| **SCF** | The Secure Controls Framework — the single control library every framework maps to. Implement a control once; it counts for every framework that references it. |
| **Framework** | A standard or regulation the platform scores you against — one of the 27 in the catalog, such as SOC 2, ISO 27001, PCI DSS, NIST CSF, SEBI CSCRF and India's DPDPA. Activated by the platform administrator. The RBI Cyber Security Framework is not in the catalog. |
| **Control status** | Implemented · Partial · Not implemented · Not assessed · Not applicable; evidence-only counts a quarter. The **Why this status** panel shows who or what set it and on which evidence. |
| **Compliance score** | Implemented (1) + partial (0.5) + evidence-only (0.25) over all in-scope controls, per framework, refreshed every four hours. |
| **Drift** | A control that was implemented and is no longer, a clean control that gained findings, expired evidence, or a score crossing a threshold — detected from daily snapshots. |
| **Evidence** | An artifact proving a control: auto-collected from scans, uploaded, or API-recorded; graded for quality and freshness in the Evidence Hub. |
| **Auditor package** | The per-framework ZIP of evidence by control an auditor receives, in four layers: governance, technical, operational and monitoring. |
| **Statement of Applicability (SoA)** | Requirement → controls → status → justification for exclusions; exported for ISO 27001 and ISO 42001. |
| **Assessment (compliance)** | A guided questionnaire against a framework (ASVS, NIST CSF, SOC 2, SAMM…), scored, with SCF-based auto-fill. |
| **DPIA** · **SDF** | Data Protection Impact Assessment; Significant Data Fiduciary — terms from India's DPDP Act, handled in the DPDP module. |

## Threat intelligence and AI

| Term | Meaning |
| --- | --- |
| **Indicator (IOC)** | An IP, domain, URL, hash, CVE or certificate from a threat feed or your own import, with severity, confidence and time-to-live. |
| **Feed** | One of the eight built-in sources (CISA KEV, URLhaus, OTX, Feodo Tracker, SSL Blacklist, Blocklist.de, Spamhaus DROP, OpenPhish). Enabled feeds are checked every 15 minutes and each is fetched when its own refresh interval has passed. PhishTank is retired. |
| **Indicator aging** | Confidence decay per day and expiry after a time-to-live, so old intelligence retires. |
| **Rule-based mode** | The Security Command Center without an LLM provider: verdicts from the rule set, templated advisor answers. **LLM Active** adds model reasoning. |
| **Auto-Fix action** | A remediation playbook matched to a cloud finding, waiting for approval; simulated until the operator enables live execution (`REMEDIATION_LIVE_EXECUTE`). |
| **Agentic fix** | The fix agent in Code Command Center that changes code for a finding, re-scans to verify and opens a pull request ("verified PR" / "unverified PR"). Off by default (`AGENTIC_FIX_ENABLED`), then opted in per team; it never merges. |
| **AIBOM** | AI bill of materials — the AI SDKs, frameworks, models and vector stores found in your SBOMs. |
| **AI discovery** | Finding AI services in your cloud inventory and LLM configuration and adding them to the AI Governance registry. |
| **Knowledge Base** | Your uploaded policies and standards, chunked and embedded, answering questions and questionnaires with citations. |
| **Answer bank** | Approved questionnaire answers reused for semantically matching questions. |

## Platform and access

| Term | Meaning |
| --- | --- |
| **Team** | The tenancy boundary. Every record belongs to one team; you work in one *active team* and may belong to several. |
| **Role** | One of six per team — Admin, Security Manager, Security Analyst, Compliance Officer, Auditor, Viewer — mapped to named permissions. |
| **Permission** | A named capability checked on every request (`run_scans`, `manage_integrations`, `execute_remediations`…). |
| **Platform administrator** | The first account on a deployment; sees across teams, runs User Activity and Client Menu Visibility, keeps password sign-in when SSO is enforced. |
| **API key** | `osk_…` credential for automation, acting as its creator within a scope set, with expiry, IP allowlist and rate limit. |
| **Scope** | A permission granted to an API key, e.g. `scans:trigger`, `vulnerabilities:read`. |
| **Audit trail** | The record of every authenticated change and export — actor, team, action, outcome — kept in a tamper-evident per-team hash chain that can be verified and exported to a SIEM. |
| **Capability (integration)** | What an integration does once connected: *pulls data in*, *two-way*, *sends out*, *connection test only*, *catalog only*. |
| **Webhook subscription** | A signed JSON delivery of platform events to an endpoint you control. |
| **Unified Scheduler** | The one view of every recurring scan and job across modules. |
| **On-premises** | The full platform as a Docker Compose stack on your own host, with private targets in scope. |
| **Endpoint 360** | One page per Wazuh agent: identity, what to fix first, vulnerabilities, network findings from OpenVAS, alerts, compliance, file integrity, ATT&CK techniques and logins. In Infra Command Center → Endpoint Security. |
| **Capability health** | Per-integration and per-feed status: whether each source is still delivering, why it stopped, and how to restore it. |
| **Help panel** | The **Help** button on each module page: task guides with steps, errors and limits; `?help=<guide>` links open one guide. |
| **Deep link** | A URL that opens a specific module tab (`?tab=`) or filtered view; dashboard tiles and coverage cards use them to drill down. |

Terms specific to one module are defined on that module's page; use the search box for anything not listed here.
