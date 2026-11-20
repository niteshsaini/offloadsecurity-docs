---
title: "Cloud Asset Inventory"
sidebar_label: "Asset Inventory"
sidebar_position: 10
description: "A live, normalized catalog of every resource discovered across your AWS, GCP and Azure accounts — searchable, filterable, exportable, and the map that Attack Path Analysis is built on."
---

# Cloud Asset Inventory

Asset Inventory is the searchable catalog of everything you run in the cloud. Every scan's discovery jobs feed it, so once accounts are connected it fills itself — across **AWS, GCP and Azure**, every scanned region, with no agents to install. It is also the foundation the rest of Cloud Security builds on: public-exposure and encryption summaries, and [Attack Path Analysis](./attack-paths.md), all read from the same inventory.

**Where:** left navigation → **Asset Inventory** (under *Cloud & Infrastructure*).

![Asset Inventory overview: 124 total assets, 43 high risk, 32 public, 78% encrypted, and asset distribution per cloud provider by category](/img/screenshots/cloud-security/asset-inventory-overview.webp)

## What it does

- **Multi-cloud discovery** — resources from all connected accounts, discovered with the same read-only credentials used for scanning.
- **One normalized shape** — name, type, service, account, project, region, status, tags and metadata, whichever cloud they came from, so AWS, GCP and Azure sit side by side in one table.
- **Categories** — every resource lands in a functional bucket for reporting:

  | Category | Examples |
  | --- | --- |
  | **Compute** | EC2, Compute Engine, Azure VMs, ECS/EKS/GKE/AKS nodes |
  | **Storage** | S3, EBS/EFS, Cloud Storage, Persistent Disk, Storage Accounts, Managed Disks |
  | **Database** | RDS, DynamoDB, ElastiCache, Cloud SQL, Firestore, Azure SQL, Cosmos DB |
  | **Network** | VPCs, security groups, load balancers, CloudFront, VNets, NSGs |
  | **Security** | IAM, KMS, Certificate Manager, Key Vault, Entra ID |
  | **Serverless** | Lambda, API Gateway, Cloud Functions, Cloud Run, Azure Functions |
  | **Containers** | ECR, Artifact Registry, ACR, ECS/EKS/GKE clusters |
  | **Management** | CloudFormation, Systems Manager, Deployment Manager, ARM |

