---
title: "AI & Threat Intelligence Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 8
description: "Fix the common problems — a feed that shows API key required or Retired, findings that never show IOC matches, an empty ATT&CK matrix, Run Triage Now that triaged 0 findings, AI requests refused for budget, an Auto-Fix Engine that says No Remediation Actions, a Knowledge Base that answers 'retrieval unavailable', discovery that finds nothing — and answers to frequent questions."
---

# AI & Threat Intelligence Troubleshooting & FAQ

## Threat Intelligence

**A feed shows "API key required" and no indicators.**
URLhaus and AlienVault OTX need a key from the vendor; Feodo Tracker and SSL Blacklist accept an optional one; the rest need none. **Add API Key** on the card, **Test Connection**, save, then **Process Feed Now**. Keys are per team and encrypted.

**The PhishTank card says Retired and its switch is locked.**
The provider shut the feed down. Use OpenPhish for phishing URLs.

**The header says *Feeds degraded* or *Feeds failing*.**
It reads the last 24 hours of fetches across enabled feeds. Open the failing card: the last error is classified — *auth* (rotate the key), *rate_limited* / *quota* (wait; the next scheduled fetch retries), *timeout* / *unreachable* (egress from the platform to the feed URL), *parse* (the vendor changed format — report it), *discontinued*. Transient classes retry on their own.

**A feed has not refreshed for hours.**
Built-in feeds refresh once a day by default; the scheduler checks every 15 minutes whether each feed is due. Use **Process Feed Now** for an immediate fetch.

**Active threats went down overnight.**
A daily clean-up archives indicators not seen for 90 days, and, where indicator aging is configured, confidence decays and indicators expire after their time-to-live. That is intended — see [Indicator aging](./threat-intelligence.md#import--export-and-indicator-aging).

**No finding ever shows an IOC match.**
Automatic correlation uses only IP, domain and URL indicators, and matches them exactly against the *public* IPs, host names and URLs on open findings and their assets. Private addresses and shared cloud host names never match, and false-positive indicators are skipped. It runs every 30 minutes and after each feed fetch.

**Correlate returns nothing for an IP I know is in our estate.**
The manual search covers assets, cloud findings, vulnerability occurrences, scan targets and cloud accounts discovered by scans. An asset that has not been scanned, or an internal-only address, is not there to match. If an amber *Partial result* note appears, some stores were not searched.

**Vuln Prioritization is empty or says it is computing.**
It lists open CVEs from Vulnerability Management; with no open CVE findings there is nothing to show. On first open the signals are computed in the background; counts are unknown until then. Misconfigurations and most code findings have no CVE and never appear.

**The MITRE ATT&CK matrix is empty.**
It shows techniques from your indicators, threat actors and alerts that carry ATT&CK ids — chiefly Wazuh alerts. Check **Sources**: a source marked *never synced* is not contributing, and widen the telemetry window.

**The Threat Actors / Campaigns / Alert Rules / Hunting tabs are missing.**
They are API-only in the current release (`/api/enhanced-threat-intelligence/…`); the tabs were removed from the UI to reduce clutter. Records you create over the API still feed prioritisation.

## Security Command Center

**Run Triage Now or Triage new/changed says there is nothing to triage.**
Every open finding already has a current AI verdict — only new findings, and findings that changed since their last verdict, are sent. This is not an error.

**AI triage stopped at 300 findings.**
One run handles up to 300 findings, highest risk first; the result says how many still need triage. Run it again.

**The Triage Center has no Fix / Suppress buttons.**
Decisions are recorded in VM Triage. Use **Open in VM Triage →** on the row; you need the **Manage Triage** permission.

**Process All Findings says "Created 0 remediation actions from 0 findings".**
Fixed in the current release — older builds read a collection nothing wrote to. If you are current and it reports *from N findings* but creates 0, no playbook matches those checks; the playbook library covers common storage, network, IAM and logging misconfigurations.

**Actions were created but the Auto-Fix Engine tab shows "No Remediation Actions".**
Fixed in the current release — the tab filtered on `pending_approval` while new actions are `pending`. Upgrade; the Pending tab now shows both.

**Execute did nothing in the cloud account.**
Expected unless the operator set `REMEDIATION_LIVE_EXECUTE=true`: the action is listed under **Simulated** and no cloud API call was made. This is a deployment decision, not a per-team setting.

**Prepare fixes says auto-fix is off for this team.**
A team member with **Manage Team** switches it on in Code Command Center (*Enable for this team*). If that switch is not shown, the operator has not enabled agentic fixes for the deployment (`AGENTIC_FIX_ENABLED`).

**The briefing says "monitoring 0 cloud accounts".**
Fixed in the current release (the count keyed on the wrong field). Upgrade.

**The badge says Rule-Based Mode.**
No LLM provider is available to the team. Everything still works from rules; add a provider under Knowledge Base → AI Assistant → *AI Configuration*, or ask the operator to set a deployment-wide key, for model-assisted reasoning.

**An advisor answer is labelled "Rule-based answer, not AI".**
No provider is configured, or the AI call failed or timed out; the note under the answer says which.

**AI requests fail with "rate limit" / HTTP 429.**
The team has used its AI budget — by default 30 requests a minute, 120,000 prompt tokens a minute or 20 million tokens a month. Wait for the window to pass, or ask the operator to raise `LLM_RPM_PER_TEAM`, `LLM_TPM_PER_TEAM` or `LLM_MONTHLY_TOKENS_PER_TEAM`.

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

**Answers come back with 0 % confidence and no sources.**
Document retrieval could not run: it uses OpenAI embeddings, and neither the team nor the deployment has an OpenAI key (or the team is over its AI budget). Add an OpenAI key in AI Configuration (the answering model can stay whichever you prefer). About 25 % with no sources means something else — no uploaded document matches the question.

**Uploading a `.doc` file fails.**
Legacy Word, Excel and PowerPoint files cannot be read reliably and are refused. Save the file as `.docx` or PDF and upload that.

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
Only those in the [AI Data & Privacy](./ai-data-privacy.md) table, and only when a provider is configured. Feeds, correlation, the open-CVE lens, the ATT&CK matrix, rule-based triage, incident grouping, the Auto-Fix Engine, discovery and the AIBOM never do.

**Is AI Security Testing available?**
No. It is in development, hidden from the menu, and its API is off unless the operator sets `AI_SECURITY_TESTING_ENABLED=true`. The prompt-injection tests on AI Governance → **Testing** are a separate, available feature.

**Can an agent close a finding or change my cloud on its own?**
No. AI verdicts are advisory and never set the human decision (even *auto-resolved* is a verdict to confirm), FP/TP assessment never suppresses, and Auto-Fix actions need approval and execution — which is simulated until an operator enables live execution.

**Can I bring my own indicators or share ours?**
Yes — CSV / JSON / STIX 2.1 import and STIX 2.1 export on the Import/Export tab, or `+ Create IOC` for one at a time.

**Is the model registry the same thing as the AIBOM?**
No. The registry is the governed list of AI *systems* (with owners, assessments, incidents); the AIBOM is the inventory of AI *components* in your code. Discovery bridges cloud services into the registry; the AIBOM is context for which repositories ship which SDKs.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment. When contacting support include the feed id and last error for feed problems, the `finding_id` and the agent decision from the Activity Log for triage questions, and the `document_id` and question for Knowledge Base answers.
