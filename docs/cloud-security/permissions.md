---
title: "Required Permissions"
sidebar_label: "Required Permissions"
sidebar_position: 1.5
description: "The exact APIs and IAM roles Offload Security needs to onboard AWS, GCP, and Azure — cloud/CSPM, asset inventory, Kubernetes, container registries, and cloud events."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Required Permissions

Most onboarding problems are **missing permissions**, not bad configuration. This
page lists **exactly** what Offload Security needs, per cloud. Access is
**read-only** everywhere except the one-time Cloud Events setup.

Think of it as **three buckets** — you don't need all of them for every feature:

| Bucket | What it is | Where it's granted |
| --- | --- | --- |
| **A. Read-only scanning** | Asset Inventory, Cloud/CSPM, Kubernetes & registry discovery | An IAM role / service account / service principal on the cloud |
| **B. Kubernetes in-cluster RBAC** | Reading workloads/RBAC/network policies inside a cluster | A Kubernetes `ClusterRole` bound **inside each cluster** |
| **C. Cloud Events setup** | Streaming audit/activity events to Offload Security | **One-time** event source → webhook wiring |

---

## Bucket A — Read-only scanning

Pick your cloud. These are the exact roles the connect wizard provisions.

<Tabs groupId="cloud">
<TabItem value="aws" label="AWS">

Offload Security assumes a **cross-account IAM role** via STS (with an **External
ID**) — no long-lived keys required.

**Managed policies:** `SecurityAudit` + `ReadOnlyAccess`
**Plus an inline policy** for native-findings ingestion: `securityhub`,
`guardduty`, `inspector2`, `access-analyzer`, `config`, `cloudtrail`.

**CloudFormation**

```yaml
Resources:
  CSPMSecurityAuditRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: CSPMSecurityAuditRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal: { AWS: !Sub 'arn:aws:iam::${TrustedAccountId}:root' }   # Offload Security's account
            Action: sts:AssumeRole
            Condition: { StringEquals: { sts:ExternalId: !Ref ExternalId } }
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/SecurityAudit
        - arn:aws:iam::aws:policy/ReadOnlyAccess
      Policies:
        - PolicyName: CSPMAdditionalPermissions
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: [securityhub:*, guardduty:*, inspector2:*, access-analyzer:*, config:*, cloudtrail:*]
                Resource: '*'
```

**Terraform**

```hcl
resource "aws_iam_role" "cspm_security_audit" {
  name               = "CSPMSecurityAuditRole"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json  # trusts Offload's account + external_id
}
resource "aws_iam_role_policy_attachment" "security_audit" {
  role = aws_iam_role.cspm_security_audit.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}
resource "aws_iam_role_policy_attachment" "read_only" {
  role = aws_iam_role.cspm_security_audit.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}
```

You then paste the **Role ARN** and **External ID** into the connect wizard
(access keys are also supported, but the cross-account role is preferred).

</TabItem>
<TabItem value="gcp" label="GCP">

Offload Security uses a **service account** (key or Workload Identity Federation).

**Enable the APIs:**

```bash
gcloud services enable \
  cloudasset.googleapis.com cloudresourcemanager.googleapis.com \
  compute.googleapis.com iam.googleapis.com storage.googleapis.com \
  logging.googleapis.com monitoring.googleapis.com securitycenter.googleapis.com \
  container.googleapis.com artifactregistry.googleapis.com pubsub.googleapis.com
```

