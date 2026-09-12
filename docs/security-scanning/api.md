---
title: "Scanning API"
sidebar_label: "API"
sidebar_position: 9
description: "Every App & Infrastructure Scanning workflow over REST — web/API/host scans, code scans and findings lifecycle, SBOMs, container registries and image scans, policies and CI gates, Kubernetes clusters, scans and findings."
---

# Scanning API

Everything in this section can be driven over the REST API. This page maps each workflow to its endpoints; [API Reference](../api-reference/index.md) covers authentication and conventions, [CLI & CI/CD](../cli-and-cicd.md) covers the pipeline contract in depth, and Swagger at `https://<your-host>/api/docs` is exhaustive.

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"
```

Send the key as `X-API-Key`; calls are scoped to the key's team.

## Web, API & host scans

| Task | Endpoint | Notes |
| --- | --- | --- |
| Start a scan | `POST /api/native-scans/web-vulnerability` · `/network-discovery` · `/ssl-security` · `/security-headers` · `/api-security-testing` · `/nuclei/url-scan` (`/nuclei/bulk-scan` for many URLs) | Body per tool: `target_url` or `target`, `scan_type` (`quick` / `standard` / `comprehensive`; network: `ping_sweep` / `port_scan` / `service_detection` / `comprehensive` / `vulnerability_scan`), optional auth and `rate_limit_profile`. Returns `scan_id` and `status`. Headers scan completes inline. |
| Poll / read | `GET /api/native-scans/results/{scan_id}` | `status` (`running` → `completed` / `failed` / `partial`), `findings[]`, `findings_count`, `raw_output`. |
| List | `GET /api/native-scans/results?tool_type=&status=&limit=&skip=` | `count` is the page size. |
| Download report | `GET /api/native-scans/results/{scan_id}/download?format=html\|pdf\|docx` | File stream. |
| Re-scan / delete | `POST /api/native-scans/results/{scan_id}/rescan` · `DELETE /api/native-scans/results/{scan_id}` | |
| Statistics | `GET /api/native-scans/statistics` | Totals by tool and status. |
| Reconnaissance & lightweight | `POST /api/domain-recon` · `POST /api/lightweight-scans/technologies` · `/waf` · `/subdomains` · `/comprehensive` | Domain OSINT, fingerprint, WAF detection, subdomains. |
| API discovery / deep scan | `POST /api/api-scan/discover` · `POST /api/api-scan/deep-scan` | Endpoint discovery, then OWASP API Top 10 testing with optional spec upload. |
| App Scan (all tools) | `POST /api/app-scan` | One run, standards mapping, consolidated report. |
| Consolidated report | `POST /api/reports/consolidated` | Merge selected scans into one HTML/PDF/Word report. |
| CI trigger / poll / gate | `POST /api/cicd/scans/trigger` · `GET /api/cicd/scans/{scan_id}/status` · `GET /api/cicd/scans/{scan_id}/results` | `scan_type`, `target`, `scan_profile`, `fail_on_severity` → `gate_passed`. Release-gate policy: `GET /api/ci/gate/policy`, history `GET /api/ci/gate/history`; SARIF `GET /api/ci/scan/{scan_id}/sarif`; badges `GET /api/ci/badge/{type}.svg`. |

## Code

| Task | Endpoint | Notes |
| --- | --- | --- |
| Git connections | `GET /api/code/connections` · `POST /api/code/connections/{provider}` · `DELETE …/{provider}` | `provider` = `github` \| `gitlab` \| `bitbucket`; body `{ "token", "username" }`. Token is validated against the provider. |
| Repositories & branches | `GET /api/code/repos?provider=` · `GET /api/code/repos/{repo}/branches` | Live from the provider. |
| Start a scan | `POST /api/code/scan` | `{ "provider", "repo", "branch", "scan_type" }` — `code_security` \| `sast` \| `dependency_scan` \| `secret_scan` \| `iac_scan` \| `sbom` \| `compiled_image`; optional `policy_pack`. Returns `scan_id`. |
| Upload a ZIP / artifact / image | `POST /api/code/upload-scan` (multipart `file`) · `POST /api/code-scan/artifact` · `POST /api/code-scan/image` | ZIP up to 500 MB; artifacts `.jar .war .ear .whl .egg .tgz .gem .nupkg`. |
| Poll | `GET /api/code/scan-status/{scan_id}` | `status`, `progress`, `phase`. |
| Reports | `GET /api/code/reports?limit=&offset=&application=&owner=` · `GET /api/code/reports/{scan_id}` · `GET …/export` · `GET …/artifact/{kind}` · `DELETE …` · `POST /api/code/reports/bulk-delete` | |
| Findings lifecycle | `GET /api/code/findings/lifecycle` · `POST /api/code/findings/{fingerprint}/lifecycle` · `POST /api/code/findings/bulk-lifecycle` | Body `{ "state": "triaged" \| "resolved" \| "risk_accepted" \| "false_positive" \| "reopened", "justification", "owner", "expires_at", "evidence" }` — required fields depend on the state and the policy pack. |
| Comments & activity | `POST /api/code/findings/{fingerprint}/comment` · `GET …/activity` | |
| AI analysis / fix | `POST /api/code/scan/{scan_id}/ai-analyze` · `POST /api/code/scan/{scan_id}/ai-fix` | |
| Fix pull request | `POST /api/code/findings/fix-pr` | `{ repo, branch?, provider?, patch?, finding{…} }` — **writes to your Git host**; needs *Execute Remediations*. |
| SBOM & licences | `POST /api/code/sbom` · `POST /api/code/sbom/upload` · `GET /api/code/sbom` · `GET /api/code/sbom/{scan_id}` · `…/download` · `…/export?format=csv\|csv-vulns\|json` · `…/notices` · `…/fix-plan` · `…/report` · `DELETE …` | Upload accepts CycloneDX (JSON/XML) or SPDX (JSON). |
| Licence enrichment | `GET` · `PUT /api/code/settings/license-enrichment` | `{ "enabled": true }` opts in to deps.dev lookups. |
| SCA policy | `GET /api/code/sca/policy` · `GET /api/code/sca/policy-packs` | Active rules and the versioned packs. |
| Repository ownership | `GET` · `PUT /api/code/repo-ownership` | `{ "repo", "application", "owner", "environment", "criticality" }`. |
| Pipeline generation | `GET /api/ci/pipeline/{provider}` · `POST /api/cicd/pipeline/comprehensive` | `provider` = `github_actions` \| `gitlab_ci` \| `bitbucket` \| `azure_devops` \| `jenkins`. |
| WAF test / load test | `POST /api/code/waf-scan` · `GET /api/code/waf-scans` · `POST /api/code/load-test` · `GET /api/code/load-tests` | Load test: `{ "target_url", "method", "rate" (≤500), "duration": "10s" }`. |

## Containers

| Task | Endpoint | Notes |
| --- | --- | --- |
| Providers & registries | `GET /api/container-registries/providers` · `POST /api/container-registries/saved` · `GET /api/container-registries/saved` · `GET` · `DELETE …/saved/{registry_id}` · `POST …/test-connection` | Providers `aws_ecr` \| `gcp_artifact_registry` \| `azure_container_registry` \| `docker_hub`. |
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
