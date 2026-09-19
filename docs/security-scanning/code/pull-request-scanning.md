---
title: "Pull Request Scanning"
sidebar_label: "Pull Request Scanning"
sidebar_position: 5
description: "Scan every pull or merge request automatically: only the changed files, diffed against the base branch, with inline annotations, a summary comment and a pass/fail check you can make required."
---

# Pull Request Scanning

Open a pull request and see the findings **this change introduced** — on the changed lines, with a check that fails on those and not on the four hundred pre-existing issues in the repository. Nothing to click per pull request: the Git provider tells the platform a PR was opened or updated, the platform scans it and reports back on the PR.

**Where:** DevSecOps → **GitHub App** (GitHub), or the merge-request webhook endpoints (GitLab, Bitbucket). Results also land in Code Command Center → **Reports** like any other scan.

## What a PR scan does

| Step | What happens |
|---|---|
| **Scope** | Only findings in the PR's **changed files** count. Dependency (SCA) findings are included only when a manifest or lockfile changed (`package-lock.json`, `requirements.txt`, `go.sum`, `pom.xml`, `Cargo.lock`, …) — an untouched lockfile cannot have gained a CVE in this PR. |
| **Baseline diff** | Each scoped finding is compared with the latest scan of the **base branch** by a line-insensitive identity (tool, rule, file, normalised snippet), so a PR that only shifts lines introduces nothing. Findings split into **new** and **already present**. |
| **Review** | A GitHub Check Run (or GitLab/Bitbucket commit status) with **inline annotations** on the diff — new findings first, worst first, up to 50 — plus one **summary comment** (the same text as the check output). |
| **Gate** | The check passes or fails from the findings the reviewer actually sees. With `fail_on_severity` set, any in-scope finding at or above that severity fails it. |

:::tip The baseline matters
The verdict is only meaningful once the **base branch has been scanned** (a push to the default branch with auto-scan on, or a manual scan of `main`). Until then the summary says so and every finding in the changed files counts as new.
:::

## GitHub — the GitHub App

### 1. Create the app (once, an org owner)

At GitHub → *Settings → Developer settings → GitHub Apps → New GitHub App*:

- **Webhook URL:** `https://<your-instance>/api/github/webhook`, with a webhook secret.
- **Permissions:** `Checks: write`, `Pull requests: write`, `Contents: read`, `Metadata: read`.
- **Subscribe to events:** `push`, `pull_request`, `check_suite`, `installation`.
- Generate a **private key** (PEM) and note the **App ID**.

### 2. Register it in the platform

DevSecOps → **GitHub App** → paste the App ID, the private key and the webhook secret. (API: `POST /api/github/config`; requires the *manage integrations* permission. The key is stored encrypted.)

### 3. Install it on repositories

On GitHub, install the app on the repositories you want scanned. The `installation` event registers them; they appear under DevSecOps → repositories.

### 4. Per-repository behaviour

`PUT /api/github/repos/config?repo=owner/name` (defaults in brackets):

| Field | Meaning |
|---|---|
| `auto_scan_on_pr` [true] | Scan when a PR is opened, updated (new commits) or reopened. |
| `auto_scan_on_push` [true] | Full scan on every push to the default branch. This is what becomes the **baseline** the PR is diffed against. |
| `scan_types` [`code_security`] | Or a subset: `sast`, `dependency_scan`, `secret_scan`, `iac_scan`. |
| `fail_on_severity` [none] | Fail the check when an in-scope finding is at or above `critical`, `high` or `medium`. |
| `post_pr_comment` [true] | Post the summary as a PR comment. |
| `create_check_run` [true] | Create the `OffloadSecurity / <scan type>` check with inline annotations. |

### 5. Make it blocking

In the repository's branch protection, add the `OffloadSecurity / …` check to **Require status checks to pass before merging**. Without this the check is advisory.

### What you see on the PR

- A check named `OffloadSecurity / code_security` (or the scan type you chose), passing or failing, with annotations on the changed lines.
- A comment: *Offload security review — PASSED/FAILED*, the number of changed files scanned, new vs. already-present counts by severity, and a link to the full report.
- When the PR is a fix PR the platform itself opened, merging it triggers a re-scan of the base branch to verify the fix.

## GitLab and Bitbucket — merge-request webhooks

1. Create the team's hook: `POST /api/scm/webhooks/gitlab/secret` (or `/bitbucket/secret`; *manage integrations* permission). The response carries the `hook_id`, the **secret — shown once**, the URL to configure and the events to enable.
2. In the project's webhook settings add `https://<your-instance>/api/scm/webhooks/<provider>/<hook_id>` with that secret. GitLab sends it as `X-Gitlab-Token`; Bitbucket signs the body with it (`X-Hub-Signature`, HMAC-SHA256). Enable **Merge request events** and **Push events**.
3. A merge request opened or updated gets the PR-scoped scan, inline MR notes, a summary note and a commit status; a push runs the full-branch scan that becomes the next baseline.
4. `GET /api/scm/webhooks/<provider>` shows the hook's status (never the secret). Re-run step 1 to rotate the secret.

## From a CI pipeline instead

If you cannot install an app or webhook, trigger scans from the pipeline with an API key (`POST /api/cicd/scans/trigger`) or the GitHub Action — see [CLI & CI/CD](../../cli-and-cicd.md). Those run a **full-branch** scan and post a results comment; the changed-files scope and base-branch diff described above are specific to the app/webhook path.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Nothing happens on a PR | The app is not installed on that repository, `auto_scan_on_pr` is off for it, or the webhook secret in the platform does not match the app's. Check the webhook's recent deliveries on GitHub for the response code. |
| Every finding shows as new | The base branch has never been scanned. Enable `auto_scan_on_push` or run one scan of the default branch. |
| Check passes but the PR has findings | `fail_on_severity` is unset (advisory mode), or the findings are pre-existing on the base branch and the gate only counts new ones. |
| Dependency findings missing on a PR | No manifest or lockfile changed, so SCA findings are out of scope by design. |
| GitLab returns 401 on delivery | The `X-Gitlab-Token` does not match the secret returned when the hook was created; rotate it and update the project webhook. |

## Related

- [CI/CD & Automation](./ci-cd-and-automation.md) — schedules and generated pipelines.
- [CLI & CI/CD](../../cli-and-cicd.md) — the REST trigger, the GitHub Action, SARIF and release-gate policy.
- [Findings & Reports](./findings-and-reports.md) — where a PR scan's full report lives.
