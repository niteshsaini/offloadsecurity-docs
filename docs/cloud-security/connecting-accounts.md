---
title: "Connecting Cloud Accounts"
sidebar_label: "Connecting Cloud Accounts"
sidebar_position: 1
---

# Connecting Cloud Accounts

To scan your cloud posture, you connect each cloud account (AWS, Azure, or GCP) once. Offload Security stores the credentials **encrypted at rest** and uses **read-only** access to assess configuration, ingest native findings, and build your asset inventory.

![Cloud Security management](/img/screenshots/cloud-security.png)

:::tip[Grant permissions first]
Onboarding most often fails because the service account is missing IAM roles.
See **[Required Permissions](./permissions.md)** for the exact APIs and
roles per capability — cloud/CSPM, asset inventory, Kubernetes, container
registries, and cloud events.
:::

## How connection works

1. In the platform, go to **Cloud Security → Cloud Accounts** (or **Account Setup**) and select **Add Cloud Account**.
2. Choose the provider and enter credentials (details per provider below).
3. The platform runs a **connection test** using the provider SDK (for AWS, an STS `GetCallerIdentity` call) to confirm the credentials and permissions are valid.
4. On success, credentials are encrypted and stored, and an initial posture scan can be kicked off automatically.

:::tip[Least privilege]
Offload Security only needs **read/security-audit** permissions. Never give it write or administrative access. The Terraform below provisions exactly the read-only roles required — nothing more.
:::

---

## AWS

### Option A — IAM role (recommended)
A cross-account IAM **role** with an external ID is the most secure option (no long-lived keys).

**Required permissions** (read-only): `securityhub:GetFindings`, `config:GetComplianceSummaryByConfigRule`, `guardduty:ListDetectors`, `guardduty:ListFindings`, `guardduty:GetFindings`, `ec2:Describe*`, `iam:Get*`, `iam:List*`, `s3:Get*`, `s3:List*`, `rds:Describe*`, `lambda:GetFunction*`, `lambda:List*`, `cloudtrail:DescribeTrails`, `cloudtrail:LookupEvents`, `kms:DescribeKey`, `kms:ListKeys`, `tag:GetResources`. For container (ECR) scanning, also add `ecr:DescribeRepositories` and `ecr:DescribeImages`.

The AWS-managed **`SecurityAudit`** policy covers most of these; the Terraform below uses it plus a small supplement so you stay current as services evolve.

```hcl
# offload-security-aws.tf
variable "offload_principal_arn" {
  description = "The AWS principal Offload Security uses to assume this role (from your tenant settings)"
  type        = string
}

variable "external_id" {
  description = "A unique external ID you also enter in the platform when adding the account"
  type        = string
}

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

# Broad read-only baseline
resource "aws_iam_role_policy_attachment" "security_audit" {
  role       = aws_iam_role.offload_security_scanner.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}

# Supplemental permissions for findings ingestion + container scanning
resource "aws_iam_role_policy" "offload_supplement" {
  name = "OffloadSecuritySupplement"
  role = aws_iam_role.offload_security_scanner.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "securityhub:GetFindings",
        "guardduty:ListDetectors",
        "guardduty:ListFindings",
        "guardduty:GetFindings",
        "config:GetComplianceSummaryByConfigRule",
        "cloudtrail:LookupEvents",
        "tag:GetResources",
        "ecr:DescribeRepositories",
        "ecr:DescribeImages"
      ]
      Resource = "*"
    }]
  })
}

output "role_arn" {
  value = aws_iam_role.offload_security_scanner.arn
}
```

Apply it, then in the platform choose **IAM Role**, paste the `role_arn`, and enter the same `external_id`.

### Option B — Access keys
For a quick start you can use an IAM user's **access key ID + secret** (and optional session token). Attach the same `SecurityAudit` policy + supplement above to the user. Then in the platform choose **Access Keys** and paste the values. Rotate keys regularly.

---

## GCP

Offload Security uses a **service account JSON key** with read-only roles.

**Required roles:** `roles/cloudasset.viewer`, `roles/securitycenter.findingsViewer`, `roles/securitycenter.assetsViewer`, `roles/iam.securityReviewer`, `roles/viewer`. For Artifact Registry scanning, also `roles/artifactregistry.reader`.

```hcl
# offload-security-gcp.tf
variable "project_id" { type = string }

resource "google_service_account" "offload_scanner" {
  account_id   = "offload-security-scanner"
  display_name = "Offload Security Scanner (read-only)"
  project      = var.project_id
}

resource "google_project_iam_member" "roles" {
  for_each = toset([
    "roles/viewer",
    "roles/cloudasset.viewer",
    "roles/securitycenter.findingsViewer",
    "roles/securitycenter.assetsViewer",
    "roles/iam.securityReviewer",
    "roles/artifactregistry.reader",
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.offload_scanner.email}"
}

resource "google_service_account_key" "offload_key" {
  service_account_id = google_service_account.offload_scanner.name
}

# Write the key to a file to upload in the platform (handle securely; delete after upload)
resource "local_file" "key_json" {
  content  = base64decode(google_service_account_key.offload_key.private_key)
  filename = "${path.module}/offload-gcp-sa.json"
}
```

In the platform choose **GCP**, upload the generated `offload-gcp-sa.json` (or paste its contents), and enter your `project_id`.

:::warning[Key hygiene]
Service-account keys are sensitive. Upload the key, then delete the local file. The platform warns when a key approaches its rotation window (60 days) and recommends rotation by 90 days.
:::

---

## Azure

Offload Security uses a **service principal** (`client_id` + `client_secret` + `tenant_id`) scoped to a subscription.

**Required built-in roles:** `Reader` (general read), `Security Reader` (Defender for Cloud findings), `Log Analytics Reader` (activity log + alerts). Optionally `Storage Blob Data Reader`.

```hcl
# offload-security-azure.tf
variable "subscription_id" { type = string }

data "azurerm_subscription" "current" {
  subscription_id = var.subscription_id
}

resource "azuread_application" "offload" {
  display_name = "Offload Security Scanner"
}

resource "azuread_service_principal" "offload" {
  client_id = azuread_application.offload.client_id
}

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

In the platform choose **Azure**, then enter `tenant_id`, `client_id`, `client_secret`, and `subscription_id`.

:::tip[Workload identity]
To avoid managing a client secret, configure a **federated credential** (workload identity) on the application instead. Azure secrets should be rotated within 90 days.
:::

---

## Container registries & Kubernetes

The same cloud credentials also unlock:

- **Container registries** — once an AWS/GCP/Azure account is connected, the platform can discover and scan **ECR**, **GCP Artifact Registry**, and **ACR** repositories. **Docker Hub** is supported with a username + access token (or anonymously for public images). See **[Container Security](../security-scanning/container-security.md)**.
- **Kubernetes clusters** — EKS/GKE/AKS clusters are auto-discovered from connected cloud accounts, and you can onboard any cluster with a read-only kubeconfig or service-account token. See **[Kubernetes Security](../security-scanning/kubernetes-security.md)**.

## Verify the connection

After adding an account:

1. Confirm the status shows **Connected / Active**.
2. Trigger (or wait for) the first posture scan.
3. Review results in **Cloud Security** and the new resources in **[Asset Inventory](./asset-inventory.md)**.

If the connection test fails, see **Troubleshooting** for the most common causes (invalid credentials, missing permissions, or — for IAM roles — a mismatched external ID).
