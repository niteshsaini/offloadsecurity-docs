---
title: "First 7 Days"
sidebar_label: "First 7 Days"
sidebar_position: 1
description: "A day-by-day plan that takes you from a first connected account to an operating security program: visibility, baseline, prioritization, SLAs, compliance, shift-left, and executive reporting."
---

# First 7 Days — from first scan to operating program

The **[Quickstart](../getting-started.md)** gets you to your first finding. This plan takes the next step: seven focused sessions that end with the platform running as a program — scheduled scans, owned findings, SLAs, alerts, compliance tracking, and an executive view.

Each "day" is a working session of roughly one to two hours. Compress or stretch the calendar as you like — the **order** is what matters, because each day builds on the previous one.

:::info[Who does what]
Days 1–4 need the **Admin** or **Security Manager** role (connecting accounts and configuring scans require management access). Day 5 is natural **Compliance Officer** territory, and Day 7 is where **Viewer**/executive accounts start to matter. See [Roles, Teams & API Keys](../authentication/rbac-team-management.md).
:::

## Day 1 — Establish visibility

**Goal: everything you're responsible for is connected and discovered.**

1. Set up your team and invite colleagues with appropriate roles — [Roles, Teams & API Keys](../authentication/rbac-team-management.md).
2. Connect your cloud accounts (AWS, GCP, Azure) with read-only access — [Connecting Cloud Accounts](../cloud-security/connecting-accounts.md). For the exact permissions per provider, see [Required Permissions](../cloud-security/permissions.md); granting at the AWS Organization / GCP org node / Azure management group covers current *and future* accounts with one binding.
3. Connect container registries (ECR, Artifact Registry/GCR, ACR, Docker Hub) — [Container Security](../security-scanning/container-security.md). The same cloud credentials often unlock these.
4. Onboard Kubernetes clusters — EKS, GKE, and AKS clusters are auto-discovered from connected cloud accounts; on-prem clusters onboard with a read-only kubeconfig or service-account token — [Kubernetes Security](../security-scanning/kubernetes-security.md).
5. Review what was found — [Asset Inventory](../cloud-security/asset-inventory.md).

**Done when:** every production cloud account shows **Connected**, and Asset Inventory lists resources from each of them.

## Day 2 — Establish a security baseline

**Goal: one full scan of everything connected, so you have a "day zero" picture.**

1. Cloud posture: a first scan starts automatically when an account connects — confirm each account's scan reached **Completed** on the Scans page ([How Cloud Scans Run](../cloud-security/scan-orchestration.md)).
2. Run scans for the surfaces you own: web applications and APIs ([Native Scans](../security-scanning/native-scans.md)), container images ([Container Security](../security-scanning/container-security.md)), and clusters ([Kubernetes Security](../security-scanning/kubernetes-security.md)).
3. Connect a repository and run code scanning — SAST, secrets, SCA, SBOM, and license checks — [Code Command Center](../security-scanning/api-code-scanning.md).
4. Open [Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx) and note your baseline: total findings by severity. This is the number you'll measure progress against.

**Done when:** each connected surface has at least one **Completed** scan, and you've recorded the baseline counts.

## Day 3 — Prioritize

**Goal: know which ten findings matter most, and why.**

1. In [Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx), sort by **priority rank (P0–P4)** — it rolls severity (CVSS), exploit probability (**EPSS**), and known exploitation (**CISA KEV**) into one order of work.
2. Add business context for your most important assets with a [Business Impact Analysis](../vulnerability-risk/business-impact-analysis.md) — BIA criticality multiplies risk scores, so crown-jewel systems float to the top.
3. Promote the findings that represent real business exposure into the [Risk Register](../vulnerability-risk/risk-register.md) with owners and treatment plans.

**Done when:** your top findings have named owners, and at least your most critical items exist as governed risks with treatment plans.

## Day 4 — Operationalize

**Goal: the platform chases the work, not you.**

