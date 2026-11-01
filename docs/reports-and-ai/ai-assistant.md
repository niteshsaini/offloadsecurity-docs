---
title: "AI Assistant"
sidebar_label: "AI Assistant"
sidebar_position: 4
description: "The AI Security Assistant on every page, the in-context AI features across modules (summaries, explanations, fix suggestions, auto-fill), how to configure Anthropic / OpenAI / Google as the provider per team, what is answered without a model call, and how your data is handled."
---

# AI Assistant

AI in Offload Security has one job: help a human read, explain and act on security data faster. It sits on the same normalised data the dashboards use — findings, controls, risks, evidence — and it drafts; a person decides. Nothing in this section closes a finding, accepts a risk, changes a control or touches your cloud on its own.

## The security assistant

**Where:** the **AI Security Assistant** button at the bottom-right of every page.

![AI Security Assistant panel: "How can I help you today?", suggested questions under Security Posture (current security posture, most critical vulnerabilities) and Compliance (SOC 2 requirements, NIST CSF gaps), a message box](/img/screenshots/reports-and-ai/ai-assistant-widget.webp)

Open it and ask in plain language — *what are my most critical vulnerabilities*, *am I compliant with SOC 2 requirements*, *what are my NIST CSF gaps*. The panel offers **suggested questions** for the page you are on, keeps a **conversation** so follow-ups work ("and which of those are internet-exposed?"), and shows which provider and model answered. Conversations are per user and can be cleared.

The assistant answers from two places, checked in order:

1. **Platform knowledge, without a model call.** Questions about the product itself — what a module does, how to connect an account, where a setting lives, common troubleshooting — are served from a curated knowledge base that is refreshed from this documentation site, and from answers the model previously gave to *generic* questions (kept behind a normalised-question hash with a semantic fallback, and expired so they cannot drift). Zero tokens, consistent answers, fast.
2. **The configured LLM**, for anything about *your* data. For a question about your environment the platform first retrieves matching records from your team's data — open findings from the unified findings lake, assets from the asset inventory, and SCF controls with your control state — and sends them with the question and the security context of the current page, under a system prompt that keeps the model to security posture, risk and remediation guidance and treats the retrieved records as data, not instructions.

### Grounded answers and citations

An answer built from your data cites the records it used — **[F1]** for a finding, **[A1]** for an asset, **[C1]** for a control — and the panel lists the cited records under the answer with links to open them. Retrieval is small on purpose (a few findings, assets and controls per question); the answer states the true number of matching records next to the ones it was given.

Each source is read only if you hold its read permission: findings need **View Scans**, assets **View Cloud Accounts**, controls **View Assessments**. A source you cannot read is never queried, and a source that fails to load is reported as an error rather than answered around — the assistant does not answer a question about your data without the data.

Only questions with no tenant context are ever cached; a grounded answer is neither served from nor stored in the shared response cache, and a conversation cannot be continued from another team.

## AI across the modules

The same provider powers small, specific helpers where a human would otherwise have to read a lot:

