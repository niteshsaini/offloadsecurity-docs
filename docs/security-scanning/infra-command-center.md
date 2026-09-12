---
title: "Infra Command Center"
sidebar_label: "Infra Command Center"
sidebar_position: 8
description: "Wire the platform's scan into GitHub Actions or Jenkins in three steps, test whether your WAF actually blocks common attack payloads, and load-test an API endpoint."
---

# Infra Command Center

The Infra Command Center collects the operational checks that sit next to scanning: the **CI/CD setup guides** (GitHub Actions and Jenkins) for the platform's scan step, a **WAF test** that fires real attack payloads at a URL to see what gets through, and an **API load test**.

**Where:** left navigation → **Infra Command Center**.

## GitHub Actions and Jenkins

**Where:** Infra Command Center → **GitHub Actions** / **Jenkins**.

![GitHub Actions tab: how it works, step 1 create a CI/CD API key, step 2 add repository secrets OFFLOAD_API_URL and OFFLOAD_API_KEY with copy buttons, step 3 add the workflow step](/img/screenshots/security-scanning/infra-github-actions.webp)

Both tabs walk through the same three steps for their CI system:

1. **Create a CI/CD API key** — generated here with the CI preset (scan trigger + read scopes); the key is shown once. [Manage all API keys](../api-reference/authentication.md).
2. **Add the secrets** — `OFFLOAD_API_URL` (pre-filled with this instance's URL) and `OFFLOAD_API_KEY`: in GitHub under *Settings → Secrets and variables → Actions → New repository secret*; in Jenkins under *Manage Jenkins → Credentials → System → Global credentials → Add Credentials* (the tab shows the credential IDs the Jenkinsfile expects).
3. **Add the step** — GitHub gets the **Offload Security Scan** action; Jenkins gets a `Jenkinsfile` stage that runs `bash jenkins/scan.sh`. Both trigger an **App Scan** of your target (a web URL, or a container image), poll until it finishes, print the results, and **fail the build when the severity threshold is breached** (`fail_on`, default `critical`; `timeout` default 30 minutes). On GitHub the action also posts the results as a pull-request comment and can set a commit status.

![Jenkins tab: the same three steps with Jenkins credential IDs and the Jenkinsfile stage](/img/screenshots/security-scanning/infra-jenkins.webp)

The action's inputs cover `target_url` or `container_image`, optional `code_repo` / `code_branch` / `git_provider` for code scans, `cloud_account_id` for a posture scan, signature verification (`signature_identity`, `signature_oidc_issuer`) and `secrets_only_verified` to fail only on live secrets. For GitLab, Bitbucket and Azure DevOps use the generator in [CI/CD & Automation](./code/ci-cd-and-automation.md#generate-a-pipeline); the underlying REST calls are documented in [CLI & CI/CD](../cli-and-cicd.md).

## WAF Testing

**Where:** Infra Command Center → **WAF Testing**.

![WAF Testing tab: target URL field, Test WAF button, and a recent test of the company site scoring 100/100](/img/screenshots/security-scanning/infra-waf-testing.webp)

Enter a URL and select **Test WAF**. The platform sends **ten attack payloads** — SQL injection (UNION and boolean), reflected XSS and event-handler XSS, local file inclusion, remote code execution, XXE, SSRF to cloud metadata, URL path traversal and Log4Shell (JNDI) — and records, per rule, whether the request was **blocked** or **passed**. The result is a score out of 100, the detected WAF vendor where one identifies itself, and the list of payloads that got through — the ones to add rules for. Recent tests are kept per target.

:::warning[Real attack traffic]
These payloads are genuine attack strings. Only test endpoints you own; on shared platforms confirm your provider's testing policy first.
:::

## API Load Test

**Where:** Infra Command Center → **API Load Test**.

![API Load Test tab: target URL, method, rate (requests per second), duration, and a recent test of 50 requests with average latency](/img/screenshots/security-scanning/infra-load-test.webp)

Point it at an endpoint, choose the **method**, a **rate** (requests per second, up to 500) and a **duration** (5 seconds to 2 minutes), and **Start Load Test**. You get total, successful and failed requests, the status-code distribution and latency (average, min, max). It is a quick sanity check that an endpoint — or the rate limit in front of it — behaves as expected, not a replacement for a full performance suite.

## Related

- [CLI & CI/CD](../cli-and-cicd.md) — the complete pipeline contract.
- [CI/CD & Automation](./code/ci-cd-and-automation.md) — generated pipelines for every provider and the release gates.
- [Running Web, API & Host Scans](./native-scans.md) — the scans a pipeline triggers.
