---
title: "Running Web, API & Host Scans"
sidebar_label: "Web, API & Host Scans"
sidebar_position: 2
description: "Launch an App Scan or a targeted single-tool run — ZAP, Nuclei, Nmap, testssl.sh, headers, API discovery and reconnaissance — from the Scanning module, and know what each one tests."
---

# Running Web, API & Host Scans

The **Scanning** module is where you actively test a target you can reach over the network: a web application, an API, a host or network range, a TLS endpoint or a whole domain. In 1.4.0 it is one module with three tabs:

| Tab | What it holds |
| --- | --- |
| **Assessments** (default) | App Scan runs: one graded, optionally authenticated assessment of an application that runs every relevant tool. The tool runs an App Scan launches are shown inside the assessment, not repeated in Targeted runs. See [Run an App Scan](./app-scan.md). |
| **Targeted runs** | Single-tool runs (ZAP, Nuclei, Nmap, testssl.sh, headers, API, recon), grouped by target. See [Scan Results](./scan-results.md). |
| **New scan** | The one launcher for both. App Scan is its default. |

**Where:** left navigation → **Scanning** → **New scan**. The **?** button in the page header opens the Scanning "How do I…" guides.

![New Web Vulnerability Scan form: assessment type, target URL, OWASP ZAP configuration (Standard: spider + active, 5–10 min), authenticated-scan toggle and launch button](/img/screenshots/security-scanning/scans-new-scan.webp)

:::note[Older links]
Links to the former **App Scan** sidebar entry (`?section=app-scan`) open the **Assessments** tab, and the former New Scan links open the **New scan** tab.
:::

## App Scan or a targeted run?

Use **App Scan** when you want an application assessment: one verified login, access-control checks with a second user, standards mapping (ASVS, OWASP Web / API Top 10, NIST SSDF), an A–F rating and one report. Use a **targeted run** when you need one tool's result on its own — a port scan, a TLS check, a Nuclei sweep — or a tool App Scan does not run (domain reconnaissance, API discovery on its own).

## What you can run

The **Assessment Type** list groups the options as the launcher shows them.

| Assessment | What it tests | Engine | Profiles (times as the form states them) |
| --- | --- | --- | --- |
| **App Scan** (recommended) | Every relevant web / API tool against one application, with standards mapping and a consolidated report | ZAP, Nuclei, Nmap, testssl.sh and native analyzers | Depends on the tools and profile you select |
| **Web Vulnerability Scan** | Injection (XSS, SQLi), insecure configuration, crawl of SPA routes | OWASP ZAP | Quick 1–2 min (passive) · Standard 5–10 min (spider + active) · Comprehensive 15–20 min (AJAX spider + active) |
| **Nuclei Vulnerability Scan** | Known CVEs, exposures and misconfigurations from a pinned template release | Nuclei | Quick 1–2 min (critical/high) · Standard 3–5 min (critical/high/medium) · Comprehensive 5–10 min (full template set) · CVE Detection · Misconfiguration Scan |
| **Security Headers Check** | HSTS, CSP, X-Frame-Options and the rest | shcheck | seconds |
| **API Discovery** | Find endpoints: OpenAPI / Swagger spec paths, JavaScript crawl, GraphQL introspection, common REST paths, `.well-known` | native API scanner | varies |
| **API Deep Scan** | OWASP API Top 10 testing of discovered or supplied endpoints; upload an OpenAPI file or Postman collection, or give a spec URL | native API scanner | varies |
| **Network Discovery** | Host discovery, TCP / UDP port scans, service and version detection, NSE scripts, OS detection | Nmap | See [Network Scans](./network-scans.md) |
| **SSL/TLS Security Test** | Protocol versions, cipher strength, certificate chain, known TLS weaknesses, on the port you give (default 443) | testssl.sh | Quick · Standard · Comprehensive · Vulnerability Focus |
| **Domain Scan** | Reconnaissance and OSINT for a domain: DNS records, email security (SPF, DKIM, DMARC), WHOIS, subdomains, common ports, WAF, technologies, headers, certificate, exposed paths, HTTP methods | native recon | minutes |
| **Subdomain Enumeration** · **Technology Detection** · **WAF Detection** · **Comprehensive Lightweight Scan** | Single lightweight checks | native analyzers | seconds–minutes |

:::note[What changed in 1.4.0]
The separate "API Security Testing" option is gone from the launcher; use **API Deep Scan**. Form and session logins are no longer offered for targeted Nuclei runs; use App Scan, which verifies the login and runs Nuclei with the session.
:::

## Run a targeted scan