- **Security at a glance** — headline counts of **total assets**, **high-risk assets**, **public assets** and the share of encryptable assets that is **encrypted at rest** (see [Encryption at rest](#encryption-at-rest)).
- **Untagged resources included** — on AWS, discovery also lists untagged EC2 instances, security groups, volumes, VPCs, RDS instances and Lambda functions, which the tagging API alone would miss.
- **Change tracking** — each asset records when it was **first discovered** and **last seen**. Re-discovery updates assets in place (no duplicates) and refreshes *last seen*, so you can tell what is new and what may have gone away.
- **Export** — download every asset matching the current search and filters as CSV.

## Asset Overview

The **Asset Overview** tab summarizes your estate: the headline tiles, **Asset Distribution by Cloud Provider** (per-provider counts by category) and one card per connected account with its asset count and last discovery time, plus **Refresh Assets** to re-run discovery for that account.

Click a tile (Total, High Risk, Public, an encryption state, or a provider / category) or **View Assets** on an account card to open **Detailed Inventory** with that filter applied.

| Tile | How it is counted |
| --- | --- |
| **High Risk** | Assets with failing critical or high cloud findings. |
| **Public Assets** | Assets with a failing finding whose check mentions public, internet, anonymous or `0.0.0.0/0` exposure — a keyword match, not a network test. For a verified answer, see the asset's Security panel below. |
| **Encrypted at rest** | Encrypted ÷ encryptable assets that were assessed — see [Encryption at rest](#encryption-at-rest). |

A tile that reads **—** with *Summary unavailable*, *being computed* or *Not evaluated* means the number is not known; a 0 is only shown when the count was actually measured.

Discovery runs as a background job and typically finishes in a few minutes; the tiles and table update when it completes. You do not normally need to refresh by hand — every scheduled scan refreshes the inventory.

## Detailed Inventory

![Detailed Inventory: search and filters (account, provider, status, category, region) above a sortable table of assets with account, project, type, provider and region](/img/screenshots/cloud-security/asset-inventory-table.webp)

Switch to **Detailed Inventory** for the full list. The table shows **Asset** (name and native ID), **Account**, **Project**, **Type**, **Provider**, **Region**, **Status** and **Last Seen**; every column sorts.

Narrow it with **search** (name, native ID, type, region, project or account name), and the **Account**, **Provider**, **Status**, **Category** and **Region** filters. Search, filters and sorting cover the whole inventory, not just the page on screen; the heading shows *(N assets match)*. Sorting by Account sorts by account ID, not the name shown.

Select a row to expand it: native ID, project, service, discovery method, **Discovered At**, **Last Seen**, its **encryption at rest**, the **Security** panel (below), the cloud **tags**, and the raw metadata the provider returned (for example instance type, VPC, public and private IPs).

**Export CSV** downloads **every** asset that matches the current search and filters, across all pages, with the columns *Name, Account, Account ID, Project, Provider, Type, Service, Region, Status, Native ID, Asset ID, Last Seen, Discovered At* — ready for a CMDB reconciliation or an auditor's asset-scope request. If an export stops part-way, the file ends with a line starting `# EXPORT INCOMPLETE`; export again.

### The Security panel

The expanded row's **Security** panel collects everything security-related about that one resource: the highest triage priority and risk score, internet exposure, findings past their SLA, open counts by severity, the business context and owners; then its findings, cloud misconfigurations, open vulnerabilities, **identities with access**, what it runs as, what it can reach, and the compliance controls linked to its findings. Each list shows its first 8 entries and *…and N more*.

- **internet-reachable (verified)** means [network reachability](./identity-and-network.md#internet-reachability) confirmed a route from the internet; **internet-reachable** alone comes from public-exposure signals; **not in attack graph yet** means exposure and identities are not known yet.
- **Identities with access** is filled only after identity analysis has run for the account.

## Encryption at rest

Discovery records whether each **encryptable** resource is encrypted at rest, with which kind of key:

| Cloud | Resources assessed |
| --- | --- |
| **AWS** | S3 buckets, EBS volumes, RDS instances and clusters, EFS, DynamoDB, SQS, SNS — with AWS-managed vs customer-managed KMS keys distinguished. |
| **GCP** | Resources whose Cloud Asset Inventory record states customer-managed (CMEK) vs Google-managed encryption. |
| **Azure** | Storage accounts, managed disks and Cosmos DB. |

The **Encrypted at rest** card shows the percentage of *assessed* encryptable assets that are encrypted, with *N of M encryptable assets assessed*. It reads **Not assessed** when nothing could be assessed, and its **Encrypted assets**, **Unencrypted assets** and **Encryption not assessed** counts each open the matching list. The expanded row shows the status, key type, key ID, algorithm and, when not assessed, why.

A resource whose encryption could not be read — for example a denied permission — is shown as **Not assessed** with the reason, never as unencrypted. The reads involved are listed in [Required Permissions](./permissions.md#encryption-at-rest-and-exposure).

## How it feeds Attack Path Analysis

Discovered resources become the nodes of the security graph: **cloud resources** (and whether they are internet-reachable), **identities**, **data stores** and **network controls**. Findings and vulnerabilities attach to those nodes, and Attack Path Analysis then looks for chains from an internet-exposed entry point to a sensitive target. A more complete inventory means more accurate paths — see [Attack Path Analysis](./attack-paths.md).

## Good to know

:::note[Team scope]
The inventory shows assets discovered for your **active team**. Switch teams from the account menu if you expect different resources.
:::

**New resources** appear after the next discovery of their account. Trigger **Refresh Assets** on that account if you cannot wait for the schedule.

**Deleted resources** are marked deleted when a cloud scan of their account completes successfully and no longer sees them (on AWS, only for the regions that scan covered), disappear from the list and counts, and are purged 30 days later. **Refresh Assets** does not remove deleted resources, and a failed or partial scan removes nothing. Deleted assets can be listed over the API with `GET /api/unified-cloud-security/assets?status=deleted`.

**Short-lived resource types** — compute snapshots, Kubernetes pods, ReplicaSets and Jobs, Cloud Run executions and similar — are not stored at all.

## Related

- [Connecting Cloud Accounts](./connecting-accounts.md) — populate the inventory.
- [Running Cloud Scans](./scan-orchestration.md) — how discovery jobs run and are scheduled.
- [Attack Path Analysis](./attack-paths.md) — what the inventory makes possible.
