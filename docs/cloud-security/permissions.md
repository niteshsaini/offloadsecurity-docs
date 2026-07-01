---
title: "Required Permissions (GCP)"
sidebar_label: "Required Permissions (GCP)"
sidebar_position: 1.5
description: "The exact GCP APIs and IAM roles Offload Security needs to onboard Cloud/CSPM, Asset Inventory, Kubernetes (GKE), Container Registries, and Cloud Events."
---

# Required Permissions (GCP)

Most onboarding problems are **missing permissions**, not bad configuration. This
page lists **exactly** what Offload Security calls so you can grant it up front —
all **read-only**, except the one-time Cloud Events setup.

Think of it as **three buckets** — you don't need all of them for every feature:

| Bucket | What it is | Where it's granted |
| --- | --- | --- |
| **A. Read-only scanning** | Asset Inventory, Cloud/CSPM, Kubernetes, Container Registries | IAM roles on the **service account**, bound at the **org node** so they inherit to every project |
| **B. Kubernetes in-cluster RBAC** | Reading workloads/RBAC/network policies inside a cluster | A Kubernetes `ClusterRole` bound **inside each cluster** (GCP IAM ≠ Kubernetes RBAC) |
| **C. Cloud Events setup** | Streaming Cloud Audit Logs to Offload Security | **One-time** create of a log sink + Pub/Sub topic + subscription |

:::info Org-level = grant once, covers everything
Binding the roles on the **organization** node makes them apply to all current
**and future** projects, so new projects onboard automatically. Org-node
bindings require an **Organization Admin**. Every table below also works at
project scope if you prefer to onboard one project at a time.
:::

---

## Step 0 — Enable the APIs

Enable these on each project you want to scan (or org-wide):

```bash
gcloud services enable \
  cloudasset.googleapis.com cloudresourcemanager.googleapis.com \
  compute.googleapis.com iam.googleapis.com storage.googleapis.com \
  logging.googleapis.com monitoring.googleapis.com securitycenter.googleapis.com \
  container.googleapis.com artifactregistry.googleapis.com pubsub.googleapis.com
```

---

## Bucket A — Read-only scanning roles

Grant these to the Offload Security service account.

### Asset Inventory &amp; Cloud Security (CSPM)

| Capability | API | Predefined role | Why (what we call) |
| --- | --- | --- | --- |
| Asset discovery | `cloudasset` | `roles/cloudasset.viewer` | `assets.searchAllResources`, `assets.listAssets`, `assets.searchAllIamPolicies` |
| Project/folder enumeration *(org)* | `cloudresourcemanager` | `roles/resourcemanager.organizationViewer`, `roles/resourcemanager.folderViewer` | `projects.list`, `folders.list` — discover every project under the org |
| IAM posture | `iam` | `roles/iam.securityReviewer` | list service accounts, keys, IAM policies |
| Security Command Center *(org)* | `securitycenter` | `roles/securitycenter.findingsViewer` | `findings.list` |
| Compute posture | `compute` | `roles/compute.viewer` | instances, firewall, networks |
| Storage posture | `storage` | `roles/storage.objectViewer` | bucket/object read |
| Logging posture | `logging` | `roles/logging.viewer` | `logEntries.list` |
| Monitoring posture | `monitoring` | `roles/monitoring.viewer` | metrics / time series |

### Kubernetes (GKE) — control plane

| Capability | API | Predefined role | Why |
| --- | --- | --- | --- |
| Cluster discovery + kubeconfig | `container` | `roles/container.viewer` | `container.clusters.list`/`.get`, `locations.list` — enumerate clusters and mint a read-only kubeconfig |

:::note
GKE control-plane read is **not** enough to read workloads — you also need
**Bucket B** (in-cluster RBAC).
:::

### Container Registries

| Capability | API | Predefined role | Why |
| --- | --- | --- | --- |
| Artifact Registry | `artifactregistry` | `roles/artifactregistry.reader` | `repositories.list/get`, `packages.list`, `dockerimages.list`, `downloadArtifacts` (pull images to scan) |
| Legacy GCR (`gcr.io`) | `storage` | `roles/storage.objectViewer` | GCR stores images in Cloud Storage; needs `storage.objects.get` |

### Grant it — `gcloud` (org-level)

```bash
ORG_ID="123456789012"
SA="serviceAccount:offloadsecurity-audit@YOUR_PROJECT.iam.gserviceaccount.com"

for ROLE in \
  roles/cloudasset.viewer \
  roles/resourcemanager.organizationViewer \
  roles/resourcemanager.folderViewer \
  roles/iam.securityReviewer \
  roles/securitycenter.findingsViewer \
  roles/compute.viewer \
  roles/storage.objectViewer \
  roles/logging.viewer \
  roles/monitoring.viewer \
  roles/container.viewer \
  roles/artifactregistry.reader ; do
  gcloud organizations add-iam-policy-binding "$ORG_ID" \
    --member="$SA" --role="$ROLE" --condition=None
done
```

### Grant it — Terraform

```hcl
locals {
  offloadsecurity_roles = [
    "roles/cloudasset.viewer",
    "roles/resourcemanager.organizationViewer",
    "roles/resourcemanager.folderViewer",
    "roles/iam.securityReviewer",
    "roles/securitycenter.findingsViewer",
    "roles/compute.viewer",
    "roles/storage.objectViewer",
    "roles/logging.viewer",
    "roles/monitoring.viewer",
    "roles/container.viewer",
    "roles/artifactregistry.reader",
  ]
}

resource "google_organization_iam_member" "offloadsecurity" {
  for_each = toset(local.offloadsecurity_roles)
  org_id   = var.org_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.offloadsecurity_audit.email}"
}
```

