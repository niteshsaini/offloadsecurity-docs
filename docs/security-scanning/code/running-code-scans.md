---
title: "Running Code Scans"
sidebar_label: "Running Code Scans"
sidebar_position: 2
description: "Scan a repository branch, an uploaded ZIP, a build artifact or a compiled image — choosing SAST, SCA, secrets, IaC, SBOM or all at once — and follow the scan to completion."
---

# Running Code Scans

**Where:** Code Command Center → **New Scan**.

![New Scan tab: source selector (Repository, Upload ZIP, Container Image, Build Artifact), provider tabs, repository and branch pickers, scan type Full Code Security, and the scheduled repository scans panel](/img/screenshots/security-scanning/code-new-scan.webp)

## Choose a source

| Source | Give it | Needs |
| --- | --- | --- |
| **Repository** | Provider (GitHub / Bitbucket / GitLab), repository, branch (picked from the repository's real branches) | A [Git connection](./connecting-repositories.md) |
| **Upload ZIP** | A ZIP of the source tree (up to 500 MB) | Nothing — ideal for vendor code or air-gapped projects |
| **Container Image** | An image reference the platform can pull, scanned with Trivy + Grype + Syft | Registry access for private images |
| **Build Artifact** | A `.jar`, `.war`, `.ear`, `.whl`, `.egg`, `.tgz`, `.gem` or `.nupkg` (up to 200 MB), scanned with Syft + Grype | Nothing |

## Choose a scan type

For a **Repository** source (an **Upload ZIP** has no scan-type choice; it runs the code scanners on the uploaded tree):

| Scan type | Runs | When |
| --- | --- | --- |
| **Full Code Security** (default) | SAST + SCA + Secrets + IaC + SBOM & Licenses (and SonarQube when configured) | Baseline scan of a repository; the scheduled run. |
| **SAST Only** | OpenGrep + Bandit | Fast feedback on code changes. |
| **Secrets Scan** | Gitleaks over the source tree and the last 200 commits of history, each secret validated live against its provider | Before publishing a repository; after an incident. See [Secret Detection](./secret-detection.md). |
| **Dependency / SCA Scan** | OSV.dev CVE scan of every lockfile, enriched with KEV and EPSS | Daily; after a dependency bump. |
| **IaC Scan (Checkov)** | Checkov on Terraform and OpenTofu, CloudFormation, Kubernetes manifests, Helm, Dockerfiles | Infrastructure repositories; before `apply`. |
| **SonarQube Analysis** | Quality gate, code smells, duplication | Only when an administrator has configured a SonarQube server. |
| **SBOM & License Scan** | Syft SBOM + Grype CVEs + licence compliance; the result appears under SBOM & Licenses | Inventory and licence review — see [SBOM & Licences](./sbom-and-licenses.md). |

The **Container Image** and **Build Artifact** sources have their own scan button and run their own tools (above); pair an image scan with the [container CI gate](../containers/governance.md#gate-a-pipeline).

Select **Start Scan**. The scan is queued immediately with a scan ID and runs in the background — clone or unpack, then each engine in turn. Progress shows the current **phase** (`sast`, `opengrep`, `bandit`, `dependencies`, `secrets`, `iac`, `sbom`, `sonarqube`) and a percentage; you can leave the page and pick the result up under **Reports**.

Each repository and ZIP scan records its authorization. By default it is recorded as *authorization not recorded*; a deployment that sets `SCAN_REQUIRE_AUTHORIZATION=true` refuses a scan that carries no authorization attestation (the API's `engagement` field, or a repository's standing authorization) before anything is queued.

A typical small service completes in one to three minutes; large monorepos take longer, dominated by dependency resolution and SAST.

:::note[Where credentials come from]
Repository scans use the team's Git connection; SonarQube results are attached when a SonarQube server is configured under Integrations. Nothing is written back to the repository by a scan — only the optional **Fix PR** action does that, and it is a separate, permissioned step.
:::

## How repository files are treated

A scan reads the repository; it never runs code from it.

- **IaC file names Checkov does not recognize.** Checkov skips Dockerfiles named like `Dockerfile-prod`, `Dockerfile_dev`, `DOCKERFILE` or `Containerfile`, and OpenTofu `*.tofu` files. The scan assesses them through byte-identical copies under names Checkov reads (a `.tofu` file with its module's `.tf` files), including copies in hidden directories, and reports every finding against the original file and line. A copy that cannot be made or assessed in the scan's time budget is disclosed as **not assessed**, and that file's earlier findings stay open.
- **The repository's `.checkov.yaml`.** Only `check`, `skip-check`, `framework`, `skip-framework` and `skip-path` are carried over. Every other key is ignored, including `external-checks-dir` and `external-checks-git`, which would run the repository's Python on the platform. Use the [custom rules](./custom-rules.md) directory for your own IaC policies. When a repository has a Checkov config, Checkov runs after the secrets scan, so a secret in that file is still found.
- **SonarQube.** A `.scannerwork` directory or link committed to the repository is removed before `sonar-scanner` runs, so the platform reads only the report the scanner itself wrote.
- **Paths.** File reads and writes stay inside the scan's workspace; path-traversal and symbolic-link tricks that point out of the checkout are blocked.

## What a scan produces

- **Findings** — one per issue, fingerprinted so re-scans update rather than duplicate: SAST findings carry file, line and code context; SCA findings carry package, installed and fixed versions, CVE, CVSS, EPSS and KEV; secrets carry the detector, location (values are masked), a live-validation badge and, for history-only leaks, the introducing commit; IaC findings carry the resource and the Checkov check. See [Findings & Reports](./findings-and-reports.md).
- **Every finding the tools report**, one record each. The only per-scan limit is a sanity ceiling of 50,000 findings (`CODE_FINDINGS_MAX`); a scan that reaches it is marked truncated in the UI and the PDF, never silently.
- **Custom-rule results** when a [custom rules](./custom-rules.md) directory is mounted — the report records which rules were in force.
- **Run provenance** — what ran and against what: the commit scanned (recorded at checkout, so even a failed scan names it), the branch actually checked out and any fallback to the default branch, scanner versions read from the binaries, the pinned OpenGrep rules commit, the path exclusions in force, the SHA-256 of an uploaded ZIP, and gaps such as git submodules (not scanned) and Git LFS files (scanned as pointer stubs).
- **Coverage, stated per tool.** A tool that could assess only part of the input is reported as **partial coverage** with the reason, not as a failed tool. For example, when npm can resolve only some of a project's dependencies, the scan completes, the resolved dependencies are assessed, and the scan says how many could not be resolved. The quality gate still fails on partial dependency coverage by default ([Gating](./ci-cd-and-automation.md#gating)). A scan finishes **completed with errors** only when a tool actually failed.
- **Each tool's raw output**, kept compressed with its SHA-256 (secret values are stripped first). A storage failure is recorded per tool and never fails the scan.
- **A frozen scan report** — the report, including the triage state at that moment, is frozen when the scan completes; the PDF export renders that frozen copy by default. See [Scan reports](./findings-and-reports.md#scan-reports).
- **An SBOM** (Full or SBOM scans) with licence data, listed under SBOM & Licences.
- **Coverage** — the repository is now *scanned* on the Overview; put it on a schedule so it does not turn *stale*.

## Scheduled repository scans

Below the form, **Scheduled repository scans** lists the repositories on a recurring schedule and lets you add them: one or more repositories, the scan type and the cadence — **Daily**, **Weekly (Mondays)** or **Monthly (1st)** — with **Run once now** to test. Nothing is scheduled unless you add it.

**Branch.** With exactly one repository selected, the **Branch** dropdown lists that repository's real branches, with its default branch first. With several repositories selected, each is scanned on its own default branch. If the branch list cannot be loaded, the form says so rather than showing an empty list.

Scheduled SBOM & licence scans are configured the same way on the SBOM & Licenses tab. Details and pipeline integration in [CI/CD & Automation](./ci-cd-and-automation.md).

## Related

- [Findings & Reports](./findings-and-reports.md) — triage what the scan found.
- [CI/CD & Automation](./ci-cd-and-automation.md) — run the same scans from GitHub Actions, GitLab CI or Jenkins.
- [Scanning API](../api.md#code) — `POST /api/code/scan`, `POST /api/code/upload-scan`, `GET /api/code/scan-status/{scan_id}`.
