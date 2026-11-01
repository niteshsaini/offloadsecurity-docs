---
title: "Compliance & Fleet Posture"
sidebar_label: "Compliance & Fleet Posture"
sidebar_position: 3
description: "Score every cluster against CIS, NIST 800-53, PCI DSS and SOC 2, keep each scan's frozen compliance reports, compare the fleet by severity and MITRE ATT&CK tactic, and read coverage including discovered clusters."
---

# Compliance & Fleet Posture

Three tabs turn cluster findings into the views auditors and platform leads ask for: **Compliance** scores each cluster per framework, **Fleet Heatmap** compares all clusters side by side — by severity and by the MITRE ATT&CK tactics your findings map to — and **Coverage** shows which clusters are assessed at all.

## Compliance

**Where:** Kubernetes Security → **Compliance**.

![Compliance tab: 3 clusters across 4 frameworks, average score 88%, 3 compliant clusters, 0 at risk, and a per-cluster table with grade, overall score and per-framework scores](/img/screenshots/security-scanning/k8s-compliance.webp)

### How scores are built

Each engine's checks are mapped to controls in four frameworks — **CIS Kubernetes Benchmark**, **NIST 800-53**, **PCI DSS** and **SOC 2** (HIPAA is available over the API). For each cluster and framework the platform evaluates the mapped controls against the cluster's open findings:

- A control **fails** when a critical or high finding maps to it, and is **warned** for lower severities.
- A control **passes** only when no open finding maps to it **and** a scanner that evaluates it actually ran. Nothing passes by absence alone.
- A control or requirement that no scanner evaluated is **not assessed**. This always includes **CIS sections 1–4** (control plane, etcd, node and kubelet configuration), which need kube-bench on a node — see [What a scan does not cover](./scanning-and-findings.md#not-covered). Manual CIS controls are not scored.

The score is the pass ratio of the assessed controls; the **overall score** is the average across frameworks and drives the letter grade.

| Band | Meaning |
| --- | --- |
| **Compliant** | Overall score 80% or above |
| **At risk** | Below 70% |

Clusters between 70% and 80% count as neither — they are the ones to schedule fixes for before they slip.

A cluster whose scans have never produced a result from any scanner is **Not Assessed** rather than scored, and a framework where nothing was assessed has no score. The platform never presents an unscanned cluster as compliant. Scores refresh automatically after each scan; **Refresh** recomputes on demand.

### Reading the table

One row per cluster: **grade**, **overall score**, and a score per framework. Expand a row to see each framework's score with passed, failed and warned counts, then:

- **Generate Report** (or **Refresh**) for a framework — a structured report with controls total / passed / failed / warned / not assessed, grouped into the framework's **control sections** (for CIS: "5.1 RBAC and Service Accounts", …), each failed control listing the findings behind it. The report includes a **scope and coverage** section: the cluster identity reached, whether the scan was partial, end-of-life Kubernetes versions, and the not-tested list.
- **View Details** — open the current report; **Export JSON** from there for evidence or downstream tooling. HTML and PDF renderings are available over the API.

### Frozen per-scan reports {#frozen-reports}

Every scan that is not a complete failure freezes its CIS, NIST, PCI DSS and SOC 2 reports as the **point-in-time record** of that scan. Unlike the live scores above, a frozen report never changes when findings are later resolved or suppressed. Each one holds:

- a **scan manifest** — scanners and versions, scanner image digests, the SHA-256 of each raw output, the Trivy database, the cluster identity, the credential used (type, principal, fingerprint — never the secret) and who authorized the scan;
- a **coverage statement** — partial or not, what was not tested, how many findings were evaluated;
- the **exact findings graded**, stored compressed with their SHA-256.

| Task | Endpoint |
| --- | --- |
| List a cluster's frozen reports | `GET /api/k8s/compliance/history/{cluster_id}?framework=&limit=&skip=` |
| Open one exactly as issued | `GET /api/k8s/compliance/reports/{report_id}?format=json\|html\|pdf` |

Frozen reports are API-only in 1.4.0 and are removed with the compliance retention period.

Every compliance export downloaded over the API — live or frozen — carries its SHA-256 in the `X-Content-SHA256` header and is recorded, so the file can be verified later with `GET /api/native-scans/exports/verify?sha256={hex}`.

:::tip[Evidence for an audit]
For each production cluster, take the frozen CIS and SOC 2 reports of the weekly scan and attach them to the control in [Evidence Hub](../../compliance/evidence-hub.md). They carry the scan, the cluster identity, what was not tested and the exact failing findings — what auditors ask for.
:::

## Fleet Heatmap {#fleet-heatmap}

**Where:** Kubernetes Security → **Fleet Heatmap**.

![Fleet Heatmap: severity tiles across clusters, a cluster × severity matrix (prod-aks-weu, staging-gke-usc1, prod-eks-use1) and the MITRE ATT&CK container tactic coverage row](/img/screenshots/security-scanning/k8s-fleet-heatmap.webp)

- **Severity tiles** — critical / high / medium / low totals and how many clusters each affects.
- **Cluster matrix** — every cluster with its provider and status and the count per severity, sorted so the worst cluster is on top, with search and paging. Select a cluster to open its dashboard, or a severity count to open those findings.
- **MITRE ATT&CK tactic coverage** — the eleven tactics in kill-chain order (Initial Access through Impact). A tactic lights up when at least one open finding in the fleet maps to a technique under it, so you can see, for example, that *Privilege Escalation* and *Credential Access* are exposed while *Exfiltration* is not.

Use the heatmap for the weekly platform review: which cluster regressed, which tactic newly lit up, and whether the staging cluster's posture is drifting from production's.

## Coverage {#coverage}

The **Coverage** tab (the landing tab) applies the same coverage model as Cloud Security, over **one list of clusters**: the clusters you connected plus the clusters discovered on your cloud accounts but not connected.

- **Scanned**, **scheduled** and **not covered** clusters, findings by severity, and the top clusters by severity. Discovered clusters are labelled in *Not Covered* — they are never counted as covered and have no scan action until you [connect them](./onboarding-clusters.md#connect-discovered-clusters).
- **Missing sources** — each source the count may be missing (for example a cloud account where discovery has not run or lacks a permission) is named, with where to fix it. While any is missing, the total is marked partial.
- **Coverage decay** — clusters whose last scan is 30 days old or more.

Fleet views are not silently truncated: the compliance posture and coverage count the whole fleet.

## Related

- [Scanning & Findings](./scanning-and-findings.md) — the findings behind the scores; compare two scans.
- [Compliance Dashboard](../../compliance/compliance-dashboard.md) — the organisation-wide framework view that includes Kubernetes controls.
- [Scan Management & Scheduling](../scan-management.md) — keep scores current with recurring scans.
