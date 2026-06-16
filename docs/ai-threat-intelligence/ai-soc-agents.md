---
title: "Security Command Center (AI-SOC)"
sidebar_label: "Security Command Center (AI-SOC)"
sidebar_position: 2
---

# Security Command Center (AI-SOC)

The **Security Command Center** is your AI-assisted security operations hub. Instead of working findings module by module, it pulls everything together in one place — taking raw results from your cloud, container, Kubernetes, code, and web scans and turning them into a single prioritized list of what to fix first, complete with the reasoning behind every decision.

Behind the scenes, a set of AI agents triage findings, draft remediation steps, map issues to compliance controls, hunt for threats using the **MITRE ATT&CK** framework, and answer plain-language questions about your posture. You stay in control: nothing destructive happens without your approval, and every AI decision is logged with its reasoning and confidence.

![Security Command Center (AI-SOC)](/img/screenshots/ai-soc.png)

## What it does

The Command Center brings five jobs together on one screen:

- **Correlates findings across every module.** Results from all your scanners flow through a single processing pipeline — Collect → Normalize → **Enrich** → **Correlate** → **Prioritize** → Remediate → Prove — so duplicate and related issues are connected and ranked together rather than scattered across tools.
- **Prioritizes by real-world risk.** Each finding is weighed by **severity**, its **CISA KEV** (Known Exploited Vulnerabilities) status, and its **EPSS** score (the predicted likelihood of exploitation), plus whether the affected asset is internet-facing. Actively-exploited and high-likelihood issues rise to the top.
- **Drafts remediation.** For prioritized issues, the platform proposes concrete fix steps and, where applicable, ready-to-run commands — which you review before anything is applied.
- **Adds threat context.** Findings are correlated against known attack patterns and tagged with the relevant **MITRE ATT&CK** tactics and techniques, so you can see not just *what* is wrong but *how* an attacker could use it.
- **Answers questions.** A built-in Security Advisor responds to plain-language questions like *"What is our biggest risk right now?"* or *"Are we ready for our SOC 2 audit?"* and can generate an executive briefing.

## How to use it

1. From the left navigation, open **AI & Threat Intelligence → Security Command Center**.
2. The **Overview** tab is your starting point. At the top you'll see headline counts — active agents, auto-triggers, open remediations, auto-fixable items, and pipeline runs. Below that, the **Triage Distribution** shows how findings break down (Critical, Investigate, Monitor, and so on) and the **AI Remediation Queue** lists fixes that are ready to review.
3. Switch tabs to drill in:
   - **Triage Center** — every triage decision, with the assigned priority, confidence score, and the reasoning the agent used. Expand a row to see the affected resource, account, and region.
   - **AI Remediation** — the fix guidance generated for findings, including suggested commands and steps. Where a remediation workflow was created, you can click through to it.
   - **Auto-Fix Engine** — proposed automated fixes for compliance violations, grouped by status (Pending, Executed, Denied). This is where you **Approve**, **Deny**, **Execute**, or **Roll back** an action.
   - **Security Advisor** — ask a question, use a quick-prompt chip, or generate an executive briefing.
   - **Activity Log** — a chronological record of every agent decision across the platform.
4. To run agents on demand, use **Run Triage Now** or **Run Threat Hunt** on the Overview tab, or **Process All Findings** in the Auto-Fix Engine. Otherwise, agents run automatically after a scan completes (see below).

:::tip It runs itself after a scan
You don't have to kick off the Command Center manually. When a cloud scan finishes, the agents automatically triage the new findings, draft remediation, and map them to compliance — so by the time you open the page, the work is usually already done. If the page is empty, connect a cloud account and run a scan to populate it.
:::

## Reviewing and approving automated fixes

The **Auto-Fix Engine** is the only part of the Command Center that can change your environment, and it always asks first.

1. Open the **Auto-Fix Engine** tab and review the **Pending** list. Each item shows the playbook, a description, the affected resource, a risk level, and any noted side effects.
2. **Approve** an action to queue it, then **Execute** it to apply the fix — or **Deny** it (with a reason) to discard it.
3. After execution, you can **Roll back** an action if the result isn't what you expected.

:::warning Approval is required for changes
Triage and remediation *suggestions* are generated automatically, but no automated fix is applied to your environment until you explicitly approve and execute it. High-impact triage outcomes (such as marking a finding a false positive or auto-resolving it) are also routed for human review rather than acted on silently.
:::

## Understanding the indicators

| What you'll see | What it means |
|---|---|
| **Priority label** (Critical, Investigate, Monitor, False Positive, Auto-Resolved) | The triage outcome for a finding. Critical means act now; Investigate needs analyst review; Monitor is low-urgency. |
| **Confidence %** | How sure the agent is about its decision. Lower confidence is a cue to double-check. |
| **KEV / EPSS** | Whether the issue is a known exploited vulnerability and its predicted exploitation likelihood — the main drivers of priority. |
| **MITRE ATT&CK tactic/technique** | The attacker behavior the finding maps to, added during threat hunting. |
| **LLM Active / Rule-Based Mode** badge | Whether AI reasoning is enabled. In Rule-Based Mode the platform still triages and prioritizes using its built-in rules. |

:::note Every decision is auditable
Each agent decision is recorded with the agent that made it, the finding it relates to, its reasoning, and a confidence score. All of this is scoped to your **active team**, so the Command Center only ever shows — and only ever acts on — data that belongs to the team you're currently in.
:::

:::tip Bring your own AI provider
AI reasoning works with major model providers (OpenAI, Anthropic, and Google Gemini). Your administrator configures the provider and key in platform settings. If no provider is configured, the Command Center continues to operate in Rule-Based Mode.
:::

## Related

- [AI & Threat Intelligence overview](./index.md) — how the AI and threat-intelligence area fits together.
- [Threat Intelligence & Feeds](./threat-intelligence.md) — the KEV, NVD, and OTX feeds that power exploit-aware prioritization.
- [Vulnerability Management](../vulnerability-risk/vulnerability-management.md) — triage, risk scoring, and tracking findings to remediation.
- [Risk Register](../vulnerability-risk/risk-register.md) — promote significant findings into the risk register with treatment plans.
