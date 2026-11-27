---
title: "Scanning Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 10
description: "Fix the common problems across web, code, container and Kubernetes scanning — scans that stay running, empty results, token and credential errors, gates that fail unexpectedly — and answers to frequent questions."
---

# Scanning Troubleshooting & FAQ

## Web, API & host scans

**The scan stays `running` far longer than its profile says.**
Comprehensive ZAP and Nuclei scans of large applications can take longer than the estimate, but a scan that shows no progress for over an hour is usually a target that stopped responding or blocks the scanner. Check the target from the platform's network, then **Rescan** with a *Standard* profile, or run an App Scan with the **Gentle** resource mode.

**Submit is greyed out in the launcher.**
App Scan, ZAP, Nuclei, Nmap and testssl.sh runs need the **I am authorized to test this target** box ticked under **Authorization & scope**.

**API or CI calls fail with 400 "confirm you are authorized to test these targets".**
The deployment sets `SCAN_REQUIRE_AUTHORIZATION=true`. Send an `engagement` object with `"attested": true` ([Scanning API](./api.md#web-api--host-scans)). A `valid_until` in the past is also refused.

**"Target refused" for an internal host or range.**
Private (RFC 1918) targets need `ALLOW_PRIVATE_SCAN_TARGETS=true` on the deployment; loopback, link-local and cloud-metadata addresses are always refused. An Nmap range larger than `SCAN_MAX_NETWORK_HOSTS` (default 4,096 addresses) is refused too.

**Rescan is refused.**
The run's authorized window (**Authorized until**) has ended. Start a new scan with a fresh attestation.

**The App Scan failed before any tool ran.**
The pre-scan login check failed; the failure card names the reason. For OAuth2, the token could not be obtained or the probe URL rejected it — use **Test authentication** in the launcher.

**Browser Login is missing from the Auth Type list.**
It is offered only when the deployment sets `DAST_BROWSER_AUTH=true`.

**The result is suspiciously clean.**
An unauthenticated scan only sees the public surface; run an authenticated App Scan so the tools reach the application. Check the run for a **partial** status or a **Degraded coverage** badge: if ZAP could not run, only built-in HTTP checks ran. For App Scans, check **Session checks during scan** — requests made after a lost session were unauthenticated.

**Nmap: "partial — no host responded".**
The hosts drop ping probes, so nothing was port-scanned. Tick **Skip host discovery (-Pn)** and rescan.

**Nmap UDP is refused, or the run says "OS detection skipped".**
Both need raw sockets, which the Docker scanner engine has and an unprivileged local engine does not.

**Findings I fixed still show.**
Results are per run. **Rescan** the target and open the new run: **Compared with the previous run** lists what is now fixed. A finding missing from a **partial** run is listed as *not seen*, not fixed. For an App Scan finding, use **Retest this finding**.

**I deleted a scan by mistake.**
Deleted runs are kept as tombstones for `SCAN_TOMBSTONE_DAYS` (default 30) but are not restorable from the UI; contact your administrator or support with the scan ID.

**Scheduled network or container scans always fail with "not yet implemented".**
Those two schedule types do not run in 1.4.0 — see [Scan Management](./scan-management.md#which-scan-types-can-be-scheduled).

**Cloud posture scans are not in the list.**
By design — they live on Cloud Security → [Cloud Scans](../cloud-security/scan-orchestration.md#scan-history). Scanning is for application and host testing.

## Code

**"GitHub rejected the stored token" / repositories do not load.**
The token expired, was revoked, or lacks read access to the organization. Reconnect under Automation → Git Connections with a fresh token that has repository read scope (and SSO authorization if your organization enforces it).

**The scan finished `completed_with_errors`.**
One engine could not run — most often a missing lockfile for SCA, a language OpenGrep has no rules for, or a build artifact that is not a supported type. Open the report: the tools that ran are complete; the failing tool's error is shown. Re-run after fixing the input.

**Far fewer dependency findings than expected.**
SCA resolves dependencies from **manifests and lockfiles** (such as `package-lock.json`, `yarn.lock`, `requirements.txt`, `poetry.lock`, `go.sum`, `pom.xml`). Repositories without them cannot be resolved precisely; commit the lockfile or upload an SBOM under SBOM & Licenses.

**Licenses show as *unknown*.**
Enable **license enrichment via deps.dev** on the SBOM & Licenses tab (opt-in); it looks up licenses the manifests omit. In air-gapped deployments unknown licenses must be classified manually.

**Fix PR fails.**
The token needs pull-request write scope and the user needs the **Execute Remediations** permission. Branch protection that forbids bot pushes also blocks it — allow the bot identity or open the PR manually with **Copy PR body**.

**A secret shows *verified live* although we rotated it.**
Validation happens during the scan; re-run the scan after rotating. If the badge persists, the credential is still accepted by the provider — check that the rotation actually revoked the old key (some providers keep the previous key valid for a grace period).

**Datadog / regional keys always come back *not validated*.**
Datadog keys are bound to a site and the platform validates against `datadoghq.com` unless `DATADOG_SITE` names yours (`datadoghq.eu`, `us3.datadoghq.com`, …). A wrong-site answer is deliberately reported as *not validated*, never as *inactive*.

**Custom rules are not applied.**
`GET /api/code/scan-rules/custom` says whether the directory is mounted and lists rejected files with the reason. A file that fails validation is skipped, the rest still run. The directory is read on the next scan — no restart needed — but a file the scanner cannot parse never becomes active.

**GitLab / Bitbucket merge requests are not reviewed.**
Check `GET /api/scm/webhooks/<provider>` says *configured*, that the webhook URL on the project ends in the `hook_id` you were given, and that the secret matches — a mismatch is rejected with 401 and logged. The provider's webhook delivery log shows the response.

**A fix pull request merged but the finding says *verification inconclusive*.**
The verification scan could not prove the fix: it ran on a different commit, its findings were truncated, or the scanner that produced the original finding did not complete. Re-run a scan of the merged branch; a completed run of that scanner records the verdict.

**Fix with agent is disabled / runs stay queued.**
The button's tooltip names the reason. The deployment switch is `AGENTIC_FIX_ENABLED=true` **and** the fix worker must be running under the `agentic-fix` compose profile; then a team admin switches agentic fixes on in the Findings tab banner. A run also needs a model provider configured for the team.

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
Web, API, network and WAF tests **send traffic**. Active scans submit payloads, and an authenticated scan acts as its account, so they can create, change or delete data the application lets that account touch; App Scan's state-changing API probes are off unless you opt in. Use staging and a test account for comprehensive active scans. Code, image and cluster scans are read-only. The only write actions are explicit: **Fix PR** (opens a pull request) and the CI gate's exit code.

**Where do the engines run?**
Inside the platform's own workers — Trivy, Grype, Syft, OpenGrep, Bandit, Gitleaks, Checkov, Polaris, Kubescape, ZAP, Nuclei, Nmap and testssl.sh ship with it. ZAP, Nuclei (and its template release), testssl.sh and Nmap run from pinned image versions recorded on every run. Your code and images are scanned locally. Data leaves the platform only for lookups you enable or configure — for example deps.dev license enrichment (package names and versions) — and for AI features, which send finding details and, for code, snippets to the AI provider your team configures.

**How long are results kept?**
Per the retention policy under [Scan Management](./scan-management.md#result-retention); findings with triage decisions and their history are kept with the finding.

**Can I scan on-premises clusters and registries?**
Clusters: yes — any cluster the platform can reach with a kubeconfig or service-account token. Registries: saved registry connections support Amazon ECR, Google Artifact Registry and Azure Container Registry; see [Container Security](./containers/index.md) for other ways to scan an image.

**Which scan should gate a pull request?**
SAST + Secrets on every PR; Full Code Security and a Compiled Image Scan on merge and nightly; the SCA policy pack and image admission policy at release. See [CI/CD & Automation](./code/ci-cd-and-automation.md).

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment. When contacting support include the **scan ID** and, for code scans, the report's tool breakdown.
