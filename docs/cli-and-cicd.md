---
title: "CLI & CI/CD Integration"
sidebar_label: "CLI & CI/CD"
sidebar_position: 10
---

# CLI & CI/CD Integration

Run Offload Security scans straight from your pipeline and **gate releases on the results**. You can call the platform with plain `curl` from any CI system (GitHub Actions, GitLab CI, Jenkins, CircleCI, and more), or drop in the ready-made **GitHub Action** for application and container scans with results posted right on the pull request.

Every scan you trigger from CI/CD also shows up in the platform UI alongside your other scans, so findings flow into the same Vulnerability Management, Risk, and Reporting workflows you already use.

## What it does

- **Trigger scans from a pipeline** — start a web, network, SSL/TLS, API, container, Kubernetes, or code-security scan with a single authenticated request.
- **Fail the build on findings** — set a severity threshold (`critical`, `high`, `medium`, `low`) and let the pipeline fail when matching findings are detected.
- **Poll for status and pull results** — check progress and fetch the full findings payload when the scan finishes.
- **Get a verdict** — each completed scan returns a `gate_passed` flag and a severity breakdown so your job can pass or fail accordingly.
- **Use the GitHub Action** — a turn-key action that runs the scan, waits for it, posts a summary comment on the PR, and exposes findings counts and a report link as step outputs.

:::note Authentication
Pipeline requests authenticate with an **API key** (not your login). Create the key once, store it as a CI secret, and send it on every request. Keys are scoped, expirable, and revocable.
:::

---

## 1. Create an API key

API keys are managed from the **API Keys** screen, reached from the **account menu in the top-right** of the platform.

1. Open the **account menu (top-right)** and select **API Keys**.
2. Select **Create API Key**.
3. Give the key a recognizable **name** (for example, `GitHub Actions – web app`).
4. Choose a **scope preset**. For pipeline scanning use **CI/CD Pipeline (Basic)**, which grants exactly `scans:trigger` and `scans:read` — enough to start scans and read their results. Use **CI/CD Pipeline (Full)** if your jobs also need to manage scans or read vulnerabilities.
5. Set **Expires in (days)** (default **90**, maximum **365**). Optionally adjust the environment label and per-minute rate limit.
6. Select **Create** and **copy the key immediately** — it is shown only once. Keys begin with the prefix `osk_`.

Store the key in your CI provider's secret store (GitHub Actions secrets, GitLab CI/CD variables, Jenkins credentials, a vault, etc.). Never commit it to your repository.

:::tip Least privilege & rotation
Pick the narrowest preset that works (start with **CI/CD Pipeline (Basic)**), keep an expiry set, and rotate keys periodically. You can **revoke** a key at any time from the same screen if it is ever exposed.
:::

---

## 2. Trigger a scan from any CI system (REST API)

Any pipeline that can run `curl` can drive the platform. Send your API key in the **`X-API-Key`** header.

### Start a scan

```bash
curl -s -X POST "$OFFLOAD_API_URL/api/cicd/scans/trigger" \
  -H "X-API-Key: $OFFLOAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_type": "nuclei",
    "target": "https://staging.example.com",
    "scan_profile": "standard",
    "fail_on_severity": "high"
  }'
```

**Request fields**

| Field | Required | Description |
|---|---|---|
| `scan_type` | Yes | What to run (see the table below). |
| `target` | Yes | URL, IP, hostname, container image reference, or Git repository URL — depending on the scan type. |
| `scan_profile` | No | Scan depth/profile (defaults to a sensible value per scan type). |
| `fail_on_severity` | No | Severity gate: `critical`, `high`, `medium`, or `low`. Sets `gate_passed=false` when findings at or above this level are found. |
| `branch` | No | Git branch to scan, for the code-security scan types. |
| `pipeline_context` | No | Free-form metadata about the build (repo, branch, commit, build ID) stored with the scan. |
| `callback_url` | No | HTTPS webhook the platform POSTs to when the scan completes (must resolve to a public address). |

**Common `scan_type` values and their profiles**

