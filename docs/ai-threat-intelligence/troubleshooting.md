---
title: "AI & Threat Intelligence Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 8
description: "Fix the common problems — a feed that shows API key required, Run Triage Now that triaged 0 findings, an Auto-Fix Engine that says No Remediation Actions, a Knowledge Base that answers 'retrieval unavailable', discovery that finds nothing — and answers to frequent questions."
---

# AI & Threat Intelligence Troubleshooting & FAQ

## Threat Intelligence

**A feed shows "API key required" and no indicators.**
URLhaus (Auth-Key) and AlienVault OTX need a key from the vendor; PhishTank's is optional. **Add API Key** on the card, then **Process Feed Now**. Keys are per team and encrypted.

**A feed is *degraded* or *critical*.**
Health is the success rate of recent fetches, recalculated every six hours. Open the card: the last error is classified — *auth* (rotate the key), *rate_limited* / *quota* (wait; the next hourly fetch retries), *timeout* / *unreachable* (egress from the platform to the feed URL), *parse* (the vendor changed format — report it), *discontinued*. Transient classes retry on their own.

**Active threats went down overnight.**
Indicator aging: confidence decays daily and indicators expire after their time-to-live (90 days by default). That is intended — see [Indicator aging](./threat-intelligence.md#import--export-and-indicator-aging). Raise the TTL for a type if your programme needs longer memory.

**Correlate returns nothing for an IP I know is in our estate.**
Correlation matches against the [asset inventory](../cloud-security/asset-inventory.md) — public IPs, hostnames and hashes discovered by scans. An asset that has not been scanned, or an internal-only address, is not there to match.

**Vuln Prioritization scores every CVE 50.**
50 is the base with no intelligence attached. Enable **CISA KEV** (+25 for listed CVEs) and, if you record them, actors and campaigns; without any feed the score cannot move.

**The Threat Actors / Campaigns / Alert Rules / Hunting tabs are missing.**
They are API-only in the current release (`/api/enhanced-threat-intelligence/…`); the tabs were removed from the UI to reduce clutter. Records you create over the API still feed prioritisation.

## Security Command Center

**Run Triage Now says "Triaged 0 findings".**
Fixed in the current release — older builds looked for a scan id field that cloud findings do not carry and took `"latest"` literally, so the button never triaged anything. If you are current and still get 0, the team has no open (`fail`) cloud findings from a scan run; use **Triage new/changed** in the Triage Center, which triages every open finding regardless of run.

**Process All Findings says "Created 0 remediation actions from 0 findings".**
Fixed in the current release — older builds read a collection nothing wrote to. If you are current and it reports *from N findings* but creates 0, no playbook matches those checks; the playbook library covers common storage, network, IAM and logging misconfigurations.

**Actions were created but the Auto-Fix Engine tab shows "No Remediation Actions".**
Fixed in the current release — the tab filtered on `pending_approval` while new actions are `pending`. Upgrade; the Pending tab now shows both.

**Execute did nothing in the cloud account.**
Expected unless the operator set `REMEDIATION_LIVE_EXECUTE=true`: executions and rollbacks are recorded as *simulated*. This is a deployment decision, not a per-team setting.

**The briefing says "monitoring 0 cloud accounts".**
Fixed in the current release (the count keyed on the wrong field). Upgrade.

**The badge says Rule-Based Mode.**
No LLM provider is configured for the team. Everything still works from rules; add a provider under Knowledge Base → AI Assistant → *AI Configuration* for model-assisted reasoning.

**Assess FP/TP marked most findings *needs review*.**
By design: only findings with code or reachability evidence are assessed; the rest are left for a person rather than guessed at. Code findings get better coverage through **Assess code**.

## AI Governance, discovery and AIBOM

**Run Discovery finds nothing.**
Discovery reads the cloud asset inventory and the LLM configuration. If no cloud scan has run, there is no inventory to read; if your AI runs somewhere the platform does not scan (a SaaS vendor, a laptop), register it by hand.

**The Discovery table is empty on the next visit although the registry has discovered entries.**
The table shows the result of the run you just started; the entries themselves are in **Model Registry** (type *discovered*). Run discovery again to see the table.

**The AIBOM shows 0 components / "N SBOM reports exist but have not been folded yet".**
Click **Reconcile now** (or wait for the daily job). 0 components after a reconcile means none of the packages in your SBOMs are in the AI catalogue — check a repository you know uses an AI SDK has a completed [code scan with SBOM](../security-scanning/code/sbom-and-licenses.md).

**ISO 42001 posture stays "Not Ready" although controls are implemented.**
Two independent causes: the score is below 50 %, or a **high** blocker exists — ISO 42001 not activated as a framework, no systems registered, or a registered system without a risk / impact assessment. The blockers list on the Compliance tab names each one.

**Prompt tests all "pass" instantly.**
No endpoint was given, so it was a dry run — payloads were recorded, nothing was sent. Provide an OpenAI-compatible chat endpoint (and key) for a live run.

**A page showed "AI Governance" twice.**
Cosmetic, fixed in the current release.

## Knowledge Base

**Questions answer "retrieval unavailable" / the questionnaire fill reports it.**
Retrieval uses OpenAI embeddings; only an Anthropic or Google key is configured. Add an OpenAI key in AI Configuration (the answering model can stay whichever you prefer). Older builds returned a 25 % confidence answer instead of this error.

**A document is *ready* but never appears as a source.**
Extraction found little or no text (scanned PDF, image-only pages). Use **Re-process documents** → *re-extract & re-embed*; if the file is an image, OCR it before uploading.

**Upload fails with a validation error on document type.**
`document_type` must be one of the listed types (`policy`, `sop`, `compliance_framework`, `audit_report`, `technical_documentation`, `security_playbook`, `incident_response`, `risk_assessment`, `training_material`, `vendor_documentation`, `regulatory_guidance`, `best_practices`) and `section_id` must be an existing section id (`GET /api/knowledge-base/sections`).

**The questionnaire came back with no question column detected.**
The detector looks for a header containing *question*, *query*, *requirement*, *control*, *criteria*, *check*, *assessment* or *description*, then falls back to the column with the longest text. Rename the column or use `POST …/questionnaire/detect-columns` to see what it found.

## Frequently asked questions

**Do the threat feeds send anything about my environment to the vendors?**
No. Feeds are fetched (with your key where required); correlation happens inside the platform.

**Which of these features call a model?**
Only those in the [AI Data & Privacy](./ai-data-privacy.md) table, and only when a provider is configured. Feeds, correlation, prioritisation, rule-based triage, the Auto-Fix Engine, discovery and the AIBOM never do.

**Can an agent close a finding or change my cloud on its own?**
No. Triage verdicts are advisory (even *auto-resolved* is a verdict to confirm), FP/TP assessment never suppresses, and Auto-Fix actions need approval and execution — which is simulated until an operator enables live execution.

**Can I bring my own indicators or share ours?**
Yes — CSV / JSON / STIX 2.1 import and STIX 2.1 export on the Import/Export tab, or `+ Create IOC` for one at a time.

**Is the model registry the same thing as the AIBOM?**
No. The registry is the governed list of AI *systems* (with owners, assessments, incidents); the AIBOM is the inventory of AI *components* in your code. Discovery bridges cloud services into the registry; the AIBOM is context for which repositories ship which SDKs.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment. When contacting support include the feed id and last error for feed problems, the `finding_id` and the agent decision from the Activity Log for triage questions, and the `document_id` and question for Knowledge Base answers.
