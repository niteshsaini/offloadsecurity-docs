---
title: "SBOM & Licences"
sidebar_label: "SBOM & Licences"
sidebar_position: 4
description: "Generate or upload SBOMs, see licence families and obligations, enforce a versioned SCA policy pack, get a fix plan, and export commit-pinned CycloneDX, SPDX, VEX and NOTICE files you can verify later."
---

# SBOM & Licences

A Software Bill of Materials answers "what exactly is in this build?" — and once the platform has it, it can answer the questions that follow: which components are vulnerable, which licences you are bound by, what to upgrade, and what attribution you owe. That is what this tab does, for SBOMs the platform generates from a repository and for SBOMs you already have.

**Where:** Code Command Center → **SBOM & Licenses**.

![SBOM & Licenses tab: licence-enrichment opt-in banner, Generate SBOM (provider, repository), Upload an existing SBOM, and the SBOM reports list showing payments-api.zip with 0 components analysed](/img/screenshots/security-scanning/code-sbom-licenses.webp)

## Getting an SBOM

| Path | How |
| --- | --- |
| **Generate** | Pick the provider and repository (leave the branch blank for the repository's default branch) and select **Generate SBOM**. Syft builds a CycloneDX SBOM from a fresh clone and the SCA analysis runs on it. |
| **Upload** | **Choose SBOM file** — CycloneDX (JSON or XML) or SPDX (JSON), up to 25 MB (`MAX_SBOM_UPLOAD_BYTES`) — and **Upload & Analyze**. You get the full analysis without connecting the repository; the report is listed with provider *upload*. |
| **As part of a scan** | Every **Full Code Security** or **SBOM & License Scan** produces one ([Running Code Scans](./running-code-scans.md)). |

Reports list the repository, the commit it describes, status, component count and licence summary; **Show: application / owner** narrows the list once repositories are mapped ([Repository ownership](./connecting-repositories.md#repository-ownership)).

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
| **Auto-Fix Plan** | **Fix Plan**: fixable vs unfixable vulnerable packages and the upgrade commands per ecosystem, from the same engine as [Upgrade Impact](./upgrade-impact.md), with **Copy Commands** and **Copy PR Body** ready for a pull request. A package's "⬆ version" or "resolves N" opens its upgrade drawer. |
| **NOTICE file** | **Notices**: the third-party attribution file assembled from the licence families — download it and ship it with the product. |

## Exports and snapshot evidence

The buttons at the top of an SBOM report:

| Button | You get |
| --- | --- |
| **PDF report** / **HTML** | The licence and SCA report, including a *Snapshot provenance* section. |
| **CycloneDX** | The SBOM as generated (CycloneDX JSON). Not offered for an SBOM uploaded as SPDX. |
| **SPDX** | SPDX 2.3 JSON, converted from the CycloneDX document (root = repository @ commit, licences, checksums, purl/CPE, dependency relationships). |
| **VEX** | OpenVEX — one statement per dependency vulnerability (affected / not affected / fixed) from your triage decisions. |
| **Notices** | The third-party notices / attribution file. |
| **CSV** / **JSON** | The per-package analysis (licence, vulnerabilities, KEV/EPSS, health, risk) and the machine-readable roll-up. `GET /api/code/sbom/{scan_id}/export?format=csv-vulns` adds one row per vulnerability with the manifest location (API only). |

### What the snapshot pins

An SBOM is evidence about one point in time, so the **Snapshot** panel under the buttons states exactly what was assessed:

- the **commit** SHA and the **branch** actually checked out (and a note when the requested branch did not exist and the default branch was scanned), plus any tags at that commit;
- the SBOM **generator** and the vulnerability **matcher** with their versions (and the advisory database);
- for an uploaded SBOM, the uploaded file's **SHA-256**.

The CycloneDX document itself is stamped with the commit and branch.

### Verify an export

Every SBOM, VEX, NOTICE, report and analysis export is served as exact, hashed bytes and recorded on the report. The panel shows the **last export** with its SHA-256. To check that a file someone sends you is an unmodified export from this platform, use **Verify a file…**: it compares the file's SHA-256 with the platform's export record (`GET /api/code/sbom-exports/verify?sha256=`). This is tamper-evidence through the platform's record, not a detached signature.

### Import a supplier's VEX

**Import supplier VEX…** records a supplier's OpenVEX statements next to your own decisions; the result says how many statements matched findings. Supplier statements are shown as the supplier's assertions — they do not replace your triage.

## SCA policy packs

Licence and vulnerability decisions are governed by a **versioned policy pack**, so "which policy blocked this release" is always answerable:

| Pack | Adds | Exceptions |
| --- | --- | --- |
| **Baseline (built-in floor)** | Blocks malicious packages, secrets, missing SBOM and AGPL. | Allowed, up to 90 days, justification required. |
| **Production workloads** | Baseline + hard blocks on fixable high/critical and unknown licences, EPSS ≥ 0.5 blocks release, no-fix critical/high blocks until reviewed. | Up to 30 days, justification **and approver**. |
| **Regulated environment** | Production + stricter licence and provenance rules (blocked until reviewed). | Up to 30 days, justification, approver **and compensating controls**. |

Packs only ever make a rule *more* blocking, never less. The pack in force is chosen per scan — an explicit `policy_pack` on the scan or pipeline request, otherwise the platform default (`SCA_DEFAULT_PACK`, falling back to *Baseline*) — shown under **Licence governance**, and its version is recorded on every gate decision ([CI/CD & Automation](./ci-cd-and-automation.md)). `GET /api/code/sca/policy` and `/policy-packs` expose the active rules and all packs.

:::tip[Customer SBOM requests]
When a customer asks for an SBOM, download the CycloneDX or SPDX document, the VEX and the Notices file for the release commit, and attach the CSV export as the vulnerability detail. All come from the same report — the Snapshot panel names the commit they describe — and each download's SHA-256 is recorded so the customer's copy can be verified later.
:::

## Related

- [Findings & Reports](./findings-and-reports.md) — the vulnerability side of the same analysis, with lifecycle.
- [Container SBOMs](../containers/governance.md#sbom-lifecycle) — SBOMs of built images rather than source.
- [Scanning API](../api.md#code) — generate, upload, export and fix-plan endpoints.
