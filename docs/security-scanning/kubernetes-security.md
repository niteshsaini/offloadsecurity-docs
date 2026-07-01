---
title: "Kubernetes Security"
sidebar_label: "Kubernetes Security"
sidebar_position: 4
---

# Kubernetes Security

Kubernetes Security scans your clusters for misconfigurations, insecure RBAC, risky workloads, and vulnerable images — then maps what it finds to the **MITRE ATT&CK Container Matrix** so you can see which attacker techniques your clusters are exposed to. It works across managed clusters (Amazon EKS, Google GKE, Azure AKS) and on-premises Kubernetes, using **read-only** access.

![Kubernetes Security cluster dashboard](/img/screenshots/kubernetes-security.png)

:::note Prerequisites (GCP/GKE)
GKE cluster discovery needs `roles/container.viewer` **plus** an in-cluster RBAC
`ClusterRole` (GCP IAM alone can't read workloads). See
**[Required Permissions (GCP)](../cloud-security/permissions.md)**.
:::

## What it does

- **Onboards clusters** with read-only credentials — a kubeconfig file or a service-account token — so the platform can talk to your API server without write access.
- **Runs a suite of best-in-class scanners** in one pass:
  - **kube-bench** — CIS Kubernetes Benchmark checks for control-plane and node configuration.
  - **Polaris** — workload best practices (resource limits, health probes, security context).
  - **Kubescape** — CNCF scanner covering the NSA-CISA Kubernetes Hardening Guidance, MITRE ATT&CK, and CIS frameworks.
  - **Trivy** — vulnerability and misconfiguration scanning for cluster resources and the images running in them.
- **Normalizes every result into findings** with a severity, the affected resource, and remediation guidance — deduplicated and scoped to your active team.
- **Maps findings to MITRE ATT&CK for Containers**, so each relevant finding shows the attacker technique it relates to and you get a coverage heatmap across your fleet.
- **Reports against compliance frameworks** — results roll up to CIS controls and cross-map to NIST 800-53, PCI-DSS, and SOC 2.

## How to use it

### 1. Onboard a cluster

1. Go to **Kubernetes Security** in the left navigation and select **Add Cluster**.
2. Give the cluster a **name** and pick its **environment** — Amazon EKS, Google GKE, Azure AKS, or On-Premises.
3. Choose how you'll connect:
   - **Kubeconfig file** — upload a kubeconfig that points at your cluster.
   - **Service Account Token** — paste a token for a read-only service account.
4. Choose an **access profile** for the platform's service account:
   - **Minimal (recommended)** — no access to Secrets or ConfigMaps.
   - **Extended** — additionally reads ConfigMap and Secret **metadata** (not values). Use only when you need that depth.
5. Save. The platform runs a **connectivity test** that confirms the API server is reachable, detects the Kubernetes version, and counts nodes and namespaces. On success, the cluster shows as connected and is ready to scan.

:::tip Least privilege
Onboard with **read-only** credentials and the **Minimal** access profile wherever possible. The platform never needs write access to your cluster — it only reads configuration and workload specs to assess posture.
:::

### 2. Run a scan

1. Open the cluster and select **Scan** (or **Start Scan**).
2. By default the platform runs **Trivy, kube-bench, Polaris, and Kubescape** together. You can choose a subset if you only need certain checks.
3. Optionally narrow the scan:
   - **Namespaces** — limit scanning to specific namespaces.
   - **Severity** — return only findings at or above a chosen severity (for example, Critical and High).
4. Start the scan. It runs in the background; the cluster view updates with status and a count of findings by severity when it completes.

:::note Large clusters
Scans are bounded by a per-scan API-call budget so they stay safe to run against big production clusters. Very large environments may take longer to complete.
:::

### 3. Read the findings

Open a completed scan to review its findings. For each finding you'll see:

- **Severity** — Critical, High, Medium, Low, or informational.
- **Affected resource** — the workload, namespace, node, or control-plane component involved.
- **Which scanner reported it** and the underlying check or control ID.
- **Remediation guidance** — what to change to resolve it.
- **MITRE ATT&CK technique** — where the finding maps to the Container Matrix, the related tactic and technique are shown so you can reason about it in attacker terms.

Use the **severity filters** to focus on what matters first, and the **MITRE ATT&CK coverage heatmap** to see which tactics and techniques your clusters are most exposed to across the fleet.

### 4. Track compliance and remediate

- Findings roll up to **CIS Kubernetes Benchmark** controls and cross-map to **NIST 800-53, PCI-DSS, and SOC 2**, so you can show control status to auditors.
- Significant findings can be promoted into the **Risk Register** and tracked to closure like any other finding. See **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)** for triage and SLA tracking.

## Prerequisites

:::note Before you onboard
- Network connectivity from the platform to your cluster's **API server**.
- A **read-only** kubeconfig or service-account token. For managed clusters, EKS/GKE/AKS clusters can also be auto-discovered from a connected cloud account — see **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)**.
- Confirm you're working in the correct **team** before onboarding or scanning — clusters and findings are scoped to your active team.
:::

## Related

- [Connecting Cloud Accounts](../cloud-security/connecting-accounts.md) — auto-discover EKS/GKE/AKS from connected accounts.
- [Container Security](./container-security.md) — scan the images that run in your clusters.
- [Vulnerability Management](../vulnerability-risk/vulnerability-management.md) — triage and track Kubernetes findings to remediation.
- [Getting Started](../getting-started.md) — sign in and learn the Scan → Finding → Risk → Report flow.