**Roles** (the wizard's project template + the org-only additions):

| Role | For |
| --- | --- |
| `roles/cloudasset.viewer` | asset inventory (`searchAllResources`) |
| `roles/iam.securityReviewer` | IAM posture |
| `roles/securitycenter.findingsViewer` | SCC findings *(org)* |
| `roles/compute.viewer`, `roles/storage.objectViewer` | compute / storage posture |
| `roles/logging.viewer`, `roles/monitoring.viewer` | logs / metrics |
| `roles/container.viewer` | GKE discovery |
| `roles/artifactregistry.reader` | registry discovery |
| `roles/resourcemanager.organizationViewer` + `folderViewer` | enumerate all projects *(org only)* |

**Grant at the org node** (covers all current + future projects):

```bash
for R in roles/cloudasset.viewer roles/resourcemanager.organizationViewer \
  roles/resourcemanager.folderViewer roles/iam.securityReviewer \
  roles/securitycenter.findingsViewer roles/compute.viewer \
  roles/storage.objectViewer roles/logging.viewer roles/monitoring.viewer \
  roles/container.viewer roles/artifactregistry.reader ; do
  gcloud organizations add-iam-policy-binding "$ORG_ID" \
    --member="serviceAccount:$SA_EMAIL" --role="$R" --condition=None
done
```

Terraform: `google_organization_iam_member` with `for_each` over the same list.

</TabItem>
<TabItem value="azure" label="Azure">

Offload Security uses a **service principal** (app registration) with roles at
**subscription** scope.

**Roles:** `Reader`, `Security Reader`, `Key Vault Reader`,
`Network Contributor`, `Storage Blob Data Reader`.

**Azure CLI**

```bash
# Create the SP with Reader, then add the security roles
SP=$(az ad sp create-for-rbac --name "offloadsecurity-cspm" \
  --role "Reader" --scopes "/subscriptions/$SUBSCRIPTION_ID" -o json)
CLIENT_ID=$(echo $SP | jq -r '.appId')

for ROLE in "Security Reader" "Key Vault Reader" "Network Contributor" "Storage Blob Data Reader" ; do
  az role assignment create --assignee "$CLIENT_ID" --role "$ROLE" \
    --scope "/subscriptions/$SUBSCRIPTION_ID"
done
# Paste appId (client_id), password (client_secret), tenant into the wizard.
```

**Terraform:** `azuread_application` + `azuread_service_principal` +
`azurerm_role_assignment` (`for_each` over the five roles) at subscription scope.

</TabItem>
</Tabs>

:::tip[Scope = grant once]
Grant at the **AWS Organization / GCP org node / Azure management group** to cover
every account/project/subscription (current and future) with one binding.
Everything above also works at single account/project/subscription scope.
:::

---

## Bucket B — Kubernetes in-cluster RBAC

Cluster **discovery** (EKS / GKE / AKS) is already covered by the read roles in
Bucket A. But reading workloads, RBAC, and network policies **inside** a cluster
requires **Kubernetes RBAC** — apply this `ClusterRole` in each cluster and bind
it to the identity Offload Security uses (the kubeconfig / service-account token
you provide at onboarding):

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

Clusters are onboarded with a **read-only kubeconfig or service-account token**
(base64-encoded) — see [Kubernetes Security](../security-scanning/kubernetes-security.md).

---

## Container registries

Registry **discovery** rides on Bucket A; **pulling images to scan** needs pull access:

| Registry | Pull permission |
| --- | --- |
| **AWS ECR** (`*.dkr.ecr.*.amazonaws.com`) | `ecr:GetAuthorizationToken` + read — already in `ReadOnlyAccess` (or attach `AmazonEC2ContainerRegistryReadOnly`) |
| **GCP Artifact Registry / GCR** | `roles/artifactregistry.reader` (+ `roles/storage.objectViewer` for legacy `gcr.io`) |
| **Azure ACR** (`*.azurecr.io`) | **`AcrPull`** — add this role to the service principal (it is **not** in the base Azure role set above) |

See [Container Security](../security-scanning/container-security.md).

---

## Bucket C — Cloud Events (audit/activity streaming)

Cloud Events is **push-based**: your cloud sends audit/activity events to an
Offload Security **webhook**. This is a **one-time setup**, and the scanning role
needs **no** extra permission for ongoing ingestion.

| Cloud | Event source → webhook |
| --- | --- |
| **AWS** | CloudTrail → **EventBridge** rule → API destination → `POST /api/cloud-events/webhook/aws` |
| **GCP** | Cloud Audit Logs → **Pub/Sub** log sink → push subscription → `POST /api/cloud-events/webhook/gcp` |
| **Azure** | Activity Log → **Event Grid** system topic → subscription → `POST /api/cloud-events/webhook/azure` |

The setup permissions belong to whoever **creates the event source** (an admin):
create an EventBridge rule (AWS), a Logging sink + Pub/Sub topic/subscription
(GCP — `logging.configWriter` + `pubsub.admin`), or an Event Grid subscription
(Azure). The connect UI shows you the exact per-provider webhook URL to target.

---

## Quick reference

| Cloud | Bucket A (scanning) | Registry pull | Cloud Events |
| --- | --- | --- | --- |
| **AWS** | Cross-account role: `SecurityAudit` + `ReadOnlyAccess` (+ securityhub/guardduty/inspector2/access-analyzer/config/cloudtrail) | ECR (in ReadOnlyAccess) | EventBridge → webhook |
| **GCP** | `cloudasset.viewer`, `iam.securityReviewer`, `securitycenter.findingsViewer`, `compute/storage/logging/monitoring.viewer`, `container.viewer`, `artifactregistry.reader` (+ `organizationViewer` at org) | `artifactregistry.reader` | Pub/Sub sink → webhook |
| **Azure** | SP: `Reader`, `Security Reader`, `Key Vault Reader`, `Network Contributor`, `Storage Blob Data Reader` | `AcrPull` (add) | Event Grid → webhook |

---

## Notes

- **Least privilege.** Every role is read-only except the one-time Cloud Events
  setup. On AWS the cross-account role uses an **External ID**; on GCP prefer
  **Workload Identity Federation** (keyless); on Azure the SP secret should be
  rotated (the wizard defaults it to 1 year).
- **Authentication into the wizard.** AWS = role ARN + external ID (or access
  keys); GCP = service-account JSON (or WIF); Azure = client id + secret + tenant.
- **Scope.** Grant at account/project/subscription scope, or at the
  org/management-group for one-and-done coverage of all children.

## Related

- [Connecting Cloud Accounts](./connecting-accounts.md)
- [Kubernetes Security](../security-scanning/kubernetes-security.md)
- [Container Security](../security-scanning/container-security.md)
