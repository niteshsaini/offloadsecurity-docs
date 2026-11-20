---
title: "AI & Threat Intelligence"
sidebar_label: "Overview"
sidebar_position: 0
description: "Outside-in context and AI assistance for the whole program — eight threat feeds correlated onto your findings automatically, a threat-intelligence lens over open CVEs and an ATT&CK matrix from your telemetry, a Security Command Center that adds AI verdicts and prepared fixes to the one triage queue, an AI governance registry with ISO 42001 posture, AI discovery and an AI bill of materials, and a knowledge base that answers from your own policies."
---

# AI & Threat Intelligence

This area does two different jobs that share one idea — bring context to a finding so a person spends less time deciding and more time fixing. **Threat Intelligence** brings the outside world in (what is being exploited, by whom, where it maps on ATT&CK) and pushes it into prioritisation. The **AI** pages turn the platform's own data into decisions: triage verdicts, prepared fixes, an executive briefing, answers from your policies — and, because you run AI too, a registry and posture for *your* AI systems.

**Where:** left navigation → *Threat & Intelligence* → **Threat Intelligence** and **AI Governance**; *Core Security* → **Security Command Center**; *Management* → **Knowledge Base**.

## What is in this section

| Page | What it is | Read it for |
| --- | --- | --- |
| [Threat Intelligence](./threat-intelligence.md) | Eight built-in feeds (CISA KEV, URLhaus, OTX, Feodo Tracker, SSL Blacklist, Blocklist.de, Spamhaus DROP, OpenPhish) normalised into indicators and matched against your findings and assets automatically; a TI lens over your open CVEs; a MITRE ATT&CK matrix from your Wazuh and alert telemetry; landscape reports; STIX / CSV import-export | Which of your exposures are tied to *active* exploitation |
| [Security Command Center](./ai-soc-agents.md) | AI verdicts, correlation and FP/TP assessment on the same queue as VM Triage; remediation queue; Auto-Fix Engine with approvals; Security Advisor; activity log — rule-based out of the box, LLM-assisted when a provider is configured | What to fix first and why, with an audit trail |
| [AI Governance](./ai-governance.md) | Model registry, risk assessments and bias tests, incidents and human-oversight logs, training records, ISO 42001 control posture and auditor exports | Governing the AI systems your organisation builds and buys |
| [AI Discovery, AIBOM & Testing](./ai-spm.md) | Discovery of AI services in your cloud inventory and LLM configuration; the AI bill of materials folded from your SBOMs; OWASP LLM01 prompt-injection tests | Knowing what AI you actually run, in code and in cloud |
| [Knowledge Base & AI Assistant](./knowledge-base.md) | Policy library with sections and sensitivity, question answering with citations, questionnaire auto-fill with an answer bank, policy acknowledgement campaigns, usage analytics | Answering "what is our policy on…" and security questionnaires from your own documents |
| [AI Data & Privacy](./ai-data-privacy.md) | Which features call a model and what each sends, which never do, the per-team budget, caching and tenant isolation | The commitments behind every AI feature |
| [API](./api.md) · [Troubleshooting & FAQ](./troubleshooting.md) | Endpoints and permissions; common problems | |

## How the pieces connect

1. **Feeds → indicators → findings.** Enabled feeds are fetched on their own schedule (daily by default) and normalised into indicators (IPs, domains, URLs, hashes, CVEs, certificates). Every 30 minutes the platform correlates them — together with the CISA KEV catalogue and EPSS, refreshed daily — onto your open findings and their assets, and re-scores what changed, so a KEV-listed or IOC-matched finding rises in the [Triage](../vulnerability-risk/vulnerability-management/triage.md) queue without anyone pressing a button. [Vuln Prioritization](./threat-intelligence.md#vulnerability-prioritisation) shows the same signals per open CVE.
2. **Findings → triage → fixes.** The Command Center works the one triage queue that Vulnerability Management uses: its agents add an AI verdict (*Critical / Investigate / Monitor / False positive / Auto-resolved*) from severity, KEV, EPSS, exposure, environment and age, and the analyst records the decision in VM Triage. Cloud findings that match a remediation playbook become Auto-Fix actions that wait for approval; findings sent to auto-fix get prepared fix suggestions.
3. **Your AI → registry → posture.** Discovery finds AI services in the asset inventory and LLM configuration; the AIBOM finds AI libraries in your SBOMs; both feed the model registry, whose assessments, tests, incidents and training records roll up into the ISO 42001 control posture.
4. **Your documents → answers.** Knowledge Base documents are chunked and embedded; the assistant and the questionnaire filler answer from them with citations and a confidence score, and approved answers build an answer bank.

:::note[With and without an AI provider]
Threat intelligence and correlation, rule-based triage, the Auto-Fix Engine, the Security Advisor's data-driven answers, discovery, the AIBOM and the governance registry all work with **no model provider configured**. An LLM (Anthropic, OpenAI or Google — a team key under Knowledge Base → AI Assistant → *AI Configuration*, or a deployment-wide key set by the operator) adds reasoning to triage, FP/TP assessment, incident narratives, remediation drafting, the briefing, and document Q&A; Knowledge Base retrieval specifically needs an **OpenAI** key for embeddings. AI use is metered against a per-team budget. Each page says which mode it is describing. See [AI Data & Privacy](./ai-data-privacy.md) for what is sent to the provider.
:::

## Permissions at a glance

| Action | Permission |
| --- | --- |
| Read the threat dashboard, indicators, feeds, Vuln Prioritization, ATT&CK matrix and reports | any authenticated member |
| Correlate by hand, generate a landscape report, configure or refresh feeds, add indicators or mark them false positive, actors, campaigns, rules, aging, import / export | **Manage Threat Intelligence** (`manage_threat_intelligence`) |
| Run agents and AI actions, read the Triage Center, ask the advisor | **Run AI Agent** (`run_ai_agent`) |
| Record triage decisions | **Manage Triage** (`manage_triage`) |
| Approve / deny / execute / roll back Auto-Fix actions | **Execute Remediations** |
| AI governance registry, assessments, incidents, oversight, discovery, prompt tests | **Manage Assessments** |
| Knowledge Base uploads, questions, questionnaire fill, policy acknowledgement campaigns | **Manage Assessments**; reading the library and analytics needs only a login |

Everything is scoped to the **active team**: feeds, indicators, agents, registry entries and documents belong to the team that created them.
