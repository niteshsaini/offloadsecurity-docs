---
title: "Policies, Webhooks, SBOM & Compliance"
sidebar_label: "Policies, Webhooks, SBOM & Compliance"
sidebar_position: 3
description: "Gate deployments with image policies (in the UI and from CI), auto-scan on registry push, keep CycloneDX/SPDX SBOMs per image, and issue frozen CIS Docker, NIST, PCI DSS and SOC 2 reports."
---

# Policies, Webhooks, SBOM & Compliance

Scanning tells you what is in an image. These four tabs turn that into control: **policies** decide what may deploy, **webhooks** make sure every new image is scanned, **SBOMs** keep the inventory auditors and customers ask for, and **compliance reports** express image posture in framework terms.

## Image admission policies

**Where:** Container Security → **Image Policies**.

![Image Policies tab: quick-start templates (Production – Strict Security, Development – Permissive, CI/CD Pipeline Validation), an active Production – Strict Security policy, and the validate-image form](/img/screenshots/security-scanning/ctr-image-policies.webp)

A policy is a set of rules an image must satisfy. The create form sets **Max Critical Vulnerabilities**, **Max High Vulnerabilities** and **Max Image Age (days)**; starting from a template also carries the template's other rules.

| Rule | Effect | Set from |
| --- | --- | --- |
| **Max critical / high vulnerabilities** | Violation when the count is over the limit, or when the count is unknown (the image was not scanned). | Form, templates |
| **Max image age** | Warning only, never a violation. | Form, templates |
| **Allowed / blocked registries** | Violation when the registry host does not match (exact, glob such as `*.amazonaws.com`, domain suffix, or dotted-label match). | Templates, API |
| **Block `latest` tag** | Violation for `:latest` or an untagged reference. | Templates, API |
| **Allowed tag pattern** | Violation when the tag does not match the regular expression (for example semantic versions). | Templates, API |
| **Required labels** | Violation for each missing label. | Templates, API |
| **Require signature** | Violation unless the request says the image is signed. | Templates, API |

**Quick Start from Template** offers **Production - Strict Security**, **Development - Permissive** and **CI/CD Pipeline Validation**. Adjust the thresholds and save. Policies are team-scoped.

