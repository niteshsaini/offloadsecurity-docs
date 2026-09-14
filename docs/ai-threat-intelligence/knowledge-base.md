---
title: "Knowledge Base & AI Assistant"
sidebar_label: "Knowledge Base"
sidebar_position: 5
description: "Upload your policies, procedures and standards into a sectioned, sensitivity-labelled library; ask questions and get answers with citations and a confidence score; auto-fill security questionnaires from those documents with an answer bank and a review queue; and see who asks what."
---

# Knowledge Base & AI Assistant

Every security team answers the same questions over and over — *what is our password policy*, *how fast do we patch criticals*, *do you encrypt backups* — from the same handful of documents. The Knowledge Base holds those documents once, answers questions from them with a citation and a confidence score, and fills whole security questionnaires the same way. Approved answers go into a bank, so the next questionnaire starts mostly done.

**Where:** left navigation → *Management* → **Knowledge Base**.

## Documents

![Document Management: single or bulk upload; title, section, document type, sensitivity level, description, tags, file (PDF, Word, text)](/img/screenshots/ai-threat-intelligence/kb-upload.webp)

**Document Management** uploads one document with metadata, or several at once:

| Field | Values |
| --- | --- |
| **Section** | Security Policies · Compliance Frameworks · Technical Documentation · Incident Response · Risk Assessment — plus any section you add |
| **Document type** | policy · SOP · compliance framework · audit report · technical documentation · security playbook · incident response · risk assessment · training material · vendor documentation · regulatory guidance · best practices |
| **Sensitivity** | public · internal · confidential · restricted |
| **File** | PDF, Word (`.docx`) or plain text |

On upload the text is extracted, split into chunks and **embedded** for semantic retrieval; the status goes *processing* → *ready*. If extraction produced nothing useful (a scanned PDF, an image-only page) the document is flagged and **Re-process documents** on the Questionnaire tab re-extracts and re-embeds it.

![Document Library: search, section filter, document cards with type, status, tags, questions asked and views; Ask AI About This](/img/screenshots/ai-threat-intelligence/kb-documents.webp)

**Document Library** searches by title, content or topic, filters by section, and shows per document how many questions it has answered and how often it was viewed. **Ask AI About This** opens the assistant scoped to that document. Documents are team-scoped and sensitivity is metadata for your own handling rules — every member of the team can read the library.

## AI Assistant

![AI Assistant: AI Configuration cards (Anthropic Claude, OpenAI Direct, Google Gemini — Add Key); quick-start templates for compliance, incident response, risk and control questions](/img/screenshots/ai-threat-intelligence/kb-chat.webp)

Ask in plain language and the assistant retrieves the most relevant chunks across your documents, answers from them, and returns the **sources** it used with a **confidence** level — *high* (85–100 %), *medium* (60–84 %) or *low*. Quick-start templates cover the common shapes: a compliance requirement check, an incident-response procedure, risk-assessment guidance, how a control is implemented. Thumbs up / down on an answer is recorded with the question for review.

The same tab hosts **AI Configuration** — the team's providers for every AI feature on the platform (Anthropic, OpenAI, Google: Add Key → Test → Activate). See [AI Assistant](../reports-and-ai/ai-assistant.md) for the full picture.

:::warning[Retrieval needs an OpenAI key]
Document retrieval uses OpenAI embeddings (`text-embedding-3-small`). With only an Anthropic or Google key configured, uploads still index and the library works, but questions and questionnaire fills report that retrieval is unavailable rather than guessing — an honest error, not a low-confidence answer. Configure an OpenAI key alongside your preferred answering model.
:::

## Questionnaire auto-fill

![Questionnaire Auto-Fill: how it works; choose an .xlsx; answer detail level short / standard / detailed; Auto-Fill Questionnaire; re-process documents](/img/screenshots/ai-threat-intelligence/kb-questionnaire.webp)

Upload the security questionnaire you received as **Excel (`.xlsx`)**. The platform detects the question column, answers each question from your documents (and from the **answer bank**, below), writes the answers, confidence and source citations back into the sheet, and returns the filled file. **Answer detail level** — short (1–2 sentences), standard (2–5), detailed (full paragraphs) — sets the length; answers are consolidated and rewritten in a customer-facing tone at that length (refinement is on by default; the per-team word limits are adjustable over the API).

## Answer review and the answer bank

![Answer Review: pending review counts by priority — urgent, high, normal, spot-check; pending and history](/img/screenshots/ai-threat-intelligence/kb-answer-review.webp)

Every filled answer is queued for a person to **approve**, **edit** or **reject**, prioritised so the queue is worked in the right order:

| Priority | When |
| --- | --- |
| **Urgent** | The filler flagged the answer as needing review |
| **High** | Confidence below 50 %, or the answer came from the platform's knowledge rather than your documents |
| **Normal** | Everything else answered from your documents |
| **Spot-check** (low) | The answer was auto-filled from the bank — approved once already |

Approved and edited answers are written to the team's **question bank**; the next questionnaire that asks a semantically matching question is filled from the bank first. That loop is what turns the third questionnaire of the quarter into a review job rather than a writing job.

## Usage analytics

![Knowledge Base Analytics: total documents, questions asked, AI accuracy, user satisfaction; popular questions; most referenced documents](/img/screenshots/ai-threat-intelligence/kb-analytics.webp)

Documents, questions asked (today / week / month), **AI accuracy** (the average confidence of the answers given), **user satisfaction** (1–5, from answer feedback), the most-asked questions and the most-referenced documents — a plain view of whether the library is answering what people actually ask, and which document to write next.

:::note[Permissions]
Uploading and deleting documents, asking questions, filling questionnaires and working the review queue need **Manage Assessments**. The library, analytics and templates are readable by any team member.
:::

## Related

- [AI Assistant](../reports-and-ai/ai-assistant.md) — provider configuration and the assistant that lives on every page.
- [Assessments](../compliance/interactive-assessments.md) — the SCF-based auto-fill for framework assessments is a different mechanism and works without a provider.
- [AI Data & Privacy](./ai-data-privacy.md) — what leaves the platform when a question is asked.
