---
title: "Security Engineer Journey"
sidebar_label: "Security Engineer"
sidebar_position: 2
description: "The reading and configuration path for the person who owns scanning, triage, and remediation — from connecting environments to verified fixes and full automation."
---

# Security Engineer Journey

You own scanning, triage, and remediation. This is the documentation path in the order you'll need it — each stage says what you should be able to do before moving on.

Typical role: **Security Manager** — Stages 1 and 5 involve connecting accounts and configuring schedules, which need management access; a **Security Analyst** can follow Stages 2–4 (see [Roles, Teams & API Keys](../authentication/rbac-team-management.md)).

## Stage 1 — Connect everything you defend

1. [Connecting Cloud Accounts](../cloud-security/connecting-accounts.md) — AWS, GCP, and Azure with read-only access and copy-paste Terraform.
2. [Required Permissions](../cloud-security/permissions.md) — the exact per-provider permission sets, and how granting at the org level covers future accounts.
3. [Container Security](../security-scanning/container-security.md) — connect ECR, Artifact Registry/GCR, ACR, or Docker Hub.
4. [Kubernetes Security](../security-scanning/kubernetes-security.md) — clusters auto-discovered from cloud accounts, or onboarded via read-only kubeconfig.

**You can now:** see your estate in [Asset Inventory](../cloud-security/asset-inventory.md).

## Stage 2 — Understand how scanning works

1. [App & Infrastructure Scanning overview](../security-scanning/index.md) — every scan type and the open-source engines behind it.
2. [How Cloud Scans Run](../cloud-security/scan-orchestration.md) — per-provider partitioning, statuses, and the daily/weekly scheduled-scan options.
3. [Native Scans](../security-scanning/native-scans.md) — web (ZAP, Nuclei), network (Nmap), TLS, API scanning, and authenticated scanning.
4. [Compliance & Benchmark Checks](../cloud-security/prowler-integration.md) — CIS benchmarks and framework mappings for cloud posture.

**You can now:** run any scan type on demand and explain what a **Partial** status means.

## Stage 3 — Work findings like a queue

1. [Vulnerability & Risk overview](../vulnerability-risk/index.md) — the detection-to-remediation lifecycle.
2. [Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx) — deduplication, occurrences, lifecycle statuses, and the prioritization signals: CVSS severity, EPSS, CISA KEV, and P0–P4 priority rank.
3. [Business Impact Analysis](../vulnerability-risk/business-impact-analysis.md) — add asset criticality so scores reflect *your* business, not just CVSS.
4. [Risk Register](../vulnerability-risk/risk-register.md) — promote what matters into governed risks with owners and treatment plans.

**You can now:** answer "what are our ten most important findings, and why those?"

## Stage 4 — Make remediation accountable

1. [SLA Management](../vulnerability-risk/sla-management.md) — policies by severity and environment, breach dashboard, escalation. Use **Create Default Policies** to start.
2. [Third-Party Integrations](../integrations/third-party.md) — Jira/ServiceNow with two-way status sync.
3. [Notifications](../integrations/notifications.md) — Slack/Teams/email routing rules so critical findings interrupt someone.
4. **Verify fixes with scans, not tickets:** a finding only reaches **Verified** when a follow-up scan no longer detects it — and a finding that comes back is automatically **Reopened**. This behavior is documented in [Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx).

**You can now:** see every finding currently past its SLA on the Breach Dashboard, and prove closures with scan evidence.

## Stage 5 — Automate yourself out of the loop

1. [Scan Management & Scheduling](../security-scanning/scan-management.md) — the Unified Scheduler: cron/interval schedules, failure notifications, and history.
2. [CLI & CI/CD](../cli-and-cicd.md) — gate builds via the GitHub Action or plain REST; SARIF export for other tools.
3. [API & Automation](../api-automation/index.md) and [Automation Use Cases](../api-automation/automation-use-cases.md) — API keys, release gates, findings export, webhook receivers.
4. [API Reference](../api-reference/index.md) — the full endpoint catalog when you outgrow the recipes.

**You can now:** go on holiday. Scans run on schedule, failures notify the channel, criticals become tickets, and builds gate themselves.

## Going deeper

- [Attack Path Analysis](../cloud-security/attack-paths.md) — from individual findings to exploitable chains.
- [Threat Intelligence](../ai-threat-intelligence/threat-intelligence.md) — KEV/OTX/URLhaus feeds correlated against your assets.
- [Security Command Center (AI-SOC)](../ai-threat-intelligence/ai-soc-agents.md) — AI-assisted triage and remediation drafts (human approval required for any change).
- [On-Premises & Private Infrastructure](../on-premises/index.mdx) — internal networks, Wazuh, and OpenVAS.
