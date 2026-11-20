---
title: "Security Command Center"
sidebar_label: "Security Command Center"
sidebar_position: 2
description: "The AI-assist layer on the one triage queue — AI verdicts, correlation and FP/TP assessment recorded on the same findings Vulnerability Management works, the AI remediation queue, the Auto-Fix Engine with approval and rollback, remediation workflows, a Security Advisor that answers from your posture numbers, and an activity log of every agent decision. Rule-based out of the box, LLM-assisted when a provider is configured."
---

# Security Command Center

Scanners produce findings faster than a team can read them. The Security Command Center puts a set of agents in front of that stream: one gives every open finding an AI verdict with a stated reason and confidence, one groups findings that share a root cause, one drafts the fix, one matches cloud findings to remediation playbooks that wait for a human's approval, and one answers questions about the posture in plain language. Since 1.4.0 the agents work the **same queue** as [Vulnerability Management → Triage](../vulnerability-risk/vulnerability-management/triage.md): their verdicts are recorded on the finding, and the decision is made there. Nothing changes in your environment without an explicit approve-and-execute, and every agent decision is written to an activity log with its reasoning.

**Where:** left navigation → *Core Security* → **Security Command Center**. Tabs: **Overview**, **Triage Center**, **AI Remediation**, **Auto-Fix Engine**, **Remediation Workflows**, **Security Advisor**, **Activity Log**.

![Security Command Center overview in Rule-Based Mode: agents active, auto-triggers, AI remediations, auto-fixable, pipeline runs; triage distribution of AI verdicts (Critical, Investigate) with Run Triage Now; AI remediation queue](/img/screenshots/ai-threat-intelligence/soc-overview.webp)

## Two modes

The header badge says which mode the agents are in:

| Badge | Meaning |
| --- | --- |
| **Rule-Based Mode** | No LLM provider is configured for the team. Triage uses the built-in rule set below, remediation comes from the playbook and pattern library, the advisor answers from posture data with templated prose. Fully functional, deterministic, free. |
| **LLM Active** | A provider is configured (a team key under Knowledge Base → AI Assistant → *AI Configuration*, or a deployment-wide key set by the operator). The model adds reasoning on top of the same signals — it can raise a verdict, explain it in context and draft resource-specific fixes — and falls back to the rules if the call fails. |

## Overview

