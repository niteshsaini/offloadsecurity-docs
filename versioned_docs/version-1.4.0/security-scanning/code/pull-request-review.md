---
title: "Pull Request Review"
sidebar_label: "Pull Request Review"
sidebar_position: 6
description: "Scan every pull or merge request on GitHub, GitLab and Bitbucket: only the changed files, new findings separated from pre-existing ones, inline comments on the diff, and a commit status pinned to the exact commit."
---

# Pull Request Review

A repository scan tells you where a codebase stands. A **pull request review** tells a developer what *this change* introduces — in the diff, before it merges — and lets you make that a required check. The platform reviews pull requests on **GitHub**, merge requests on **GitLab** (gitlab.com or the self-managed instance of your Git connection) and pull requests on **Bitbucket** with the same engines as a full scan.

**Where:** Code Command Center → **Automation** → **PR Review** (per-repository GitHub settings, GitLab / Bitbucket webhooks and the team quality gate) and **GitHub App**.

## What a review does

```mermaid
flowchart LR
    E[PR / MR event] --> C[Checkout the<br/>head commit]
    C --> S[Scan changed files<br/>SAST · secrets · SCA · IaC]
    S --> D{New vs<br/>pre-existing}
    D -->|new| I[Inline comments<br/>on the diff]
    D --> SUM[Summary comment]
    S --> ST[Commit status<br/>pass / fail]
```

1. **Exact commit.** The review checks out the commit the event names, not "the latest on the branch", so a status is always about the code it is attached to. The result records the requested and resolved commit.
2. **Changed files only.** Only files touched by the change are scanned, which is what keeps a review fast enough to sit in the merge path.
3. **New vs pre-existing.** Each finding is classified as **new** (introduced by this change) or **pre-existing** (already on the target branch). The classification ignores line numbers, so a file re-indented by the change does not turn old findings into new ones.
4. **Decoration.** New findings get **inline comments** on the affected lines, worst severity first, up to 30 per review; one **summary comment** lists everything; a **commit status** reports pass or fail. If the scan itself fails, a *failed* status is published with the reason — a review never leaves a required check pending.
5. **Findings land in the platform** too: the same rows appear under **Findings** and the scan under **Reports**, with the usual triage lifecycle.

### The gate

The pass/fail decision is made from **the review's own findings** against the **team quality gate** (Automation → PR Review → *Team quality gate*: max critical / high / medium / low, minimum score, block on critical or known-exploited, stale-database handling) and the active [SCA policy pack](./sbom-and-licenses.md#sca-policy-packs) — never from findings elsewhere in the platform. By default the gate counts **only findings the pull request introduces**; per GitHub repository you can switch *Pull request gate counts* to **every finding in the scanned files**. Findings you have already triaged — false positive, accepted risk — do not fail a review. A scan whose tools failed fails the gate rather than passing it. See [CI/CD & Automation](./ci-cd-and-automation.md#gating).

## GitHub

