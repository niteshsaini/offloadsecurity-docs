---
title: "Image Scanning"
sidebar_label: "Image Scanning"
sidebar_position: 2
description: "Scan images by digest with Syft, Grype and Trivy, read vulnerabilities with fix versions, understand reused and superseded results, export, and grade Dockerfiles before you build."
---

# Image Scanning

Three ways to scan: **Quick Scan** for any image reference the platform can pull, registry scans for the images you already synced ([Registries](./registries.md)), and **Compiled Image Scan** from the Code Command Center for the image a pipeline just built. Results land on the **Scan Results** tab.

## Quick Scan

**Where:** Container Security → **Quick Scan**.

:::warning[Known issue in 1.4.0: Quick Scan fails on on-premises installs]
Quick Scan runs its scanners inside the API service, which has no Docker access in the on-premises deployment, so every Quick Scan ends **failed** with *Cannot connect to the Docker daemon*. Scan an image by reference on the scan workers instead: `POST /api/container-registries/scan-image` with `{ "image_uri": "nginx:1.27" }`. The results appear under **Scan Results** like any other image scan.
:::

![Quick Scan tab: SBOM / vulnerability detection / real-time integration cards, container image name field and scan type selector](/img/screenshots/security-scanning/ctr-quick-scan.webp)

1. Enter the **image reference** — `nginx:1.27`, `ghcr.io/org/app:2.4.0`, or a full registry path such as `<account>.dkr.ecr.<region>.amazonaws.com/app:1.4`. Public images work without setup. Private ECR, Artifact Registry and ACR images use a connected cloud account; images in other private registries cannot be pulled.
2. Pick the **scan type**:

   | Type | Runs | Use when |
   | --- | --- | --- |
   | **Full Analysis** (recommended) | Syft SBOM + Trivy vulnerabilities, recommendations | Default — what you need to decide whether an image may ship. Runs in the background. |
   | **Vulnerabilities** | Trivy CVE scan with fix versions | Fast check of a base image. |

3. **Start Security Scan.** The result opens on **Scan Results**; a Full Analysis appears there when it completes.

