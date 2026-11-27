---
title: "Run an App Scan"
sidebar_label: "App Scan (DAST)"
sidebar_position: 2.1
description: "Run a graded, authenticated DAST assessment of one web application or API — login, exclusions, second user, session checks, retest — and read what it proved."
new_in: 1.4.0
---

# Run an App Scan

App Scan is the platform's DAST assessment of one application. It runs every relevant web and API tool in one job, logs in once and verifies the login, tests access control with a second user, maps results to security standards, grades the application A–F and produces one report. This guide takes about ten minutes to set up; the scan itself runs in the background.

## Before you begin

- The **Run Scans** permission ([RBAC](../authentication/rbac-team-management.md)).
- Written authorization to test the application. You attest to it in the launcher.
- For an authenticated scan: a **dedicated test account**, ideally on staging. An authenticated scan acts as that user and can change or delete data the account can reach.
- A private (RFC 1918) target needs `ALLOW_PRIVATE_SCAN_TARGETS=true` on the deployment.

## Steps

1. **Open the launcher.** **Scanning** → **New scan** (or **Launch App Scan** on the **Assessments** tab). **App Scan** is preselected.
2. **Enter the application URL**, for example `https://app.example.com`.
3. **Choose the tools.** Security Headers, SSL/TLS Config, OWASP Web Misconfiguration, OWASP API Top 10, Technology Fingerprint, Known CVEs in Stack (NVD + CISA KEV + FIRST EPSS), WAF Detection, Traffic Capture (headless browser recording of XHR / fetch calls), Information Disclosure, OWASP ZAP, Nuclei, Nmap and testssl.sh.
4. **Choose standards to map to**: ASVS Level 1, ASVS Level 2, OWASP Web Top 10, OWASP API Top 10, NIST SSDF.
5. **Set the scan intensity** (Quick, Standard, Comprehensive) and the **Scanner Resource Mode**:
   - **Gentle** — fragile target: tools run one after another at a low request rate with a pause between them.
   - **Normal** (default) — one scanner at a time at a moderate rate.
   - **Aggressive** — all heavy tools at once at full rate; only for a well-resourced platform host and a target behind a CDN or WAF.