1. Create SLA policies — the **Create Default Policies** button gives you documented starting points (Critical–Production: 24 hours; High–Production: 7 days; Medium–Production: 30 days) — [SLA Management](../vulnerability-risk/sla-management.md).
2. Connect Jira or ServiceNow so findings become tickets with two-way status sync — [Third-Party Integrations](../integrations/third-party.md).
3. Set up Slack, Microsoft Teams, or email notifications, with routing rules so critical findings reach the right channel — [Notifications](../integrations/notifications.md).
4. Schedule recurring scans in **Management → Unified Scheduler** — cloud accounts already get a daily incremental and weekly full scan; add schedules for web, container, Kubernetes, and code scans. Turn on schedule **failure notifications** so a silently broken scan can't hide — [Scan Management & Scheduling](../security-scanning/scan-management.md).

**Done when:** a test notification has arrived in your channel, a finding is linked to a real ticket, SLA policies are active, and every scan type you rely on has a schedule.

## Day 5 — Configure compliance

**Goal: continuous compliance tracking against the frameworks you actually answer to.**

1. Activate the frameworks that apply to you — start with one or two, not ten — [Supported Frameworks](../compliance/supported-frameworks.md) lists the full catalog (ISO 27001, SOC 2, PCI DSS, DPDP Act, SEBI CSCRF, and more).
2. Review your posture on the [Compliance Dashboard](../compliance/compliance-dashboard.md) — scores populate from the scans you ran on Day 2 via [Autonomous Compliance](../compliance/autonomous-compliance.md).
3. Open the [Evidence Hub](../compliance/evidence-hub.md) and run **Collect All**; review what was auto-collected and upload manual evidence (policies, screenshots) where automation can't reach.
4. Turn failing controls that matter into governed risks — compliance gaps can be promoted into the [Risk Register](../vulnerability-risk/risk-register.md) just like findings.
5. **Indian regulated entities:** run the DPDP readiness assessment ([DPDP Act (India) Privacy](../compliance/dpdp-privacy.md)) and read [India Regulatory Readiness](../industries/india-regulatory-readiness.md) for the RBI / SEBI CSCRF / CERT-In mapping.

**Done when:** at least one framework is active with a real score, and its top gaps are either evidenced or tracked as risks.

## Day 6 — Shift left

**Goal: new code is scanned before it ships, not after.**

1. Connect your GitHub or Bitbucket repositories for SAST, secrets, SCA, SBOM, and license scanning — [Code Command Center](../security-scanning/api-code-scanning.md).
2. Add scanning to your pipeline — the [GitHub Action](../cli-and-cicd.md), or plain `curl` against the REST API from any CI system ([Automation Use Cases](../api-automation/automation-use-cases.md) has a copy-paste release-gate recipe).
3. Decide your gate policy: which severities block a build. Start permissive (fail on Critical only) and tighten once the team trusts the signal.
4. On GitHub, install the GitHub App for inline PR annotations and automatic scans — [CLI & CI/CD](../cli-and-cicd.md).

**Done when:** a pull request or pipeline run has been scanned automatically, and a Critical finding would block the build.

## Day 7 — Executive visibility

**Goal: leadership can see posture without asking you for a status update.**

1. Review the Dashboard trends: security score, findings by severity, and recent activity.
2. Check the SLA **Breach Dashboard** — this is your operational health metric from now on — [SLA Management](../vulnerability-risk/sla-management.md).
3. Generate reports for your stakeholders — executive and audit outputs in PDF and HTML — [Reports & AI Assistance](../reports-and-ai.md). AI summaries turn scan results into narrative for non-specialist readers.
4. Give leadership their own access: a **Viewer** role for dashboards, or **Auditor** for read-only evidence and report export — [Roles, Teams & API Keys](../authentication/rbac-team-management.md).

**Done when:** a stakeholder outside the security team has viewed a dashboard or received a report without you exporting it by hand.

## After the first week

- Harden your setup against the **[Recommended Production Configuration](./production-configuration.md)** checklist.
- Go deeper on your own track: the **[Security Engineer](./security-engineer-journey.md)** or **[Compliance Officer](./compliance-officer-journey.md)** journey.
- Extend coverage to what the first week skipped: [Attack Path Analysis](../cloud-security/attack-paths.md), [Threat Intelligence](../ai-threat-intelligence/threat-intelligence.md), and [on-premises visibility](../on-premises/index.mdx).
