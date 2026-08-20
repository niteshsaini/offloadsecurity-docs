---
title: "AI-SPM (AI Security Posture)"
sidebar_label: "AI-SPM"
sidebar_position: 3.5
---

# AI Security Posture Management (AI-SPM)

AI-SPM finds the AI models and services running in your environment, classifies how risky each one is, and tests them for prompt-injection weaknesses — so the AI you build and use is covered by the same security program as the rest of your stack.

It complements **[AI Governance](./ai-governance.md)**, which handles the policy, structured assessment, and evidence side. AI-SPM is the technical posture layer: *what AI do we run, how risky is it, and does it hold up under attack?* Significant findings feed the same **[Risk Register](../vulnerability-risk/risk-register.md)** as everything else.

## What it does

- **Discover AI models** — builds an inventory of the AI/ML services already found in your connected cloud accounts, plus the LLM providers you've configured in the platform.
- **Classify risk** — scores each model against the **EU AI Act** risk tiers and the **NIST AI RMF** functions.
- **Test for prompt injection** — runs a battery of prompt-injection payloads against a model's endpoint and judges whether it was compromised.

All three are surfaced under **AI Governance** in the platform, and everything is scoped to your active team.

## Discovering AI models

Discovery draws on two sources that already live inside the platform:

- **Cloud asset inventory** — AI/ML services that your [cloud scans](../cloud-security/index.md) have already discovered are matched by service name. Recognized services include AWS SageMaker, Bedrock, Comprehend, Rekognition, Textract, Translate, Polly, Lex, Kendra, Personalize, and Forecast; GCP Vertex AI, AutoML, and Dialogflow; Azure Cognitive Services, Azure ML, and Azure OpenAI; and hosted providers such as OpenAI, Anthropic, Cohere, Mistral, Hugging Face, and Replicate.
- **Configured LLM providers** — the LLM connections you've set up in the platform.

Discovered models are saved to your model registry, deduplicated, and scoped to your team, so teammates work from the same inventory.

:::note[Discovery reads your existing inventory — it doesn't call the cloud AI APIs directly]
AI-SPM matches AI services from the assets your **cloud scans have already inventoried**; it does not enumerate the cloud AI APIs itself. If an account hasn't been scanned, or its AI services aren't yet in [Asset Inventory](../cloud-security/asset-inventory.md), they won't appear here yet — run a cloud scan first for the fullest picture.
:::

**To run it:** open **AI Governance → Discovery** and select **Run Discovery**. You'll see counts of models discovered, newly registered, and already known, and you can classify any model inline.

## Classifying risk

Each model is classified against two frameworks:

- **EU AI Act risk tiers** — Unacceptable, High, Limited, or Minimal — derived from the model's use case, sector, data types, and decision impact.
- **NIST AI RMF** — scored across the Govern, Map, Measure, and Manage functions, based on the metadata recorded for the model.

Classification is automated and rule-based. Treat it as a fast first-pass triage that points you at the models worth a closer look — not a legal determination. For structured EU AI Act assessments, conformity work, and audit evidence, use **[AI Governance](./ai-governance.md)**.

## Testing for prompt injection

AI-SPM ships a set of prompt-injection test payloads spanning direct instruction-override, jailbreak, encoding, context-manipulation, data-exfiltration, indirect-injection, multi-turn, and output-manipulation techniques. You can also supply your own payloads.

**How it runs:**

1. Open **AI Governance → Testing**, choose the model, and provide its **API endpoint** (and an API key if the endpoint requires one). The endpoint must speak the OpenAI-compatible chat-completions format.
2. AI-SPM sends each payload to that endpoint and evaluates the response. Where a platform LLM key is configured, an **LLM judge** decides whether each payload compromised the model; otherwise it falls back to keyword heuristics.
3. Results record which payloads succeeded, with reasoning and remediation, plus an overall risk level for the model.

:::note[What testing actually requires]
Live testing only happens when you supply a **reachable model endpoint**. Without one, the payloads are recorded as a **dry run** for you to execute manually — no model is contacted. Outbound test requests are SSRF-guarded: private and cloud-metadata addresses are blocked and redirects are disabled.
:::

## Permissions

Running discovery, classification, and prompt tests requires the **assessments management** permission. Viewing the AI-SPM dashboard is available to any authenticated team member. All data is scoped to your active team.

## Related

- **[AI Governance](./ai-governance.md)** — EU AI Act classification, structured assessments, and audit evidence for your AI systems.
- **[Threat Intelligence & Feeds](./threat-intelligence.md)** — external threat context for the rest of your estate.
- **[Risk Register](../vulnerability-risk/risk-register.md)** — where significant AI risks are tracked to treatment.
- **[Cloud Asset Inventory](../cloud-security/asset-inventory.md)** — the inventory AI-SPM discovers models from.
