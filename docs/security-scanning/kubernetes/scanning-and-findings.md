---
title: "Scanning & Findings"
sidebar_label: "Scanning & Findings"
sidebar_position: 2
description: "Run Trivy, Polaris and Kubescape against a cluster, see what each scan did not assess, compare two scans finding by finding, and triage findings across the fleet."
---

# Scanning & Findings

A cluster scan runs several engines in one pass and normalizes everything they report into findings with a severity, the affected Kubernetes resource, the scanner and check that produced it, and remediation guidance. Findings are deduplicated across runs, so a re-scan updates what you already triaged instead of creating duplicates.

## Run a scan

1. **Open Kubernetes Security → Clusters** and select **🚀 Scan** on a cluster card (or **🚀 Start Scan** on its dashboard).
2. **Choose scanners.** Trivy, Polaris and Kubescape are selected by default.
3. **Choose the scope:** all namespaces, or selected namespaces. Namespace scoping applies to Trivy and Kubescape; Polaris always assesses the whole cluster.
4. **Authorization & scope** (only if your deployment requires a recorded authorization): tick **I am authorized to test this target**, optionally with a reference and an *authorized until* date. It is recorded on the scan and kept on the cluster for later scans until that date. Leave it unticked to use the authorization already recorded on the cluster.
5. **Start Scan.**

To scan several clusters, tick them and use the bulk scan. The bulk scan does not ask for an authorization, so when one is required, start each cluster's first scan from its own 🚀 Scan. Scans also run on the schedule you set via **Schedule Scans** ([Scan Management & Scheduling](../scan-management.md)) and from the API (`POST /api/k8s/scan`).

| Engine | Version | What it assesses | Default |
| --- | --- | --- | --- |
| **Trivy** | 0.74.0 | Misconfigurations in workload objects and vulnerabilities in the images they run. | ✓ |
| **Polaris** | 10.1.8 | Workload best practices — resource limits, health probes, security contexts, image tags — at pod and controller level. | ✓ |
| **Kubescape** | 4.0.15 | All Kubescape controls (NSA-CISA, MITRE ATT&CK and CIS mappings) against live resources, from pinned offline framework artifacts. | ✓ |
| **kube-bench** | 0.7.0 | CIS node and control-plane checks. Selectable, but **always skipped as not applicable**: it must run on a node, and clusters here are scanned remotely. | — |

kube-hunter (active probing) is not offered in the scan settings and is not in the default scanner set used for automatic scans.

:::note[Kubescape fixed in 1.4.0]
Kubescape now runs its full control set (`allcontrols`) and reports each control's own severity. Earlier releases ran a smaller default set and rated every Kubescape finding Medium, so expect more Kubescape findings, and a spread of High, Medium and Low, after upgrading.
:::

A scan is bounded by a **per-scan API-call budget** (5,000 calls by default, `K8S_SCAN_MAX_API_CALLS`) so it is safe to run against large production clusters. Large clusters may also need a longer scanner time limit (`K8S_SCANNER_TIMEOUT_SECONDS`).

While it runs the card shows **Scanning**. The scan ends **complete**, **partial** (at least one scanner failed or was denied access — the cluster shows **Degraded**) or **failed**. A scanner that exits successfully but produces no output counts as failed, not as a clean result.

## What a scan does not cover {#not-covered}

Every scan records a **coverage** block that states what it did not assess, and nothing in it is counted as passed:

| Not tested | Why |
| --- | --- |
| **CIS sections 1–4** — control plane, etcd, node and kubelet configuration | Needs kube-bench on a node. Always not tested in 1.4.0. |
| Trivy node-level checks | Off: they would create a job in your cluster. Trivy still scans workload images and objects. |
| Checks of any scanner that failed | Named with its error. |
| Kubescape controls it skipped | Usually missing read access. |
| Namespaces the credential was denied | Open findings there are **not** auto-resolved. |

The coverage block also flags a Kubernetes version past upstream end of life. Managed control planes (EKS, GKE, AKS) are configured by the provider; their settings are not read.

To read it, open the cluster's dashboard: each recent scan has **Not tested in this scan** with the reason for each item. Compliance reports carry the same list under `scan_coverage`.

## What each scan records {#scan-record}

