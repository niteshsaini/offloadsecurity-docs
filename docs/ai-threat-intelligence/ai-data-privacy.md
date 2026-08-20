---
title: "AI Data & Privacy"
sidebar_label: "AI Data & Privacy"
sidebar_position: 4.5
---

# AI Data & Privacy

Offload Security uses AI to help you work faster — summarizing scans, answering questions, drafting remediation and assessment content, and assisting triage. This page explains exactly **what the AI sees, where your data goes, how it's isolated, and how to turn it off** — so you can make an informed decision for regulated or data-residency-sensitive environments.

:::info[The short version]
AI features are **optional and assistive**. They run only when your operator configures an LLM provider, they only ever see data your team already has access to, tenant data is never served from a shared cache, and remediation suggestions are **advisory** — a person makes the change. If you don't want prompts leaving your environment, you can run the platform with AI **disabled**.
:::

## Which features use AI

| Feature | What the AI does |
|---|---|
| **AI assistant / chat** | Answers questions about your security posture, using context from your own data. |
| **Scan summaries** | Turns a completed scan into a plain-language summary. |
| **AI SOC agents** | Assist with triage, remediation guidance, compliance mapping and threat hunting. |
| **AI-SPM** | Judges whether a prompt-injection test compromised a model (see [AI-SPM](./ai-spm.md)). |
| **Auto-fill** | Suggests answers for assessments and DPIAs, always for human review. |
| **Knowledge Base Q&A** | Answers from documents you upload (see [Knowledge Base](./knowledge-base.md)). |

All of these are **assistive**. AI never changes your cloud, closes findings, or approves compliance on its own.

## Model providers

AI features call an **external LLM provider's API**. The platform supports:

- **Anthropic Claude** (the default provider)
- **OpenAI**
- **Google Gemini**

Your operator chooses the provider and supplies the API key, which is **stored encrypted at rest**. The model is accessed over the network through the provider's API — the platform does not run a model locally.

## What the AI sees, and where it goes

- The AI is given **only data your active team already has access to** — for example, the scan or finding you're asking about, or the documents you uploaded to the Knowledge Base. It is scoped to your team; it cannot see another tenant's data.
- That context is sent to the **configured LLM provider** to generate the response, then returned to you.
- How the provider handles data sent to its API is governed by **your organization's agreement with that provider**. Offload Security does not train models on your data; it uses the providers' inference APIs.

## Caching and tenant isolation

To cut cost and latency, the AI assistant uses a three-tier cache:

1. **Curated platform knowledge** — generic, product-level answers shipped with the platform.
2. **Learned response cache** — generic question/answer pairs learned over time.
3. **The LLM** — used when neither cache has a match.

**Tenant-derived content is never served from a shared cache** — only generic, non-tenant answers are cached. Everything else the AI stores (conversations, summaries) is **team-scoped** and lives in your platform's own database, under the same tenant isolation as the rest of your data.

## Turning AI off

AI features are active **only when an LLM provider is configured**. If no provider/key is set, AI features are simply off and the rest of the platform works unchanged. To disable AI, remove (or don't configure) the provider key.

## On-premises and data residency

The whole platform can run **fully on-premises** — see [On-Premises](../on-premises/index.mdx). One caveat to plan for:

:::warning[AI features still call the external provider]
Even in an on-premises deployment, AI features send prompts to the **external** LLM provider over the network using your key — the model itself is not run inside your environment. If sending prompts to an external AI provider is not acceptable for your data-residency requirements, **disable AI features** (above) and use the platform without them. Everything else — scanning, findings, risk, compliance, reporting — runs entirely within your environment.
:::

## Related

- **[Trust & Security](../trust-and-security.md)** — encryption, tenant isolation, and credential handling across the platform.
- **[Knowledge Base](./knowledge-base.md)** — how uploaded documents are used for Q&A.
- **[AI Governance](./ai-governance.md)** and **[AI-SPM](./ai-spm.md)** — governing and testing the AI *you* build and run.
