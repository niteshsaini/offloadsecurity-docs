---
title: "Registries"
sidebar_label: "Registries"
sidebar_position: 1
description: "Connect AWS ECR, Google Artifact Registry and Azure Container Registry through a connected cloud account, sync and browse images, scan them in bulk, on a schedule or on push, and track drift between syncs."
---

# Registries

A registry connection is how the platform learns which images you actually ship. Once connected, the registry is **synced** (repositories, tags, digests, push dates), its images can be **browsed and scanned** in place, new pushes can be **auto-scanned**, and each sync produces a **drift report** of what appeared, disappeared or changed.

**Where:** Container Security → **Cloud Registries**.

![Cloud Registries tab: three saved registries (Azure ACR, GCP Artifact Registry, AWS ECR) with image and repository counts, severity chips, last sync time, schedule badge, and Browse / Sync / Drift actions](/img/screenshots/security-scanning/ctr-registries.webp)

## Supported registries

| Registry | Connect with | Registry connection |
| --- | --- | --- |
| **AWS ECR** | A connected AWS account | ✓ |
| **Google Artifact Registry** (and legacy GCR) | A connected GCP account | ✓ |
| **Azure Container Registry** | A connected Azure account (service principal) | ✓ |
| **Docker Hub** | — | — |
| **Harbor, Quay, GitLab, JFrog, other OCI registries** | — | — |

A registry connection always authenticates through a cloud account you have already added under **Cloud Accounts**. The **Enter Credentials** option and the **Docker Hub** provider appear in the Add Registry form but cannot be saved in 1.4.0: saving shows *"Manual credentials cannot be persisted yet"*, and a Docker Hub connection test fails with *"Docker Hub registry scanning is not yet supported"*.

For images in any other registry, use [Quick Scan](./image-scanning.md#quick-scan) with the full image reference, or start a `container_image` scan from your pipeline through the API. The platform does not store credentials for those registries, so only images it can pull **without signing in** can be scanned that way.

Pull permission is required to scan: `ecr:GetAuthorizationToken` + read (inside `ReadOnlyAccess`), `roles/artifactregistry.reader`, or `AcrPull` — see [Required Permissions](../../cloud-security/permissions.md#container-registries).

## Add a registry

### Before you begin

- Role with **Manage Container Security**.
- The cloud account that owns the registry is connected under **Cloud Accounts**, and its identity can pull from the registry.
- Azure: the subscription is connected with a **service principal** (client ID + secret). Registry sign-in does not work with a managed-identity connection.

### Steps

1. **Add Registry**, give it a **name** (for example *Production ECR*) and pick the **provider**: AWS ECR, GCP Artifact Registry or Azure Container Registry.
2. Choose **Use Existing Cloud Account** and select the account.
3. **Automation settings** (optional, editable later):
   - **Scan Schedule (cron)** — for example `0 2 * * *` for a nightly scan; leave empty for manual only.
   - **Auto-scan images detected by push webhooks/polling** — sync only discovers; this setting decides whether new images are scanned.
   - **Notify when new images are detected.**
4. **Test Connection**, then save.
5. Select **Sync** on the registry card to list its repositories and images.

Saved registries persist across sessions and appear on the Coverage tab.

## Working with a registry

| Action | What it does |
| --- | --- |
| **Sync** | Re-reads repositories, tags and digests from the registry. Sync **discovers** — it does not scan. ECR images are listed by digest, including untagged images. |
| **Browse** | Opens the repository list: image and tag counts, last push, scan status per image, per-image severity counts, search, and sort by name, image count, latest push or vulnerabilities. Select an image to scan it or open its latest result. |
| **Scan Existing Images** | Shows an estimate (unscanned images, already scanned, total size, estimated time), then queues scans for up to **50** unscanned images per batch. Run it again for the next batch. Over the API the batch can be up to 500 (`max_images`). |
| **Scan Jobs** (inside Browse) | **New Scan Job** scans many images at once, matched by **repository filter** and **tag filter** (regular expressions such as `apps/.*` or `latest\|v1.*`), with the scan tools you choose (Syft, Grype, Trivy). Jobs can be **paused, resumed or cancelled**. |
| **Drift** | The drift report since the previous sync: **new images**, **removed images**, and **vulnerability changes** on images that were re-scanned. |
| **Edit schedule** | Change the cron expression. |
| **Remove** | Deletes the registry connection and its saved image list (scan results are kept). |

![Browsing a registry: repository list for the ACR registry with tag counts, sizes, push dates and a Scan Existing Images action](/img/screenshots/security-scanning/ctr-registry-images.webp)

Registry totals are complete: the vulnerability summary and repository list cover every image and repository in the registry, and a sync that could not read part of a registry stores a warning with how many parts were affected. (Before 1.4.0 both views stopped silently at 1,000.)

## Keeping registries current

- **Webhooks** queue a scan within seconds of a push — set them up under [Registry webhooks](./governance.md#registry-webhooks).
- **Polling** covers registries where you cannot add a webhook: the platform checks for new tags at a set interval and scans them if auto-scan is on. The interval (5 minutes – 24 hours) is set over the API: `PUT /api/container-registries/saved/{registry_id}/polling-config` with `polling_interval_seconds` between 300 and 86400.
- **Scheduled scans** re-scan what you already have so newly published CVEs show up on old images.

:::tip[Scope before you scan]
A production registry can hold thousands of tags. Use a scan job's repository and tag filters (for example only `v*` tags of `apps/*`) and let the schedule handle the rest — scanning every historical tag adds noise, not safety.
:::

## Registry sweeps report what they covered {#sweep-coverage}

A comprehensive registry sweep (`POST /api/container-security/scan-registry`) scans up to **25 images per registry** by default (`CONTAINER_SWEEP_MAX_IMAGES`, or `max_images_per_registry` in the request). It never presents a partial sweep as complete:

- The sweep records its coverage: images **listed**, **selected**, **scanned**, **partial**, **failed** and **not scanned**. Images beyond the limit, or beyond the sweep's time budget, are listed as not scanned and the run is kept.
- A sweep that fell short is marked **degraded**.
- Each image gets a status from what its tools returned: **completed**, **partial** (one engine failed) or **failed**. An image whose engines both failed is never counted as analysed, and its earlier findings are marked *not re-evaluated* rather than resolved.
- When the sweep had to assume a `:latest` tag, it says so.

Bulk scans from **Scan Existing Images** also keep their outcome on the registry: how many images remain and how many failed to start.

## Limits

- ECR sign-in uses the access keys stored on the AWS account. For an account connected with a cross-account role, it uses the platform host's own AWS identity instead of that role. Use an access-key account for ECR, or ask your administrator.
- A Quick Scan of a private ECR, Artifact Registry or ACR image without a linked account uses the first cloud account of that provider found for you.

## Related

- [Image Scanning](./image-scanning.md) — what a scan produces and how to read it.
- [Policies, Webhooks, SBOM & Compliance](./governance.md) — auto-scan on push and gate what deploys.
- [Connecting Cloud Accounts](../../cloud-security/connecting-accounts.md) — the accounts registries authenticate through.
