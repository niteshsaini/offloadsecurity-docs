---
title: "SBOM & Licences"
sidebar_label: "SBOM & Licences"
sidebar_position: 4
description: "Generate or upload SBOMs, see licence families and obligations, enforce a versioned SCA policy pack, get an auto-fix plan and a third-party NOTICE file, and export the analysis."
---

# SBOM & Licences

A Software Bill of Materials answers "what exactly is in this build?" — and once the platform has it, it can answer the questions that follow: which components are vulnerable, which licences you are bound by, what to upgrade, and what attribution you owe. That is what this tab does, for SBOMs the platform generates from a repository and for SBOMs you already have.

**Where:** Code Command Center → **SBOM & Licenses**.

![SBOM & Licenses tab: licence-enrichment opt-in banner, Generate SBOM (provider, repository), Upload an existing SBOM, and the SBOM reports list showing payments-api.zip with 0 components analysed](/img/screenshots/security-scanning/code-sbom-licenses.webp)

## Getting an SBOM

| Path | How |
| --- | --- |
| **Generate** | Pick the provider and repository (branch defaults to `main`) and select **Generate SBOM**. Syft builds a CycloneDX SBOM from a fresh clone and the SCA analysis runs on it. |
| **Upload** | **Choose SBOM file** — CycloneDX (JSON or XML) or SPDX (JSON) — and **Upload & Analyze**. You get the full analysis without connecting the repository; the report is listed with provider *upload*. |
| **As part of a scan** | Every **Full Code Security** or **SBOM Generation** scan produces one ([Running Code Scans](./running-code-scans.md)). |

Reports list the repository, status, component count and licence summary; **Show: application / owner** narrows the list once repositories are mapped.

### Licence enrichment (opt-in)

Package manifests often omit licences. **OSS licence enrichment via deps.dev** looks up each unknown package's licence by name and version against Google's deps.dev service. It is **off until you opt in** — the banner asks once — because it sends package coordinates (never your code) to an external service. Enable it for accurate licence families; keep it disabled in air-gapped deployments.

## Reading a report

| Section | What you get |
| --- | --- |
| **Packages** | Every component with version, ecosystem, licence, vulnerability count, KEV/EPSS flags, a **risk** rating and **health** signals (maintenance, age) where available. |
| **Licence families** | Components grouped into permissive / weak-copyleft / strong-copyleft / network-copyleft / unknown, with **obligations by family** spelled out (attribution, source disclosure, network-use clauses). |
| **Vulnerabilities** | Grype results per package with fixed versions, KEV and EPSS. |
| **AI components** | The AI SDKs, frameworks, agent libraries, model runtimes and vector stores among the packages — by role and provider — and the external model providers the repository references. A dependency proves the SDK is present, not which model is called or what data reaches it; the section says so. The same components fold into the cross-repository [AI Bill of Materials](../../ai-threat-intelligence/ai-spm.md). |
| **Licence governance** | The **active SCA policy** and how this SBOM fares against it (below). |
| **Auto-Fix Plan** | Fixable vs unfixable vulnerable packages and the exact upgrade commands per ecosystem, with **Copy upgrade commands** and **Copy PR body** ready for a pull request. |
| **NOTICE file** | The third-party attribution file assembled from the licence families — download it and ship it with the product. |
| **Export** | `csv` (one row per package: licence, vulnerabilities, KEV/EPSS, risk, health), `csv-vulns` (one row per vulnerability with file location), `json` (the stored analysis), and **Download** for the raw CycloneDX/Syft document. |

## SCA policy packs

Licence and vulnerability decisions are governed by a **versioned policy pack**, so "which policy blocked this release" is always answerable:

| Pack | Adds | Exceptions |
| --- | --- | --- |
| **Baseline (built-in floor)** | Blocks malicious packages, secrets, missing SBOM and AGPL. | Allowed, up to 90 days, justification required. |
| **Production workloads** | Baseline + hard blocks on fixable high/critical and unknown licences, EPSS ≥ 0.5 blocks release, no-fix critical/high blocks until reviewed. | Up to 30 days, justification **and approver**. |
| **Regulated environment** | Production + stricter licence and provenance rules (blocked until reviewed). | Up to 30 days, justification, approver **and compensating controls**. |

Packs only ever make a rule *more* blocking, never less. The pack in force is chosen per scan — an explicit `policy_pack` on the scan or pipeline request, otherwise the platform default (`SCA_DEFAULT_PACK`, falling back to *Baseline*) — shown under **Licence governance**, and its version is recorded on every gate decision ([CI/CD & Automation](./ci-cd-and-automation.md)). `GET /api/code/sca/policy` and `/policy-packs` expose the active rules and all packs.

:::tip[Customer SBOM requests]
When a customer asks for an SBOM, download the CycloneDX document and the NOTICE file for the release tag, and attach the `csv` export as the vulnerability disclosure. All three come from the same report, so they agree with each other.
:::

## Related

- [Findings & Reports](./findings-and-reports.md) — the vulnerability side of the same analysis, with lifecycle.
- [Container SBOMs](../containers/governance.md#sbom-lifecycle) — SBOMs of built images rather than source.
- [Scanning API](../api.md#code) — generate, upload, export and fix-plan endpoints.
