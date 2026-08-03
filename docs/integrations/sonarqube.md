---
title: "SonarQube Integration"
sidebar_label: "SonarQube"
sidebar_position: 6
---

# SonarQube Integration

Connect **SonarQube** to pull its static-analysis results into Offload Security's unified data layer. Instead of SonarQube findings staying stranded in their own console, they flow into the platform's code-security and **[Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)** views — deduplicated against native findings and prioritized alongside cloud, container, and runtime risk.

## What it brings in

SonarQube analysis surfaces issues across your codebase; the integration ingests them with their context intact:

| SonarQube output | In the platform |
|---|---|
| **Vulnerabilities** | Code-security findings with severity, rule, and file/line location. |
| **Security hotspots** | Security-sensitive code flagged for review. |
| **Bugs** | Reliability issues affecting the code's correctness. |
| **Code smells** | Maintainability issues (surfaced for completeness; prioritized below security). |

Each issue keeps its **rule id, severity, and file + line location**, so a finding links back to the exact code — and joins the same triage, deduplication, and risk-mapping as every other source.

## Connect SonarQube

1. In the platform, open **Integrations** and choose **Add Integration → SonarQube**.
2. Enter your **SonarQube server URL**, a **project key**, and an **authentication token** (a user token generated in SonarQube).
3. **Test the connection.** The platform makes a live call to confirm the URL, token, and project before saving; any error is reported so you can fix and re-test.
4. **Save.** Credentials are stored **encrypted at rest** and isolated to your **active team**. SonarQube issues begin flowing into the code-security findings view.

:::note[Self-hosted or SonarCloud]
The integration works with a self-hosted SonarQube server reachable by the platform. For a private, network-isolated SonarQube, deploy the platform's on-premises components so the connection stays inside your boundary — see **[On-Premises](../on-premises/index.mdx)**.
:::

## Where the data goes

- **Code security & Vulnerability Management** — SonarQube vulnerabilities and hotspots are normalized into the same finding schema and **deduplicated** against native SAST/SCA results, so you don't triage the same issue twice.
- **Risk & compliance** — findings are severity-ranked, risk-mapped, and available as evidence alongside the rest of your posture.

## Related

- **[Third-Party Integrations](./third-party.md)** — the full catalog, including other code-security tools (Snyk, Checkmarx, Veracode, GitHub CodeQL).
- **[Vulnerability Management](../vulnerability-risk/vulnerability-management.mdx)** — where connected findings are triaged and deduplicated.
