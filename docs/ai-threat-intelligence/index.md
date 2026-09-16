---
title: "AI & Threat Intelligence"
sidebar_label: "Overview"
sidebar_position: 0
description: "Outside-in context and AI assistance for the whole program — nine threat feeds correlated against your findings, a Security Command Center that triages and prepares fixes, an AI governance registry with ISO 42001 posture, AI discovery and an AI bill of materials, and a knowledge base that answers from your own policies."
---

# AI & Threat Intelligence

This area does two different jobs that share one idea — bring context to a finding so a person spends less time deciding and more time fixing. **Threat Intelligence** brings the outside world in (what is being exploited, by whom, where it maps on ATT&CK) and pushes it into prioritisation. The **AI** pages turn the platform's own data into decisions: triage verdicts, prepared fixes, an executive briefing, answers from your policies — and, because you run AI too, a registry and posture for *your* AI systems.

**Where:** left navigation → *Threat & Intelligence* → **Threat Intelligence** and **AI Governance**; *Core Security* → **Security Command Center**; *Management* → **Knowledge Base**.

## What is in this section

| Page | What it is | Read it for |
| --- | --- | --- |
| [Threat Intelligence](./threat-intelligence.md) | Nine curated feeds (CISA KEV, URLhaus, OTX, Feodo Tracker, SSL Blacklist, PhishTank, Blocklist.de, Spamhaus DROP, OpenPhish) normalised into indicators, hourly; IOC correlation; CVE prioritisation; MITRE ATT&CK coverage; landscape reports; STIX / CSV import-export | Which of your exposures are tied to *active* exploitation |
| [Security Command Center](./ai-soc-agents.md) | Triage agent, remediation queue, Auto-Fix Engine with approvals, Security Advisor, activity log — rule-based out of the box, LLM-assisted when a provider is configured | What to fix first and why, with an audit trail |
| [AI Governance](./ai-governance.md) | Model registry, risk assessments and bias tests, incidents and human-oversight logs, training records, ISO 42001 control posture and auditor exports | Governing the AI systems your organisation builds and buys |
| [AI Discovery, AIBOM & Testing](./ai-spm.md) | Discovery of AI services in your cloud inventory and LLM configuration; the AI bill of materials folded from your SBOMs; OWASP LLM01 prompt-injection tests | Knowing what AI you actually run, in code and in cloud |
| [Knowledge Base & AI Assistant](./knowledge-base.md) | Policy library with sections and sensitivity, question answering with citations, questionnaire auto-fill with an answer bank, usage analytics | Answering "what is our policy on…" and security questionnaires from your own documents |
| [AI Data & Privacy](./ai-data-privacy.md) | Which features call a model, which never do, what leaves the platform, caching and tenant isolation | The commitments behind every AI feature |
| [API](./api.md) · [Troubleshooting & FAQ](./troubleshooting.md) | Endpoints and permissions; common problems | |

## How the pieces connect

1. **Feeds → indicators → priority.** Every hour the enabled feeds are fetched and normalised into indicators (IPs, domains, URLs, hashes, CVEs, certificates). A CVE that appears in CISA KEV, or is tied to active indicators, actors or campaigns, scores higher in [Vuln Prioritization](./threat-intelligence.md#vulnerability-prioritisation) and in the [Triage](../vulnerability-risk/vulnerability-management/triage.md) engine's exploitability signal.
2. **Findings → triage → fixes.** The Command Center's triage agent classifies open findings into *Critical / Investigate / Monitor / False positive / Auto-resolved* using severity, KEV, EPSS, exposure, environment and age. Findings that match a remediation playbook become Auto-Fix actions that wait for approval; code findings with a *fix* disposition can be handed to the agentic fix pipeline.
3. **Your AI → registry → posture.** Discovery finds AI services in the asset inventory and LLM configuration; the AIBOM finds AI libraries in your SBOMs; both feed the model registry, whose assessments, tests, incidents and training records roll up into the ISO 42001 control posture.
4. **Your documents → answers.** Knowledge Base documents are chunked and embedded; the assistant and the questionnaire filler answer from them with citations and a confidence score, and approved answers build an answer bank.

:::note[With and without an AI provider]
Threat intelligence, rule-based triage, the Auto-Fix Engine, the Security Advisor's data-driven answers, discovery, the AIBOM and the governance registry all work with **no model provider configured**. An LLM (Anthropic, OpenAI or Google — configured per team under Knowledge Base → AI Assistant → *AI Configuration*) adds reasoning to triage, FP/TP assessment, remediation drafting, the briefing, and document Q&A; Knowledge Base retrieval specifically needs an **OpenAI** key for embeddings. Each page says which mode it is describing. See [AI Assistant](../reports-and-ai/ai-assistant.md) for provider setup.
:::

## Permissions at a glance

| Action | Permission |
| --- | --- |
| Read the threat dashboard, indicators, feeds, heatmap and reports | any authenticated member |
| Correlate, prioritise, generate a landscape report, configure or refresh feeds, add indicators, actors, campaigns, rules, aging, import / export | **Manage Threat Intelligence** (`manage_threat_intelligence`) |
| Run agents, triage, FP/TP assessment, ask the advisor | **Run AI Agent** (`run_ai_agent`) |
| Approve / deny / execute / roll back Auto-Fix actions | **Execute Remediations** |
| AI governance registry, assessments, incidents, oversight, discovery, prompt tests | **Manage Assessments** |
| Knowledge Base uploads, questions, questionnaire fill | **Manage Assessments**; reading the library and analytics needs only a login |

Everything is scoped to the **active team**: feeds, indicators, agents, registry entries and documents belong to the team that created them.
