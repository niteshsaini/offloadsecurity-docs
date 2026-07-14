---
title: "Knowledge Base & AI Assistant"
sidebar_label: "Knowledge Base"
sidebar_position: 4
---

# Knowledge Base & AI Assistant

The **Knowledge Base** turns your own security documents — policies, standards, runbooks, prior questionnaires — into a searchable library that an AI assistant can answer questions from. Instead of digging through files to find "what's our MFA policy?" or "how do we handle a data breach?", you ask in plain language and get an answer grounded in **your** documents, with the sources cited.

![AI Knowledge Base with assistant, document management, and questionnaire auto-fill tabs](/img/screenshots/knowledge-base.png)

It also helps with two recurring chores: auto-filling security questionnaires from your existing material, and searching across everything you've uploaded.

## What it does

- **Document Q&A (RAG)** — ask questions in natural language and get answers drawn from the documents you've uploaded, not the open internet. Each answer shows a **confidence score**, the **source documents** it used, and suggested **follow-up questions**.
- **Document library** — upload, organize, search, and manage your security documents. Files are grouped into **sections** (for example, Security Policies, Compliance Frameworks, Technical Documentation, Incident Response, Risk Assessment), and you can create your own sections too.
- **Questionnaire auto-fill** — upload a security questionnaire as an Excel (`.xlsx`) file and the assistant fills in answers from your knowledge base, complete with confidence scores and source citations, then hands you the completed file to download and review.
- **Usage analytics** — see how the knowledge base is being used: total documents, questions asked, popular questions, and the most-referenced documents.

:::note[Bring your own AI provider]
The assistant works with major model providers, including OpenAI, Anthropic (Claude), and Google Gemini, plus a built-in default. Your administrator chooses and configures the provider; you select which one to use from the **AI Assistant** tab.
:::

## How to use it

Open **Knowledge Base** from the left navigation. The page has five tabs across the top: **AI Assistant**, **Document Management**, **Document Library**, **Questionnaire Auto-Fill**, and **Usage Analytics**.

### 1. Upload your documents

The assistant can only answer from what you've given it, so start by adding documents.

1. Go to the **Document Management** tab.
2. Choose **Single Upload** (one file with full details) or **Bulk Upload** (many files at once, sharing the same settings).
3. Select a **file**, give it a **title**, pick a **section**, and optionally set a document type, sensitivity level, tags, and description.
4. Select **Upload**. The document is processed in the background and becomes available for Q&A shortly — its status changes to **Ready** when it's searchable.

:::tip[Supported files]
You can upload **PDF, Word (`.doc` / `.docx`), text (`.txt`), and Markdown (`.md`)** files, up to **50 MB each**. Bulk upload accepts up to **50 files** at a time.
:::

### 2. Ask the AI assistant

1. Open the **AI Assistant** tab.
2. (Optional) Narrow the scope with the **question type** (General, Compliance, Technical, Policy, Procedure, Risk, Incident) and a specific **section** — leave both as-is to search everything.
3. Type your question (for example, *"What is our password rotation policy?"*) and select **Ask**.
4. Read the answer, check its **confidence level** and **Sources**, and select a **Related Question** to dig deeper. The assistant remembers the conversation, so follow-ups build on what you've already asked.
5. Give a quick 👍 / 👎 on each answer to help improve future results, or select **Start New Conversation** to reset the context.

Need a starting point? The **Quick Start Templates** on the same tab pre-fill common questions about compliance, incidents, risk, and controls.

### 3. Find a specific document

1. Go to the **Document Library** tab.
2. Search by title, content, or topic, or filter by **section**.
3. Open a document's actions to **Ask AI About This** (jumps to the assistant with the document pre-loaded) or **Delete** it.

### 4. Auto-fill a security questionnaire

1. Open the **Questionnaire Auto-Fill** tab.
2. Upload an Excel (`.xlsx`) file that has a column of questions.
3. Select **Auto-Fill Questionnaire**. The assistant searches your documents for relevant answers (this can take a few minutes for large files).
4. The completed Excel downloads automatically, with AI answers, confidence scores, and source citations. A summary shows how many questions were filled, skipped, and the average confidence.

:::warning[Always review AI answers]
Auto-fill is a drafting aid, not a final submission. Review every answer — especially low-confidence ones — before you send a questionnaire to a customer or auditor.
:::

## Tips & prerequisites

:::tip[Better answers from cleaner documents]
If the assistant returns low-confidence answers, or a document is flagged as unreadable, use **Re-extract & Re-embed** (on the Questionnaire Auto-Fill tab) to redo text extraction, or **Regenerate AI Summaries** if only the summaries are missing. Both run in the background.
:::

:::note[Everything stays in your team]
Your documents, questions, and answers are scoped to your **active team**. You only see — and the assistant only answers from — material that belongs to the team you're currently in. Check the team selector in the top-right before uploading or asking.
:::

:::warning[Mind document sensitivity]
Anything you upload can be used to answer questions for your team. Only add material your team is permitted to see, set an appropriate **sensitivity level**, and review your team membership before adding confidential policies.
:::

## Related

- [AI & Threat Intelligence Overview](./index.md) — how AI and threat context fit together across the platform.
- [AI SOC Agents](./ai-soc-agents.md) — automated triage, remediation, and threat hunting on your findings.
- [AI Governance & Privacy Compliance](./ai-governance.md) — govern your own AI systems against the EU AI Act and other regulations.
- [Threat Intelligence & Feeds](./threat-intelligence.md) — live feed ingestion and indicator correlation.
