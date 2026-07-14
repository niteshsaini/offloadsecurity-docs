---
title: "Reports & AI Assistance"
sidebar_label: "Reports & AI Assistance"
sidebar_position: 5.5
---

# Reports & AI Assistance

Every module on the platform feeds one reporting layer, and AI assistance is available wherever a human has to read, explain, or act on the results. This page covers what you can produce — from a per-repository findings report to an executive compliance package — and what the AI features do (and deliberately don't do).

## Reports

- **Unified findings reports.** Findings from cloud, code, containers, Kubernetes, on-prem scanners, and integrated third-party tools share one normalized model — so a report can slice by module, source, severity, asset, or team without stitching exports together.
- **Per-repository report.** A single consolidated report per code repository: SAST, secrets, dependency (SCA), SBOM, and license findings for that repo in one place, suitable for handing to the owning engineering team.
- **Module reports.** Cloud posture, vulnerability management, container/SBOM and license, compliance posture, and risk register views each export their own report.
- **Executive & audit outputs.** Compliance and risk reporting is generated from live data — the same numbers the dashboard shows — in **PDF, HTML, and Excel**, and evidence-backed packages come from the [Evidence Hub](./compliance/evidence-hub.md) and [DPDP audit packs](./compliance/dpdp-privacy.md).
- **Scheduled and on-demand.** Run reports ad hoc, or export on a schedule via the [API](./api-automation/index.md).

:::tip Reports are team-scoped
Like everything else on the platform, reports contain only the active team's data. Switch teams before generating a report intended for a different business unit.
:::

## AI assistance

AI features are built to save analyst time, with a human deciding what to do:

- **AI summaries on reports.** Any report view can generate an AI summary — what changed, what matters most, and where to start — so the person receiving the report doesn't need to parse hundreds of findings to get the point.
- **AI remediation suggestions.** Findings carry AI-generated remediation guidance: what the issue means in context and a suggested fix approach. Suggestions are **advisory drafts** — they never modify your configuration, close a finding, or accept a risk on their own.
- **Questionnaire & assessment auto-fill.** Security questionnaires, DPIAs, and assessments can be pre-populated from evidence the platform already holds — see [Knowledge Base](./ai-threat-intelligence/knowledge-base.md) and [DPDP](./compliance/dpdp-privacy.md) — then reviewed and approved by a person.
- **The assistant.** Platform questions ("how do I connect a GCP org?", "what does this control require?") are answered from a curated knowledge layer; common questions are served from a cache without a model call at all.

:::note How AI handles your data
AI answers are generated only from data your team can already access, and nothing derived from your tenant is stored in any shared cache. Details in [Trust & Security](./trust-and-security.md#how-ai-features-handle-your-data).
:::

## Related

- [Vulnerability & Risk Overview](./vulnerability-risk/index.md)
- [Evidence Hub](./compliance/evidence-hub.md)
- [Knowledge Base](./ai-threat-intelligence/knowledge-base.md)
- [Trust & Security](./trust-and-security.md)
