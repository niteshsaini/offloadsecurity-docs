---
title: "Code Command Center"
sidebar_label: "Code Command Center"
sidebar_position: 5
---

# Code Command Center

The **Code Command Center** scans your source code and software supply chain for security problems before they ship. Point it at a repository (or upload code or an SBOM) and it runs static analysis, secrets detection, dependency vulnerability checks, and open-source **license-compliance** review — then rolls the results into findings you can triage like any other scan.

## What it does

The Code Command Center runs several industry-standard scanners and consolidates their output for you:

| Capability | What it catches | Powered by |
|---|---|---|
| **SAST (static analysis)** | Insecure code patterns — injection, weak crypto, unsafe deserialization, and more, across many languages | OpenGrep, Bandit (Python) |
| **IaC scanning** | Misconfigurations in infrastructure-as-code (Terraform, CloudFormation, Kubernetes manifests, Dockerfiles) | Checkov |
| **Secrets detection** | Hardcoded credentials — API keys, tokens, passwords, and private keys committed to the repo | GitLeaks |
| **SCA (dependency scanning)** | Known vulnerabilities (CVEs) in your open-source dependencies | OSV (OSV.dev database) |
| **SBOM generation** | A complete Software Bill of Materials of every component and version | Syft (CycloneDX / SPDX) |
| **License compliance** | Open-source licenses classified by risk — permissive, weak copyleft, strong copyleft, or commercially restrictive | SBOM-based analysis |
| **Malicious-package & typosquat checks** | Dependencies flagged as known-malicious, plus suspicious package names that imitate popular libraries (typosquatting) | SCA rulebook (OSV malicious-package data) |
| **Import-level reachability** | Whether your code actually imports a vulnerable package — advisory context that helps you deprioritize CVEs in dependencies you never load | Import analysis |

Every finding carries a **severity** so you can focus on what matters first, and results flow into the platform's central [Vulnerability Management](../vulnerability-risk/vulnerability-management.md) view alongside the rest of your security data.

## How to use it

### Scan a Git repository

1. Open **Code Command Center** from the left navigation.
2. Choose **Scan repository** and select a source:
   - Pick a repository from a **connected Git provider** (GitHub or Bitbucket), then choose the **branch** to scan, or
   - Paste a **Git URL** (HTTPS or SSH) directly. For a private repo, make sure the platform has access via your Git connection.
3. (Optional) Choose which checks to run. By default the platform runs the full set — SAST, secrets, SCA, and SBOM with license analysis. You can also keep **Generate SBOM** and **License analysis** enabled to get supply-chain coverage in the same pass.
4. Start the scan. It runs in the background, so you can leave the page and come back — the scan appears in your reports list with a live status (running, then completed, partial, or failed).
5. Open the finished report to review findings.

### Scan uploaded code (ZIP)

If your code isn't in a connected repository, you can scan an archive directly:

1. In **Code Command Center**, choose **Upload code**.
2. Select a **`.zip`** archive of your project (up to **500 MB**).
3. The platform extracts and scans it just like a repository, and the report lands in the same list.

### Upload an SBOM for a license check

Already have a Software Bill of Materials from your build pipeline? You can check it for license compliance without re-scanning the code:

1. Go to the **SBOM & Licenses** area of the Code Command Center.
2. Choose **Upload SBOM** and select a **JSON** SBOM in **CycloneDX** or **SPDX** format (up to **25 MB**).
3. The platform parses every component, classifies its license, and produces a **license-compliance verdict** — no repository clone or SBOM generation required.
4. The result appears in the same SBOM & Licenses list (marked as an upload) so it sits next to SBOMs generated from your repos.

### Read the findings

Open any completed scan to see results grouped by check:

- **Code & IaC findings** — each issue shows its severity, the rule that flagged it, and the file it was found in.
- **Secrets** — every detected credential is listed with its location so you can rotate and remove it.
- **Dependencies (SCA)** — vulnerable packages are listed with the associated CVEs and severity.
- **SBOM & Licenses** — the full component inventory with each license sorted into a risk category, and any **license violations** called out (for example, a strong-copyleft package in a product you distribute).

From a scan you can also:

- **Download the SBOM** as CycloneDX JSON for use in your own tooling.
- **Export a license-compliance report** (PDF or HTML) to share with engineering or legal.

:::tip[Run it in CI/CD]
You don't have to start every scan by hand. Wire code scanning into your pipeline so each build is checked automatically and you can gate merges on the results. See **[Scan Management & CI/CD](./scan-management.md)**.
:::

:::note[License enrichment is opt-in]
To resolve licenses that an SBOM leaves blank, the platform can look up component coordinates against the public **deps.dev** service. This is **off by default** — until your team explicitly turns it on, no dependency information leaves your environment. You can change the setting from the Code Command Center's license settings.
:::

:::warning[Scans run isolated, but mind what you scan]
Code scans run in a hardened, sandboxed environment with no network access to your code. Still, only scan repositories and archives you trust and are authorized to analyze. Private-repo scans require a valid Git connection with appropriate access.
:::

## Related

- [Native Security Scans (Web, Network, SSL)](./native-scans.md) — scan running web apps, networks, and TLS.
- [Container & Registry Security](./container-security.md) — image scanning, SBOMs, and secret detection in layers.
- [Scan Management & CI/CD](./scan-management.md) — automate scans and gate your pipelines.
- [Vulnerability Management](../vulnerability-risk/vulnerability-management.md) — triage, prioritize, and track every finding to remediation.
