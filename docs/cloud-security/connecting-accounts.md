---
title: "Connecting Cloud Accounts"
sidebar_label: "Connecting Cloud Accounts"
sidebar_position: 1
description: "Connect an AWS account, GCP project or Azure subscription with read-only access using the six-step wizard, or onboard a whole GCP organization at once."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Connecting Cloud Accounts

You connect each cloud account once. Offload Security validates the credentials against the provider before saving them, stores them **encrypted at rest**, kicks off a first posture scan and registers a recurring schedule — so a newly connected account shows results within minutes and stays current without further setup.

**Where:** left navigation → **Cloud Accounts** (under *Management*) → **Add Account**. The **+ Add Account** button on the Cloud Security → Accounts tab opens the same page. Earlier releases called this page *Account Setup*.

:::tip[Provision access first]
Almost every failed connection is a missing permission, not a wrong credential. Grant the read-only roles from **[Required Permissions](./permissions.md)** before you open the wizard — that page has ready-to-apply Terraform, CloudFormation and CLI for each cloud.
:::

## Before you start

| You need | AWS | GCP | Azure |
| --- | --- | --- | --- |
| **Identity the platform uses** | Cross-account IAM role (recommended) or an IAM user's access keys | Service account JSON key (Workload Identity is also offered) | Service principal (client ID + secret); Managed Identity is also offered |
| **Identifier** | 12-digit account ID | Project ID | Subscription ID + tenant ID |
| **Access level** | `SecurityAudit` + `ReadOnlyAccess` (+ a small inline supplement) | `roles/viewer`, `cloudasset.viewer`, `iam.securityReviewer`, … | `Reader`, `Security Reader`, `Log Analytics Reader` |
| **Platform permission** | **Manage Cloud Accounts** (see [RBAC](../authentication/rbac-team-management.md)) | same | same |