1. **Set up the GitHub App** (once, an administrator): create the App on GitHub and save its App ID, private key and webhook secret under **Automation → GitHub App** — step by step in [Pull Request Scanning](./pull-request-scanning.md#github--the-github-app). Install it on your repositories.
2. **Choose the repository settings** under **Automation → PR Review**: pick a repository from the App's installation (if none appear, select **Sync from GitHub** or link the installation by ID), then set:

   | Setting | Default |
   | --- | --- |
   | **Scan on push to the default branch** — keeps the baseline current | on |
   | **Scan pull requests** — on open and on every new commit | on |
   | **Post a summary comment on the pull request** | on |
   | **Create a GitHub check run** — the merge gate | on |
   | **Scan types** — Full code security, or SAST / Dependencies / Secrets / Infrastructure as Code | Full code security |
   | **Pull request gate counts** — only findings the PR introduces, or every finding in the scanned files | introduced only |

   Select **Save repository settings**. Changing them needs **Manage Integrations**.
3. **Make it blocking.** Mark the check run as a **required status check** in the repository's branch protection.

The check run is what gates the merge. If you turn it off, the PR comment says the result **does not block the merge**, and a scan that fails is reported as a failure comment (when comments are on) rather than disappearing.

**Webhook deliveries.** **Automation → GitHub App** shows what GitHub recorded when it sent the App's events to the platform: delivered and failed counts, the last success, the latest deliveries, and for a failure its likely cause and fix — 401 (webhook secret mismatch), 403 (no secret), 404 (wrong URL path), no response (firewall, DNS or timeout) or a server error. This includes deliveries that never reached the platform, so an App that shows *Connected* while every delivery is rejected is visible here instead of only in GitHub's *Recent Deliveries*. An App that is saved but not working is shown as **Saved, but not working**, with the problems listed.

## GitLab and Bitbucket

GitLab and Bitbucket reviews are driven by a webhook the platform gives you, authenticated by a secret only the two sides know.

**1. Connect the provider.** Under Code Command Center → Automation → **Git Connections**, connect GitLab or Bitbucket with a token that can read the repository and comment on merge/pull requests (GitLab: `read_api`, `read_repository` and `api` for comments and statuses; Bitbucket: repository read plus pull-request write).

**2. Create the review hook** (once per team and provider — needs *Manage Integrations*). Under **Automation → PR Review**, the GitLab and Bitbucket merge-request panels have **Create webhook secret**: copy the **Webhook URL** and the secret, which is shown once. Or over the API:

```bash
curl -s -X POST https://<your-host>/api/scm/webhooks/gitlab/secret \
  -H "Authorization: Bearer $API_KEY"
```

Use `bitbucket` in place of `gitlab` for Bitbucket. The response contains the `hook_id`, the inbound `path` and a `secret`:

```json
{ "hook_id": "3f9c…", "secret": "…", "path": "/api/scm/webhooks/gitlab/3f9c…" }
```

:::warning
The secret is shown **once**. For GitLab only its hash is stored; for Bitbucket it is also kept encrypted, because Bitbucket signs each delivery with it. If you lose it, **Rotate secret** — this issues a new URL and secret, and the old webhook stops working until you update it on the provider.
:::

**3. Register it on the repository.**

| Provider | Where | URL | Secret | Events |
| --- | --- | --- | --- | --- |
| **GitLab** | Project → Settings → Webhooks | `https://<your-host>` + `path` | *Secret token* = `secret` | Merge request events, Push events |
| **Bitbucket** | Repository settings → Webhooks | `https://<your-host>` + `path` | *Secret* = `secret` | `pullrequest:created`, `pullrequest:updated`, `pullrequest:fulfilled`, `pullrequest:rejected`, `repo:push` |

The panel then shows **Webhook configured** with its URL and creation time; `GET /api/scm/webhooks/gitlab` (or `…/bitbucket`) returns the same status, never the secret.

**4. Open a merge request.** Within a minute the MR shows inline comments on new findings, a summary note and a commit status. Make the status required in the project's merge-request approval settings to block merges.

## Reading a review

| You see | It means |
| --- | --- |
| Inline comment on a line | A **new** finding introduced by this change — rule, severity, and what to do. |
| Summary comment | Counts by severity for new and pre-existing findings, the gate result, and the files that were reviewed. If the changed-file list could not be read, the whole branch was scanned and the summary says so. |
| Status **failed** with a reason | The gate failed, or the scan itself could not run (clone failure, unsupported input). The reason is in the status text. |
| No comments, status **passed** | Nothing new at or above the threshold. Pre-existing findings are listed in the summary only. |

Decisions you make on a finding from the review — false positive, accepted risk — apply to the next review of the same repository, so a known false positive does not fail every subsequent pull request. See [Findings & Reports](./findings-and-reports.md#lifecycle) for scope.

## Related

- [CI/CD & Automation](./ci-cd-and-automation.md) — scheduled scans and pipeline jobs for full scans on merge and nightly.
- [CLI & CI/CD](../../cli-and-cicd.md) — the GitHub Action alternative and the release-gate policy.
- [Scanning API](../api.md#code) — the webhook endpoints.
