---
title: "Identity & Network Posture"
sidebar_label: "Identity & Network Posture"
sidebar_position: 7
description: "Evaluate effective identity permissions (CIEM) on AWS, GCP and Azure, see where an analysis was incomplete, check AWS internet reachability, and export identity and network issues for the owning teams."
---

# Identity & Network Posture

Two tabs on the Cloud Security page take the same scan results and present them the way an identity team and a network team think about them. On top of the findings, two analyses run **daily per account** (identity analysis can also be started on demand): **identity analysis (CIEM)**, which works out who can actually do what from the policies themselves, and **network reachability**, which decides whether a resource can really be reached from the internet. Both only read your cloud, and both say plainly when part of an account could not be evaluated.

## IAM Analysis

**Where:** Cloud Security → **IAM Analysis**.

![IAM Analysis tab: Identity Coverage & Risk with 46 identities, findings by severity, identities coverage, and top identities by severity](/img/screenshots/cloud-security/iam-analysis.webp)

Read the tab top to bottom:

1. **Last-attempt notice.** An amber notice names each account whose last identity analysis **failed or completed only partly**, and how old the result being shown is. A failed or partial analysis never replaces the last complete one, so the older result stays on screen and the notice says so.
2. **Identity Coverage & Risk** — how many identities (IAM users and roles, GCP service accounts, Azure principals and managed identities) the platform knows about, how many have a current analysis, how many are scheduled and how many are not covered; findings by severity across identities, the **top identities by severity** and **coverage decay** (identities whose analysis is older than 30 days).
3. **CIEM evaluation coverage (AWS)** — per AWS account, how service control policies, permission boundaries and resource policies were handled, **N of M principals analysed**, and the principals that were not evaluated. See [What "Not evaluated" means](#what-not-evaluated-means).
4. **IAM Security Score** (0–10), computed from the density of open identity-category findings relative to the size of the account, and the **identity findings** list — the Findings tab filtered to the IAM category (MFA, key age, unused credentials, directly attached policies, and so on) — with **Export IAM findings as CSV**.
5. **Identity Analysis Actions** (below).

An identity's severity collapses its analysis flags into one tier: **critical** when it holds admin-level rights, **high** when it is over-privileged, otherwise its assessed risk. Identities that have not been used for a long time surface as **dormant**.

### Identity analysis actions

With more than one account, pick the account first. These actions **read** your cloud; none of them changes anything.

| Action | What it does |
| --- | --- |
| **Run IAM Analysis** | Runs the identity analysis for the account now, as a background job (the page waits for it). Results are persisted for the identity roster, the asset Security panel and the [attack graph](./attack-paths.md). It also runs automatically once a day for every account. |
| **Access Review** | Generates an access-review report for the account — who has what — for periodic recertification. |
| **Cleanup Unused** | Lists unused IAM resources (users, roles, access keys) with their last activity, as a **dry-run** recommendation set. Nothing is deleted. |

### How effective permissions are evaluated

Identity analysis evaluates access **from the policies**, not from role or policy names. An identity is *admin* because of what it can do, not because a policy is called `AdministratorAccess`.

| Cloud | What is evaluated |
| --- | --- |
| **AWS** | Every user's and role's identity policies (including group policies), with explicit Deny winning and wildcards expanded; **permission boundaries** and **service control policies** as caps on what a principal can do; the **resource policies** of data stores in the graph (S3, KMS, Secrets Manager, SQS, SNS, Lambda, DynamoDB, EFS); S3 Block Public Access before a bucket is called public. Unused roles and unused services for privileged principals come from IAM last-used data. |
| **GCP** | Project IAM merged with every folder and the organization above it; predefined and **custom** roles resolved to permissions; **IAM deny policies** subtracted; bucket and service-account IAM policies. Covers admin, data access and service-account impersonation. Grants to `allUsers` / `allAuthenticatedUsers` are treated as public. |
| **Azure** | Built-in and **custom** role definitions (actions, not-actions, data actions); assignments at subscription, resource-group and resource scope merged with those on parent **management groups**; **deny assignments** subtracted. Covers admin, data access and **managed-identity takeover** (run-command, extension or app-configuration writes on compute that runs as a managed identity). |

**Cross-account access (AWS).** When a data store's resource policy names a principal of **another AWS account onboarded in the same team**, that principal's access is evaluated with AWS's cross-account rule — both the identity policy and the resource policy must allow, an explicit deny in either wins, and the principal's own SCPs and boundary still apply. The resulting attack-graph edge is marked *cross-account*. Organization-wide shares are evaluated for onboarded accounts known to be in that organization; organizational-unit shares are listed on the store but OU membership is not read.

**Service control policies.** A member account cannot read its own SCPs. They are read through your organization's **management account** or a **delegated administrator for AWS Organizations**, onboarded in the same team with the Organizations read permissions in [Required Permissions](./permissions.md#identity-analysis-ciem). Without one, SCPs are shown as *not evaluated* with the account to onboard — they are never assumed to restrict anything.

**Time budget.** Each account is analysed under its own time budget (15 minutes by default). If it runs out, the run is marked partial and says how many principals were analysed — nothing is cut silently.

### What "Not evaluated" means

Any part that could not be read is marked **Not evaluated** with the reason (often the missing permission) — never shown as "no access":

- A principal whose policies could not be read completely is *not evaluated*, and the run is partial.
- An unreadable SCP chain, boundary, resource policy, deny policy or role definition is listed as *not evaluated*; the analysis continues without it, so uncertainty never shrinks reach.
- A run in which a whole part could not be read is recorded as **partial**: it is not scored and does not replace the last complete analysis.

:::note[Limits]
This is not a full IAM policy simulation. Conditions are flagged as *conditional* and listed, not simulated. Group membership is not expanded (Google groups, Entra groups — a grant to a group is shown on the group), and AWS session policies, resource control policies, S3 ACLs and access points, KMS grants, Azure PIM eligible assignments and Key Vault access policies are not evaluated. The CIEM evaluation coverage table covers AWS only.
:::

## Network Posture

**Where:** Cloud Security → **Network Posture**.

![Network Posture tab: unique network issues, critical/high and medium/low tiles, a low/score tile, and a list of network issues such as publicly accessible RDS and public EKS endpoints with affected resource counts](/img/screenshots/cloud-security/network-posture.webp)

### Network issues

The tab lists the **unique network-category checks** currently failing — public data stores, internet-open security groups and NSGs, public cluster endpoints, missing flow logs, HTTP listeners — each with the number of affected resources, regions and accounts, and its risk score. Filter by **cloud** and **account**; **Export CSV** hands the list to the network team. Each issue expands to the affected resources and console links exactly as on the Findings tab.

### Internet reachability

A security group open to `0.0.0.0/0` does not by itself make an instance reachable. The reachability analysis walks the actual path and gives each resource one of three verdicts — **reachable**, **not reachable** or **not evaluated** — with the hop-by-hop path or the blocking reason.

| Cloud | What is evaluated |
| --- | --- |
| **AWS** | The subnet's route table (longest-prefix match; only an internet gateway route counts — NAT, egress-only gateways, blackholes or no route block), the **network ACL** in both directions (ordered rules, ephemeral return ports), the **security group**, and **load balancers** (listener → rules → target group → target), so an instance with no public IP behind an internet-facing ALB or NLB is found. |
| **Azure** | Each public NIC through its **subnet NSG and its own NSG** (both must allow), matched to the NIC's addresses. |
| **GCP** | Instances with an external IP against the VPC firewall and the firewall policies in effect on the network. |

A verdict of *not reachable* is given only when the path is certain. Anything the model does not cover — transit gateway or peering routes, prefix-list sources, classic load balancers, API Gateway VPC links, CloudFront VPC origins — or a layer that could not be read gives **not evaluated**, which never lowers a resource's exposure.

Verified verdicts feed the [attack graph](./attack-paths.md) (a resource verified as not reachable is not used as an entry point) and the asset **Security panel** in [Asset Inventory](./asset-inventory.md) (*internet-reachable (verified)*).

The analysis refreshes **daily, one job per account**. The **Internet reachability refresh, per account** panel on this tab lists every account with when it was last refreshed and how the last attempt ended (completed, partial, failed, timed out, no credentials, not reached and so on), and counts accounts never refreshed or stale (over 48 hours) — so an account the refresh did not reach is visible instead of silently aging.

### Network analysis actions

| Action | What it does |
| --- | --- |
| **Firewall Audit** | Security-group / firewall-rule analysis for the selected account: overly permissive rules, unused groups, risky ports. |
| **Public Exposure** | Discovers internet-facing endpoints (public IPs, load balancers, exposed services) and classifies the high-risk ones. |
| **Segmentation** | Network topology discovery and segmentation assessment between VPCs / VNets / subnets. |

Results are summarized in a notification when the analysis finishes and feed the network findings list and the network posture score.

## How to use these tabs

1. **Identity team:** read the last-attempt notice and the CIEM evaluation coverage first — a partial analysis means the picture is incomplete. Then start with the *top identities by severity*: admin users without MFA and dormant service accounts are the fastest risk reduction available.
2. **Network team:** filter Network Posture to **Critical/High** — public data stores first, then internet-open management ports (22/3389). Check the reachability refresh panel for accounts that were not refreshed.
3. Track fixes through the [Remediation Queue](./remediation-queue.md) and confirm on the next scan.

## Related

- [Required Permissions](./permissions.md#identity-analysis-ciem) — the reads identity and reachability analysis need.
- [Reviewing & Triaging Findings](./findings.md) — the underlying findings and actions.
- [Attack Path Analysis](./attack-paths.md) — how identity and exposure combine into exploitable paths.
- [Asset Inventory](./asset-inventory.md) — per-asset exposure, identities with access, and encryption.
