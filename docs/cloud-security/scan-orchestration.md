---
title: "How Cloud Scans Run"
sidebar_label: "How Cloud Scans Run"
sidebar_position: 4
---

# How Cloud Scans Run

When you scan a connected cloud account, Offload Security breaks the work into many smaller jobs and runs them **in parallel across regions**. This keeps even large, multi-region accounts fast, and it lets you watch progress region by region instead of waiting for one long, opaque job. This page explains what a scan covers, how it executes, and how to read its status and progress.

## What a scan covers

Each scan looks at a single cloud account (AWS, GCP, or Azure) and does two main things in **every region** it covers:

- **Asset discovery** — builds an inventory of the resources running in that region (compute, storage, networking, IAM, and more). These feed your [Asset Inventory](./asset-inventory.md).
- **Compliance scanning** — runs security posture checks (powered by Prowler) against those resources to surface misconfigurations and policy violations. These become findings you can triage. See [Prowler Integration](./prowler-integration.md).

Alongside the per-region work, every scan also runs two **account-wide** discovery jobs once:

- **Kubernetes cluster discovery** — finds EKS, GKE, and AKS clusters in the account so they can be scanned in [Kubernetes Security](../security-scanning/kubernetes-security.md).
- **Container registry discovery** — finds ECR, GCR/Artifact Registry, and ACR repositories so their images can be scanned in [Container Security](../security-scanning/container-security.md).

:::note[Read-only, always]
Scans only ever **read** your environment using the read-only credentials you provided when [connecting the account](./connecting-accounts.md). Nothing is changed in your cloud.
:::

## Regions: what gets scanned

You can choose which regions to scan, or let the platform pick a sensible default based on the scan type:

| Scan type | Regions covered | When to use it |
|---|---|---|
| **Quick** | A single primary region (for example, `us-east-1` on AWS) | Fast smoke test or a first look. |
| **Full / Standard** | A curated set of major commercial regions per provider (around a dozen for AWS, fewer for GCP and Azure) | Your everyday, realistic multi-region posture scan. |
| **Incremental** | Same regional footprint as a full scan, but focused on what changed | Lightweight follow-up runs (used by daily schedules). |

If you have resources outside the default set, specify the exact regions you want when you start the scan — the platform will scan precisely those.

## How a scan executes

1. **You start a scan** from **Cloud Security** (or it's triggered by a schedule). The platform first checks that no other scan is already running for the same account in your team.
2. **Jobs are created** — one discovery job and one compliance job per region, plus the two account-wide discovery jobs.
3. **Jobs run in parallel.** Discovery and compliance work proceed side by side, and regions are processed concurrently. Compliance jobs are gently staggered so the scan stays within your cloud provider's API rate limits.
4. **Results stream in** as each job finishes — assets land in your inventory and findings appear in Cloud Security, so you don't have to wait for the entire scan to complete before reviewing early results.
5. **The scan reaches a final state** once all jobs have finished (see below).

:::tip[One scan per account at a time]
To avoid duplicate work and conflicting results, only one scan can run for a given cloud account within your team at a time. If you try to start another, the platform tells you a scan is already in progress and shows its ID and status.
:::

## Reading scan status and progress

Every scan shows an overall **status**, a **progress** indicator, and a per-region breakdown.

### Scan status

| Status | What it means |
|---|---|
| **Queued** | The scan has been accepted and is waiting to begin. |
| **Running** | Jobs are actively discovering assets and running checks. |
| **Completed** | Every job finished successfully. |
| **Partial** | Some jobs succeeded and some failed — you have usable results, but coverage is incomplete (for example, one region's checks failed). This is deliberately *not* shown as a clean "green" run so you know to look closer. |
| **Failed** | Every job failed (commonly a credentials or permissions problem). No usable results. |
| **Cancelled** | The scan was stopped before finishing. |

### Progress

While a scan is running you'll see:

- An **overall percentage** for the whole scan, plus separate progress for the **discovery** and **compliance** stages.
- An **estimated completion time**. This scales with how many regions you're scanning, so a full multi-region scan shows a longer estimate than a quick single-region one.

### Per-region detail

Because work is split by region, you can expand a scan to see each region's own **status** and **progress**, along with running counts of **assets discovered** and **findings** for that region. This makes it easy to spot, for example, that one region is lagging or that a specific region failed.

### Summary and warnings

When a scan finishes it reports a **summary**: total assets discovered, total findings, and a breakdown of findings by severity (**critical, high, medium, low**).

If the platform hits a permission gap or an API limit in your account, it surfaces a **warning** on the scan rather than failing silently — so a missing read permission shows up as an explicit note instead of a quietly incomplete result.

:::warning[A "Partial" result usually means permissions or limits]
The most common causes of partial scans are **missing read permissions** for a service or region, or **API rate limits** in your cloud account. Check the scan's warnings first, then revisit the IAM role or service account you set up when [connecting the account](./connecting-accounts.md).
:::

## Scheduled scans

You don't have to run scans by hand. The platform can keep posture current automatically:

- **Daily** — a lightweight **incremental** scan of your active accounts.
- **Weekly** — a complete **full** scan that re-runs all checks.

Scheduled runs honor the same "one scan per account at a time" rule and skip any account that was scanned very recently, so they never pile up. You can manage timing and other automated runs from the **Unified Scheduler**.

## Related

- [Connecting Cloud Accounts](./connecting-accounts.md) — set up the read-only access scans rely on.
- [Prowler Integration](./prowler-integration.md) — the compliance checks behind your findings.
- [Asset Inventory](./asset-inventory.md) — where discovered resources show up.
- [Account Management](./account-management.md) — manage your connected cloud accounts.
