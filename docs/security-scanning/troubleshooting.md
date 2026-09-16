---
title: "Scanning Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 10
description: "Fix the common problems across web, code, container and Kubernetes scanning — scans that stay running, empty results, token and credential errors, gates that fail unexpectedly — and answers to frequent questions."
---

# Scanning Troubleshooting & FAQ

## Web, API & host scans

**The scan stays `running` far longer than its profile says.**
Comprehensive ZAP and Nuclei scans of large applications can take longer than the estimate, but a scan that shows no progress for over an hour is usually a target that stopped responding or blocks the scanner. Check the target from the platform's network, then **Rescan** with the *gentle* rate-limit profile or a *Standard* scan.

**The result is suspiciously clean.**
An unauthenticated scan only sees the public surface; enable an **authenticated scan** so the engine reaches the application. If the pre-scan credential check fails, fix the credentials before re-running — a run whose login failed is flagged rather than presented as clean.

**Findings I fixed still show.**
Results are per run. **Rescan** the target and read the new run; older runs are kept as history.

**Cloud posture scans are not in the list.**
By design — they live on Cloud Security → [Cloud Scans](../cloud-security/scan-orchestration.md#scan-history). The Scan Results hub is for application and host testing.

## Code

**"GitHub rejected the stored token" / repositories do not load.**
The token expired, was revoked, or lacks read access to the organisation. Reconnect under Automation → Git Connections with a fresh token that has repository read scope (and SSO authorisation if your organisation enforces it).

**The scan finished `completed_with_errors`.**
One engine could not run — most often a missing lockfile for SCA, a language OpenGrep has no rules for, or a build artifact that is not a supported type. Open the report: the tools that ran are complete; the failing tool's error is shown. Re-run after fixing the input.

**Far fewer dependency findings than expected.**
SCA resolves dependencies from **manifests and lockfiles** (such as `package-lock.json`, `yarn.lock`, `requirements.txt`, `poetry.lock`, `go.sum`, `pom.xml`). Repositories without them cannot be resolved precisely; commit the lockfile or upload an SBOM under SBOM & Licenses.

**Licences show as *unknown*.**
Enable **licence enrichment via deps.dev** on the SBOM & Licenses tab (opt-in); it looks up licences the manifests omit. In air-gapped deployments unknown licences must be classified manually.

**Fix PR fails.**
The token needs pull-request write scope and the user needs the **Execute Remediations** permission. Branch protection that forbids bot pushes also blocks it — allow the bot identity or open the PR manually with **Copy PR body**.

**A CI pipeline fails the gate but I see no critical findings.**
Check the gate that fired: the severity threshold (`fail_on_severity`), the **SCA policy pack** (an AGPL or malicious-package rule blocks regardless of severity), or the **image admission policy**. The pipeline log names the rule and the pack version.

## Containers

**Registry sync fails with "Cloud account … not found".**
The registry was linked to a cloud account that has since been removed. Edit the registry and select a current account, or supply inline credentials.

**Image scan fails immediately or reports 0 packages.**
The platform could not pull the image — private registry without credentials, wrong tag, or a registry that requires a pull token. Check the scan's error, add the registry connection, and re-scan. A result with **0 components** is not a clean image; treat it as a failed pull.

**Scan of a very large image fails.**
Images with tens of thousands of packages can exceed the result size the platform stores inline. Scan the image through a **registry** (results are offloaded to object storage) rather than Quick Scan.

**Webhook deliveries are rejected.**
Verify the registry sends to the exact callback URL and that its signature matches the secret shown when the webhook was created. **View Events** lists every delivery and why it was rejected.

## Kubernetes

**Connectivity test fails.**
In order: the API server URL is reachable from the platform (private clusters need a route or a bastion); the token or kubeconfig has not expired; the RBAC profile is applied (`kubectl auth can-i list pods --as=system:serviceaccount:<ns>:<sa>`). A kubeconfig that points at a private-network or metadata address, or uses an `exec` credential plugin, is rejected on purpose.

**The scan finished `degraded`.**
The per-scan API budget (`K8S_SCAN_MAX_API_CALLS`, default 5,000) was exhausted on a large cluster. Results are partial; raise the budget for that deployment or scan namespaces selectively.

**Compliance shows "Not Assessed" or "pending".**
A cluster is scored only after a scan has **completed**. Run a scan; the posture refreshes on the next sweep (a few minutes). If it never fills in, check the backend logs for `Failed to store report snapshot` — environments provisioned before mid-2026 may carry a legacy unique index that blocks report inserts; upgrading to a current release drops it automatically.

**Findings I suppressed came back.**
Suppressions persist across scans; what returns is a **new** finding on a different resource with the same check. Suppress at the resource, or fix the underlying policy so the check passes.

## Frequently asked questions

**Does any scan modify my systems?**
Web, API, network and WAF tests **send traffic** but do not change data unless the application itself does so on the payloads they send; use staging for comprehensive active scans. Code, image and cluster scans are read-only. The only write actions are explicit: **Fix PR** (opens a pull request) and the CI gate's exit code.

**Where do the engines run?**
Inside the platform's own workers — Trivy, Grype, Syft, OpenGrep, Bandit, Gitleaks, Checkov, kube-bench, Polaris, Kubescape, ZAP, Nuclei, Nmap and testssl.sh ship with it. Nothing about your code or images leaves the platform except the optional deps.dev licence lookups (package names and versions only).

**How long are results kept?**
Per the retention policy under [Scan Management](./scan-management.md#result-retention); findings with triage decisions and their history are kept with the finding.

**Can I scan on-premises clusters and registries?**
Yes — any cluster the platform can reach with a kubeconfig or service-account token, and images from any registry the platform can pull from with credentials.

**Which scan should gate a pull request?**
SAST + Secrets on every PR; Full Code Security and a Compiled Image Scan on merge and nightly; the SCA policy pack and image admission policy at release. See [CI/CD & Automation](./code/ci-cd-and-automation.md).

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment. When contacting support include the **scan ID** and, for code scans, the report's tool breakdown.
