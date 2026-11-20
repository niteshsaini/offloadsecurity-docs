---
title: "Required Permissions"
sidebar_label: "Required Permissions"
sidebar_position: 1.5
description: "The exact APIs and IAM roles Offload Security needs on AWS, GCP and Azure — posture scanning, asset inventory, identity (CIEM) and exposure analysis, Kubernetes, container registries and cloud events."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Required Permissions

Most onboarding problems are **missing permissions**, not bad configuration. This
page lists what Offload Security needs, per cloud. Access is **read-only**
everywhere except the one-time Cloud Events setup, which you perform yourself.
Never grant write or administrator roles: nothing in the platform needs them.

Think of it as **three buckets** — you don't need all of them for every feature:

| Bucket | What it is | Where it's granted |
| --- | --- | --- |
| **A. Read-only scanning** | Asset Inventory, Cloud/CSPM, identity and exposure analysis, Kubernetes & registry discovery | An IAM role / service account / service principal on the cloud |
| **B. Kubernetes in-cluster RBAC** | Reading workloads/RBAC/network policies inside a cluster | A Kubernetes `ClusterRole` bound **inside each cluster** |
| **C. Cloud Events setup** | Streaming audit/activity events to Offload Security | **One-time** event source → webhook wiring |

A permission that is denied makes only the affected part **Not evaluated** (or *Not assessed*), with the missing permission named — never "clean", "no access" or "not exposed".

---

## Bucket A — Read-only scanning

Pick your cloud.

<Tabs groupId="cloud" queryString>
<TabItem value="aws" label="AWS">

Offload Security assumes a **cross-account IAM role** via STS with an **External
ID** — no long-lived keys required. Access keys are also supported.

**Managed policies:** `SecurityAudit` + `ReadOnlyAccess` (what the connect wizard asks for).
**Plus an inline policy** with the explicit reads below, for native-findings
ingestion, ECR listing, and the resource-policy and exposure reads used by
identity and network analysis.

**CloudFormation**

```yaml
Parameters:
  PlatformPrincipalArn: { Type: String }   # the AWS principal your Offload Security deployment runs as
  ExternalId:           { Type: String }   # the external ID entered or generated in the wizard
Resources:
  OffloadSecurityScanner:
    Type: AWS::IAM::Role
    Properties:
      RoleName: OffloadSecurityScanner
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal: { AWS: !Ref PlatformPrincipalArn }
            Action: sts:AssumeRole
            Condition: { StringEquals: { sts:ExternalId: !Ref ExternalId } }
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/SecurityAudit
        - arn:aws:iam::aws:policy/ReadOnlyAccess
      Policies:
        - PolicyName: OffloadSecuritySupplement
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - securityhub:GetFindings
                  - guardduty:ListDetectors
                  - guardduty:ListFindings
                  - guardduty:GetFindings
                  - config:GetComplianceSummaryByConfigRule
                  - cloudtrail:LookupEvents
                  - tag:GetResources
                  - ecr:DescribeRepositories
                  - ecr:DescribeImages
                  - cloudfront:ListVpcOrigins
                  - secretsmanager:GetResourcePolicy
                  - dynamodb:GetResourcePolicy
                  - elasticfilesystem:DescribeFileSystemPolicy
                  - sqs:GetQueueUrl
                  - s3:GetAccountPublicAccessBlock
                Resource: '*'
              - Effect: Allow
                Action: apigateway:GET
                Resource:
                  - 'arn:aws:apigateway:*::/vpclinks'
                  - 'arn:aws:apigateway:*::/vpclinks/*'
```