1. Open **Scanning** → **New scan** and choose the **Assessment Type**.
2. Enter the **target**: a full URL (`https://app.example.com`) for web and API scans, a hostname, IP or CIDR range for Nmap, a hostname for testssl.sh, a bare domain for reconnaissance.
3. Pick the tool's **profile** (see the table above).
4. For a page behind a login, set up authentication (below).
5. For ZAP, Nuclei, Nmap and testssl.sh, fill in **Authorization & scope** (below). **Submit** stays disabled until you tick the attestation.
6. **Launch.** The scan runs in the background; you can leave the page. A targeted run opens its own run detail under **Targeted runs**, where it shows as running and then completed, partial or failed.

### Authorization & scope

App Scan, Web Vulnerability Scan (ZAP), Nuclei, Network Discovery (Nmap) and SSL/TLS Security Test runs carry an **engagement record**:

| Field | Purpose |
| --- | --- |
| **I am authorized to test this target** | Recorded with your name and the time (taken from your session) and printed in the report. |
| **Engagement / ticket reference** | Optional, up to 200 characters. |
| **Environment** | Production, Staging, Development, Test, or not specified. The report states what you chose instead of assuming production. |
| **Authorized until** | Optional end of the authorized window. A past date is refused, and **Rescan** is refused once the window has ended. |
| **Excluded hosts** (Nmap) / **Excluded paths** (ZAP) | Hosts or CIDRs Nmap must skip; paths ZAP must not touch, such as `/logout` or `/admin/**`. |

The record is described in [Engagement & Evidence](./scan-evidence.md).

### Authenticated targeted scans

| Tool | Methods offered |
| --- | --- |
| **ZAP** (Web Vulnerability Scan) | Bearer / JWT token · Cookie string · Custom header · Form-based login (login URL, field names, credentials, optional logged-in indicator) |
| **Nuclei** | Basic auth (sent as an `Authorization` header) · Custom headers (bearer token or API key) |
| **API Deep Scan** | Bearer token · API key header |
| **App Scan** | Everything above plus OAuth2 and browser login — see [Run an App Scan](./app-scan.md#authenticate-the-scan) |

For anything beyond a static token or a simple form, run an App Scan: it checks that the login works before any tool starts, re-checks the session during the scan, and reports when authenticated coverage was lost.

### Opt-in state-changing probes

App Scan and API Deep Scan have an **Allow state-changing probes** switch, off by default. When on, the OWASP API checks send `X-HTTP-Method-Override: DELETE/PUT/PATCH` with the scan's credentials to discovered GET endpoints and submit test data to sign-up, password-reset and webhook endpoints. When off, those checks are skipped and recorded on the scan as not run. Use it only on a test environment.

:::tip[Scan a staging copy with production data shape]
Active scans submit payloads. Point comprehensive web and API scans at a staging environment that mirrors production, and use a **Quick** or **Standard** profile when production is the only option.
:::

## Reading a result

Open a run from **Targeted runs** to see the summary — target, type, status, finding count — what ran (engine, pinned version, templates release, profile, UTC start and end), links to the tool's kept raw output, a comparison with the previous run of the same tool on the same target, and the findings: each with a severity, what was observed, the tool's own proof (CVE, CVSS, matched URL, reproducing request where the tool gives one) and the **fix**. Export the run as **HTML, PDF or Word**, with screenshots for web scans, or ask for an **AI Summary**. Details in [Scan Results](./scan-results.md).

![ZAP scan result dialog: quick scan of a public site, six header-related findings each with a plain-language fix, and HTML / PDF / DOCX / with-screenshots export buttons](/img/screenshots/security-scanning/scans-result-detail.webp)

A run that could not finish is never shown as clean. If ZAP could not run and only the built-in HTTP checks ran, the run is **partial** and marked **Degraded coverage**; if Nmap timed out, the hosts it finished are kept and the run is **partial** with the reason.

## Automating these scans

Every assessment is an API call (`POST /api/app-scan`, `POST /api/native-scans/web-vulnerability`, `/network-discovery`, `/ssl-security`, `/security-headers`, `/nuclei/url-scan`) that returns an id you poll — see the [Scanning API](./api.md#web-api--host-scans) and, for pipelines, [CI/CD & Automation](./code/ci-cd-and-automation.md). Recurring runs are configured in [Scan Management & Scheduling](./scan-management.md).

## Related

- [Run an App Scan](./app-scan.md) — authenticated DAST with exclusions, second user, retest and pinned tools.
- [Network Scans & VAPT Report](./network-scans.md) — Nmap depth, the network VAPT report and Wazuh host correlation.
- [Scan Results](./scan-results.md) — the target tree, run comparison, reports and consolidated reports.
- [Infra Command Center](./infra-command-center.md) — WAF testing and API load tests.
- [SSL Certificate Monitoring](../cloud-security/ssl-certificates.md) — continuous expiry tracking, complementing the one-off TLS test.
