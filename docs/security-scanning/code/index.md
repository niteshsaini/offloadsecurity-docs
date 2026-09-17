---
slug: "/security-scanning/api-code-scanning"
title: "Code Command Center"
sidebar_label: "Code Command Center"
sidebar_position: 6
description: "SAST, dependency (SCA), secrets, IaC and SBOM/licence scanning for your repositories — connect GitHub, GitLab or Bitbucket, scan on demand, on a schedule or from CI, and triage findings with a full lifecycle."
---

# Code Command Center

The Code Command Center is where source code gets tested before it becomes a running system: static analysis, vulnerable dependencies, leaked secrets, infrastructure-as-code mistakes, and the licences you are shipping. Connect a Git provider once, then scan repositories on demand, on a schedule, or from every pipeline run — and work the findings with a lifecycle that survives re-scans.

**Where:** left navigation → **Code Command Center**.

![Code Command Center — Overview: repository security coverage (1 scanned repository, 100 findings by severity), repository coverage and top repositories by severity](/img/screenshots/security-scanning/code-overview.webp)

## What you get

| Scan type | Engine | Finds |
| --- | --- | --- |
| **SAST** | OpenGrep + Bandit (+ SonarQube when connected) | Injection, insecure deserialization, weak crypto, dangerous calls — per file and line, with code context |
| **Dependency / SCA** | OSV.dev, enriched with CISA KEV and EPSS | Vulnerable packages across lockfiles (npm, pip, Go, Maven, …), with fixed versions and exploit-likelihood signals |
| **Secrets** | Gitleaks + live validation | API keys, tokens, passwords and private keys in code, config **and git history** — each checked against its provider to tell a live credential from a rotated one |
| **IaC** | Checkov | Terraform, CloudFormation, Kubernetes manifests, Dockerfiles — public buckets, open security groups, unencrypted storage |
| **SBOM & Licences** | Syft (CycloneDX), licence enrichment via deps.dev | Component inventory, licence families and obligations, policy-pack checks |
| **Compiled Image Scan** | Trivy + Grype | The Docker image a pipeline just built |

**Full Code Security** runs all of the above in one pass. All three rule-based engines also run your own [custom rules](./custom-rules.md).

## The workspace

| Tab | Use it to | Page |
| --- | --- | --- |
| **Overview** | Repository coverage — scanned, scheduled, uncovered, stale (no push in 90 days) — and findings by severity. | *this page* |
| **New Scan** | Scan a repository, an uploaded ZIP, a build artifact or a compiled image. | [Running Code Scans](./running-code-scans.md) |
| **Findings** | Triage across repositories: SAST, secrets, dependency CVEs and IaC grouped by rule, with lifecycle states and bulk decisions. | [Findings & Reports](./findings-and-reports.md) |
| **Suppressions** | What is hidden, since when and until when — by rule, with revoke. | [Findings & Reports](./findings-and-reports.md#suppressions) |
| **Reports** | Per-scan reports, exports and AI analysis. | [Findings & Reports](./findings-and-reports.md#scan-reports) |
| **SBOM & Licenses** | Generate or upload SBOMs, licence governance, fix plans. | [SBOM & Licences](./sbom-and-licenses.md) |
| **Automation** | Git connections, scheduled scans, CI/CD pipeline generation. | [Connecting Repositories](./connecting-repositories.md) · [CI/CD & Automation](./ci-cd-and-automation.md) |

## How it flows

```mermaid
flowchart LR
    G[Git provider<br/>GitHub · GitLab · Bitbucket] --> R[Repository / branch]
    Z[ZIP · artifact · image] --> S
    R --> S[Scan<br/>SAST · SCA · secrets · IaC · SBOM]
    CI[CI pipeline<br/>scan.sh / API] --> S
    PR[Pull / merge request<br/>GitHub · GitLab · Bitbucket] --> S
    S --> F[Findings<br/>fingerprinted · lifecycle]
    S --> RP[Reports · SBOM · AI components]
    S --> PRV[Inline review comments<br/>+ commit status]
    F --> FIX[AI fix · Fix PR · Fix with agent]
    F --> V[Vulnerability Mgmt · Risk]
```

Findings are **fingerprinted** (rule + file + code context, or package + CVE), so a re-scan updates the same finding instead of creating a new one, and a triage decision — triaged, risk accepted with an owner and justification, false positive — carries forward. Decisions are scoped to the repository they were made in unless you apply them to every repository ([scope](./findings-and-reports.md#scope-this-repository-or-every-repository)).

Pull and merge requests get a review of their own: only the changed files, new findings separated from pre-existing ones, comments on the diff and a commit status pinned to the exact commit — see [Pull Request Review](./pull-request-review.md).

## Prerequisites

- **Run Scans** to scan; **Execute Remediations** to open fix pull requests (manually or with an [agent](./agentic-fixes.md)).
- A Git provider token with repository read access — see [Connecting Repositories](./connecting-repositories.md). Uploaded ZIPs and artifacts need no connection.

## Related

- [Pull Request Review](./pull-request-review.md) · [Secret Detection](./secret-detection.md) · [Custom Rules](./custom-rules.md) · [Fix with Agent](./agentic-fixes.md) — the deeper pages of this section.
- [CLI & CI/CD](../../cli-and-cicd.md) — the `scan.sh` script, the CLI and release gates.
- [Container Security](../containers/index.md) — the images your code becomes.
- [Vulnerability Management](../../vulnerability-risk/vulnerability-management/index.mdx) — code findings in the unified view with SLAs.