The same role in Terraform is on [Connecting Cloud Accounts](./connecting-accounts.md#aws).
Ask your platform administrator for the principal ARN to trust. You then paste the
**Role ARN** and **External ID** into the connect wizard.

</TabItem>
<TabItem value="gcp" label="GCP">

Offload Security uses a **service account** JSON key (the wizard also offers Workload Identity).

**Enable the APIs** on the service account's own project (the project where API calls are metered):

```bash
gcloud services enable \
  cloudasset.googleapis.com cloudresourcemanager.googleapis.com \
  serviceusage.googleapis.com iam.googleapis.com compute.googleapis.com \
  storage.googleapis.com container.googleapis.com artifactregistry.googleapis.com \
  logging.googleapis.com monitoring.googleapis.com securitycenter.googleapis.com \
  --project="$SA_PROJECT"
```

**Roles for a single project** (the connect wizard):

| Role | For |
| --- | --- |
| `roles/viewer` | Baseline read across resources |
| `roles/cloudasset.viewer` | Asset inventory enumeration |
| `roles/iam.securityReviewer` | Reading IAM policies for identity analysis |
| `roles/securitycenter.findingsViewer`, `roles/securitycenter.assetsViewer` | Security Command Center findings and assets |
| `roles/artifactregistry.reader` | Artifact Registry discovery and image pulls (optional) |

**Roles for organization or folder onboarding** (what **GCP Organizations → Check readiness** verifies, granted at the organization or folder):

| Role | For |
| --- | --- |
| `roles/viewer` | Baseline read across all resources |
| `roles/cloudasset.viewer` | Asset inventory enumeration |
| `roles/compute.viewer` | VMs, disks, networks, firewalls |
| `roles/storage.objectViewer` | Buckets and GCR image pulls |
| `roles/container.viewer` | GKE cluster discovery |
| `roles/iam.securityReviewer` | IAM policies for identity analysis |
| `roles/logging.viewer` | Log-based configuration checks |
| `roles/monitoring.viewer` | Monitoring/alerting configuration |
| `roles/securitycenter.findingsViewer` | Security Command Center findings |

```bash
for R in roles/viewer roles/cloudasset.viewer roles/compute.viewer \
  roles/storage.objectViewer roles/container.viewer roles/iam.securityReviewer \
  roles/logging.viewer roles/monitoring.viewer roles/securitycenter.findingsViewer ; do
  gcloud organizations add-iam-policy-binding "$ORG_ID" \
    --member="serviceAccount:$SA_EMAIL" --role="$R"
done
```

The wizard's **Show setup commands** generates these commands for your organization or folder ID.

</TabItem>
<TabItem value="azure" label="Azure">

Offload Security uses a **service principal** (app registration) with read-only roles at
**subscription** scope.

**Roles:** `Reader`, `Security Reader` (Defender for Cloud findings) and
`Log Analytics Reader` (activity log and alerts).

**Azure CLI**

```bash
SP=$(az ad sp create-for-rbac --name "offloadsecurity-cspm" \
  --role "Reader" --scopes "/subscriptions/$SUBSCRIPTION_ID" -o json)
CLIENT_ID=$(echo $SP | jq -r '.appId')

for ROLE in "Security Reader" "Log Analytics Reader" ; do
  az role assignment create --assignee "$CLIENT_ID" --role "$ROLE" \
    --scope "/subscriptions/$SUBSCRIPTION_ID"
done
# Paste appId (client_id), password (client_secret) and tenant into the wizard.
```

**Terraform:** `azuread_application` + `azuread_service_principal` +
`azurerm_role_assignment` (`for_each` over the three roles) at subscription scope — see
[Connecting Cloud Accounts](./connecting-accounts.md#azure).

</TabItem>
</Tabs>

:::note[Granting broadly does not onboard broadly]
Granting roles at a GCP organization or folder lets organization onboarding discover and scan every project under it. On AWS and Azure, accounts and subscriptions are still connected **one by one** — a role deployed across an AWS Organization (for example with a StackSet) or `Reader` at an Azure management group gives the access, but each account or subscription must be added in the wizard.
:::

## Additional reads for analysis

These reads are used by identity analysis (CIEM), internet-exposure analysis and the encryption-at-rest view. On AWS most of them are already in `SecurityAudit` / `ReadOnlyAccess`; the ones that are not are in the inline policy above.

### Identity analysis (CIEM)

| Cloud | Reads | If denied |
| --- | --- | --- |
| **AWS** | Every user's and role's policies (`iam:GetAccountAuthorizationDetails`, with `iam:List*` / `iam:Get*` as the fallback); data-store resource policies: `s3:GetBucketPolicy`, `kms:GetKeyPolicy`, `secretsmanager:GetResourcePolicy`, `sqs:GetQueueUrl` + `sqs:GetQueueAttributes`, `sns:GetTopicAttributes`, `lambda:GetPolicy`, `dynamodb:GetResourcePolicy`, `elasticfilesystem:DescribeFileSystemPolicy`; S3 Block Public Access: `s3:GetAccountPublicAccessBlock`, `s3:GetBucketPublicAccessBlock`. | The principal or store is *not evaluated* with the missing permission; the run is partial. |
| **AWS SCPs** | Only through the organization's **management account** or a **delegated administrator for AWS Organizations**, onboarded in the same team with: `organizations:DescribeOrganization`, `organizations:ListRoots`, `organizations:ListParents`, `organizations:ListPoliciesForTarget`, `organizations:ListPolicies`, `organizations:DescribePolicy`. | SCPs are *not evaluated* and never assumed to restrict anything. |
| **GCP** | At the **organization** (or the top folder you onboard): `roles/iam.securityReviewer` (IAM policies, custom roles, bucket and service-account IAM), `roles/browser` (project ancestry), `roles/iam.denyReviewer` (IAM deny policies). | Inherited bindings, ancestry or deny policies are *not evaluated*; project bindings are still evaluated. |
| **Azure** | `Reader` on the **management group** above the subscription (or the tenant root group) for inherited role assignments, role definitions and deny assignments. | The management-group cross-check is *not evaluated*; unreadable deny assignments make the run partial. If the subscription's own role assignments cannot be read, the analysis fails. |

AWS SCP read policy, for the management account or delegated administrator only:

```hcl
resource "aws_iam_role_policy" "offload_scp_read" {
  name = "OffloadSecurityScpRead"
  role = aws_iam_role.offload_security_scanner.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "organizations:DescribeOrganization", "organizations:ListRoots",
        "organizations:ListParents", "organizations:ListPoliciesForTarget",
        "organizations:ListPolicies", "organizations:DescribePolicy"
      ]
      Resource = "*"
    }]
  })
}
```

GCP organization-level identity roles:

```hcl
resource "google_organization_iam_member" "ciem" {
  for_each = toset(["roles/iam.securityReviewer", "roles/browser", "roles/iam.denyReviewer"])
  org_id   = var.org_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.offload_scanner.email}"
}
```

### Encryption at rest and exposure

| Cloud | Reads | If denied |
| --- | --- | --- |
| **AWS — encryption** | `s3:GetEncryptionConfiguration`, `dynamodb:DescribeTable`, `elasticfilesystem:DescribeFileSystems`, `sqs:ListQueues`, `sqs:GetQueueAttributes`, `sns:GetTopicAttributes`, `kms:DescribeKey` (all in `SecurityAudit`). | The resource is **Not assessed** with the reason — never unencrypted. |
| **AWS — exposure** | Route tables, network ACLs, security groups, subnets and load balancers (`ec2:Describe*`, `elasticloadbalancing:Describe*`), plus the front-door reads in the inline policy (`cloudfront:ListVpcOrigins`, `apigateway:GET` on VPC links). Enabled regions: `ec2:DescribeRegions`. | The resource is **Not evaluated**, never "not reachable". |
| **GCP — exposure** | `compute.networks.getEffectiveFirewalls`, `compute.networks.getRegionEffectiveFirewalls` (in `roles/compute.viewer` / `roles/viewer`). | Instances with an external IP are **Not evaluated**. |
| **Azure — exposure** | Network interfaces, public IPs, NSGs, virtual networks and subnets (`Microsoft.Network/*/read`, in `Reader`). | The VM is **Not evaluated**. |

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
(base64-encoded) — see [Kubernetes Security](../security-scanning/kubernetes/index.md)
for the full RBAC profile the scanner expects.

---

## Container registries

Registry **discovery** rides on Bucket A; **pulling images to scan** needs pull access:

| Registry | Pull permission |
| --- | --- |
| **AWS ECR** (`*.dkr.ecr.*.amazonaws.com`) | `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer` — all in `ReadOnlyAccess` (or attach `AmazonEC2ContainerRegistryReadOnly`) |
| **GCP Artifact Registry / GCR** | `roles/artifactregistry.reader` (+ `roles/storage.objectViewer` for legacy `gcr.io`) |
| **Azure ACR** (`*.azurecr.io`) | **`AcrPull`** — add this role to the service principal (it is **not** in the base Azure role set above). An account connected with Managed Identity cannot sign in to ACR. |

See [Container Security](../security-scanning/containers/index.md).

---

## Bucket C — Cloud Events (audit/activity streaming)

Cloud Events is **push-based**: your cloud sends audit/activity events to an
Offload Security **webhook** that carries your team's webhook token. This is a
**one-time setup**, and the scanning role needs **no** extra permission for
ongoing ingestion.

| Cloud | Event source → webhook |
| --- | --- |
| **AWS** | CloudTrail → **EventBridge** rule → API destination → `POST /api/cloud-events/webhook/aws` (token in the `x-offload-webhook-token` header) |
| **GCP** | Cloud Audit Logs → **Pub/Sub** log sink → push subscription → `POST /api/cloud-events/webhook/gcp/<team token>` |
| **Azure** | Activity Log → **Event Grid** system topic → subscription → `POST /api/cloud-events/webhook/azure/<team token>` |

The setup permissions belong to whoever **creates the event source** (an admin):
create an EventBridge rule (AWS), a Logging sink + Pub/Sub topic/subscription
(GCP — `logging.configWriter` + `pubsub.admin`), or an Event Grid subscription
(Azure). See [Real-Time Cloud Events](./cloud-events.md).

---

## Quick reference

| Cloud | Bucket A (scanning) | Identity analysis extras | Registry pull | Cloud Events |
| --- | --- | --- | --- | --- |
| **AWS** | Cross-account role: `SecurityAudit` + `ReadOnlyAccess` + inline supplement | Organizations reads in the management account / delegated admin (for SCPs) | ECR (in ReadOnlyAccess) | EventBridge → webhook |
| **GCP** | Project: `viewer`, `cloudasset.viewer`, `iam.securityReviewer`, `securitycenter.findingsViewer`, `securitycenter.assetsViewer`; org onboarding: the nine roles above | `iam.securityReviewer`, `browser`, `iam.denyReviewer` at the organization | `artifactregistry.reader` | Pub/Sub sink → webhook |
| **Azure** | SP: `Reader`, `Security Reader`, `Log Analytics Reader` | `Reader` on the parent management group | `AcrPull` (add) | Event Grid → webhook |

---

## Notes

- **Least privilege.** Every role is read-only except the one-time Cloud Events
  setup. On AWS the cross-account role uses an **External ID**; rotate access keys
  and Azure client secrets regularly — the platform flags stored credentials older
  than 60 days and marks them critical at 90 (see
  [Credentials & Health](./account-management.md#credentials--health)).
- **Authentication into the wizard.** AWS = role ARN + external ID (or access
  keys); GCP = service-account JSON; Azure = client id + secret + tenant.

## Related

- [Connecting Cloud Accounts](./connecting-accounts.md)
- [Identity & Network Posture](./identity-and-network.md)
- [Kubernetes Security](../security-scanning/kubernetes/index.md)
- [Container Security](../security-scanning/containers/index.md)
