---
title: "Troubleshooting & FAQ"
sidebar_label: "Troubleshooting"
sidebar_position: 11
---

# Troubleshooting & FAQ

Most problems in Offload Security come down to one of a few things: a credential or permission that's slightly off, a target that doesn't match what you typed, or a scan that ran out of time. This page walks through the issues people hit most often, framed as **symptom → likely cause → fix** so you can get unblocked quickly.

:::tip Read the status and warnings first
Before you dig in, open the scan and check its **status** and any **warnings**. The platform deliberately surfaces a **Partial** or **Failed** status (rather than a misleadingly clean "green" run) and attaches a plain-language reason whenever it can. That note is usually the fastest path to the fix.
:::

---

## Scans

### A scan completed but shows no findings

**Likely cause.** The run may not have fully succeeded, even though it looks finished. A scan can end as **Partial** (some jobs succeeded, some failed) or **Failed** (everything failed) — and a partial run with the failing half missing can look empty.

**Fix.**
1. Open the scan and check its **status**. In your scan results view, the **Failed** tab lists runs that errored or were rejected; the **Completed** tab holds genuinely successful runs.
2. If the status is **Partial**, expand the scan and read its **warnings**. For cloud scans you can also expand the **per-region** breakdown to see exactly which region or check failed.
3. If the status really is **Completed** with zero findings, that's a clean result — nothing was wrong with the resources or target you scanned. Confirm you scanned the target you intended (right account, right regions, right image).

:::note "Partial" almost always means permissions or API limits
For cloud scans, the two most common causes of a partial result are a **missing read permission** for a service or region, or **API rate limits** in your cloud account. Check the scan's warnings, then revisit the IAM role or service account from [Connecting Cloud Accounts](./cloud-security/connecting-accounts.md).
:::

### A scan is stuck on "Running" or seems to hang

**Likely cause.** Heavier profiles legitimately take a while (a Comprehensive web scan can run 15–20 minutes; a full multi-region cloud scan longer still). It may simply be in progress.

**Fix.**
- Open the **Running** tab in your scan results — it refreshes on its own so you can watch progress. Cloud scans show an **overall percentage**, separate **discovery** and **compliance** progress, and an **estimated completion time** that scales with the number of regions.
- If you started a cloud scan and got a message that one is **already in progress**, that's expected: only **one scan per cloud account per team** can run at a time. Wait for the running scan (its ID and status are shown) to finish, or cancel it.
- If a scan stays stuck far past its estimate, your team can be notified about stuck scans where that's configured; otherwise cancel it and re-run.

### A scan times out

**Symptom.** The scan fails with a timeout, often on a large upload (a big code ZIP or API spec) or a long-running cloud validation.

**Likely cause.** The request exceeded the time limit for that kind of work, or — heavy profiles aside — the target was slow to respond.

**Fix.**
- For **code/SBOM uploads**, keep within the documented size limits (code archives up to **500 MB**, SBOM files up to **25 MB**) and retry; oversized or very slow uploads are the usual culprit.
- For **active scans**, start with a lighter **profile** (for example **Standard** instead of **Comprehensive**, or a **Quick** cloud scan) to confirm the target responds, then scale up.
- For **cloud scans**, scan **fewer regions** at once. Coverage is split per region, so narrowing the region list shortens the run.
- If you're triggering scans through a reverse proxy or load balancer of your own, make sure its read timeout is generous enough for long scans; the platform's longer operations (cloud validation, large uploads) are designed to run for several minutes.

### "Unsupported scan type" (or the scan type isn't accepted)

**Likely cause.** The `scan_type` (or assessment type) you passed isn't valid for that target.

**Fix.**
- For **cloud scans**, use a supported scan type: **`full`** (or **`incremental`**). A **full** scan re-runs every check across the default regions; an **incremental** scan focuses on what changed.
- For **native scans**, pick the **Assessment Type** from the launcher rather than typing a free-form value — Web Vulnerability (ZAP), Nuclei, Security Headers, Network Discovery (Nmap), SSL/TLS, or API Security. Each expects a specific kind of target (a URL, a host/CIDR, or a hostname + port).
- For **container scans**, the valid types are **Vulnerabilities** (CVEs only) and **Full Analysis** (CVEs plus SBOM, secrets, and misconfigurations).

---

## Cloud connections

### The connection test fails when I add a cloud account

When you add an account, the platform runs a **connection test** (for AWS, an STS `GetCallerIdentity` call) before saving. If it fails, the account isn't connected. Work through these in order:

**1. Invalid credentials.**
The keys, service-account JSON, or service-principal secret are wrong or expired.
- *Fix:* Re-check the values you pasted, regenerate them if needed, and confirm the secret hasn't expired or been rotated out. The platform warns when a credential approaches its rotation window — a stale key can fail silently.

**2. Missing permissions.**
The identity is valid but lacks the **read-only** access the platform needs.
- *Fix:* Attach the documented permissions — for AWS the managed **`SecurityAudit`** policy plus the supplemental read permissions; for GCP the viewer/security-reviewer roles; for Azure **Reader**, **Security Reader**, and **Log Analytics Reader**. The exact lists and ready-to-apply Terraform are in [Connecting Cloud Accounts](./cloud-security/connecting-accounts.md). The platform only ever needs **read** access — never grant write or admin.

