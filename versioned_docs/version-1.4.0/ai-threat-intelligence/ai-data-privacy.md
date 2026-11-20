---
title: "AI Data & Privacy"
sidebar_label: "AI Data & Privacy"
sidebar_position: 6
description: "What the platform's own AI features send to the model — including finding, asset and control records, code snippets and policy document text — where it goes, the per-team budget, how it is cached and isolated per tenant, which features never call a model, and how to run with AI off, including the on-premises caveat that prompts still reach the provider you chose."
---

# AI Data & Privacy

Offload Security uses AI to help you work faster — summarizing scans, answering questions, drafting remediation and assessment content, and assisting triage. This page explains exactly **what the AI sees, where your data goes, how it's isolated, and how to turn it off** — so you can make an informed decision for regulated or data-residency-sensitive environments.

:::note[The short version]
AI features are **optional and assistive**. They run only when a team or the operator configures an LLM provider, they only send data the requesting team already holds, tenant data is never served from a shared cache, and remediation suggestions are **advisory** — a person makes the change. What is sent is not limited to finding summaries: depending on the feature it includes records from your findings, assets and controls, **code snippets**, and **text from documents you upload**. If you don't want prompts leaving your environment, run the platform with AI **disabled**.
:::

## Which features use AI, and what they send

| Feature | What the AI does | What is sent to the model |
| --- | --- | --- |
| **AI assistant** (page-level chat) | Answers questions about your posture, grounded in your team's data | Your question, the conversation so far, and matching **finding, asset and control records** from your team (only sources your role may read) |
| **Scan analysis and summaries** | Turns a scan into a plain-language summary | Scan results and findings |
| **Code analysis and fix suggestions** | Explains code findings and proposes a corrected snippet | Finding details and the **code snippet** around the issue |
| **Security Command Center** | Triage reasoning, FP/TP assessment, incident narratives, remediation drafts, the briefing | Finding details (including code snippets for SAST), resource details, posture numbers |
| **Knowledge Base and questionnaire auto-fill** | Answers from your documents, fills questionnaires | Your question and **passages of your uploaded documents**; document text is also sent to the embeddings provider for indexing |
| **Evidence mapping** | Maps an uploaded policy document to SCF controls | The document title and its **first 3,000 characters** |
| **Risk assistant · AI Governance assessment helper** | Suggests risk details, scores, mitigations and summaries | The risk or AI-system description you entered |
| **AI-SPM** | Judges whether a prompt-injection test compromised a model (see [AI-SPM](./ai-spm.md)) | The probe and the tested model's response |

All of these are **assistive**. AI never changes your cloud, closes findings, or approves compliance on its own.

**Never call a model:** threat feeds and IOC correlation, KEV/EPSS enrichment, the deterministic risk score and priorities, rule-based triage, incident grouping, the Auto-Fix Engine's playbook matching and execution, AI discovery and the AIBOM, and the AI Governance registry.

## Model providers and keys

AI features call an **external LLM provider's API**. The platform supports:

- **Anthropic Claude**
- **OpenAI**
- **Google Gemini**

Keys come from two places. A team can add its own key under Knowledge Base → AI Assistant → *AI Configuration* (stored **encrypted at rest**, used only for that team). The operator can also set one deployment-wide key — `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` or `GOOGLE_AI_API_KEY`, tried in that order — which every team without its own key uses. Knowledge Base embeddings use the team's OpenAI key, else the deployment's `OPENAI_API_KEY`; a team's key is never used for another team. The model is accessed over the network through the provider's API — the platform does not run a model locally. If a configured model has been retired by the vendor, the platform substitutes the current default for that provider, logs it, and the Knowledge Base shows a notice.

Every model call goes through one guarded path that applies a **per-team budget** — 30 requests a minute, 120,000 prompt tokens a minute and 20 million tokens a month by default (`LLM_RPM_PER_TEAM`, `LLM_TPM_PER_TEAM`, `LLM_MONTHLY_TOKENS_PER_TEAM`) — and records usage against the team. Over budget is an error (HTTP 429), never a silent blank answer.

## What the AI sees, and where it goes

- The AI is given **only data the requesting team already holds** — for example, the finding you're asking about, records retrieved for an assistant question, or the documents you uploaded to the Knowledge Base. A conversation is never continued in another team, so one team's records never enter another team's prompt.
- Retrieved records are sent as data, marked as untrusted, and the assistant cites the records it used.
- That context is sent to the **configured LLM provider** to generate the response, then returned to you.
- How the provider handles data sent to its API is governed by **your organization's agreement with that provider**. Offload Security does not train models on your data; it uses the providers' inference APIs.

## Caching and tenant isolation

To cut cost and latency, the AI assistant uses a three-tier cache:

1. **Curated platform knowledge** — generic, product-level answers shipped with the platform.
2. **Learned response cache** — generic question/answer pairs learned over time.
3. **The LLM** — used when neither cache has a match.

**Tenant-derived content is never served from a shared cache** — only generic, non-tenant answers are cached, and questions answered from your team's data bypass the cache in both directions. Everything else the AI stores (conversations, summaries) is **team-scoped** and lives in your platform's own database, under the same tenant isolation as the rest of your data.

## Turning AI off

AI features are active **only when an LLM provider key is available** to the team. To disable AI, make sure no key exists anywhere: remove the team keys under *AI Configuration* **and** leave `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_AI_API_KEY` (and the deprecated `EMERGENT_LLM_KEY`) unset in the deployment environment. The rest of the platform works unchanged; the Security Command Center falls back to its rule-based mode.

## On-premises and data residency

The whole platform can run **fully on-premises** — see [On-Premises](../on-premises/index.mdx). One caveat to plan for:

:::warning[AI features still call the external provider]
Even in an on-premises deployment, AI features send prompts — including the data listed above — to the **external** LLM provider over the network using your key; the model itself is not run inside your environment. If sending prompts to an external AI provider is not acceptable for your data-residency requirements, **disable AI features** (above) and use the platform without them. Everything else — scanning, findings, risk, compliance, reporting — runs entirely within your environment.
:::

## Related

- **[Trust & Security](../trust-and-security.md)** — encryption, tenant isolation, and credential handling across the platform.
- **[Knowledge Base](./knowledge-base.md)** — how uploaded documents are used for Q&A.
- **[AI Governance](./ai-governance.md)** and **[AI Discovery, AIBOM & Testing](./ai-spm.md)** — governing and testing the AI *you* build and run.
- **[AI Assistant](../reports-and-ai/ai-assistant.md)** — the page-level assistant and provider setup.
