---
title: "Recommended Production Configuration"
sidebar_label: "Production Configuration"
sidebar_position: 4
description: "Opinionated starting points for coverage, scan schedules, SLAs, alerting, ticketing, compliance, and access control in a production deployment."
---

# Recommended Production Configuration

This page is the answer to "what does a *good* setup look like?" — opinionated starting points for each area of the platform.

:::warning[Starting points, not requirements]
These are recommended defaults for a typical production deployment, not universal requirements. Your regulators, risk appetite, and team size may justify different choices — the point is to start from something deliberate rather than from empty settings.
:::

## Coverage

**Principle: connect everything you'd be embarrassed to discover was unmonitored.**

| Surface | Recommendation |
|---|---|
| Cloud accounts | Connect **all** production accounts/projects/subscriptions, not a sample. Grant access at the AWS Organization / GCP org node / Azure management group so future accounts are covered by one binding — [Required Permissions](../cloud-security/permissions.md). |
| Container registries | Every registry that feeds production deploys — [Container Security](../security-scanning/container-security.md). |
| Kubernetes | All production clusters; EKS/GKE/AKS are auto-discovered from connected cloud accounts — [Kubernetes Security](../security-scanning/kubernetes-security.md). |
| Code repositories | Every repo that ships to production — [Code Command Center](../security-scanning/api-code-scanning.md). |
| Web apps & APIs | Your externally reachable applications and APIs — [Native Scans](../security-scanning/native-scans.md). |
| Internal infrastructure | If you have significant on-prem estate, see [On-Premises & Private Infrastructure](../on-premises/index.mdx). |

All scanning access is **read-only** — there is no write path from the scanner into your environment.

## Scan schedules

Cloud accounts already get a built-in cadence — a **daily incremental** scan and a **weekly full** scan of active accounts ([How Cloud Scans Run](../cloud-security/scan-orchestration.md)). Add schedules for the rest in **Management → Unified Scheduler** ([Scan Management & Scheduling](../security-scanning/scan-management.md)):

| Scan type | Recommended starting cadence |
|---|---|
| Cloud posture | Built-in daily incremental + weekly full — keep it. |
| Container images | Weekly, plus webhook auto-scan on push where the registry supports it. |
| Kubernetes | Weekly. |
| Web application / API (DAST) | Weekly for key applications; after major releases for the rest. |
| Code (SAST/SCA/secrets) | On every pipeline run via [CI/CD integration](../cli-and-cicd.md); a weekly scheduled scan as a safety net for repos without CI coverage. |

Two settings that matter more than the cadence itself:

- **Turn on failure notifications** for every schedule. A scan that silently stops running is worse than one that runs rarely — you keep trusting stale data.
- Schedules run in **UTC** by default — pick hours that avoid your own maintenance windows.

## Remediation SLAs

Start with the documented defaults via **Create Default Policies** in [SLA Management](../vulnerability-risk/sla-management.md):

| Policy | Resolution target |
|---|---|
| Critical – Production | 24 hours |
| High – Production | 7 days |
| Medium – Production | 30 days |

Then:

- Add an escalation rule so an approaching breach notifies the finding's owner, and an actual breach notifies their manager.
- Treat the **Breach Dashboard** as your weekly operational health check.
- Rely on scan-verified closure: a finding reaches **Verified** only when a follow-up scan no longer detects it, and reappearing findings are automatically **Reopened** — a closed Jira ticket is not proof of a fix ([Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)).

## Alerting & ticketing

**Principle: criticals interrupt a human; everything else batches.**

- **Slack or Teams** ([Notifications](../integrations/notifications.md)): route **Critical and High** findings to your on-call/security channel using routing rules. Don't route Medium/Low to chat — that's how channels get muted.
- **Email (SMTP)**: configure as the fallback channel and for people who don't live in chat.
- **Jira or ServiceNow** ([Third-Party Integrations](../integrations/third-party.md)): connect with two-way sync so remediation happens in the tool engineers already use.
- **Webhooks / SIEM**: if you run Splunk, Sentinel, or QRadar, forward events so the SOC sees platform activity alongside everything else.

## Compliance

- Activate **one or two frameworks** you actually answer to — not the whole catalog. The SCF common-control model means adding more later costs little ([Supported Frameworks](../compliance/supported-frameworks.md)).
- Run **Collect All** in the [Evidence Hub](../compliance/evidence-hub.md) once scans are flowing, then keep evidence fresh automatically: cloud and scan evidence is valid for 90 days, so your weekly full scans keep it perpetually current.
- **Indian regulated entities:** follow the deployment shape in [India Regulatory Readiness](../industries/india-regulatory-readiness.md) (private deployment, anchor framework, reporting clocks) and enable the [DPDP module](../compliance/dpdp-privacy.md).

## Access control

- **Least role that works** ([Roles, Teams & API Keys](../authentication/rbac-team-management.md)): engineers get **Security Analyst**, leads get **Security Manager**, GRC gets **Compliance Officer**, executives get **Viewer**, external reviewers get **Auditor**. Keep **Admin** to a small number of people.
- Use **teams** to separate environments or business units that shouldn't see each other's data.
- **API keys**: use the scoped presets (CI/CD Basic for pipelines, Read Only for exports) rather than Full Access; keep the default 90-day expiry and rotate on schedule. Add IP allowlists for keys used from fixed infrastructure.

## CI/CD gates

- Start with **fail on Critical only**, then tighten to include High once the team trusts the signal and the backlog is under control — [CLI & CI/CD](../cli-and-cicd.md).
- Prefer the **GitHub App** on GitHub (inline PR annotations, auto-scan); use the GitHub Action or plain REST calls elsewhere.
- Export **SARIF** if other tools in your pipeline consume it (SARIF is export-only — the platform doesn't import SARIF from other scanners).

## What "healthy" looks like

Run through this list monthly:

- [ ] Every production account, registry, cluster, and repo is connected — spot-check against your cloud org's account list.
- [ ] No schedule has been silently failing — the Unified Scheduler history shows recent successful runs for every schedule.
- [ ] The SLA Breach Dashboard trend is flat or improving.
- [ ] Critical alerts have a named channel and someone acknowledges them.
- [ ] Compliance evidence isn't expiring faster than it's refreshed.
- [ ] API keys in use are scoped, unexpired, and attributable to an owner.

If all six hold, your configuration is doing its job — the interesting work is now remediation and risk reduction, not platform upkeep.
