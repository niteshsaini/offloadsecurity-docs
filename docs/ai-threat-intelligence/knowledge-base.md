---
title: "Knowledge Base & AI Assistant"
sidebar_label: "Knowledge Base"
sidebar_position: 5
description: "Upload your policies, procedures and standards into a sectioned, sensitivity-labelled library; ask questions and get answers with citations and a confidence score; auto-fill security questionnaires from those documents with an answer bank and a review queue; run policy acknowledgement campaigns; and see who asks what."
---

# Knowledge Base & AI Assistant

Every security team answers the same questions over and over — *what is our password policy*, *how fast do we patch criticals*, *do you encrypt backups* — from the same handful of documents. The Knowledge Base holds those documents once, answers questions from them with a citation and a confidence score, and fills whole security questionnaires the same way. Approved answers go into a bank, so the next questionnaire starts mostly done.

**Where:** left navigation → *Management* → **Knowledge Base**. Tabs: **AI Assistant**, **Document Management**, **Document Library**, **Questionnaire Auto-Fill**, **Answer Review**, **Policy Acknowledgement**, **Usage Analytics**.

## Documents

![Document Management: single or bulk upload; title, section, document type, sensitivity level, description, tags, file (PDF, Word, text)](/img/screenshots/ai-threat-intelligence/kb-upload.webp)

**Document Management** uploads one document with metadata, or up to 50 at once:

| Field | Values |
| --- | --- |
| **Section** | Security Policies · Compliance Frameworks · Technical Documentation · Incident Response · Risk Assessment — plus any section you add |
| **Document type** | policy · SOP · compliance framework · audit report · technical documentation · security playbook · incident response · risk assessment · training material · vendor documentation · regulatory guidance · best practices |
| **Sensitivity** | public · internal · confidential · restricted |
| **File** | PDF, Word (`.docx`), plain text or Markdown, up to 50 MB. Legacy `.doc`, `.xls` and `.ppt` files are refused — save them as `.docx` or PDF first |

On upload the text is extracted, split into chunks and **embedded** for semantic retrieval; the status goes *processing* → *ready*. From Word files the body text and the text in **tables** is read (headers, footers, text boxes and images are not), up to 2,000,000 characters with a warning beyond that. A scanned or image-only PDF has no text and there is no built-in OCR: the document is flagged, and you should OCR it before uploading. **Re-process documents** on the Questionnaire tab re-extracts and re-embeds everything.

![Document Library: search, section filter, document cards with status, type, key topics, questions asked, views and date; Ask AI About This, Delete](/img/screenshots/ai-threat-intelligence/kb-documents.webp)

**Document Library** searches by title, content or topic, filters by section, and shows per document how many questions it has answered, how often it was viewed, and any extraction warning. **Ask AI About This** opens the assistant scoped to that document. Documents are team-scoped and sensitivity is metadata for your own handling rules — every member of the team can read the library.

## AI Assistant

![AI Assistant: AI Configuration cards (Anthropic Claude, OpenAI Direct, Google Gemini — Add Key); quick-start templates for compliance, incident response, risk and control questions](/img/screenshots/ai-threat-intelligence/kb-chat.webp)

Ask in plain language and the assistant retrieves the most relevant passages across your documents, answers from them, and returns the **sources** it used with a **confidence** level — *high* (85–100 %), *medium* (60–84 %) or *low*. Quick-start templates cover the common shapes: a compliance requirement check, an incident-response procedure, risk-assessment guidance, how a control is implemented. Thumbs up / down on an answer is recorded with the question for review. When a question cannot be answered, the chat shows the reason (for example, no provider configured, the key was rejected, or the team is over its AI budget).

The same tab hosts **AI Configuration** — the team's providers for every AI feature on the platform (Anthropic, OpenAI, Google: Add Key → Test → Activate). The operator can instead set one deployment-wide key. See [AI Assistant](../reports-and-ai/ai-assistant.md) for the full picture.

:::warning[Retrieval needs an OpenAI key]
Document retrieval uses OpenAI embeddings (`text-embedding-3-small`) — the team's own OpenAI key, or else the deployment's `OPENAI_API_KEY`. With only an Anthropic or Google key available, uploads cannot be searched: answers come back with **0 % confidence and no sources**, which means "retrieval unavailable", not "your documents don't cover this" (that case is about 25 %). Configure an OpenAI key alongside your preferred answering model.
:::