| `scan_type` | Scans | Typical `scan_profile` |
|---|---|---|
| `nuclei` | Fast template-based vulnerability scan | `quick`, `standard`, `comprehensive`, `cve`, `misconfig` |
| `web_vulnerability` | Web application (OWASP ZAP) | `quick`, `standard`, `comprehensive` |
| `network_discovery` | Network discovery / port scan (Nmap) | `ping_sweep`, `port_scan`, `service_detection`, `comprehensive`, `vulnerability_scan` |
| `ssl_security` | SSL/TLS configuration (testssl.sh) | `quick`, `standard`, `comprehensive`, `vulnerability` |
| `security_headers` | HTTP security headers | `standard` |
| `api_security` | API security testing | `standard` |
| `container_image` | Container image vulnerabilities | `standard` |
| `kubernetes_manifest` | Kubernetes manifest checks | `standard` |
| `lightweight_comprehensive` | Combined lightweight scans with scoring | `standard` |
| `code_security` | SAST + dependencies + secrets + IaC + SBOM | `standard` |
| `sast` / `dependency_scan` / `secret_scan` / `iac_scan` / `sbom` | Individual code-security scans | `standard` |

:::tip Discover scan types programmatically
`GET /api/cicd/scan-types` (with your `X-API-Key`) returns the live list of supported scan types, their available profiles, and descriptions — handy for keeping pipeline config in sync.
:::

### Read the trigger response

A successful trigger returns a `scan_id` and the URLs to follow it:

```json
{
  "data": {
    "scan_id": "…",
    "status": "pending",
    "scan_type": "nuclei",
    "scan_profile": "standard",
    "target": "https://staging.example.com",
    "status_url": "/api/cicd/scans/<scan_id>/status",
    "results_url": "/api/cicd/scans/<scan_id>/results"
  }
}
```

Capture the `scan_id` for the next steps:

```bash
SCAN_ID=$(curl -s -X POST "$OFFLOAD_API_URL/api/cicd/scans/trigger" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"scan_type":"nuclei","target":"https://staging.example.com","scan_profile":"standard","fail_on_severity":"high"}' \
  | jq -r '.data.scan_id')
```

### Poll status

The scan runs in the background. Poll its status until it reaches a terminal state (`completed` or `failed`):

```bash
curl -s "$OFFLOAD_API_URL/api/cicd/scans/$SCAN_ID/status" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq '.data.status'
```

### Fetch results and gate the build

Once the scan is `completed`, fetch the full results — including the severity breakdown and the `gate_passed` verdict — and fail the job if the gate didn't pass:

```bash
RESULT=$(curl -s "$OFFLOAD_API_URL/api/cicd/scans/$SCAN_ID/results" \
  -H "X-API-Key: $OFFLOAD_API_KEY")

echo "$RESULT" | jq '.data.findings_by_severity'

if [ "$(echo "$RESULT" | jq -r '.data.gate_passed')" = "false" ]; then
  echo "Security gate failed — findings at or above the configured severity."
  exit 1
fi
```

The results payload includes `status`, `findings_count`, `findings_by_severity`, `gate_passed`, `fail_on_severity`, your `pipeline_context`, and the full `result` object.

:::note Container image policies
For `container_image` scans, any **enforce-mode** image policies configured for your team are evaluated against the findings, and a failing policy also sets `gate_passed=false`. Audit-mode policies are recorded but don't fail the gate. See **[Container Security](./security-scanning/container-security.md)**.
:::

### Example: minimal pipeline step

```bash
# 1) Trigger
SCAN_ID=$(curl -s -X POST "$OFFLOAD_API_URL/api/cicd/scans/trigger" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"scan_type":"web_vulnerability","target":"'"$STAGING_URL"'","scan_profile":"standard","fail_on_severity":"high"}' \
  | jq -r '.data.scan_id')

# 2) Poll until terminal
while :; do
  STATUS=$(curl -s "$OFFLOAD_API_URL/api/cicd/scans/$SCAN_ID/status" \
    -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.data.status')
  echo "status: $STATUS"
  case "$STATUS" in completed|failed) break;; esac
  sleep 15
done

# 3) Enforce the gate
GATE=$(curl -s "$OFFLOAD_API_URL/api/cicd/scans/$SCAN_ID/results" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.data.gate_passed')
[ "$GATE" = "true" ] || { echo "Security gate failed"; exit 1; }
```

---

## 3. The GitHub Action

For GitHub repositories, the **Offload Security Scan** action wraps everything above: it triggers the scan, waits for completion, posts a results comment on the pull request, and fails the job based on your threshold.

### Set up

1. Create an API key with the **CI/CD Pipeline (Basic)** preset (see step 1).
2. In your repository, add these **secrets** (Settings → Secrets and variables → Actions):
   - `OFFLOAD_API_URL` — your platform URL (for example `https://security.yourcompany.com`).
   - `OFFLOAD_API_KEY` — the API key you created.
   - `STAGING_URL` — the environment to scan.
3. Add a workflow, for example `.github/workflows/security-scan.yml`:

```yaml
name: Security Scan

on:
  pull_request:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write   # required to post the PR comment
      contents: read
    steps:
      - name: Run Offload Security Scan
        uses: niteshsaini/offload-cspm/github-action@main
        with:
          api_url: ${{ secrets.OFFLOAD_API_URL }}
          api_key: ${{ secrets.OFFLOAD_API_KEY }}
          target_url: ${{ secrets.STAGING_URL }}
          fail_on: high
```

### Key inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `api_url` | Yes | — | Base URL of your Offload Security platform. |
| `api_key` | Yes | — | API key with `scans:trigger` and `scans:read` scopes. |
| `target_url` | Yes* | — | URL to scan for a web scan. *Required unless `container_image` is set. |
| `container_image` | No | — | Image reference to scan instead of a URL (for example `…dkr.ecr.<region>.amazonaws.com/<repo>:<tag>`). Triggers a container scan and takes precedence over `target_url`. |
| `scan_types` | No | all | Comma-separated scan types. Web: `security_headers`, `ssl_config`, `owasp_top_10`, `technology_detection`, `waf_detection`, `owasp_api`, `zap`, `nuclei`, `nmap`, `testssl`. Container: `vulnerability`, `trivy`, `sbom`, `secrets`, `signature`. |
| `standards` | No | `asvs-l2,owasp-web-top10` | Compliance standards to map findings against: `asvs-l1`, `asvs-l2`, `owasp-web-top10`, `owasp-api-top10`, `nist-ssdf`. |
| `fail_on` | No | `critical` | Severity that fails the job: `critical`, `high`, `medium`, `low`, or `none` (never fail). |
| `timeout` | No | `1800` | Maximum seconds to wait for the scan (default 30 minutes). |
| `comment_on_pr` | No | `true` | Post the results summary as a PR comment. |
| `auth_config` | No | — | JSON for authenticated scanning (form login, bearer token, cookie, or custom header). |

### Outputs

The action exposes results you can use in later steps, including `scan_id`, `status`, `total_findings`, `critical_count`, `high_count`, `medium_count`, `low_count`, `info_count`, `security_rating` (A–F), `security_score` (0–100), and `report_url`.

```yaml
      - name: Run Security Scan
        id: scan
        uses: niteshsaini/offload-cspm/github-action@main
        with:
          api_url: ${{ secrets.OFFLOAD_API_URL }}
          api_key: ${{ secrets.OFFLOAD_API_KEY }}
          target_url: https://staging.example.com
          fail_on: none   # capture results without failing the job
      - name: Block deploy on critical findings
        if: steps.scan.outputs.critical_count > 0
        run: |
          echo "Blocking — ${{ steps.scan.outputs.critical_count }} critical findings"
          exit 1
```

:::tip Authenticated scans
To scan behind a login, pass an `auth_config` JSON string (`form`, `bearer`, `cookie`, or `header`). Store credentials as secrets and reference them inside the JSON. Authenticated scans take longer — raise `timeout` accordingly.
:::

:::warning Reachability
The platform performs the scan from its own network, so `target_url` (and registry images) must be **reachable from the platform** — `localhost` and private-only addresses won't work. For PR workflows, point at a preview or staging environment.
:::

---

## After the scan

Scans triggered from CI/CD are first-class citizens in the platform:

- They appear in your scan history and on the **Dashboard**, scoped to your active team.
- Findings flow into **[Vulnerability Management](./vulnerability-risk/vulnerability-management.md)** for triage and SLA tracking.
- Significant findings can be promoted to the **[Risk Register](./vulnerability-risk/risk-register.md)** and rolled into reports.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `401 Unauthorized` | Missing/invalid `X-API-Key`, an expired or revoked key, or a key without the required scope. |
| `400 Unknown scan_type` | The `scan_type` isn't one of the supported values — check `GET /api/cicd/scan-types`. |
| Status stays `pending`/`running` | The scan is still in progress; keep polling. Large scans (full ZAP) can take 20+ minutes. |
| GitHub Action: no PR comment | The job is missing `permissions: pull-requests: write`. |
| Scan can't reach the target | The target isn't reachable from the platform (private/`localhost` address). |

## Related

- **[Scan Management](./security-scanning/scan-management.md)** — review, filter, and re-run scans in the UI.
- **[Container Security](./security-scanning/container-security.md)** — image scanning, SBOMs, and image policies.
- **[API & Code Scanning](./security-scanning/api-code-scanning.md)** — SAST, secrets, dependency, and IaC scanning details.
- **[Vulnerability Management](./vulnerability-risk/vulnerability-management.md)** — work the findings your pipeline produces.