| Where | Button | What it does |
| --- | --- | --- |
| Scan results, cloud scan results, container scans, attack paths, cloud events | **AI Summary** | An executive summary of that report — what changed, what matters, where to start — from the counts and top findings |
| Finding detail (code, cloud, container) | **Explain** / **Suggest fix** | Plain-language explanation of the vulnerability in context and a suggested fix approach; for code findings, the starting point for a fix pull request |
| Triage work item | **Explain** | Why the engine scored it the way it did, in prose, with the evidence it used — see [Triage](../vulnerability-risk/vulnerability-management/triage.md) |
| Risk Management | **AI Summary**, auto-fill on *New Risk*, **AI Recommend KRIs**, **AI Generate Scenarios** | Narrates the register; drafts description, category, likelihood and impact from a title; proposes indicators and what-if scenarios — see [Risk Management](../vulnerability-risk/risk-management/index.md) |
| Assessments | **AI Assessment Helper** | Drafts evidence text and explanations for a question (the SCF-based *Auto-Fill* works without a provider) — see [Assessments](../compliance/interactive-assessments.md) |
| Evidence Hub | AI document mapping | Maps paragraphs of an uploaded policy to the SCF controls they satisfy, for you to confirm — see [Evidence Hub](../compliance/evidence-hub.md) |
| Knowledge Base | **AI Assistant** (document Q&A), **Questionnaire Auto-Fill** | Answers from your uploaded policies with citations; fills security questionnaires from them — see [Knowledge Base](../ai-threat-intelligence/knowledge-base.md) |
| Security Command Center | AI SOC agents | Advisory verdicts on the same findings as the Vulnerability Management Triage queue (shown there under **AI assist**), correlation and fix preparation, with an auditable decision trail — see [Security Command Center](../ai-threat-intelligence/ai-soc-agents.md) and [Triage Queue](../vulnerability-risk/vulnerability-management/triage.md#ai-assist-and-the-security-command-center) |

With no provider configured, the assistant and the helpers explain that AI is unavailable and point to AI Configuration; the non-AI paths (SCF-based assessment auto-fill, DPIA autofill suggestions, triage scoring) keep working.

## Configure a provider

**Where:** left navigation → **Knowledge Base** → *AI Assistant* tab → **AI Configuration**.

![AI Configuration: Anthropic Claude, OpenAI Direct and Google Gemini cards, each with Add Key; quick-start templates below](/img/screenshots/reports-and-ai/ai-configuration.webp)

| Provider | Default model | Fast model |
| --- | --- | --- |
| **Anthropic Claude** | `claude-sonnet-5` | `claude-haiku-4-5` |
| **OpenAI** | `gpt-4o` | `gpt-4o-mini` |
| **Google Gemini** | `gemini-3.8-flash` | `gemini-3.5-flash-lite` |

1. **Add Key** on a provider card and paste the API key. It is **encrypted before storage** and scoped to your team.
2. **Test** — the platform makes one minimal call and reports success or the provider's error.
3. **Activate** — the first configured provider becomes active automatically; with several configured, choose which one answers.

Environment variables work too for single-tenant installs: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` or `GOOGLE_AI_API_KEY` on the backend; a team key set in the UI takes precedence. The retired `EMERGENT_LLM_KEY` is honored for one more release only when it holds a real vendor key; move it to the vendor's own variable. The active provider and model are shown in the assistant's header and in `GET /api/llm/providers`. If a configured model has been retired by its vendor, the platform substitutes the current default and says so.

Every AI call — the assistant, the helpers, Knowledge Base, risk AI — goes through one budget-guarded path that records usage against the team. A team over its budget gets an explicit rate-limit error (HTTP 429), not a blank answer.

:::note[Who can use the AI features]
Asking the assistant (messages, quick insights, suggestions, conversations) needs any one of **View Scans**, **View Cloud Accounts** or **View Assessments**; what it can cite is then limited per source as described above. **Explain**, **Suggest fix**, **AI Summary** and **prioritise findings** require the **Manage Integrations** team permission (the same one that configures providers); the scan-analysis endpoints (`/api/ai/analysis/*`) require **Manage Scans**. See [Roles, Teams & API Keys](../authentication/rbac-team-management.md).
:::

## How your data is handled

- **Scope.** A request carries only data the asking user's team can already see, and only the sources that user may read; the model never has a broader view than the person.
- **What is sent.** Depending on the feature: the question and page context, retrieved finding / asset / control records, code snippets (for code findings and fix suggestions) and text from documents you uploaded to the Knowledge Base or Evidence Hub.
- **Cache.** Only tenant-agnostic questions are cached or served from cache. Anything derived from your findings, controls or risks is answered live and not stored in the shared response cache.
- **Provider.** Requests go directly from the platform to the provider you configured with your key; there is no intermediary. Provider data-use terms are yours to choose by choosing the provider.
- **Advisory only.** AI output is a draft or an explanation. State changes — closing a finding, accepting a risk, overriding a control, opening a fix PR, executing a playbook — are explicit human actions with their own audit trail.

The full commitments are in [Trust & Security → How AI features handle your data](../trust-and-security.md#how-ai-features-handle-your-data).

## Related

- [Knowledge Base & AI Assistant](../ai-threat-intelligence/knowledge-base.md) — document library, Q&A with citations, questionnaire auto-fill, usage analytics.
- [Reports & AI API](./api.md#ai) — chat, quick insights, analysis and provider endpoints.