For an SBOM only, use the [SBOM tab](./governance.md#sbom-lifecycle) instead.

:::warning[Prefer Full Analysis]
A **Vulnerabilities** scan whose scanner failed can show zero counts instead of a failure. Full Analysis and registry scans mark a scan whose vulnerability engines all failed as **failed**, never as a clean zero.
:::

## Registry scans

Registry scans (Browse → Scan, **Scan Existing Images**, scan jobs, schedules and webhooks) run three tools by default: **Syft** for the SBOM and two vulnerability engines, **Grype** and **Trivy**. Results are normalized to the same shape whichever engine reported them.

### One digest, every tool {#digest-pinning}

Before any tool runs, the image tag is resolved **once** to its content digest (`sha256:…`), and Syft, Grype and Trivy all scan that exact digest. A tag that moves between tools can no longer produce a mixed result.

- For a multi-architecture image, the scan records the index, its platforms, and the platform that was scanned.
- If the digest cannot be resolved, the scan says so (*not digest-pinned*) rather than inventing one.
- The scan record, stored results and each finding carry the digest.

### A moved tag supersedes, it does not "fix" {#moved-tag}

Each new scan is compared with the image's most recent **completed** scan. When the tag now points at a different digest, the old image's findings are marked **superseded** (reason: the image digest changed) — not resolved — because the old build may still be running somewhere. A clean completed re-scan of the same digest retires the same tools' earlier findings. Use [Image Rollout](./rollout.md) to check whether the old build is still deployed.

### Results reused by image digest {#digest-reuse}

A digest is immutable, so scanning it again with the same scanner builds against the same vulnerability databases gives the same answer. The platform can reuse the earlier result instead of pulling and scanning again.

:::note[Shadow mode by default]
Digest reuse ships in **shadow** mode (`CONTAINER_DIGEST_REUSE=shadow`): every scan still runs in full and the full result is what you see. The platform only records what reuse *would* have returned, so administrators can confirm it matches before turning it on (`on`). `off` disables the lookup.
:::

When an administrator sets it to `on`:

| Situation | What happens |
| --- | --- |
| Same team, same digest, same scanner versions and vulnerability databases, earlier full scan less than 168 hours old (`CONTAINER_DIGEST_REUSE_MAX_AGE_HOURS`) | Earlier results reused — no pull, no scan. Badge **Reused**. |
| Only Grype's database changed and the earlier scan has a Syft SBOM | Grype re-matches the stored SBOM against the current database. Badge **Re-matched**. |
| Anything else (new digest, unpinned tag, scanner upgrade, changed Trivy database, any error) | Full scan. |

A reused result shows a blue banner naming the scan it came from and when. Secrets and base-OS results in it are as of that original scan. Reuse never crosses teams, and results for one platform of a multi-arch image never serve another.

## Reading a result

**Where:** Container Security → **Scan Results** → **View Details**.

![Scan Results tab listing nginx:1.25.3, python:3.9-slim, node:18-alpine and alpine:3.17 full-analysis scans with per-severity counts and View Details buttons](/img/screenshots/security-scanning/ctr-scan-results.webp)

![Expanded scan detail for alpine:3.17: vulnerability summary by severity (26 total), risk score, JSON / CSV / SBOM export and AI Summary](/img/screenshots/security-scanning/ctr-scan-detail.webp)

Read any banner first:

| Banner | Meaning |
| --- | --- |
| Red — **Scan failed — no vulnerability results** | Nothing was assessed. The error text names the cause. |
| Amber — **Partial scan — one or more tools failed** | Counts are incomplete; the findings that were seen are kept. |
| Blue — **Results reused** / **Package inventory reused** | Served from an earlier scan of the same digest (see above). |

| Section | What it tells you |
| --- | --- |
| **Vulnerability Summary** | Counts by severity (critical / high / medium / low / negligible), total, a **risk level** and **risk score**. Negligible is not reported by these scanners and shows 0. |
| **Top Vulnerabilities** | The first 20 vulnerabilities: CVE, package, severity and **Fix Available** — the version(s) that fix it. No *Fix Available* line means the scanner reported no fixed version. |
| **Software Bill of Materials** | Total packages and the first 50 packages of the inventory. |
| **Recommendations** | Plain-language next steps — upgrade the base image, pin versions, drop packages. |
| **Exports** | **JSON** (full result), **CSV** (vulnerability table), **SBOM** (CycloneDX), and an **AI Summary** for a ticket or a release note. The exports contain every vulnerability. |

**Risk score** = 25 per critical + 10 per high + 3 per medium, capped at 100. 75 or more is Critical risk, 50 High, 25 Medium, below that Low. It ignores Low findings and whether a fix exists.

Every export is fingerprinted and recorded so it can be verified later — see [Scan Records & Evidence](./scan-evidence.md#verifiable-exports).

To see what changed between two scans of an image (new, fixed and superseded CVEs), use the compare API described in [Scan Records & Evidence](./scan-evidence.md#compare-two-scans). The **Security Posture Trend** on the Compliance tab plots total findings per scan over time.

:::tip[Fix the base image first]
Most of an application image's CVEs come from its base. Compare `python:3.9-slim` (1,200+ findings in the example above) with a current slim or distroless base before chasing individual packages.
:::

## Dockerfile scanning

**Where:** Container Security → **Dockerfile Scan**.

Paste a Dockerfile and select **Scan Dockerfile** to get a graded result in seconds — before anything is built.

![Dockerfile Security Scanner: a pasted Dockerfile, Grade F with 8 findings, and rule cards such as DS004 (secrets in ENV, critical) with the fix](/img/screenshots/security-scanning/ctr-dockerfile-scan.webp)

Two linters run on every Dockerfile: the platform's 14 native rules below, and **Hadolint** (2.15.1). The rule cards list the native findings; Hadolint's findings are added to the total and returned in full by the API (`POST /api/container-security/dockerfile/scan`, field `hadolint`).

| Rule | Severity | Checks |
| --- | --- | --- |
| **DS001** | High | Container runs as root |
| **DS002** | Medium | `latest` tag on the base image |
| **DS003** | Medium | `ADD` used where `COPY` is safer |
| **DS004** | **Critical** | Secrets in `ENV` instructions |
| **DS005** | Medium | Missing `HEALTHCHECK` |
| **DS006** | Low | Unnecessary `EXPOSE`d ports |
| **DS007** | Low | No multi-stage build |
| **DS008** | Low | `apt-get` / `apk` without `--no-cache` or cleanup |
| **DS009** | Medium | Unpinned package versions |
| **DS010** | High | `sudo` in the image |
| **DS011** | Medium | Privileged ports |
| **DS012** | Medium | `apt-get upgrade` in the build |
| **DS013** | High | No non-root `USER` before `CMD` / `ENTRYPOINT` |
| **DS014** | Medium | `VOLUME` on sensitive paths |

Each finding shows the line, the rule and the fix. Dockerfiles committed to a repository are also covered by the **IaC** scan in the Code Command Center (Checkov's Dockerfile checks).

:::note[Fixed in 1.4.0]
Before 1.4.0 the Hadolint step failed on every Dockerfile, so only the native rules were applied. It now runs.
:::

## Other image checks (API only)

| Check | Endpoint | Notes |
| --- | --- | --- |
| Secrets in image layers (TruffleHog 3.97.9) | `POST /api/container-security/image/secrets` (`{ "image", "only_verified"? }`) | Returns detector type, file path and layer digest with a masked sample — never the secret value. An image TruffleHog could not read is reported as a failed scan, not as "no secrets". |
| Signature verification (cosign 3.1.3) | `POST /api/container-security/image/verify-signature` (`{ "image", "identity"?, "oidc_issuer"? }`) | Read-only `cosign verify`. Without `identity` / `oidc_issuer` any valid Sigstore signature passes; set both for production. Not connected to image policies — see [Require signature](./governance.md#image-admission-policies). |

## Related

- [Registries](./registries.md) — scan the images you actually ship, on a schedule or on push.
- [Scan Records & Evidence](./scan-evidence.md) — what each scan records; compare two scans; verify an export.
- [Policies, Webhooks, SBOM & Compliance](./governance.md) — turn scan results into a deploy gate.
- [Running Code Scans — Compiled Image Scan](../code/running-code-scans.md) — scan the image a pipeline just built.