**3. Mismatched external ID (AWS IAM role).**
For the recommended IAM-role option, the **external ID** you entered in the platform must exactly match the one in the role's trust policy.
- *Fix:* Compare the two values character for character and make sure the role's trust policy also allows the platform's principal to assume it. A mismatch here is the single most common IAM-role failure.

:::warning Read-only, always
Offload Security only reads your environment and stores credentials **encrypted at rest**. If a connection works but a later scan returns a **Partial** result, that's typically a *specific* permission gap (one service or region), not a broken connection — check the scan's warnings.
:::

### A connected account shows no assets or findings

**Likely cause.** The connection is fine, but the scan covered different regions than where your resources live, or it hasn't run yet.

**Fix.**
- Trigger (or wait for) the first **posture scan**, then check **Cloud Security** and **[Asset Inventory](./cloud-security/asset-inventory.md)**.
- A default scan covers a curated set of major regions. If your resources are elsewhere, **specify the exact regions** when you start the scan so they're included.

---

## Container scanning

### A container scan finds nothing (or fails to pull the image)

**1. Wrong image reference.**
The image name or tag doesn't resolve.
- *Fix:* Enter a full image reference including the tag, for example `nginx:latest`, `alpine:3.18`, or a registry-qualified path like `myregistry.example.com/team/app:1.4.2`. A typo or a missing/incorrect tag means there's nothing to scan.

**2. Private registry not authenticated.**
Quick Scan works for **public** images with no setup, but a **private** image needs access.
- *Fix:* Connect the registry first on the **Cloud Registries** tab (or connect the underlying AWS/GCP/Azure account, which lets the platform discover and pull from ECR, Artifact Registry, and ACR automatically). For Docker Hub, provide a username and access token. See [Container Security](./security-scanning/container-security.md).

**3. Wrong account scope (`cloud_account_id`).**
When scanning a registry tied to a cloud account, the scan must reference the correct connected account.
- *Fix:* If you're driving scans by registry or account, make sure you're pointing at the **cloud account ID** that actually owns that registry. You can find these IDs in the **Cloud Accounts** and **Container Registries** sections. Pointing at the wrong account means the platform authenticates against a registry that doesn't contain your image.

:::tip Confirm with a public image first
If a private scan won't run, try a known public image (like `nginx:latest`) in **Quick Scan**. If that works, the problem is registry access — not the scanner.
:::

---

## CI/CD and API access

### My pipeline gets a 401 Unauthorized

**Likely cause.** The API key is missing, malformed, sent in the wrong header, expired, or out of scope.

**Fix.**
1. **Send the key in the right header.** Use the **`X-API-Key`** header — not an `Authorization: Bearer` header.
2. **Use a valid, current key.** Keys start with the **`osk_`** prefix and the full value is shown **only once** when you create it, so make sure your pipeline has the complete key stored as a secret. If the key was rotated, switch to the new one (rotation includes a short grace period, but the old key does eventually retire).
3. **Check the key's scope.** A key can only do what it's scoped for. To trigger scans it needs the scan-trigger scope; to read results it needs the read scope. A key without the right scope is rejected even though it's authentic.
4. **Check IP allowlisting.** If the key is restricted to specific IP addresses, calls from any other address are blocked. Confirm your CI runner's egress IP is on the list.

:::note Where to manage keys
Create, scope, rotate, and IP-restrict API keys under **Team Management**. For setup and pipeline examples, see [RBAC, API Keys & Team Management](./authentication/rbac-team-management.md).
:::

### My pipeline gets a 403 (authenticated but forbidden)

**Likely cause.** The key authenticated, but it lacks permission for that specific action, or you're targeting another team's data.

**Fix.** Grant the key the scope the action requires, and confirm the key belongs to the **team** whose data you're acting on. Every key — like every user — is scoped to a single team's data.

---

## General tips

- **Confirm your active team.** Everything you create is recorded under your **active team** (top-right account menu). "Missing" data is often just data sitting in a different team — switch teams and check again.
- **Re-run with the same settings.** From a completed run, use **Re-scan** to repeat it without re-entering the target. If you re-run the same target often, turn it into a **schedule** instead.
- **Remember retention.** Old scan data is summarized, archived, and eventually deleted on a schedule. If a much older run looks thinner than expected, it may have been summarized; if it's gone entirely, it aged past the delete threshold. See [Scan Management & Scheduling](./security-scanning/scan-management.md).

---

## Related

- [Connecting Cloud Accounts](./cloud-security/connecting-accounts.md) — credentials, permissions, and the external-ID setup for AWS, GCP, and Azure.
- [How Cloud Scans Run](./cloud-security/scan-orchestration.md) — scan statuses, the meaning of "Partial," and per-region progress.
- [Container Security](./security-scanning/container-security.md) — scanning images from public and private registries.
- [Scan Management & Scheduling](./security-scanning/scan-management.md) — scan history, re-running, scheduling, and retention.
- [Authentication & Access](./authentication/index.md) — API keys, teams, and how access is enforced.