:::warning[Limits of the policy engine in 1.4.0]
- **Medium counts are not enforced.** The *Production - Strict Security* template stores a `max_medium_vulns` value, but no rule evaluates it.
- **Require signature is not verified.** The policy engine reads an `is_signed` value from the request; it does not run cosign. The CI gate below always sends `is_signed: false`, so a policy that requires a signature **fails every CI check**. Verify signatures separately with `POST /api/container-security/image/verify-signature` (see [Image Scanning — Other image checks](./image-scanning.md#other-image-checks-api-only)).
- There is no enable/disable control in the UI; a policy shows **Active** unless it was disabled over the API.
:::

**Validate Image Against Policies** takes an image name plus the critical and high counts you enter and returns pass/fail with every violated rule. It does not look up a scan for you.

The **AI Policy Assistant** asks the AI assistant for recommended production policies, a gap analysis of your current policies, or an optimization review.

### Gate a pipeline

One call scans an image and validates it against the team's policies:

```bash
curl -s -X POST "$OFFLOAD_HOST/api/container-security/cicd/scan-and-validate" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "image_name": "418272957165.dkr.ecr.us-east-1.amazonaws.com/payments-api:2.14.1",
    "build_id": "'"$CI_PIPELINE_ID"'",
    "git_commit": "'"$CI_COMMIT_SHA"'",
    "fail_on_policy_violation": true
  }'
```

The gate scans the image with **Trivy**. The response carries `scan_results`, `policy_validation` (each rule and whether it passed), `allowed` and an `exit_code` (0 pass, 1 fail) you can return from the step. The gate **fails closed**: when the scan did not complete, the vulnerability counts are unknown and any policy with a vulnerability limit reports a violation. Pair it with the code-side gates in [CI/CD & Automation](../code/ci-cd-and-automation.md).

## Registry webhooks

**Where:** Container Security → **Webhooks**.

![Registry Webhooks tab: empty state with Add Webhook and View Events actions](/img/screenshots/security-scanning/ctr-webhooks.webp)

A webhook turns a push into a scan. **Add Webhook**, choose the **Registry Type** (**AWS ECR, Google GCR, Google Artifact Registry, Azure ACR, Docker Hub** or **Generic**), name it, set the **severity filter** and whether to **auto-scan on push**. The platform returns a **callback URL** (`…/api/container-security/webhooks/registry-event/{webhook_id}`).

Every delivery must prove where it came from; by default an unverified delivery is rejected:

| Registry type | How a delivery is verified | Where to configure |
| --- | --- | --- |
| **ECR** | AWS SNS message signature | EventBridge rule on `ECR Image Action` (`PUSH`) → SNS topic → HTTPS subscription to the callback URL |
| **GCR / Artifact Registry** | Google Pub/Sub push token (OIDC) | Pub/Sub topic `gcr` → push subscription with authentication enabled, to the callback URL |
| **ACR, Docker Hub, Generic** | HMAC-SHA256 of the body with the webhook's signing secret, in `X-ACR-Signature`, `X-Hub-Signature-256` or `X-Webhook-Signature` (`sha256=<hex>`) | The sender must compute the signature for each delivery |

The expected SNS topic ARN and the Pub/Sub audience and service account can be pinned when the webhook is created over the API (`POST /api/container-security/webhooks/configure`: `sns_topic_arn`, `pubsub_audience`, `pubsub_service_account`). For HMAC types, the signing secret is returned in that API response; the UI shows it masked.

:::note[Docker Hub and ACR deliveries]
Docker Hub and ACR send their own webhook deliveries without a per-message HMAC signature, so a direct delivery from them is rejected. Route them through a sender that signs the body with the webhook secret.
:::

Each verified delivery is recorded under **Recent Webhook Events**, and — when **auto-scan on push** is on for the webhook — queued as a scan of the pushed image. A repeated delivery for an image already being scanned does not queue a second scan. Webhooks can be paused with the toggle without deleting them. Registries that cannot call out use **polling** instead ([Registries](./registries.md#keeping-registries-current)).

When your deployment requires a recorded authorization for every scan (`SCAN_REQUIRE_AUTHORIZATION=true`), a webhook or polling scan of a registry without a current authorization is skipped and logged, never run silently — see [Scan Records & Evidence](./scan-evidence.md#who-authorized-the-scan).

## SBOM lifecycle

**Where:** Container Security → **SBOM**.

![SBOM tab: generate form (image name, format), and SBOM records for node:18-alpine (222 packages) and nginx:1.25.3 (151 packages) with View and Delete](/img/screenshots/security-scanning/ctr-sbom.webp)

Generate a Software Bill of Materials for any image in **Syft JSON**, **SPDX JSON** or **CycloneDX JSON**. Generation runs in the background; **Refresh** updates the list, and each record shows status, package count and, when known, the distribution. **View** opens the contents (the on-screen preview shows the first 5,000 characters); **Download JSON** gives the complete document.

The list also includes SBOMs produced by code-security scans in the Scanning module, for the current team. Those can be viewed here but not deleted. A Full Analysis scan also produces an SBOM, shown with that scan.

For source-code SBOMs with licence analysis, see [SBOM & Licences](../code/sbom-and-licenses.md) in the Code Command Center.

## Compliance reports

**Where:** Container Security → **Compliance**.

![Compliance tab: security posture trend chart, the container compliance report form (target ID, target type, framework, Generate and Latest) and the supported frameworks, starting with CIS Docker Benchmark 1.6.0 and NIST 800-53 Rev 5](/img/screenshots/security-scanning/ctr-compliance.webp)

- **Security Posture Trend** — total findings per scan over time.
- **Container Compliance Report** — choose a **target type** (**Account**, **Registry** or **Image**), the **target**, a **framework** (**CIS Docker Benchmark 1.6.0**, **NIST 800-53 Rev 5**, **PCI-DSS v4.0**, **SOC 2**) and generate. The report scores the mapped controls against the latest completed scan of each image in the target, listing controls assessed, passed and failed. Controls the scanners cannot observe are reported as *not assessed* rather than passed.

### What a report is made of {#report-manifest}

Each report states its inputs:

- **Scan manifest** — every scan the report used: image, digest, whether it was digest-pinned, tools, scan health, base OS, vulnerability-database age, secrets.
- **Coverage statement** — what weakens the result: scans that could not be read, tag-only scans, degraded scans, a stale vulnerability database, an end-of-support base OS, and the cap of 50 findings listed per control.

### Frozen when issued {#frozen-reports}

When a report is issued (new in 1.4.0), the exact findings it graded are frozen in object storage with a SHA-256 and a `report_id`. Re-opening an issued report returns it exactly as issued; if the frozen findings no longer match their hash, the platform refuses with an error (HTTP 409) rather than serve altered evidence. If freezing fails, the report says so.

| Task | Endpoint |
| --- | --- |
| Report on one past scan (not the latest) | `POST /api/container-security/compliance-report` with `scan_id` |
| List issued reports for the team | `GET /api/container-security/compliance-report/history?target_id=&limit=&skip=` |
| Open an issued report exactly as issued | `GET /api/container-security/compliance-report/{report_id}` |
| Latest report for a target (team-scoped) | `GET /api/container-security/compliance-report/latest?target_id=&framework=` |

Report history, past-scan reports and issued-report retrieval are API-only in 1.4.0.

:::tip[Registry-level reports]
Choose target type **Registry** to get one report across every scanned image in a registry — the view an auditor wants for "all production images", instead of one report per tag.
:::

## Related

- [Image Scanning](./image-scanning.md) — the scans these controls act on.
- [Scan Records & Evidence](./scan-evidence.md) — authorization, provenance and verifiable exports.
- [Registries](./registries.md) — schedules and polling for registries without webhooks.
- [CI/CD & Automation](../code/ci-cd-and-automation.md) — pipeline gates for code and images together.