## Questionnaire auto-fill

![Questionnaire Auto-Fill: how it works; choose an .xlsx; answer detail level short / standard / detailed; Auto-Fill Questionnaire; re-process documents](/img/screenshots/ai-threat-intelligence/kb-questionnaire.webp)

Upload the security questionnaire you received as **Excel (`.xlsx`)**. The platform reads the row-1 headers of the active sheet and picks the question column — check it under **Question column** and change it if needed. It answers each question from your documents (and from the **answer bank**, below), writes the answers, confidence, sources and a fill status back into the sheet, and downloads the filled file. **Answer detail level** — short (1–2 sentences), standard (2–5), detailed (full paragraphs) — sets the length; answers are consolidated and rewritten in a customer-facing tone at that length (refinement is on by default; the per-team word limits are adjustable over the API).

Limits: up to 200 questions per file; only the active sheet is read; **Download again** works for 24 hours. The result panel counts questions filled, failed, skipped and queued for review, and says in red if some answers could not be added to Answer Review.

## Answer review and the answer bank

![Answer Review: pending review counts by priority — urgent, high, normal, spot-check; pending and history](/img/screenshots/ai-threat-intelligence/kb-answer-review.webp)

Every filled answer is queued for a person to **approve**, **edit** or **reject**, prioritised so the queue is worked in the right order:

| Priority | When |
| --- | --- |
| **Urgent** | The filler flagged the answer as needing review |
| **High** | Confidence below 50 %, or the answer came from the platform's knowledge rather than your documents |
| **Normal** | Everything else answered from your documents |
| **Spot-check** (low) | The answer was auto-filled from the bank — approved once already |

Approved and edited answers are written to the team's **question bank**; the next questionnaire that asks a semantically matching question is filled from the bank first. Approved answers older than 180 days are not reused word for word — the question is re-answered from current documents. That loop is what turns the third questionnaire of the quarter into a review job rather than a writing job.

## Policy acknowledgement

New in 1.4.0. Publish a version of a policy to your team, track who has read and acknowledged it, and keep the record as compliance evidence.

1. Upload the document with type **policy**, **SOP**, **security playbook**, **incident response** or **training material**.
2. On **Policy Acknowledgement**, pick the document, enter a version label and a due date (14 days by default), choose the audience (roles and/or individual members) and the SCF controls it evidences (HRS-05.7 and GOV-02 by default), then **Publish**.
3. Recipients are notified in-app (and by email when SMTP is set), open **My policy acknowledgements**, read the version and acknowledge it. Each acknowledgement records who, when, the version and its file fingerprint, the IP address and browser.
4. Track campaigns, **Remind** pending recipients (they are also reminded automatically, at most every 3 days), and export the record as CSV or PDF.

A campaign counts as evidence for its controls only when its audience covers every active team member and all of them (except the publisher) have acknowledged; the evidence is then valid for 365 days. An overdue campaign is a gap, and publishing a new version supersedes the previous one. **Exempt** and **Remove** take a person out of the count; both ask for a reason and are audited. See [Evidence Hub](../compliance/evidence-hub.md) for how the evidence is used.

## Usage analytics

![Knowledge Base Analytics: total documents, questions asked, AI accuracy, user satisfaction; popular questions; most referenced documents](/img/screenshots/ai-threat-intelligence/kb-analytics.webp)

Documents, questions asked (today / week / month), **AI accuracy** (the average confidence of the answers given), **user satisfaction** (1–5, from answer feedback), the most-asked questions and the most-referenced documents — a plain view of whether the library is answering what people actually ask, and which document to write next. Figures with no data yet show *N/A*, not 0.

:::note[Permissions]
Uploading and deleting documents, asking questions, filling questionnaires, working the review queue and publishing acknowledgement campaigns need **Manage Assessments**. The library, analytics and templates are readable by any team member, and any member can acknowledge a policy sent to them. Exporting a campaign record needs **Export Reports**.
:::

## Related

- [AI Assistant](../reports-and-ai/ai-assistant.md) — provider configuration and the assistant that lives on every page.
- [Assessments](../compliance/interactive-assessments.md) — the SCF-based auto-fill for framework assessments is a different mechanism and works without a provider.
- [AI Data & Privacy](./ai-data-privacy.md) — what leaves the platform when a question is asked.
