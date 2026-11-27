---
title: "Reviewing & Triaging Findings"
sidebar_label: "Findings & Triage"
sidebar_position: 4
description: "Work cloud posture findings grouped by check: filter, open affected resources, jump to the console, resolve, suppress with an expiry, hand off as a task, and export."
---

# Reviewing & Triaging Findings

The **Findings** tab is the working surface for cloud findings. Instead of a flat list of every failing resource, findings are **grouped by check** — one row for "S3 bucket has public access enabled" with its five affected buckets underneath — so you make one decision per problem, not per resource.

**Where:** Cloud Security → **Findings** (called *Scanning* before release 1.4.0). Clicking an account card on the **Accounts** tab opens this tab already filtered to that account.

![Security Findings Dashboard: 103 findings grouped into 35 unique checks (67% noise reduction), severity tiles, filters, and grouped finding cards with Resolve All / Suppress / Fix actions](/img/screenshots/cloud-security/findings-dashboard.webp)

## The dashboard at a glance

- **Header line** — how many raw findings collapsed into how many unique checks, and the resulting *noise reduction*.
- **Tiles** — unique issues, and counts of critical / high / medium / low findings with the change since the previous scan. A note under the tiles says how many findings come from [custom policies](./custom-policies.md), or that the counts cover Prowler checks only when custom-policy findings could not be read.
- **Filters** — search, cloud, account, severity, category, framework and status (below).
- **Finding cards** — one per check, sorted by severity, each with a **Risk Score** (0–10, derived from severity), the service, how many regions and resources are affected, and how many accounts. Cards raised by a custom policy carry a **Custom policy** badge with the policy name.
- **CSV / Excel** — export exactly what the current filters show (see [Export](#export)).

## Filtering

| Filter | Options |
| --- | --- |
| **Cloud** | AWS, GCP, Azure |
| **Account** | Any connected account |
| **Severity** | Critical, High, Medium, Low, Info |
| **Category** | IAM, Network, Storage, Compute, Logging, Encryption |
| **Framework** | CIS Benchmarks, NIST 800-53, SOC 2, PCI-DSS, HIPAA, GDPR — shows only checks mapped to that framework |
| **Status** | **Failed Only** (default), Passed Only, Resolved, Suppressed |
| **Search** | Matches the check title, description or resource names |

The account filter is kept in the URL (`?tab=orchestration&account=…`), so a filtered view can be bookmarked or shared.

:::tip[Start with Critical + one account]
On a first pass, filter to **Critical** and a single production account. The critical list is short and every item is worth a decision today. Widen to High once the criticals are resolved or suppressed with a reason.
:::

### Findings under a risk exception

In the default view (failed findings), findings covered by an approved **risk exception** in Vulnerability Management are left out of the list and its counts. A line above the list says how many are hidden, so the total is never silently smaller.

## Reading a finding

Expand a card to see **what failed, why it matters and how to fix it**: the check description, the remediation text with a link to the provider's documentation, and the compliance controls the check maps to.

Select **N instances** (or *Click to list affected resources*) to open the **affected resources** — each with its resource name, account, region, the per-resource detail from the scanner, and a **Console** link that opens that exact resource in the AWS, GCP or Azure console.

![A finding expanded to show affected instances — bucket name, account, region and an Open-in-console link per resource](/img/screenshots/cloud-security/findings-instances.webp)

## Acting on a finding

Every card raised by a Prowler check offers three actions. **Resolve All** and **Suppress…** apply to **every instance of the check in every region** for the selected scope, so you triage the problem once.

| Action | What it does | When to use it |
| --- | --- | --- |
| **Resolve All** | Marks the finding resolved with a note. If a later scan still reports the failure, the finding **reopens** automatically — a resolve is a claim the next scan verifies. | You have fixed it (or are about to). |
| **Suppress…** | Hides the finding for a chosen window with a **reason**. When the window ends it returns to *failing* on the next scan, so accepted risks are re-examined rather than forgotten. | Accepted risk, false positive, compensating control. |
| **Fix** | Creates a **remediation task** for one affected resource you pick, with assignee, priority, due date and notes. The task appears in the [Remediation Queue](./remediation-queue.md). | Someone else owns the fix and you want to track it. |

![Suppress Finding dialog with a reason field and a duration picker (7 days to 1 year, or permanent), noting that suppression applies to every instance of the check](/img/screenshots/cloud-security/findings-suppress-dialog.webp)

Suppression windows: **7, 14, 30 (recommended), 60, 90, 180 days, 1 year**, or **permanent**. A suppressed finding shows under the *Suppressed* status filter with its reason and expiry; **Un-suppress** lifts it early.

Cards raised by a **custom policy** do not offer these buttons: those findings are triaged in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx), or changed by editing or disabling the policy under **Custom Policies**. The card says so.

:::warning[Resolve is not delete]
Resolving does not change your cloud. If the misconfiguration is still there on the next scan, the finding comes back as open. To make a finding go away for good, fix the resource — or suppress it with a documented reason.
:::

## Export

**CSV** and **Excel** download the findings matching every current filter (including Framework), one row per affected resource, with its resolved name, type, account, region and the check that failed. Custom-policy findings are included.

- In the default view, findings under an approved risk exception are left out; the file's closing note says how many.
- At most **50,000 rows** per export. A larger export says so in the file (the total and a closing note row) rather than stopping silently.
- If the download fails, the error is shown in a message.

The **IAM Analysis** and **Network Posture** tabs have their own *Export … as CSV* buttons for their findings.

## What happens between scans

- **New failures** open as findings with the time they were first detected.
- **Failures no longer reported** are auto-resolved and show under *Resolved* with the scan that closed them — but only for checks the scan actually evaluated. A check that errored, was denied access or returned *manual* leaves its findings open.
- **Your decisions survive re-scans.** Resolved and suppressed findings keep their status; a scan that returns no data at all is treated as unverified and changes nothing.
- **Trend tiles** compare the current counts with the previous run so a regression is visible at a glance.

## Where else findings show up

- **Compliance tab and Compliance Posture** — pass/fail per framework are computed from these findings ([Compliance & Benchmark Checks](./prowler-integration.md)).
- **Network Posture** and **IAM Analysis** — network- and identity-category findings are re-cut by exposure and identity ([Identity & Network Posture](./identity-and-network.md)).
- **Vulnerability Management triage** — cloud findings feed the unified views used for SLAs, risk scoring and reporting ([Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx)). When a resource's own tags name the infrastructure-as-code that owns it (Yor `git_*` tags, CloudFormation stack tags, Pulumi project/stack tags, or `managed_by` / `iac_repo` / `terraform_module`), the triage view shows an **IaC** chip such as *IaC: terraform · acme/infra:modules/s3/main.tf*, so the fix goes into code instead of the console. Nothing is inferred beyond the tags, and the chip is shown in triage only, not on this tab.
- **Reports** — a run's [point-in-time report](./point-in-time-reports.md) and the executive and compliance reports draw from the same data ([Reports & AI](../reports-and-ai/index.md)).

## Related

- [Running Cloud Scans](./scan-orchestration.md) — how findings are produced and refreshed.
- [Custom Cloud Policies](./custom-policies.md) — your own checks.
- [Remediation Queue](./remediation-queue.md) — tracking the tasks created with **Fix**.
- [Cloud Security API](./api.md#findings) — the same list, filters and actions over the API.
