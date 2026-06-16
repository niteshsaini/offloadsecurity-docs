---
title: "Compliance & Benchmark Checks"
sidebar_label: "Compliance & Benchmark Checks"
sidebar_position: 5
---

# Compliance & Benchmark Checks

When you run a posture scan, Offload Security checks your cloud configuration against hundreds of industry security benchmarks and best practices — the same checks used to measure CIS Benchmark and framework compliance. Every check that fails becomes a finding in **Cloud Security**, complete with a severity, the affected resource, and step-by-step remediation. This page explains what those checks assess and how the results show up.

## What it does

The posture engine runs read-only checks against your AWS, Azure, and GCP accounts and reports each one as **pass** or **fail**:

- **CIS Benchmarks.** Your accounts are evaluated against the Center for Internet Security (CIS) Foundations Benchmark for each provider — for example, alerting on root-account usage without MFA, public storage buckets, overly broad security groups, or disabled audit logging.
- **Security best practices.** Beyond CIS, checks cover provider-recommended hardening across identity, networking, storage, compute, logging, and encryption — even where a check isn't tied to a formal control.
- **Compliance framework mapping.** Each finding carries the framework controls it relates to, so you can see your posture through the lens of the standard you care about. Supported frameworks vary by provider:

  | Provider | Frameworks available |
  |---|---|
  | **AWS** | CIS, NIST 800-53, SOC 2, PCI-DSS, HIPAA, GDPR, ISO 27001, FedRAMP, FFIEC, AWS Well-Architected (Security Pillar) |
  | **Azure** | CIS, SOC 2, PCI-DSS, ISO 27001, MITRE ATT&CK |
  | **GCP** | CIS, SOC 2, PCI-DSS, ISO 27001, MITRE ATT&CK |

- **Severity and remediation.** Every failing check is rated **Critical**, **High**, **Medium**, **Low**, or **Informational**, and includes a plain-language description of the problem plus the recommended fix (often with a reference link).
- **Security domains.** Findings are grouped into categories — **IAM**, **Network**, **Storage**, **Compute**, **Logging**, and **Encryption** — so you can focus on one area at a time.

:::note Framework availability differs by cloud
NIST 800-53 mapping is available for **AWS only**. HIPAA, GDPR, FedRAMP, FFIEC, and AWS Well-Architected are AWS-specific as well. If you need a framework that isn't listed for a provider, the underlying CIS and best-practice checks still run — only the framework labels differ.
:::

## How to use it

1. **Connect a cloud account.** Posture checks only run against accounts you've connected. See **[Connecting Cloud Accounts](./connecting-accounts.md)** for setup and ready-to-use Terraform.
2. **Run a posture scan.** Start a scan from **Cloud Security**, or let the first scan kick off automatically when an account connects. You can choose how broad the scan is:
   - A **quick** scan runs a focused subset of checks for fast feedback.
   - A **full** scan runs the complete set of checks.
   - A **comprehensive** scan runs every check and evaluates all applicable compliance frameworks.
3. **Review the findings.** Open the findings view to see every failing check, ranked by severity and tagged with its security domain and framework controls. Identical issues across resources are grouped into a single actionable check to cut down on noise.
4. **Open a finding to remediate.** Each finding shows what failed, why it matters, and how to fix it — including a deep link into the relevant cloud console. For supported checks you can launch a guided remediation workflow.
5. **Re-scan and track over time.** Run scans on a schedule or after making fixes. Drift detection flags posture that regresses — for example, audit logging being turned off again — so a closed finding doesn't quietly come back.

:::tip Match the scan to the moment
Use a **quick** scan day to day for fast signal, and run a **comprehensive** scan before an audit or framework review so every applicable control is evaluated.
:::

## How findings show up

Once a scan finishes, its results flow straight into the standard **Cloud Security** findings view — the same place you see your cloud providers' own alerts (GuardDuty, Security Command Center, Defender for Cloud). That means benchmark and compliance findings are triaged, scored, and reported alongside everything else:

- They appear in the findings list with severity, affected resource, security domain, and mapped framework controls.
- They roll up into your **[Compliance Posture](../compliance/compliance-dashboard.md)**, contributing pass/fail counts per framework.
- They can be promoted into the **Risk Register** and exported in compliance and audit reports, just like any other finding.
- You can resolve or temporarily **suppress** individual findings during triage.

:::warning Suppressions expire
A suppressed finding is hidden only for the window you choose. When that window ends, the finding returns to a failing state so it isn't lost — review suppressed items periodically.
:::

## Related

- **[Cloud Security (CSPM)](./index.md)** — the module overview and full posture workflow.
- **[Connecting Cloud Accounts](./connecting-accounts.md)** — add AWS, Azure, or GCP with read-only access.
- **[Scan Orchestration & Lifecycle](./scan-orchestration.md)** — how posture scans are queued, run, and tracked.
- **[Asset Inventory](./asset-inventory.md)** — the live catalog of cloud resources discovered during scans.
