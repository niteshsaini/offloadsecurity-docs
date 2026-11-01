---
title: "Onboarding Clusters"
sidebar_label: "Onboarding Clusters"
sidebar_position: 1
description: "Add EKS, GKE, AKS or other clusters with a read-only kubeconfig or GKE service-account key, connect clusters discovered on your cloud accounts, choose an RBAC profile, and test connectivity."
---

# Onboarding Clusters

A cluster is onboarded once, read-only, and can then be scanned on demand or on a schedule. There are two ways in: **add** a cluster with its credentials, or **connect** one the platform already discovered on a connected cloud account.

**Where:** Kubernetes Security → **Clusters**.

![Clusters tab: total / active clusters, critical findings and active scans tiles, and a card per cluster (prod-aks-weu, staging-gke-usc1, prod-eks-use1) with severity counts, last scan and Dashboard / Scan actions](/img/screenshots/security-scanning/k8s-clusters.webp)

## Before you start — RBAC profiles {#rbac-profiles}

The platform needs a Kubernetes identity that can **read** the resources it assesses. Rather than hand-writing a `ClusterRole`, pick a profile on the **RBAC Profiles** tab and generate the deployment script.

| Profile | Reads | Secrets | ConfigMaps | Use when |
| --- | --- | --- | --- | --- |
| **Minimal (recommended)** | Workloads (pods, deployments, daemonsets, statefulsets, jobs), nodes, namespaces, services, RBAC objects, network policies, ingresses and routes | **No access** | **No access** | Almost always. |
| **Extended** | Everything in Minimal | **No access** | **Read** (`get` / `list`, including contents) | Only after your own review: the scanners can read every ConfigMap's contents. |

