---
title: "Connecting Repositories"
sidebar_label: "Connecting Repositories"
sidebar_position: 1
description: "Connect GitHub, GitLab or Bitbucket with a read-only token, pick repositories and branches to scan, and map repositories to applications and owners."
---

# Connecting Repositories

The Code Command Center reads repositories through your Git provider's API with a token you supply. The connection is per team, validated when you save it, and used for every repository and branch listing, scan checkout and fix pull request afterwards.

**Where:** Code Command Center → **Automation** → **Git Connections**.

![Automation tab, Git Connections: GitHub, Bitbucket and GitLab cards, each Not Connected with a Connect button, alongside the PR Review, GitHub App and CI/CD Pipeline sub-tabs](/img/screenshots/security-scanning/code-automation.webp)

## Supported providers and tokens

| Provider | Token | Minimum access |
| --- | --- | --- |
| **GitHub** (github.com) | Personal access token — classic or fine-grained | Classic: the `repo` scope. Fine-grained: *Contents* and *Metadata* read on the repositories to scan; add *Pull requests* and *Contents* write only if the platform should open fix PRs. |
| **GitLab** (gitlab.com or self-managed) | Personal or project access token | `read_api` and `read_repository`; add `write_repository` for fix merge requests. For a self-managed instance, enter its URL; leave it blank for gitlab.com. |
| **Bitbucket** (bitbucket.org) | Repository or Workspace Access Token, with your workspace / username | *Repositories: Read*; add *Pull requests: Write* for fix PRs. **App passwords are not supported** and are refused when you save. |

The platform **checks the token with the provider** before saving it, so an expired or revoked token is rejected immediately rather than "connecting" and failing at scan time. A classic GitHub token without the `repo` scope is saved with a warning, because it cannot list private repositories. Tokens are encrypted at rest and never returned by the API. If a stored token later expires or is revoked, repository listing fails with a clear message and you reconnect with a fresh token. A card marked **Reconnect needed** holds a token the platform can no longer decrypt (for example after an encryption-key change): select **Reconnect** and paste a token again.

A self-managed GitLab on a private network is reachable only when the administrator has set `ALLOW_PRIVATE_SCAN_TARGETS=true` on the deployment.

:::tip[Use a service identity]
Create the token under a bot or service account that is a member of the repositories, not a personal account — scans keep working when people leave, and PRs opened by the platform are attributed consistently.
:::

## Connect

1. Select **Connect GitHub** (or GitLab / Bitbucket).
2. Paste the token (for Bitbucket, also the workspace / username; for a self-managed GitLab, its URL).
3. Select **Save Connection**. The card shows **Connected as \<username\>**; **Disconnect** removes the token.

One connection per provider per team; different teams connect independently.

## Choosing what to scan

On **New Scan**, the **Repository** picker lists the repositories the token can see (search by name, organization or language) and the **Branch** picker lists that repository's real branches. Each scan clones the selected branch at its current head and records the exact commit it scanned. If a requested branch no longer exists, the default branch is scanned and the scan says so.

For code you cannot connect — a vendor drop, an air-gapped project — use **Upload ZIP** instead; no Git connection is needed. See [Running Code Scans](./running-code-scans.md).

## Repository ownership

Map repositories to an **application** and an **owner** (optionally an environment and a criticality) so the lists can be filtered by who is accountable. Ownership is set over the API only — `PUT /api/code/repo-ownership` with `{ "repo", "application", "owner", "environment", "criticality" }`. The **Show: application / owner** filter on SBOM & Licenses then narrows that list to one team's services, and the Reports search matches the application name. See the [Scanning API](../api.md#code).

## Branch hygiene (API only, off by default)

A deployment can turn on an advisory branch inventory for GitHub repositories with `BRANCH_HYGIENE_ENABLED=true`. `GET /api/code/branch-hygiene?repo=owner/name` then classifies each branch — active, merged, stale, stale-unmerged, protected — and flags **cleanup candidates** with reason codes. It never deletes a branch, and when the provider's data is incomplete it says *needs review* instead of recommending anything.

| Setting | Default | Meaning |
| --- | --- | --- |
| `BRANCH_HYGIENE_STALE_DAYS` | `90` | Days since the last commit before a branch is stale. |
| `BRANCH_HYGIENE_MERGE_GRACE_DAYS` | `30` | Days after a branch's PR merged before it can be a cleanup candidate. |
| `BRANCH_HYGIENE_PROTECTED_PATTERNS` | `main,master,develop,development,release/*,hotfix/*,production,staging,qa` | Globs that are never candidates (provider-protected branches are excluded too). |

There is no screen for it, and only GitHub is implemented: GitLab and Bitbucket repositories return no branches. One request enriches at most 200 branches (`BRANCH_HYGIENE_MAX_BRANCHES`).

## Related

- [Running Code Scans](./running-code-scans.md) — the first scan.
- [CI/CD & Automation](./ci-cd-and-automation.md) — schedules and pipeline scans that use this connection.
- [Troubleshooting](../troubleshooting.md#code) — token rejected, repositories missing, scans that stay running.