---

## Bucket B — Kubernetes in-cluster RBAC

`roles/container.viewer` lets Offload Security list clusters and get a kubeconfig,
but reading workloads, RBAC, and network policies **requires Kubernetes RBAC**.
Apply this `ClusterRole` in each cluster and bind it to the identity Offload
Security uses (the GCP service account, or an in-cluster ServiceAccount):

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: offloadsecurity-scanner
rules:
  - apiGroups: [""]
    resources: ["pods","nodes","services","namespaces","endpoints","persistentvolumes","persistentvolumeclaims","configmaps"]
    verbs: ["get","list"]
  - apiGroups: ["apps"]
    resources: ["deployments","daemonsets","statefulsets","replicasets"]
    verbs: ["get","list"]
  - apiGroups: ["rbac.authorization.k8s.io"]
    resources: ["roles","rolebindings","clusterroles","clusterrolebindings"]
    verbs: ["get","list"]
  - apiGroups: ["networking.k8s.io"]
    resources: ["networkpolicies","ingresses"]
    verbs: ["get","list"]
  - apiGroups: ["batch"]
    resources: ["jobs","cronjobs"]
    verbs: ["get","list"]
  - apiGroups: ["policy"]
    resources: ["podsecuritypolicies","poddisruptionbudgets"]
    verbs: ["get","list"]
```

Bind it with a `ClusterRoleBinding` to your scanner's ServiceAccount (or, on GKE,
to the GCP service account via `User: <sa-email>`).

---

## Bucket C — Cloud Events (audit-log streaming)

Cloud Events is **push-based**: Cloud Audit Logs → **log sink** → **Pub/Sub
topic** → **push subscription** → Offload Security webhook. So this bucket is a
**one-time setup**, and ongoing ingestion needs **no** service-account permission
(GCP pushes events to us).

**Prerequisite IAM permissions** for whoever runs the setup:

| Granular permission | Setup step | Predefined role |
| --- | --- | --- |
| `logging.sinks.create` | create the (org-aggregated) sink | `roles/logging.configWriter` |
| `logging.sinks.get` | read the sink's writer identity | `roles/logging.configWriter` |
| `pubsub.topics.create` | create the topic | `roles/pubsub.admin` |
| `pubsub.topics.getIamPolicy` + `setIamPolicy` | grant the sink writer publish rights | `roles/pubsub.admin` |
| `pubsub.subscriptions.create` | create the push subscription | `roles/pubsub.admin` |
| `iam.serviceAccounts.actAs` | attach the push-auth service account | `roles/iam.serviceAccountUser` |

Plus: the sink's **auto-created writer identity** must be granted
`roles/pubsub.publisher` **on the topic** (a grant you make *to* the sink).

```bash
ORG_ID="123456789012"; PROJECT="YOUR_PROJECT"

gcloud pubsub topics create offload-security-events --project="$PROJECT"

gcloud logging sinks create offload-org-sink \
  "pubsub.googleapis.com/projects/$PROJECT/topics/offload-security-events" \
  --organization="$ORG_ID" --include-children \
  --log-filter='logName=~"logs/cloudaudit.googleapis.com"'

WID=$(gcloud logging sinks describe offload-org-sink --organization="$ORG_ID" --format='value(writerIdentity)')
gcloud pubsub topics add-iam-policy-binding offload-security-events \
  --project="$PROJECT" --member="$WID" --role="roles/pubsub.publisher"

gcloud pubsub subscriptions create offload-security-push \
  --project="$PROJECT" --topic=offload-security-events \
  --push-endpoint="https://YOUR-DOMAIN/api/cloud-events/webhook/gcp" \
  --push-auth-service-account="offloadsecurity-audit@$PROJECT.iam.gserviceaccount.com"
```

---

## Quick reference — what each feature needs

| Onboarding | Enable API(s) | Grant role(s) |
| --- | --- | --- |
| **Asset Inventory** | cloudasset, cloudresourcemanager | `cloudasset.viewer`, `resourcemanager.organizationViewer` (+ `folderViewer`) |
| **Cloud / CSPM** | compute, iam, storage, logging, monitoring, securitycenter | `iam.securityReviewer`, `securitycenter.findingsViewer`, `compute.viewer`, `storage.objectViewer`, `logging.viewer`, `monitoring.viewer` |
| **Kubernetes (GKE)** | container | `container.viewer` **+ in-cluster ClusterRole** |
| **Container registries** | artifactregistry (+ storage for GCR) | `artifactregistry.reader` (+ `storage.objectViewer`) |
| **Cloud Events** | logging, pubsub | *setup:* `logging.configWriter` + `pubsub.admin` + `iam.serviceAccountUser`; *sink writer:* `pubsub.publisher` on topic |

---

## Notes

- **Least privilege.** Every role above is read-only/viewer except the one-time
  Cloud Events setup. We deliberately avoid `roles/editor` / `roles/owner`.
- **Authentication.** Use a downloaded **service-account key** *or* **Workload
  Identity Federation** (keyless) — both are supported by the connect wizard.
- **Project vs org.** Every row works at project scope too; grant at the **org
  node** only if you want one binding to cover all projects.
  `securitycenter.findingsViewer` and `resourcemanager.organizationViewer` are
  inherently org-scoped.

> **AWS / Azure:** the same read-only principle applies (Offload Security never
> needs write access to assess posture). Provider-specific policy documents will
> be added here as companion sections.

## Related

- [Connecting Cloud Accounts](./connecting-accounts.md)
- [Kubernetes Security](../security-scanning/kubernetes-security.md)
- [Container Security](../security-scanning/container-security.md)