6. **Authenticate** if the application has a login (see [Authenticate the scan](#authenticate-the-scan)).
7. **List excluded paths**, one per line: `/logout`, `/api/*/delete`, `/admin/**`. A malformed pattern is refused.
8. **Optionally add a second user** for access-control testing (see [Second user](#second-user-for-access-control)).
9. **Leave Allow state-changing probes off** unless this is a test environment ([what it does](./native-scans.md#opt-in-state-changing-probes)).
10. **Fill in Authorization & scope**: tick the attestation, add a reference, the environment and, if you have one, the authorized-until date ([Engagement & Evidence](./scan-evidence.md)).
11. **Launch.** The launcher stays open and shows the live login check; **View detailed results** opens the assessment.

## Authenticate the scan

| Auth type | Provide | Notes |
| --- | --- | --- |
| **Bearer Token** | The token | Sent as `Authorization: Bearer …` |
| **Cookie** | A session cookie string | |
| **Custom Header** | Header name and value | For example an API key |
| **Form Login** | Login URL, field names, username, password, optional logged-in indicator (regex) | Single-POST login forms |
| **OAuth2 Client Credentials** | Token URL, client ID, client secret, optional scope and audience, an authenticated probe URL, client authentication method | Token fetched before the scan and refreshed between phases |
| **OAuth2 Refresh Token** | As above plus the refresh token (client secret optional) | A rotated refresh token is written back to the owning schedule |
| **Browser Login (multi-step / MFA)** | Login URL, username, password, optional second-page flag, logged-in / logged-out indicators, TOTP seed, CSS selectors | Off by default; see below |

Before any tool starts, App Scan checks that the credentials actually authenticate. If the login fails, the scan does not run unauthenticated: it fails with the reason, so a failed login cannot produce a suspiciously clean report.

### OAuth2

The token URL must be `https` and redirects are not followed; loopback and cloud-metadata addresses are always refused, and a private (internal) token endpoint is reached only while `ALLOW_PRIVATE_INTEGRATION_TARGETS` is on (the shipped default). The **probe URL** must answer 401 or 403 without a valid token. **Test authentication** fetches a token and calls the probe URL — the same check the scan runs first. If a token cannot be obtained or is rejected, the scan does not run. Tools read their token at launch, so if a phase outlives a token the result marks authenticated coverage as partial and names the phase. Client secrets and refresh tokens are encrypted before the job is queued and masked in scan records, logs and schedule responses.

:::tip[Refresh tokens that rotate]
If your identity provider rotates refresh tokens, **Test authentication** uses up the token you entered. Paste a fresh one before launching.
:::

### Browser login (multi-step / MFA)

**Browser Login** appears only when the deployment sets `DAST_BROWSER_AUTH=true` (default off). A real browser performs the login, so JavaScript logins, username-then-password pages and MFA test accounts work; the platform generates the TOTP code from the seed at login time. The harvested cookies and storage token feed Nuclei and the in-platform tools; ZAP uses its own browser-based authentication. With a logged-in indicator the scan re-logs in automatically if the session expires (at most 3 times by default). Without one, the result says the login was **inferred, not verified**.

Use a test account whose TOTP seed you control. Never enter a real person's MFA seed.

### Logout and destructive-URL guard

When the deployment sets `DAST_AUTH_GUARD=true` (default off), every authenticated App Scan skips logout, sign-out, account deletion / deactivation, password and email changes, and MFA disable URLs automatically. The guard does not know your application's own destructive actions: list those under **Excluded paths** — and, with the guard off, list logout and account URLs there too.

### Session checks during the scan

While the tools run, App Scan re-checks the login every 15 minutes (`APP_SCAN_SESSION_CHECK_S`, default 900 seconds). A failed check records when coverage was lost and downgrades the authentication verdict; a form login is refreshed for tools that have not started yet. A tool already running keeps the session it started with.

## Second user for access control

Give a lower-privilege account (login form on the same page, bearer token, cookie or custom header). Discovered endpoints are replayed as both users to confirm broken object-level and function-level authorization (BOLA / BFLA). The second login is verified first; if it fails, the report says the access-control check did not run rather than reporting no findings. Excluded paths are not replayed.

## Check that it worked

Open the assessment on the **Assessments** tab:

- **Progress** — while running, each tool shows as Queued, Running, Completed, Failed, Timed out, Cancelled or Skipped. A failed tool counts as done for the bar and is named.
- **Security Score** — the A–F grade. A partial run's score is labeled **provisional**; a run where no tool completed has no grade.
- **Overview** — target, duration, tools run, authentication verdict, excluded paths and which tools enforced them, session checks, the access-control outcome, the tool versions that ran, and the API surface (endpoints in the inventory, new since last scan, no longer seen).
- **Findings** — filter by severity or **Confirmed** (findings the platform actively proved exploitable). Expand a finding for the evidence, the request to reproduce it (method, URL, parameter, payload, or Nuclei template and matcher, or a curl command) and the fix. The table shows the first 100 rows of a filter; the downloaded report has every finding.
- **Standards Coverage** — per standard: total, automated, passed, failed, manual and pass rate.

Download the assessment as **HTML Report** or **PDF Report** from the page header once it has completed.

## Retest a finding

Expand a finding and select **Retest this finding**. The platform probes that one finding again **as the scan user**: for an authenticated scan it asks only for the secret (password, token, cookie or header value), which is not stored, and takes the rest of the login from the scan; a form or OAuth login is performed again. The verdict is recorded on the finding with the time and whether it ran authenticated. An authenticated finding retested without the secret is **inconclusive**, never **fixed**.

## What App Scan records about its tools

ZAP, Nuclei, testssl.sh and Nmap run from images pinned by tag and digest, and Nuclei runs a pinned template release installed once on the scan volume, with update checks off:

| Tool | Pinned in 1.4.0 |
| --- | --- |
| OWASP ZAP | 2.17.0 |
| Nuclei | v3.11.1, templates v10.4.9 |
| testssl.sh | 3.2 |
| Nmap | 7.98 |

Each assessment records what the deployment pins and what each tool actually ran (image and digest, or local binary and the version it reported), and the report prints it per tool. If the template release cannot be installed, the scan still runs and records templates as **unpinned**. Operators can point a tool at a mirror with `SCANNER_IMAGE_<TOOL>` (for example `SCANNER_IMAGE_ZAP`) and change the template release with `NUCLEI_TEMPLATES_VERSION`.

## If something goes wrong

- **The scan failed before any tool ran** — the login check failed. The failure card shows the reason; fix the credentials or probe URL and launch again.
- **Browser Login is not in the Auth Type list** — the deployment has not set `DAST_BROWSER_AUTH=true`.
- **Partial coverage banner** — one or more tools failed; the score covers only the checks that ran. The banner names the tools.
- More in [Scanning Troubleshooting](./troubleshooting.md#web-api--host-scans).

## Next steps

- [Schedule the App Scan](./scan-management.md) to repeat it; scheduled App Scans accept the same authentication, including OAuth2.
- [Engagement & Evidence](./scan-evidence.md) — what the report says about authorization, scope and versions.
- Export findings as SARIF for CI annotation with `GET /api/app-scan/{app_scan_id}/sarif` ([Scanning API](./api.md#app-scan)).