![RBAC Profiles tab: Minimal (recommended) vs Extended profile cards with security level, and the Minimal profile's permission grant list](/img/screenshots/security-scanning/k8s-rbac-profiles.webp)

Select **Generate Deployment Script**, choose the profile, the **namespace** and the **service account name**, and copy or download the script. Run it with a `kubectl` context that has cluster-admin: it creates the namespace if needed, applies the service account, `ClusterRole` and binding, creates a long-lived service-account token Secret (falling back to a bound token only if the token controller is disabled), and prints the **API server URL and token**. The same `ClusterRole` is listed in [Required Permissions — Bucket B](../../cloud-security/permissions.md#bucket-b--kubernetes-in-cluster-rbac).

![Deployment Script dialog: profile, namespace and service account, the generated bash script, and usage instructions with copy/download](/img/screenshots/security-scanning/k8s-rbac-script.webp)

The platform needs a **kubeconfig**, not a bare token. Put the printed values into a self-contained kubeconfig before onboarding:

```yaml
apiVersion: v1
kind: Config
clusters:
- name: prod
  cluster:
    server: https://10.20.0.5:6443          # API server URL the platform can reach
    certificate-authority-data: <base64 CA>  # from your current kubeconfig
users:
- name: offload-scanner
  user:
    token: <token printed by the script>
contexts:
- name: prod
  context: { cluster: prod, user: offload-scanner }
current-context: prod
```

:::tip[Cloud IAM is not enough]
An AWS/GCP/Azure role lets the platform **discover** EKS/GKE/AKS clusters, but reading workloads inside a cluster always needs Kubernetes RBAC. Apply the profile before you onboard. The profile you choose on the cluster is what the connection test checks; what a scan can actually read is decided by the RBAC you applied.
:::

## Add a cluster

Select **➕ Add Cluster** and fill in:

![Add Kubernetes Cluster dialog: cluster name, optional project, cloud provider (Amazon EKS, Google GKE, Azure AKS, On-Premises, Other), and onboarding method (Kubeconfig File, Service Account Token, Service Account)](/img/screenshots/security-scanning/k8s-add-cluster.webp)

| Field | Notes |
| --- | --- |
| **Cluster name** | How it appears in dashboards, e.g. `production-eks`. Must be unique in the team. |
| **Project** (optional) | Groups clusters in the list, e.g. `payments-platform`. Clusters without one appear under **Ungrouped**. |
| **Cloud provider** | Amazon EKS, Google GKE, Azure AKS, On-Premises or Other. |
| **Onboarding method** | **Kubeconfig File**, **Service Account Token** or **Service Account**. Recorded with the cluster; in every case the credential below is what the platform connects with. |
| **RBAC Profile** | Minimal or Extended, matching what you applied. |
| **Credentials (Base64 Encoded)** | A self-contained kubeconfig, base64-encoded on one line (`base64 -w 0 kubeconfig.yaml`; on macOS `base64 -i kubeconfig.yaml`). For **GKE**, a GCP service-account JSON key with `roles/container.viewer` instead — a fresh token is minted for every scan. |
| **API Server URL** (optional) | The cluster's API endpoint. |
| **GKE location / GKE cluster name** (GKE, optional) | Tell the platform which GKE cluster the service-account key is for. Alternatively give its API server URL, or name the cluster exactly as in GKE. |

On save, select 🔗 on the cluster card to run the **connectivity test**: it reaches the API server, records the Kubernetes version, counts nodes and namespaces, and checks list access to pods, deployments, services, namespaces, nodes, roles, cluster roles and network policies (plus ConfigMaps for Extended). The cluster shows **Pending** until its first scan, and a **weekly scan is scheduled automatically**.

:::warning[Kubeconfig safety]
Kubeconfigs are validated before they are stored. A kubeconfig that uses an `exec:` sign-in plugin (the default from `aws eks update-kubeconfig` and `gcloud container clusters get-credentials`), a `cmd` or `tokenFile` token source, or `insecure-skip-tls-verify: true` is refused. A `server` that points at loopback, link-local or a cloud-metadata address is refused; private cluster endpoints are allowed. Credentials are encrypted at rest.
:::

Stored cluster credentials expire after **90 days** by default. Replace them before then (see [Managing clusters](#managing-clusters)).

To onboard many clusters at once, use `POST /api/k8s/clusters/bulk-import` (API only, up to 200 per request, with optional paced first scans).

## Connect discovered clusters

Every cloud scan discovers the EKS, GKE and AKS clusters in the account, in the regions the scan covers ([how cloud scans run](../../cloud-security/scan-orchestration.md#what-happens-during-a-scan)). On the Clusters tab, **🔍 Discovered on your cloud accounts — not connected** lists them, each marked **Discovered — not connected**.

1. Select **🔗 Connect cluster** on the one you want.
2. **GKE:** the cluster reuses the discovering account's service account and is usually scannable at once.
3. **EKS and AKS:** the cluster shows **No credentials** until you add a kubeconfig — open its Edit dialog (✏️) and paste it under **Replace credentials**.

**🔄 Rescan for new clusters** re-runs discovery to find clusters created since the last cloud scan.

When discovery could not run for an account — for example *"discovery not permitted: missing eks:ListClusters in us-east-1"*, or discovery has not run yet — the Clusters and Coverage tabs show a notice naming the affected accounts and where to fix it, with actions to run discovery for one account or all of them. Discovery never deletes a cluster it stops seeing; it is counted as no longer found.

## Managing clusters {#managing-clusters}

The tiles above the list count the whole fleet: **Connected Clusters** (with how many are discovered but not connected), **Scanned** (healthy, degraded, error, never scanned), **Critical Findings** (open, on scanned clusters) and **Scans Running**.

Each cluster card shows provider, status (**Active**, **Pending**, **Scanning**, **Degraded**, **Error**), findings by severity and the last scan time. Select the card, or a severity count, to open its findings. A box under the card names the problem when the last test or scan failed — see [Troubleshooting](../troubleshooting.md#kubernetes).

| Action | What it does |
| --- | --- |
| **📊 Dashboard** | Opens the cluster's own view — security score, findings by category and scanner, recent scans and what each did not test. See [Scanning & Findings](./scanning-and-findings.md#the-cluster-dashboard). |
| **🚀 Scan** | Opens the scan settings and starts a scan. |
| **🔗** | Re-runs the connectivity test. |
| **✏️ Edit** | Change name, project, RBAC profile; **Replace credentials** (the new kubeconfig must reach the same API server); **Reset cluster identity**. |
| **Delete** | Removes the cluster with its findings, scans and schedules. Its scans and findings are kept as tombstones until retention purges them, so the evidence is not erased at once. |

Tick several cards (only clusters with credentials can be selected) to scan or delete them in bulk. A bulk scan of more than five clusters asks you to confirm, and the scans are staggered.

### Cluster identity {#cluster-identity}

On every scan the platform reads the cluster's identity (the `kube-system` namespace UID, API server and version) before any scanner runs. The first scan pins it. If a later scan reaches a **different cluster** — for example a kubeconfig now points elsewhere — the scan is refused so another cluster's findings never land on this record. If the cluster was rebuilt, select **Reset cluster identity** on the card or in the Edit dialog; the next scan pins the new cluster.

## Related

- [Scanning & Findings](./scanning-and-findings.md) — run scans and work the results.
- [Connecting Cloud Accounts](../../cloud-security/connecting-accounts.md) — where discovered clusters come from.
- [Troubleshooting](../troubleshooting.md#kubernetes) — connection tests that fail, scans that stay pending.
