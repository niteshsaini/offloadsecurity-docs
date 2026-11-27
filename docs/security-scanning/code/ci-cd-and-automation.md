---
title: "CI/CD & Automation"
sidebar_label: "CI/CD & Automation"
sidebar_position: 6
description: "Put code scans on a schedule, generate a ready-to-commit GitHub Actions workflow (other CI systems from the API), and gate pull requests and releases on the team quality gate."
---

# CI/CD & Automation

Scans you have to remember to run are scans that stop happening. The Automation tab keeps repositories on a **schedule**, and the **CI/CD Pipeline** generator produces the job that scans every build and fails it on your terms. For the per-change review with comments on the diff — GitHub, GitLab and Bitbucket — see [Pull Request Review](./pull-request-review.md). The full REST contract, the GitHub Action, SARIF export and release-gate policy live in [CLI & CI/CD](../../cli-and-cicd.md); this page is the Code Command Center side of it.

**Where:** Code Command Center → **Automation** — **Git Connections**, **PR Review**, **GitHub App** and **CI/CD Pipeline** — and the *Scheduled repository scans* panel under **New Scan**.

## Scheduled scans

Two schedule types keep coverage current without pipelines:

| Schedule | Set from | Cadence |
| --- | --- | --- |
| **Repository scans** | New Scan → *Scheduled repository scans* | **Daily**, **Weekly (Mondays)**, **Monthly (1st)** — per repository and scan type; pick a branch from the real branch list when one repository is selected (otherwise each repository's default branch); **Run once now** to test |
| **SBOM & licence scans** | SBOM & Licenses → *Scheduled SBOM & license scans* | Same cadences; keeps licence and dependency intelligence fresh for repositories that do not change often |

The Overview's coverage tiles count scheduled repositories. Its cards — **Top Repositories by Severity**, **Coverage Decay** (code pushed after the last scan), **Most Active Repositories** and **Stale Repositories** (no push in 90 days) — each show their full count and open the complete ranked list of repositories in that category, with search, filters, sorting and paging. When repositories are not covered, **Scan N most-active uncovered** queues scans for up to 10 of them. Schedules are also visible in the platform-wide [Unified Scheduler](../scan-management.md).

## Generate a pipeline

**Where:** Automation → **CI/CD Pipeline**.

![CI/CD Pipeline Integration: API URL, scan types to include (Full Code Security, SAST, Dependency/SCA, Secrets, IaC, SBOM, Compiled Image Scan), optional Docker image, security quality gate toggle, and the Generate GitHub Actions (Multi-Job) button](/img/screenshots/security-scanning/code-cicd-pipeline.webp)

1. Confirm the **OffloadSecurity API URL** your runners can reach.
2. Tick the **scan types** to run on each build; add the **Docker image name** (leave it empty to use `repo:commit-sha`) to include a compiled-image scan.
3. Leave **Enable Security Quality Gate** on to fail the pipeline on critical findings.
4. Optionally tick **Also upload results to GitHub Code Scanning** (off by default). On a private repository this needs GitHub's paid Code Security add-on; without the upload, the findings are still in Offload and the SARIF file is kept as an artifact on each workflow run.
5. Select **Generate GitHub Actions (Multi-Job)**. Follow the *Setup Instructions* shown with the workflow: create an API key with the `ci_cd_full` preset, store it as `OFFLOAD_API_KEY` in the repository's Actions secrets, set `OFFLOAD_URL`, and commit the workflow as `.github/workflows/offload-security-scan.yml`.

The generated workflow declares its own token permissions — `contents: read` and `actions: read`, plus `security-events: write` only when the Code Scanning upload is on — so it works in organizations whose default workflow token is read-only. It runs one parallel job per selected scan type against the checked-out commit, polls until each finishes, and fails when the gate fails — on any critical finding, or on a failed or partial scan. Code scans are also checked against the team quality gate. Select a single scan type for a single-scan workflow; the legacy single-scan templates are retired. If generation fails, the reason is shown and no stale workflow is left on screen.

The screen generates **GitHub Actions only**. Starter templates for **GitLab CI**, **Bitbucket Pipelines**, **Azure DevOps** and **Jenkins** are available from the API — `GET /api/ci/pipeline/{provider}` with `gitlab_ci`, `bitbucket`, `azure_devops` or `jenkins` — to commit and adapt.

### The API key

Pipelines authenticate with a **CI/CD API key** (`X-API-Key`). Create one under **Settings → API Keys** (also reachable from the Infra Command Center's GitHub Actions / Jenkins tabs), use the `ci_cd_full` preset, and store it as a CI secret. Keys are per team; rotate them like any credential ([API authentication](../../api-reference/authentication.md)). The `/api/cicd/*` endpoints enforce a key's **IP allowlist** (addresses and CIDR ranges; a call from another address gets 403) and its **rotation grace period** (a rotated-out key stops working when the grace period ends). Behind a proxy or load balancer, set `TRUSTED_PROXIES` on the deployment so the platform sees the runner's real address.

## Gating

| Gate | Where it is enforced |
| --- | --- |
| **Severity threshold** | The generated job fails on critical findings with the quality gate on; API-triggered scans take `fail_on_severity` (`critical`, `high`, `medium`, `low`). |
| **SCA policy pack** | Dependency and licence rules from the active [policy pack](./sbom-and-licenses.md#sca-policy-packs) — malicious packages, AGPL, fixable criticals, EPSS — decide `block_release` vs `block_until_reviewed`; each decision records the pack version. |
| **Image admission policy** | For compiled images, `POST /api/container-security/cicd/scan-and-validate` returns `allowed` and an `exit_code` ([container gate](../containers/governance.md#gate-a-pipeline)). |
| **Team quality gate** | Automation → **PR Review** → *Team quality gate*: max critical / high / medium / low (`-1` = no limit), minimum score, block on any critical or known-exploited (KEV) finding, what a stale vulnerability database does (mark for review, fail, or note only), and whether IaC that Checkov could not assess fails the gate. Same policy as `/api/ci/gate/policy` — see [Configure a release-gate policy](../../cli-and-cicd.md#configure-a-release-gate-policy). Changing it needs **Manage Integrations**. |
| **Scanner coverage** | A scan whose tools failed or did not finish fails the gate. **Partial dependency coverage** (some dependencies could not be resolved) also fails it by default, as it did in 1.4.0; set `fail_on_partial_dependency_coverage: false` with `PUT /api/ci/gate/policy` (API only; the screen keeps the value when you save) to record it as a note instead. Other partial coverage is a note. |

Findings from pipeline scans — API-key scans and GitHub App push and pull-request scans — are filed as code findings of the repository and branch they scanned, and land in the same **Findings** and **Reports** tabs as manual scans, so a developer sees the exact finding that failed the job with its code context — and triage decisions (false positive, accepted risk) apply to the next build too. Every gate is decided from **the scan's own findings**; a pull-request check, a pipeline job and the release-gate policy all read the same result.

:::tip[Two speeds]
Run **SAST + Secrets** on every pull request (fast, blocks obvious mistakes) and the **Full Code Security** scan on merge to main and nightly. Dependency findings rarely need to block a feature PR, but they should block a release.
:::

## Results from other scanners

If a pipeline already runs CodeQL, Semgrep or another SARIF-producing tool, add one step that posts its SARIF log to `POST /api/cicd/sarif/upload`; the **SARIF Imports** tab shows the exact `curl` and GitHub Actions snippets. See [SARIF Imports](./sarif-imports.md).

## Related

- [Pull Request Review](./pull-request-review.md) — reviews on GitHub, GitLab and Bitbucket pull/merge requests.
- [Pull Request Scanning](./pull-request-scanning.md) — changed-files scans on every PR/MR with inline annotations and a required check.
- [CLI & CI/CD](../../cli-and-cicd.md) — REST trigger/poll/results, the GitHub Action, SARIF, badges, PR comments, the GitHub App.
- [Infra Command Center](../infra-command-center.md) — the GitHub Actions and Jenkins setup guides with `scan.sh`.
- [Scan Management & Scheduling](../scan-management.md) — schedules for every scan type in one place.
