---
title: "Glossary"
sidebar_position: 14
description: "The terms Offload Security uses across its screens and documentation — findings and occurrences, fingerprints, SCF controls, drift, KEV and EPSS, triage verdicts, teams and roles, API-key scopes, AIBOM — each with where to read more."
---

# Glossary

Terms as the product uses them, in the order you are likely to meet them.

## Scanning and findings

| Term | Meaning |
| --- | --- |
| **Scan** | One run of an engine against one target — a cloud account, a cluster, an image, a repository, a URL, a host. Scans are triggered by hand, by schedule or by a pipeline. |
| **Assessment (scanning)** | A scan *type* in the Scanning workspace: Web Vulnerability, Nuclei, Security Headers, SSL/TLS, Network Discovery, API Security Testing, API Discovery, Domain Scan, App Scan. |
| **Finding** | One issue observed by one scan on one resource — severity, description, resource, remediation. Cloud, code, container, Kubernetes and web / API / network findings all normalise into the same shape. |
| **Occurrence** | One instance of a *vulnerability* (a CVE, a weakness) on one asset. The same CVE on three images is three occurrences of one vulnerability. |
| **Fingerprint** | The stable identity of a finding (source, check, resource). A re-scan updates the fingerprinted finding rather than creating a duplicate; a fingerprint that stops appearing is reconciled as resolved. |
| **Reconciliation** | The step after a scan that resolves findings the scanner no longer sees — and reopens ones that come back. |
| **Severity** | Critical · High · Medium · Low · Info, normalised across sources. |
| **KEV** | CISA's Known Exploited Vulnerabilities catalog — CVEs confirmed exploited in the wild. A KEV flag raises priority everywhere: triage, threat-intel scoring, the Command Center's *Critical* verdict. |
| **EPSS** | Exploit Prediction Scoring System — the probability (0–1) a CVE is exploited in the next 30 days. |
| **SBOM** | Software bill of materials for a repository or image (CycloneDX / SPDX); the source of licence compliance and the AIBOM. |
| **Raw findings** | The per-scanner view in Vulnerability Management, before triage groups and ranks them. |

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

## Compliance

| Term | Meaning |
| --- | --- |
| **SCF** | The Secure Controls Framework — the single control library every framework maps to. Implement a control once; it counts for every framework that references it. |
| **Framework** | A standard or regulation the platform scores you against — SOC 2, ISO 27001, PCI DSS, NIST CSF, RBI, SEBI CSCRF, DPDP and the rest of the catalog. Activated per team. |
| **Control status** | Implemented · Partial · Not implemented · Not assessed · Not applicable; evidence-only counts a quarter. |
| **Compliance score** | Implemented (1) + partial (0.5) + evidence-only (0.25) over all in-scope controls, per framework, refreshed every four hours. |
| **Drift** | A control that was implemented and is no longer, a clean control that gained findings, expired evidence, or a score crossing a threshold — detected from daily snapshots. |
| **Evidence** | An artefact proving a control: auto-collected from scans, uploaded, or API-recorded; graded for quality and freshness in the Evidence Hub. |
| **Auditor package** | The per-framework ZIP of evidence by control an auditor receives. |
| **Statement of Applicability (SoA)** | Requirement → controls → status → justification for exclusions; exported for ISO 27001 and ISO 42001. |
| **Assessment (compliance)** | A guided questionnaire against a framework (ASVS, NIST CSF, SOC 2, SAMM…), scored, with SCF-based auto-fill. |
| **DPIA** · **SDF** | Data Protection Impact Assessment; Significant Data Fiduciary — terms from India's DPDP Act, handled in the DPDP module. |

## Threat intelligence and AI

| Term | Meaning |
| --- | --- |
| **Indicator (IOC)** | An IP, domain, URL, hash, CVE or certificate from a threat feed or your own import, with severity, confidence and time-to-live. |
| **Feed** | One of the nine curated sources (CISA KEV, URLhaus, OTX, Feodo Tracker, SSL Blacklist, PhishTank, Blocklist.de, Spamhaus DROP, OpenPhish) fetched hourly. |
| **Indicator aging** | Confidence decay per day and expiry after a time-to-live, so old intelligence retires. |
| **Rule-based mode** | The Security Command Center without an LLM provider: verdicts from the rule set, templated advisor answers. **LLM Active** adds model reasoning. |
| **Auto-Fix action** | A remediation playbook matched to a cloud finding, waiting for approval; simulated until the operator enables live execution. |
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
| **Platform administrator** | The first account on a deployment; sees across teams, runs User Activity and Client Menu Settings, keeps password sign-in when SSO is enforced. |
| **API key** | `osk_…` credential for automation, acting as its creator within a scope set, with expiry, IP allowlist and rate limit. |
| **Scope** | A permission granted to an API key, e.g. `scans:trigger`, `vulnerabilities:read`. |
| **Audit trail** | The record of every authenticated request — actor, team, action, outcome — kept 365 days. |
| **Capability (integration)** | What an integration does once connected: *pulls data in*, *two-way*, *sends out*, *connection test only*, *catalog only*. |
| **Webhook subscription** | A signed JSON delivery of platform events to an endpoint you control. |
| **Unified Scheduler** | The one view of every recurring scan and job across modules. |
| **On-premises** | The full platform as a Docker Compose stack on your own host, with private targets in scope. |

Terms specific to one module are defined on that module's page; use the search box for anything not listed here.
