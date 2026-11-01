---
title: "Scanning API"
sidebar_label: "API"
sidebar_position: 9
description: "Every App & Infrastructure Scanning workflow over REST — web/API/host scans, code scans and findings lifecycle, SBOMs, container registries and image scans, policies and CI gates, Kubernetes clusters, scans and findings."
---

# Scanning API

Everything in this section can be driven over the REST API. This page maps each workflow to its endpoints; [API Reference](../api-reference/index.md) covers authentication and conventions, and [CLI & CI/CD](../cli-and-cicd.md) covers the pipeline contract in depth. The interactive Swagger UI at `https://<your-host>/api/docs` is exhaustive, but it is off in production unless the deployment sets `ENABLE_API_DOCS=true`.

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"
```

Send the key as `X-API-Key`; calls are scoped to the key's team.

## Web, API & host scans

| Task | Endpoint | Notes |
| --- | --- | --- |
| Start a targeted scan | `POST /api/native-scans/web-vulnerability` · `/network-discovery` · `/ssl-security` · `/security-headers` · `/api-security-testing` · `/nuclei/url-scan` (`/nuclei/bulk-scan` for many URLs) | Body per tool: `target_url` or `target`, `scan_type` (`quick` / `standard` / `comprehensive`; network: `ping_sweep` / `port_scan` / `service_detection` / `full_tcp` / `udp_top` / `comprehensive` / `vulnerability_scan`), optional auth. Returns `scan_id` and `status`. Headers scan completes inline. |
| Engagement and scope | `engagement` object on App Scan, ZAP, Nmap, testssl.sh and Nuclei requests | `{ "attested": true, "reference", "environment": "production" \| "staging" \| "development" \| "test" \| "unspecified", "valid_until": "YYYY-MM-DD" }`. Who / when are taken from the caller. Required (else 400) only when `SCAN_REQUIRE_AUTHORIZATION=true`. ZAP also takes `exclude_paths`; Nmap takes `exclude_hosts`, `skip_host_discovery` (`-Pn`) and `timing` (`polite` / `normal` / `aggressive`). |
| Poll / read | `GET /api/native-scans/results/{scan_id}` | `status` (`running` → `completed` / `partial` / `failed`), `findings[]`, `findings_count`, `metadata.provenance`, `metadata.artifacts`, `metadata.engagement`. |
| List | `GET /api/native-scans/results?tool_type=&status=&scan_type=&search=&exclude_app_scan_children=&limit=&skip=` | `total` is the true matching count; `limit` up to 500. |
| History as a target tree | `GET /api/native-scans/scan-history?tool_type=&status=&exclude_app_scan_children=&runs_per_group=&max_targets=` | Target → scan type → runs. Each group has its true `run_count`; `runs_per_group` up to 200 (default 50), `max_targets` up to 300; `truncated`, `total_targets`, `total_scans`. |
| Compare runs | `GET /api/native-scans/results/{scan_id}/compare[?baseline={scan_id}]` | `new`, `fixed`, `not_seen`, `severity_changed`, `unchanged`, `counts`, `caveats`. Default baseline: the latest earlier completed / partial run of the same tool on the same target. 409 if a run is not completed or partial. |
| Download report | `GET /api/native-scans/results/{scan_id}/download?format=html\|pdf\|docx\|json\|csv[&include_screenshots=true]` | File stream with `X-Content-SHA256`; each download is logged and kept. |
| Raw tool output | `GET /api/native-scans/results/{scan_id}/artifacts/{name}` | Nmap XML, Nuclei JSONL, testssl JSON, ZAP JSON; `X-Content-SHA256`. |
| Re-scan / delete | `POST /api/native-scans/results/{scan_id}/rescan` · `DELETE /api/native-scans/results/{scan_id}` | Rescan carries profile, Nmap options, exclusions and attestation. Delete tombstones the run. |
| Statistics | `GET /api/native-scans/statistics` | Totals by tool and status. |
| Reconnaissance & lightweight | `POST /api/domain-recon` · `POST /api/lightweight-scans/technologies` · `/waf` · `/subdomains` · `/comprehensive` | Domain OSINT, fingerprint, WAF detection, subdomains. |
| API discovery / deep scan | `POST /api/api-scan/discover` · `POST /api/api-scan/deep-scan` · `POST /api/api-scan/upload-spec` · `POST /api/api-scan/upload-postman` | Endpoint discovery, then OWASP API Top 10 testing of discovered endpoints, an OpenAPI file or a Postman collection. |
| Consolidated report | `POST /api/reports/consolidated` · `GET /api/reports/{job_id}/download` · `GET /api/reports/history` | Merge selected scans into one HTML / PDF / Word report; generated in the background. |
| CI trigger / poll / gate | `POST /api/cicd/scans/trigger` · `GET /api/cicd/scans/{scan_id}/status` · `GET /api/cicd/scans/{scan_id}/results` | `scan_type`, `target`, `scan_profile`, `fail_on_severity` → `gate_passed`. Release-gate policy: `GET /api/ci/gate/policy`, history `GET /api/ci/gate/history`; SARIF `GET /api/ci/scan/{scan_id}/sarif`; badges `GET /api/ci/badge/{type}.svg`. |

### App Scan

| Task | Endpoint | Notes |
| --- | --- | --- |
| Start | `POST /api/app-scan` | `{ "target_url", "scan_types"?, "standards"?, "options"?, "engagement"? }`. `standards` defaults to `["asvs-l2", "owasp-web-top10"]`. `options` carries `rate_limit_profile` (`gentle` / `normal` / `aggressive`), `auth_config`, `exclude_paths`, the second user, and the state-changing-probes opt-in. |
| Auth types | `options.auth_config.auth_type` | `bearer` · `cookie` · `header` · `form` · `oauth2_client_credentials` · `oauth2_refresh_token` · `browser_login` (only with `DAST_BROWSER_AUTH=true`; otherwise refused with 400). |
| Test a login | `POST /api/app-scan/validate-auth` | Same pre-scan check the scan runs; for OAuth2 it fetches a token and calls the probe URL. |
| What this deployment accepts | `GET /api/app-scan/auth-capabilities` | `browser_login`, `auth_guard` and the guard's default keywords. |
| List / read | `GET /api/app-scan?limit=` (up to 100) · `GET /api/app-scan/{app_scan_id}` | Status, completeness, findings, coverage, rating, `tool_versions`, authentication verdict. |
| Report | `GET /api/app-scan/{app_scan_id}/report?format=html\|pdf` | Completed scans only. |
| SARIF | `GET /api/app-scan/{app_scan_id}/sarif` | SARIF 2.1.0; confirmed findings tagged `proven-exploitable`. Export only. |
| Retest a finding | `POST /api/app-scan/{app_scan_id}/findings/{finding_id}/retest` | Body for authenticated scans: `{ "secrets": { "password" \| "token" \| "cookie_string" \| "header_value": "…" } }` (not stored). Without it an authenticated finding is `inconclusive`. The old `POST /api/app-scan/retest` with a bare finding is refused (410). |
| API inventory | `GET /api/app-scan/api-inventory?target_url=&include_gone=` | Endpoints seen across scans, with first / last seen and active / gone. |

### Evidence and integrity

| Task | Endpoint | Notes |
| --- | --- | --- |
| Exports issued for a scan | `GET /api/native-scans/results/{scan_id}/exports` | Format, SHA-256, size, who, when, whether the copy is kept. |
| Re-download an issued report | `GET /api/native-scans/results/{scan_id}/exports/{sha256}` | The byte-for-byte copy as issued, not regenerated. |
| Verify a report | `GET /api/native-scans/exports/verify?sha256=` | Matches the team's scan exports and consolidated reports. |
| Network VAPT report | `GET /api/export/network-vapt` (PDF) · `/api/export/network-vapt.docx` · `/api/export/network-vapt.html` | Greenbone OpenVAS + Nmap; needs View Vulnerabilities, View Scans or View Assessments. Wazuh correlation only for users who can view integrations. |
| Retention | `GET /api/scan-retention/status` · `GET /api/scan-retention/policies` · `POST /api/scan-retention/run-cycle` | Run-cycle needs **Manage Scans**. |

See [Engagement & Evidence](./scan-evidence.md) and [Network Scans & VAPT Report](./network-scans.md).

## Code

| Task | Endpoint | Notes |
| --- | --- | --- |
| Git connections | `GET /api/code/connections` · `POST /api/code/connections/{provider}` · `DELETE …/{provider}` | `provider` = `github` \| `gitlab` \| `bitbucket`; body `{ "token", "username" }`. Token is validated against the provider. |
| Repositories & branches | `GET /api/code/repos?provider=` · `GET /api/code/repos/{repo}/branches` | Live from the provider. |
| Start a scan | `POST /api/code/scan` | `{ "provider", "repo", "branch", "scan_type" }` — `code_security` \| `sast` \| `dependency_scan` \| `secret_scan` \| `iac_scan` \| `sbom` \| `compiled_image`; optional `policy_pack`. Returns `scan_id`. |
| Upload a ZIP / artifact / image | `POST /api/code/upload-scan` (multipart `file`) · `POST /api/code-scan/artifact` · `POST /api/code-scan/image` | ZIP up to 500 MB; artifacts `.jar .war .ear .whl .egg .tgz .gem .nupkg`. |
| Poll | `GET /api/code/scan-status/{scan_id}` | `status`, `progress`, `phase`. |
| Reports | `GET /api/code/reports?limit=&offset=&application=&owner=` · `GET /api/code/reports/{scan_id}` · `GET …/export` · `GET …/artifact/{kind}` · `DELETE …` · `POST /api/code/reports/bulk-delete` | |
| Findings lifecycle | `GET /api/code/findings/lifecycle` · `POST /api/code/findings/{fingerprint}/lifecycle` · `POST /api/code/findings/bulk-lifecycle` | Body `{ "state": "triaged" \| "resolved" \| "risk_accepted" \| "false_positive" \| "reopened", "repo": "owner/name", "scope": "repo" \| "team", "justification", "owner", "expires_at", "evidence" }` — required fields depend on the state and the policy pack. `repo` is required (the decision is scoped to that repository) unless `scope` is `team`; bulk takes `items: [{ "fingerprint", "repo" }]`. |
| Suppressions | `GET /api/triage/suppressions?include_inactive=` | Rule exceptions, code lifecycle decisions and triage decisions with since / expiry / days remaining per row. |
| Custom rules | `GET /api/code/scan-rules/custom?refresh=` | What the last scan used, per engine, with rejected files and reasons ([Custom Rules](./code/custom-rules.md)). |
| Push protection | `POST /api/secrets/push-protection/scan` | `{ "content", "filename", "validate", "fail_on_block" }` — masked `findings` + `blocked`; `fail_on_block` returns 422 ([Secret Detection](./code/secret-detection.md#push-protection)). |
| Pull-request review hooks | `POST /api/scm/webhooks/{provider}/secret` · `GET /api/scm/webhooks/{provider}` · `POST /api/scm/webhooks/{provider}/{hook_id}` (inbound) | `provider` = `gitlab` \| `bitbucket`. The secret is returned once ([Pull Request Review](./code/pull-request-review.md)). |
| Fix with agent | `GET /api/agentic-fix/status` · `POST /api/agentic-fix/from-scan` · `POST /api/agentic-fix/run` · `GET /api/agentic-fix/runs` · `GET …/runs/{run_id}` · `POST /api/agentic-fix/campaigns` · `GET …/campaigns/{campaign_id}` | `from-scan` takes `{ "scan_id", "fingerprint" }`. Team switch: `GET` · `POST /api/ai-agents/triage/auto-fix/settings` `{ "enabled" }`. Needs *Execute Remediations* ([Fix with Agent](./code/agentic-fixes.md)). |
| Comments & activity | `POST /api/code/findings/{fingerprint}/comment` · `GET …/activity` | |
| AI analysis / fix | `POST /api/code/scan/{scan_id}/ai-analyze` · `POST /api/code/scan/{scan_id}/ai-fix` | |
| Fix pull request | `POST /api/code/findings/fix-pr` | `{ repo, branch?, provider?, patch?, finding{…} }` — **writes to your Git host**; needs *Execute Remediations*. |
| SBOM & licenses | `POST /api/code/sbom` · `POST /api/code/sbom/upload` · `GET /api/code/sbom` · `GET /api/code/sbom/{scan_id}` · `…/download` · `…/export?format=csv\|csv-vulns\|json` · `…/notices` · `…/fix-plan` · `…/report` · `DELETE …` | Upload accepts CycloneDX (JSON/XML) or SPDX (JSON). |
| License enrichment | `GET` · `PUT /api/code/settings/license-enrichment` | `{ "enabled": true }` opts in to deps.dev lookups. |
| SCA policy | `GET /api/code/sca/policy` · `GET /api/code/sca/policy-packs` | Active rules and the versioned packs. |
| Repository ownership | `GET` · `PUT /api/code/repo-ownership` | `{ "repo", "application", "owner", "environment", "criticality" }`. |
| Pipeline generation | `GET /api/ci/pipeline/{provider}` · `POST /api/cicd/pipeline/comprehensive` | `provider` = `github_actions` \| `gitlab_ci` \| `bitbucket` \| `azure_devops` \| `jenkins`. |
| WAF test / load test | `POST /api/code/waf-scan` · `GET /api/code/waf-scans` · `POST /api/code/load-test` · `GET /api/code/load-tests` | Load test: `{ "target_url", "method", "rate" (≤500), "duration": "10s" }`. |

## Containers

| Task | Endpoint | Notes |
| --- | --- | --- |
| Providers & registries | `GET /api/container-registries/providers` · `POST /api/container-registries/saved` · `GET /api/container-registries/saved` · `GET` · `DELETE …/saved/{registry_id}` · `POST …/test-connection` | Providers `aws_ecr` \| `gcp_artifact_registry` \| `azure_container_registry`. `docker_hub` is listed by the API but its registry scanning is not supported yet. |
| Sync, browse, drift | `POST …/saved/{id}/sync` · `GET …/sync-status` · `GET …/repositories` · `GET …/images` · `GET …/vulnerability-summary` · `GET …/drift` | |
| Scan existing images | `POST …/saved/{id}/scan-existing` (`{ "repository"?, "max_images": 50 }`) · `GET …/scan-estimate` · scan jobs: `GET`/`POST …/scan-jobs`, `…/{job_id}/pause` · `/resume` · `/cancel` | |
| Polling | `POST …/saved/{id}/poll` · `GET …/polling-status` · `PUT …/polling-config` (`polling_interval_seconds` 300–86400) | |
| Quick scan | `POST /api/container/full-analysis` · `POST /api/container/scan-vulnerabilities` (`{ "image_name", "save_to_db": true }`) | Background; poll the list. |
| Results | `GET /api/container/scans` · `GET /api/container/scans/{scan_id}` · `GET …/export` · `GET /api/container-security/scans/{scan_id}/incremental-diff` · `GET /api/container-security/scan-history` · `GET /api/container-security/posture-trend` | |
| Dockerfile / secrets / signature | `POST /api/container-security/dockerfile/scan` · `GET …/dockerfile/rules` · `POST …/image/secrets` · `POST …/image/verify-signature` | |
| Policies | `GET` · `POST /api/container-security/policies` · `GET …/policies/templates` · `POST …/policies/validate-image` | |
| CI gate | `POST /api/container-security/cicd/scan-and-validate` | `{ image_name, build_id, git_commit, fail_on_policy_violation }` → `allowed`, `exit_code`. |
| Webhooks | `POST /api/container-security/webhooks/configure` · `GET …/webhooks` · `PUT …/webhooks/{id}/toggle` · `DELETE …/webhooks/{id}` · `GET …/webhooks/events` | Registry calls back `…/webhooks/registry-event/{webhook_id}`. |
| SBOM | `POST /api/container-security/sbom/generate` (`{ image_name, format: syft-json \| cyclonedx-json \| spdx-json }`) · `GET …/sbom/list` · `GET …/sbom/{sbom_id}` | |
| Compliance | `POST /api/container-security/compliance-report` (`{ target_id, target_type: image \| registry \| account, framework: cis-docker \| nist \| pci-dss \| soc2 }`) · `GET …/compliance-report/latest` · `GET …/compliance-report/frameworks` | |
| Coverage | `GET /api/container/coverage-summary` | |

## Kubernetes

| Task | Endpoint | Notes |
| --- | --- | --- |
| Clusters | `POST /api/k8s/clusters` · `GET /api/k8s/clusters` · `GET` · `PUT` · `DELETE …/{cluster_id}` · `POST …/bulk-import` · `POST …/bulk-delete` · `POST …/{cluster_id}/test` | Onboard with a base64 kubeconfig (safety-validated) or `api_server` + service-account token, `rbac_mode` `minimal` \| `extended`. See [Kubernetes API](../api-reference/kubernetes.md). |
| Discovered clusters | `GET /api/k8s/clusters/auto-discovered` · `POST /api/k8s/clusters/import-from-cloud` | From connected cloud accounts. |
| RBAC profiles | `GET /api/k8s/rbac-profiles` · `GET …/{profile}` · `POST /api/k8s/rbac/generate-script` (`{ profile, namespace, service_account_name }`) · `GET /api/k8s/pre-scan-script` | Manifest and deployment script. |
| Scans | `POST /api/k8s/scan` (`{ cluster_id, scanners?, namespaces?, severity_filter? }`) · `POST /api/k8s/scan/bulk` · `GET /api/k8s/scan/{scan_id}` · `GET /api/k8s/active-scans` | |
| Findings | `GET /api/k8s/findings?cluster_id=&severity=&status=&scanner=` · `GET …/grouped` · `GET …/{finding_id}` · `PUT …/{finding_id}/status` (`open` \| `resolved` \| `suppressed` \| `false_positive`, with `reason`) | |
| Dashboard & metrics | `GET /api/k8s/dashboard/{cluster_id}` · `GET /api/k8s/metrics/{cluster_id}` | Score, findings by category and scanner. |
| Compliance | `POST /api/k8s/compliance/report` (`{ cluster_id, framework: cis \| nist \| pci-dss \| soc2 \| hipaa }`) · `GET /api/k8s/compliance/{cluster_id}` · `GET /api/k8s/compliance/posture` · `GET /api/k8s/mitre-tactics` | Report export formats: `json`, `html`, `pdf`. |
| Coverage | `GET /api/kubernetes/coverage-summary` | |

## Permissions

| Action | Permission |
| --- | --- |
| Start scans of any type | **Run Scans** |
| Read results, findings, reports | **View Scans** |
| Registries, policies, webhooks, clusters | **Manage Container Security** |
| Change finding lifecycle | Any authenticated team member for code findings; **Manage Risks** for cloud findings |
| Open fix pull requests | **Execute Remediations** |