| Recorded | Detail |
| --- | --- |
| **Cluster identity** | The `kube-system` namespace UID, API server and version reached — see [Cluster identity](./onboarding-clusters.md#cluster-identity). |
| **Scanners** | Per scanner: image digest, the exact command (secret values redacted), options, Trivy database version and age. |
| **Raw output** | Each scanner's original output, kept in object storage with its SHA-256 — also when parsing failed. |
| **Credential** | Auth type, principal and fingerprint — never the secret. |
| **Authorization** | Who authorized the scan, or *authorization not recorded*. With `SCAN_REQUIRE_AUTHORIZATION=true`, a scan without a current authorization is refused before anything runs. |
| **What the scanner said** | The scanner's original severity (kept apart from any inferred one), plus evidence such as Trivy's message and cause, CVE package and fixed version, Kubescape failed and fix paths. |

## The cluster dashboard

Select **📊 Dashboard** on a cluster card, or a cluster on the Fleet Heatmap.

![Cluster dashboard for prod-aks-weu: security score 34/100 (grade F), findings summary by severity, and findings by category and by scanner](/img/screenshots/security-scanning/k8s-cluster-dashboard.webp)

- **Security Score** (0–100 with a letter grade) — derived from open findings weighted by severity. It shows **Not Assessed** until a scan in which a scanner produced output completes; a scan whose scanners all failed never grades a cluster.
- **Findings Summary** — open findings by severity, with a link to the Findings tab pre-filtered to this cluster.
- **Findings by Category** and **by Scanner** — where the risk sits and which engine reported it.
- **Recent Scans** — each scan's outcome and its **Not tested in this scan** list.
- **🚀 Start Scan** and **← Back** to the clusters.

## Working the findings

**Kubernetes Security → Findings** lists every finding across your clusters, grouped by check. Selecting a cluster card opens the same view filtered to that cluster.

![Findings tab: severity tiles (24 total, 4 critical, 7 high, 9 medium, 4 low), filters for cluster, severity, status and scanner, and the finding list with AI Summary](/img/screenshots/security-scanning/k8s-findings.webp)

Filter by **cluster**, **severity**, **status** (the default is **Open Only**) and **scanner**; the tiles above update to the filtered set. **AI Summary** produces a short narrative of what matters most in the current view. An empty list says why: *No clusters connected*, *Not scanned yet*, or no findings after a scan of a cluster in scope.

Each finding shows the severity, scanner, check ID, the **resource** (kind, name, namespace), first and last seen, a description and the **remediation**. Open one for the full detail, then act:

| Action | Result |
| --- | --- |
| **✅ Resolve** | Marks it resolved. If a later scan still reports it, the finding reopens — a resolve is a claim the next scan verifies. |
| **🔇 Suppress** | Hides it from the open view with a required **reason**, recorded with who suppressed it and when. Use for accepted risk (for example a system namespace you do not control). |
| **❌ False Positive** | Records that the check does not apply. |
| **🔄 Reopen** | Returns a non-open finding to open. |

:::tip[Start from the worst cluster]
Sort the fleet by severity on the Fleet Heatmap and work the critical findings of the worst production cluster first. Most Kubernetes criticals are a handful of root causes — privileged pods, cluster-admin bindings, public API endpoints — that clear many findings at once.
:::

## What happens between scans

- New failures open as findings with **first seen**. A finding that a previous scan auto-resolved and that recurs is reopened.
- A finding is auto-resolved only when the scanner that reported it succeeded in this scan and could have seen it again: within the scanned namespaces, outside any namespace the credential was denied, and within the severity filter.
- Your **Suppressed** and **False Positive** decisions persist across re-scans.
- When a scanner upgrade changes how a finding is identified, its first-seen date and your triage carry over to the new identifier.
- Findings feed the cluster's compliance scores ([Compliance & Fleet Posture](./compliance-and-fleet.md)), Vulnerability Management, and the security graph used by Attack Path Analysis.

### Workload exposure in the triage score

Kubernetes findings carry their workload's **exposure** into the triage score, from the cluster's running-workload snapshot: **exposed** (a LoadBalancer or NodePort Service, Ingress, external route, `hostNetwork` or `hostPort` reaches it), **not exposed**, **not running**, or **not evaluated**. Privileged workloads are recorded too. *Not evaluated* never lowers priority. See [Image Rollout — How this feeds triage](../containers/rollout.md#how-this-feeds-triage) and [Triage](../../vulnerability-risk/vulnerability-management/triage.md).

## Compare two scans {#compare-scans}

```
GET /api/k8s/scans/{scan_id}/compare?base={earlier_scan_id}
```

Compares a scan with an earlier one of the same cluster (by default the previous completed scan), finding by finding, from each scan's frozen findings (SHA-256 verified):

| List | Meaning |
| --- | --- |
| `new` | In the later scan, not in the earlier one. |
| `fixed` | Gone in the later scan **and** re-evaluated by it — its scanner succeeded, its namespace was in scope and not denied, its severity was in the filter. |
| `not_reevaluated` | Gone, but the later scan could not have seen it. Never counted as fixed. |
| `triaged` | Gone because someone suppressed or accepted it in between. |
| `persisting` | In both, including a finding carried to a new identifier. |

Lists are complete. The comparison is API-only in 1.4.0.

## Related

- [Onboarding Clusters](./onboarding-clusters.md) — before the first scan.
- [Compliance & Fleet Posture](./compliance-and-fleet.md) — scores, heatmap, frozen reports.
- [Scanning API](../api.md#kubernetes) — scan, poll and list findings over REST.
