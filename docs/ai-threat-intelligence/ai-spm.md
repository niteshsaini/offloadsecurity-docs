---
title: "AI Discovery, AIBOM & Testing"
sidebar_label: "AI Discovery, AIBOM & Testing"
sidebar_position: 4
description: "Know what AI you actually run — discovery of AI services in your cloud inventory and LLM configuration, an AI bill of materials folded from the SBOMs the platform already generates, EU AI Act / NIST AI RMF risk-tier classification, and an OWASP LLM01 prompt-injection test suite."
---

# AI Discovery, AIBOM & Testing

A registry is only as good as what is in it. The **Discovery** and **Testing** tabs of AI Governance find AI systems you did not register — in your cloud accounts, in your LLM configuration, and in the dependencies of your own code — classify their risk against the EU AI Act and NIST AI RMF, and let you probe an endpoint with a prompt-injection suite before it reaches users.

**Where:** left navigation → *Threat & Intelligence* → **AI Governance** → **Discovery** and **Testing**.

## Discovery

![AI Discovery: discovered 3, newly registered 0, already known 3; discovered AI services table — SageMaker endpoint, Bedrock model access, Vertex AI endpoint — with Classify](/img/screenshots/ai-threat-intelligence/aig-discovery.webp)

**Run Discovery** looks in two places the platform already has:

| Source | What is recognised |
| --- | --- |
| **Cloud asset inventory** — the assets discovered by your [cloud scans](../cloud-security/asset-inventory.md) | AWS SageMaker, Bedrock, Comprehend, Rekognition, Textract, Translate, Polly, Lex, Kendra, Personalize, Forecast · GCP Vertex AI / AI Platform, AutoML, Dialogflow, Generative Language · Azure Cognitive Services, Azure ML, Azure OpenAI · hosted providers referenced by resource names (OpenAI, Anthropic, Cohere, Mistral, Hugging Face, Replicate) |
| **LLM configuration** — the providers the team configured for the platform's own AI features | Anthropic, OpenAI, Google |

Each hit becomes a **discovered** entry in the [model registry](./ai-governance.md#model-registry) (provider, name, service, region, source) — once; a rerun reports it as *already known*. Discovery runs as a background job and needs no cloud calls beyond what the scan already made.

**Classify** on a row assigns an **EU AI Act tier** and the matching NIST AI RMF posture from the system's use case, sector, data types and decision impact:

| Tier | Rule of thumb applied |
| --- | --- |
| **Unacceptable** (Prohibited) | Social scoring, manipulation, subliminal techniques, real-time biometric identification |
| **High-Risk** | High-risk sectors (healthcare, finance, employment, education, law enforcement, critical infrastructure…) and uses (credit, hiring, biometric identification…), or sensitive data (PII, PHI, biometric, health, financial, criminal) with high decision impact |
| **Limited Risk** | Chatbots and conversational systems, emotion recognition, deepfake / synthetic content — transparency obligations |
| **Minimal Risk** | Everything else |

The tier is a starting point for the owner's own risk assessment, not a legal determination.

## AI bill of materials

Below Discovery, the **AI Bill of Materials** is the code-level half of "what AI do we run": every AI SDK, framework, agent library, model runtime and vector store your repositories ship, **folded from the SBOMs the platform already generates** for [code scans](../security-scanning/code/sbom-and-licenses.md) — nothing new to install, nothing to scan twice.

| Tile | Meaning |
| --- | --- |
| **AI components** | Distinct AI packages across all SBOMs (and how many are *stale* — not seen in the latest SBOM of a repository) |
| **Applications** | Repositories shipping at least one AI component |
| **Models declared** | Model identifiers named in source (a `model=` string, a Hugging Face id) |
| **Provider SDKs** | Hosted-model clients — `openai`, `anthropic`, `cohere`, `boto3` Bedrock use… |
| **Agents / MCP** | Agent frameworks and Model Context Protocol tooling, and vector databases |
| **Needs confirmation** | Matches made heuristically rather than by exact package identity; confirm or dismiss them |
| **Ownership** | Components with an owner assigned |

The inventory table lists each component with type (provider SDK, orchestration, agent framework, model runtime, inference server, vector retrieval, embedding, MLOps, guardrail, MCP), provider, category, owner, environment, source SBOMs, confidence and last seen. New SBOM scans fold in automatically; **Reconcile now** re-reads every SBOM immediately, and a daily job reconciles on its own.

## Testing — prompt injection

![Prompt Injection Testing: choose a registered model, optional API endpoint and key, Run Tests; dry run when no endpoint is set](/img/screenshots/ai-threat-intelligence/aig-testing.webp)

An **OWASP LLM01** red-team suite of eight probes — direct instruction override, role-play jailbreak, encoding bypass, context manipulation, data-exfiltration probe, indirect injection via data, multi-turn manipulation, output-format injection — run against a registered model.

- Give an **OpenAI-compatible chat endpoint** (and, optionally, a key used only for this run and never stored) and the suite is sent live; each probe is scored on whether the response shows the injected behaviour, and the result is recorded against the model with pass / fail per category.
- Leave the endpoint blank for a **dry run**: the payloads are recorded for manual execution against a system the platform cannot reach (an internal assistant, a vendor console).

Results are evidence for the model's risk assessment; a production LLM system with no test is one of the ISO 42001 [certification blockers](./ai-governance.md#compliance--iso-42001).

:::note[Permissions and scope]
Discovery, classification, the AIBOM and prompt tests need **Manage Assessments**. The AIBOM reads only your team's SBOMs; discovery reads only your team's inventory and configuration.
:::

## Related

- [AI Governance](./ai-governance.md) — the registry these feed and the posture they improve.
- [SBOM & Licences](../security-scanning/code/sbom-and-licenses.md) — where the SBOMs come from.
- [AI Data & Privacy](./ai-data-privacy.md) — what the platform's own AI features do with your data.
