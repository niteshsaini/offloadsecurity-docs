---
title: "AI & Threat Intelligence"
sidebar_label: "Overview"
sidebar_position: 0
---

# AI & Threat Intelligence

The **AI & Threat Intelligence** area adds real-world context and AI assistance to your security program. It pulls in live threat feeds, uses AI agents to triage and explain findings, helps you govern your own AI systems, and gives you a searchable knowledge base for your security documents — so your team spends less time on manual analysis and more time fixing what matters.

![AI & Threat Intelligence dashboard showing active threat feeds and indicator correlation](/img/screenshots/threat-intelligence.png)

## What it does

This area brings together four capabilities, each with its own page:

- **Threat Intelligence & Feeds** — continuously ingests indicators of compromise (IOCs) from industry feeds such as **CISA KEV**, **NVD**, **AlienVault OTX**, and **Spamhaus**, then correlates them against your findings and assets. Vulnerabilities listed in the **CISA Known Exploited Vulnerabilities (KEV)** catalog, or with high **EPSS** (Exploit Prediction Scoring System) scores, are flagged as higher priority so you focus on what is actively being exploited.
- **AI SOC Agents** — a set of AI assistants that automate routine SOC work: triaging findings by severity and exploitability, generating remediation steps, mapping findings to compliance controls, hunting for threats, and answering plain-language questions about your posture.
- **AI Governance** — a place to register and govern your organization's own AI systems, classify them by risk tier against regulations like the **EU AI Act**, and track the controls that keep them compliant.
- **Knowledge Base** — upload your security policies and documents (PDF or DOCX) and ask questions in natural language. Answers are drawn from your own documents, with an AI assistant for security analysis and pentest planning.

## How to use it

1. From the left navigation, open **AI & Threat Intelligence** and choose the page you need.
2. Start with **Threat Intelligence** to see active threats and how they correlate to your environment. Feeds refresh automatically, so the dashboard stays current without any manual import.
3. Use the **AI SOC Agents** to triage and explain findings. After a scan completes, agents can run automatically and attach their analysis to the relevant findings — open a finding to see the suggested priority and remediation.
4. If your organization builds or uses AI systems, register them under **AI Governance** to get a risk-tier classification and a checklist of governance controls.
5. Upload your policies to the **Knowledge Base**, then ask questions like *"What is our MFA policy?"* to get answers grounded in your own documents.

## Why findings get prioritized

The AI SOC agents combine fast, rule-based checks with AI reasoning for the trickier cases. When ranking a finding they weigh:

- **Severity** — how serious the issue is.
- **CISA KEV status** — whether the vulnerability is in the Known Exploited Vulnerabilities catalog.
- **EPSS score** — the predicted likelihood that it will be exploited.

The result is a prioritized list that puts actively exploited and high-likelihood issues at the top, instead of treating every finding the same.

:::tip Everything stays in your team
All AI and threat-intelligence work is scoped to your **active team**. You only see — and the agents only act on — data that belongs to the team you're currently in. Check the team selector in the top-right before reviewing results.
:::

:::note Bring your own AI provider
The AI features work with major model providers, including OpenAI, Anthropic, and Google Gemini. Your administrator configures the provider and API key in platform settings. Every AI decision is recorded — including its reasoning and confidence — so you have an audit trail.
:::

:::warning Sensitive documents
Documents you add to the Knowledge Base are used to answer questions for your team. Only upload material your team is permitted to see, and review your team membership before sharing sensitive policies.
:::

## Related

- [AI SOC Agents](./ai-soc-agents.md) — automated triage, remediation, compliance mapping, and threat hunting.
- [Threat Intelligence & Feeds](./threat-intelligence.md) — feed ingestion and IOC correlation in detail.
- [Knowledge Base & AI Security Testing](./knowledge-base.md) — document Q&A and the AI security assistant.
- [AI Governance & Privacy Compliance](./ai-governance.md) — govern your own AI systems against the EU AI Act and other regulations.