:::note[One account at a time on AWS and Azure]
AWS accounts and Azure subscriptions are connected one by one — there is no AWS Organizations or Azure management-group onboarding. Only GCP can be onboarded by organization or folder ([below](#onboarding-a-gcp-organization)). For many AWS or Azure accounts, apply the same role or service principal with your own tooling (for example a CloudFormation StackSet) and add each account in the wizard.
:::

## The connect wizard

The wizard has six steps: **Provider Selection**, **Environment Setup**, **Business Context**, **Authentication**, **Credentials** and **Validation**. Your progress is kept per step for up to two hours after your last step; anything you typed as a credential is stored encrypted while the wizard is open and deleted when you complete or cancel it.

### 1. Provider

Pick **Amazon Web Services**, **Google Cloud Platform** or **Microsoft Azure**.

![Add Account wizard — provider selection with AWS, GCP and Azure cards](/img/screenshots/cloud-security/account-setup-provider.webp)

### 2. Environment

Give the account a **display name** you will recognize in dashboards (for example *Production AWS — Payments Platform*), classify its **environment**, and enter the provider's account identifier — a 12-digit AWS account number, a GCP project ID or an Azure subscription ID.

![Environment step — display name, environment classification, AWS account ID and region picker](/img/screenshots/cloud-security/account-setup-environment.webp)

- **AWS:** choose the regions to scan, or leave the selection empty. With no regions chosen, full and incremental scans cover **every region enabled on the AWS account** (looked up at scan time and cached for a day). You can add a region ID that is not in the list.
- **GCP / Azure:** there is no region picker. A project or subscription is always scanned as one unit. See [How scans partition work by provider](./scan-orchestration.md#how-scans-partition-work-by-provider).

### 3. Business context

Record the **business unit**, the **account owner's email** (required) and, optionally, the **compliance requirements** that apply. Owner and business unit appear on findings and reports, so that a critical finding can be routed to the right team, and the account's context is copied to its assets once a day (see [Asset Inventory](./asset-inventory.md)).

![Business context step — business unit, owner email and compliance requirement checkboxes](/img/screenshots/cloud-security/account-setup-business-context.webp)

### 4. Authentication method

Choose how the platform will authenticate:

| Provider | Methods |
| --- | --- |
| **AWS** | **Cross-Account Role (recommended)** — `sts:AssumeRole` with an external ID; no long-lived keys. **Access Keys** — access key ID + secret (+ optional session token). |
| **GCP** | **Service Account** — JSON key. **Workload Identity** is also offered. |
| **Azure** | **Service Principal** — tenant, client ID, client secret, subscription. **Managed Identity** is also offered, for when the platform itself runs in Azure. |

![Authentication step — Cross-Account Role (Recommended) and Access Keys options for AWS](/img/screenshots/cloud-security/account-setup-auth-method.webp)

:::note[Key-based methods are the documented path]
This guide covers the key-based methods. Check with your administrator before using GCP Workload Identity or Azure Managed Identity. An Azure account connected with Managed Identity stores no credentials, so it has nothing to rotate, and it cannot sign in to Azure Container Registry for image scans.
:::

### 5. Credentials

Paste the values for the method you chose. For an AWS cross-account role, enter the **Role ARN** and an **External ID** (use **Generate** to create one), and put the same external ID in the role's trust policy. The trust policy's principal is the AWS identity your Offload Security deployment runs as — ask your platform administrator for it. For GCP paste the JSON key and project ID; for Azure enter the tenant, client, secret and subscription IDs.

![Credentials step — AWS cross-account role setup summary with Role ARN and External ID fields](/img/screenshots/cloud-security/account-setup-credentials.webp)

Secrets are encrypted before they are written and are never returned by the API afterwards.

### 6. Validation

Select **Validate & Continue**. The platform performs a live connection test with the provider SDK (an STS `GetCallerIdentity` on AWS, a Resource Manager / Asset lookup on GCP, a subscription lookup on Azure). On success, select **Complete Setup**: the account is created as **active**, an initial scan is queued and the recurring schedule is registered. On failure, **Error Details** shows the provider's error so you can fix the role or key and retry — nothing is saved until validation passes.

:::note[Every AWS scan re-verifies the identity]
For an AWS role, every scan assumes the role and checks with `sts:GetCallerIdentity` that it really reached the 12-digit account you entered. A mismatch refuses the scan rather than scanning the wrong account.
:::

## What happens right after connecting

- **A first scan starts** in the background. Watch it on Cloud Security → **Accounts** (the card shows *Scanning…* with a progress bar) or **Cloud Scans**. If your deployment requires a recorded scan authorization, you are asked for it first — see [Scan authorization](./scan-orchestration.md#scan-authorization).
- **Recurring scans are registered** in the Unified Scheduler: a **daily incremental** scan (02:00 UTC) and a **weekly full** scan (Sunday 03:00 UTC). You can retime or pause them from **Unified Scheduler**. Operators can disable auto-scheduling platform-wide with `CSPM_AUTO_SCHEDULE_ON_ACCOUNT_ADD=false`.
- **Resources appear in [Asset Inventory](./asset-inventory.md)** as discovery jobs complete.
- **Identity analysis** runs for the account in the daily IAM sweep (or on demand from **IAM Analysis**) — see [Identity & Network Posture](./identity-and-network.md).
- **Kubernetes clusters and container registries** in the account are discovered automatically and offered in [Kubernetes Security](../security-scanning/kubernetes/index.md) and [Container Security](../security-scanning/containers/index.md).

## Onboarding a GCP organization

If you run many GCP projects, connect the **organization or a folder** once instead of each project: **Cloud Accounts → GCP Organizations → Add GCP Organization**. Organization onboarding exists for GCP only.

![GCP Organizations tab — connect an org or folder to auto-discover all projects](/img/screenshots/cloud-security/account-setup-gcp-org.webp)

1. **Scope.** Choose **Organization** (recommended) or **Folder**, and enter its ID and a connection name.
2. **Credentials.** Paste the service account JSON key and select **Check readiness**. It probes each required API and role with your key and shows the command to fix anything missing. **Show setup commands** gives the `gcloud` commands to create the service account, enable the APIs on its own project and grant the roles at the organization or folder (the role list is in [Required Permissions](./permissions.md#bucket-a--read-only-scanning)).
3. **Discovery.** Optionally set **Include patterns** (only matching projects) or **Exclude patterns** (comma-separated, wildcards allowed), then **Discover Projects**. Turn individual projects on or off; **Enable all** / **Disable all** act on the filtered list. Google's hidden `sys-*` projects (Apps Script / Forms back ends) are counted as hidden and not onboarded unless an include pattern starting with `sys-` opts them in.
4. **Confirm.** Choose the scan schedule — **Daily**, **Weekly** or **On-demand only** — and select **Connect & Start Scanning**.

Each selected project becomes its own cloud account. The connection card shows the project count and schedule, with **Projects**, **Events**, **Dashboard**, **Re-discover** and **Delete**. Automatic re-discovery runs daily to add new projects and retire ones that disappeared; every change is recorded under **Events**.

:::note[Include patterns win]
When include patterns are set, exclude patterns are ignored, and the include list also applies to projects found by later automatic discovery.
:::

## Provider setup reference

The wizard tells you what to create; the snippets below let you create it with infrastructure-as-code. They match the roles the wizard asks for. The additional reads used by identity, exposure and encryption analysis are listed in [Required Permissions](./permissions.md).

<Tabs groupId="cloud" queryString>
<TabItem value="aws" label="AWS">

### AWS {#aws}

**Cross-account role (recommended).** `SecurityAudit` + `ReadOnlyAccess`, plus a small supplement for native findings ingestion, ECR listing, and the resource-policy and exposure reads that identity and network analysis use.

```hcl
variable "offload_principal_arn" { type = string }   # ask your platform administrator
variable "external_id"           { type = string }   # the value you entered or generated in the wizard

resource "aws_iam_role" "offload_security_scanner" {
  name = "OffloadSecurityScanner"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = var.offload_principal_arn }
      Action    = "sts:AssumeRole"
      Condition = { StringEquals = { "sts:ExternalId" = var.external_id } }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "security_audit" {
  role       = aws_iam_role.offload_security_scanner.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}

resource "aws_iam_role_policy_attachment" "read_only" {
  role       = aws_iam_role.offload_security_scanner.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

resource "aws_iam_role_policy" "offload_supplement" {
  name = "OffloadSecuritySupplement"
  role = aws_iam_role.offload_security_scanner.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "securityhub:GetFindings", "guardduty:ListDetectors", "guardduty:ListFindings",
        "guardduty:GetFindings", "config:GetComplianceSummaryByConfigRule",
        "cloudtrail:LookupEvents", "tag:GetResources",
        "ecr:DescribeRepositories", "ecr:DescribeImages",
        "cloudfront:ListVpcOrigins", "secretsmanager:GetResourcePolicy",
        "dynamodb:GetResourcePolicy", "elasticfilesystem:DescribeFileSystemPolicy",
        "sqs:GetQueueUrl", "s3:GetAccountPublicAccessBlock"
      ]
      Resource = "*"
    }, {
      Effect   = "Allow"
      Action   = "apigateway:GET"
      Resource = ["arn:aws:apigateway:*::/vpclinks", "arn:aws:apigateway:*::/vpclinks/*"]
    }]
  })
}

output "role_arn" { value = aws_iam_role.offload_security_scanner.arn }
```

Paste `role_arn` and the external ID into step 5. For **Access Keys**, attach the same policies to an IAM user and rotate the key regularly. To have service control policies evaluated, also onboard your organization's management account (or a delegated administrator) with the Organizations read permissions in [Required Permissions](./permissions.md#identity-analysis-ciem).

</TabItem>
<TabItem value="gcp" label="GCP">

### GCP {#gcp}

**Service account** with read-only roles (add `artifactregistry.reader` if you will scan Artifact Registry).

```hcl
variable "project_id" { type = string }

resource "google_service_account" "offload_scanner" {
  account_id   = "offload-security-scanner"
  display_name = "Offload Security Scanner (read-only)"
  project      = var.project_id
}

resource "google_project_iam_member" "roles" {
  for_each = toset([
    "roles/viewer", "roles/cloudasset.viewer", "roles/iam.securityReviewer",
    "roles/securitycenter.findingsViewer", "roles/securitycenter.assetsViewer",
    "roles/artifactregistry.reader",
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.offload_scanner.email}"
}

resource "google_service_account_key" "offload_key" {
  service_account_id = google_service_account.offload_scanner.name
}
```

Upload the key JSON in step 5, then delete the local copy. For identity analysis to see inherited folder and organization bindings and IAM deny policies, also grant `roles/iam.securityReviewer`, `roles/browser` and `roles/iam.denyReviewer` at the organization — see [Required Permissions](./permissions.md#identity-analysis-ciem).

</TabItem>
<TabItem value="azure" label="Azure">

### Azure {#azure}

**Service principal** at subscription scope with `Reader`, `Security Reader` and `Log Analytics Reader`.

```hcl
variable "subscription_id" { type = string }

data "azurerm_subscription" "current" { subscription_id = var.subscription_id }

resource "azuread_application"       "offload" { display_name = "Offload Security Scanner" }
resource "azuread_service_principal" "offload" { client_id = azuread_application.offload.client_id }
resource "azuread_application_password" "offload" {
  application_id = azuread_application.offload.id
  display_name   = "offload-scanner-secret"
}

resource "azurerm_role_assignment" "roles" {
  for_each             = toset(["Reader", "Security Reader", "Log Analytics Reader"])
  scope                = data.azurerm_subscription.current.id
  role_definition_name = each.value
  principal_id         = azuread_service_principal.offload.object_id
}

output "client_id"     { value = azuread_application.offload.client_id }
output "client_secret" { value = azuread_application_password.offload.value, sensitive = true }
output "tenant_id"     { value = data.azurerm_subscription.current.tenant_id }
```

Enter tenant ID, client ID, client secret and subscription ID in step 5. To scan ACR images add `AcrPull`. For identity analysis to include role assignments inherited from management groups, also grant `Reader` on the management group above the subscription.

</TabItem>
</Tabs>

## Verify the connection

1. On **Cloud Accounts → Manage Accounts**, the new row shows status **active**. Use **Test Connection** at any time to re-run the provider check.
2. On **Cloud Security → Accounts**, the card shows *Scanning…* until the first run completes, then a **Last Scan** date.
3. Within a few minutes, findings appear on the **Findings** tab and resources in **Asset Inventory**.

If validation fails, the error names the cause — an unassumable role or mismatched external ID on AWS, a disabled API or missing role on GCP, an expired client secret on Azure. Fix it and retry from step 5; see [Troubleshooting](./troubleshooting.md#connection-and-validation) for the common cases.

## Related

- [Required Permissions](./permissions.md) — the exact roles per cloud and per capability.
- [Managing Connected Accounts](./account-management.md) — revalidate, rotate credentials, scan in bulk, remove.
- [Running Cloud Scans](./scan-orchestration.md) — what the first scan does and how to read its progress.