The tiles are the live state: **Agents Active**, **Auto-Triggers** (scans that kicked off agents), **AI Remediations** (the remediation agent's decisions), **Auto-Fixable** (open remediation actions with a playbook), **Pipeline Runs**. Below: the distribution of **AI verdicts on open findings** with **Run Triage Now**, the **AI Remediation Queue** (items marked *Auto-fix ready*), the **Auto-Fix Engine summary** by status, **Pipeline Processing**, and **Recent Auto-Triggers** with **Run Threat Hunt**. Summary tiles and distribution rows open the matching tab.

Agents run on their own after a **cloud scan** completes: the trigger service gives the new findings AI verdicts, drafts remediation for critical and high ones and maps them to SCF controls. Findings from other modules are on the same queue; use **Triage new/changed** for them. **Run Triage Now** previews how many open findings need an AI verdict, then triages up to 300 of them, highest risk first.

## Triage Center

![Triage Center: open findings, need action now, AI-triaged and need-AI-triage tiles; Triage new/changed, Correlate, Assess FP/TP, Assess code scans, Prepare fixes; action-queue worklist with priority, severity, AI verdict and confidence, reasoning and recommended action per finding, Open in VM Triage](/img/screenshots/ai-threat-intelligence/soc-triage.webp)

The Triage Center lists the **same findings, ids and totals** as VM Triage, with the AI layer on top:

- **Scope** — **Action queue (P1+P2)** (the default), **Backlog (P3+P4)** or **All open**. Priorities come from the platform's deterministic risk score, not from the AI.
- **Tiles** — Open findings (the same count as VM Triage), Need action now (P1 + P2), AI-triaged, Need AI triage.
- **Filters** — AI verdict (including *Not AI-triaged yet*) and severity.
- **Each row** — priority, severity, the AI verdict and recommended action, the reasoning and confidence, and any analyst decision already recorded. **Open in VM Triage →** opens the finding where the decision is made.

The AI verdict is advice. Decisions — confirm, accept risk, mark false positive, suppress, mark duplicate, resolve, assign — are recorded in VM Triage (or over the API) with the **Manage Triage** permission, and accept risk, mark false positive and suppress require a justification. An AI verdict never sets the human decision.

### AI actions

Every AI action first previews what it will touch, asks you to confirm with the exact counts, then reports the result and what remains:

| Button | What it does |
| --- | --- |
| **Triage new/changed** | Gives an AI verdict to open findings that have none, or that changed since their last one — up to 300 per run, highest risk first. Unchanged findings are not sent again |
| **Correlate** | Groups open findings that share a root cause (the same check or rule across many resources, accounts and regions) into **incidents** with one *fix once* recommendation. The grouping is deterministic; with an LLM the incident narrative is written by the model |
| **Assess FP/TP** | Rates not-yet-assessed open findings as likely true positive, likely false positive or needs review. Only findings that carry code or reachability evidence use the model; the rest are marked *needs review*. Advisory — nothing is suppressed |
| **Assess code scans** | The same for findings from your recent code scans: secrets are checked by live validation and dependencies by reachability without a model; SAST uses the code snippet |
| **Prepare fixes** | Turns findings you sent with **Send to auto-fix** into prepared fix suggestions, 25 per run. It does not open pull requests. The team must have auto-fix switched on (Code Command Center → *Enable for this team*, a **Manage Team** setting), which is only offered when the operator has enabled agentic fixes for the deployment (`AGENTIC_FIX_ENABLED`, off by default) |

### How the rule set decides

| Verdict | When |
| --- | --- |
| **Critical** (act now) | Critical and in **CISA KEV** · critical on a production, internet-facing asset · critical and internet-facing · critical with **EPSS > 0.5** · critical open for more than 30 days |
| **Investigate** | High and KEV or internet-facing · high on production · any other high |
| **Auto-resolved** | Medium or low that was previously resolved — same issue recurring, likely already addressed (higher confidence in non-production) |
| **Monitor** | A remediation workflow already exists · medium with EPSS < 0.1, not internet-facing, non-production · medium in dev / test |
| **False positive** | Low / informational severity in a non-production environment — the rule set's one severity-based FP call (0.7). Anything else needs the evidence-based assessment above |
| *(Low elsewhere)* | Low severity outside dev / test → **Monitor**; a finding no rule recognises → **Investigate** at 0.5 |

Signals come from the finding and its enrichment: severity, KEV flag, EPSS, whether the asset is public-facing, environment tags, first-seen date, and whether a similar finding was resolved before. Confidence is a property of the rule (0.97 for KEV-critical, 0.65 for medium-in-dev); a low number is a cue to look.

## AI Remediation

![AI Remediation Actions: generated fix guidance per finding with resource, severity and check](/img/screenshots/ai-threat-intelligence/soc-remediation.webp)

Fix guidance generated for prioritised findings — steps, and where a pattern exists, ready-to-run commands (an SSM downgrade, a bucket policy, a key rotation). In rule-based mode the text comes from the remediation pattern library keyed on the check; with an LLM it is drafted for the specific resource. The list says how many decisions it shows out of the total. Where a remediation workflow was created, the entry links to it. Nothing here executes.

## Auto-Fix Engine

![Auto-Fix Engine: Pending actions with playbook, risk level, resource and check; Approve / Deny per action; Process All Findings](/img/screenshots/ai-threat-intelligence/soc-auto-fix.webp)

The one part of the Command Center that can change your environment — and it always asks first.

1. **Process All Findings** matches the team's open cloud findings against the remediation **playbooks** (enforce HTTPS on a storage account, uniform bucket-level access, block public S3 access, enable flow logs, …). Each match becomes an **action** with the playbook, risk level, target resource, the exact fix and its rollback.
2. **Pending** lists actions awaiting a decision. **Approve** queues one; **Deny** discards it with a reason. Playbooks flagged *auto-approve* (low-risk, reversible) are preferred when several match, but still wait for approval.
3. **Execute** applies an approved action. Executed actions can be **rolled back**.

Tabs and tiles count **Pending**, **Executed**, **Simulated**, **Failed**, **Denied** and **Rolled Back** separately. If an approve, deny, execute or rollback fails, the server's reason is shown above the list and the action keeps its previous state. All of this needs **Execute Remediations**.

:::warning[Execution is dry-run until the operator turns it on]
Out of the box `REMEDIATION_LIVE_EXECUTE` is false: *Execute* makes no cloud API call, the page says **Simulated**, and the action is listed under *Simulated*, not *Executed*. A simulated action has nothing to roll back. An operator enables live execution deliberately, per deployment. Approvals, denials, executions and rollbacks are all audit events.
:::

## Remediation Workflows

Tracked remediation work items — status (open, assigned, in progress, fixed, verified, closed, deferred, won't fix, reopened) and priority — with the allowed transitions between statuses. Entries in AI Remediation link to their workflow when one exists.

## Security Advisor

![Security Advisor: ask a question; quick prompts Biggest risk?, SOC 2 ready?, Monthly improvement?; Generate Executive Briefing](/img/screenshots/ai-threat-intelligence/soc-advisor.webp)

Ask in plain language — *What is our biggest risk?*, *Are we ready for SOC 2?* — or **Generate Executive Briefing** for a weekly summary. Answers are built from a small set of posture numbers: open findings by severity across every module (the same count as the Dashboard), resolved findings and resolution rate, the number of risks, the number of cloud accounts, and the implementation score of each **active** framework. A readiness question that names a framework is answered with that framework's score; a framework that is not active is reported as not scored.

An answer built from rules — because no provider is configured, or the AI call failed or timed out — is labelled **Rule-based answer, not AI**, with the reason. The advisor cannot look up a specific finding, asset, CVE or document; use VM Triage for findings and the [Knowledge Base](./knowledge-base.md) for policy questions.

## Activity Log

![Agent Activity Log: agent, decision and finding, resource, resource type, severity, confidence and time for every agent decision](/img/screenshots/ai-threat-intelligence/soc-activity.webp)

Every agent decision for the team, newest first: which agent, which finding and resource, the decision, the reasoning and the confidence. It is the answer to "why did the platform call this critical", and it is scoped to the active team like everything else on the page. Agent audit records are kept for five years by default (`AGENT_AUDIT_RETENTION_DAYS`).

## Related

- [Triage](../vulnerability-risk/vulnerability-management/triage.md) — the queue the Command Center works, and where decisions are recorded.
- [Threat Intelligence](./threat-intelligence.md) — where the KEV flag and IOC matches come from.
- [Remediation Queue](../cloud-security/remediation-queue.md) — the cloud remediation workflow the Auto-Fix Engine feeds.
- [API](./api.md#security-command-center) — every endpoint on this page.
