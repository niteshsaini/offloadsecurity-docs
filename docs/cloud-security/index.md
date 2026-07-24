---
title: "Cloud Security (CSPM)"
sidebar_label: "Overview"
sidebar_position: 0
---

# Cloud Security (CSPM)

Cloud Security is the platform's Cloud Security Posture Management (CSPM) module. It continuously assesses your AWS, Azure, and GCP environments for misconfigurations, pulls in your cloud providers' own security findings, and gives you a single, prioritized view of cloud risk — with remediation guidance and drift detection so issues don't quietly reappear.

![Cloud Security management](/img/screenshots/cloud-security.png)

## What it does

- **Continuous posture scanning.** Checks your AWS, Azure, and GCP configuration against hundreds of security best practices and benchmarks, then surfaces every misconfiguration as a finding with a severity and the affected resource.
- **Native findings ingestion.** Reads the findings your cloud providers already generate — **AWS GuardDuty** (and Security Hub), **GCP Security Command Center**, and **Microsoft Defender for Cloud** — and folds them into the same view, so you don't have to jump between consoles.
- **Remediation guidance.** Every finding comes with a description, severity, and step-by-step fix. For supported checks you can launch a guided remediation workflow from a built-in playbook catalog.
- **Drift and continuous monitoring.** Watches for changes to your security posture over time — for example a logging or threat-detection service being disabled — and flags the drift so a fixed issue doesn't silently regress.
- **Read-only and least-privilege.** Connections use **read/security-audit** access only and credentials are stored **encrypted at rest**. The platform never needs write or admin permissions on your cloud.

All cloud resources discovered during scanning also flow into your live **[Asset Inventory](./asset-inventory.md)**.

## How to use it

1. **Connect a cloud account.** Go to **Cloud Security → Cloud Accounts** and add your AWS, Azure, or GCP account. The platform validates the credentials and permissions before saving them. See **[Connecting Cloud Accounts](./connecting-accounts.md)** for step-by-step setup and ready-to-use Terraform.
2. **Run a posture scan.** A first scan can start automatically once an account connects, or you can trigger one at any time. Scanning runs in the background, so you can keep working while it completes.
3. **Review findings.** Open the findings view to see misconfigurations and native-provider alerts together, ranked by severity. Identical issues are grouped into a single actionable check to cut down on alert noise.
4. **Remediate.** Open a finding to read its remediation steps, follow the deep link into the relevant cloud console, or launch a guided remediation workflow. You can also resolve or temporarily suppress findings in bulk.
5. **Track over time.** Re-scan on a schedule (or after making fixes) and let drift detection alert you if posture regresses.

:::tip[Group connected accounts by environment]
Because data is scoped per **team**, connect production and non-production accounts under the teams that should see them. Confirm you're in the right active team before adding an account or kicking off a scan.
:::

:::note[What you need first]
You can only scan accounts you've connected. If Cloud Security looks empty, start by adding a cloud account. Each provider needs a specific set of read-only permissions — these are listed, with copy-paste Terraform, on the connecting page.
:::

:::warning[Suppressions expire]
A suppressed finding is hidden only for the duration you choose. When that window ends, the finding automatically returns to a failing state so it isn't lost — review suppressed items periodically.
:::

## Related

- **[Connecting Cloud Accounts](./connecting-accounts.md)** — add AWS, Azure, or GCP and grant read-only access.
- **[Cloud Account Management](./account-management.md)** — view, validate, and manage connected accounts.
- **[Scan Orchestration & Lifecycle](./scan-orchestration.md)** — how scans are queued, run, and tracked.
- **[Prowler Integration & Findings](./prowler-integration.md)** — how compliance findings are produced and grouped.
- **[Asset Inventory](./asset-inventory.md)** — the live catalog of cloud resources discovered by scans.
