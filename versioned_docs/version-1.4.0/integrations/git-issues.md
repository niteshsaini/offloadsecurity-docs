---
title: "GitHub & GitLab Issues"
sidebar_label: "GitHub & GitLab Issues"
sidebar_position: 6
new_in: 1.4.0
description: "Open one GitHub or GitLab issue per finding or Wazuh alert group in your team's private repositories, using your existing Git connection or the GitHub App, with issue status synced back to the platform every 15 minutes."
---

# GitHub & GitLab Issues

Ticket findings where your developers already work. The platform opens **one issue per finding** (or per Wazuh alert-group episode) in a GitHub repository or GitLab project, and keeps the two in step: closing the issue resolves the finding, and resolving the finding in the platform closes the issue. It uses the Git connections your team already has — there are no new credentials to store.

**Where:** **Integrations** → **GitHub & GitLab Issues** panel (above the catalog — it is not a catalog card).

## Before you begin

- **A credential that may create issues**, one of:
  - your own Git connection in Code Command Center → Automation → **Git Connections** — GitHub with a token that has the `repo` scope (`public_repo` covers public repositories only), or GitLab with the `api` scope (`read_api` cannot create issues). Self-managed GitLab uses the instance URL saved on that connection. See [Connecting repositories](../security-scanning/code/connecting-repositories.md);
  - the platform's **GitHub App** installed on the repository with the **Issues: write** permission. It is used first for the repositories it covers. An App created before 1.4.0 needs *Issues: write* added in its settings, and the organization admin must accept the new permission on the installation;
  - the **team service connection** — an admin's own connection that the admin explicitly shared on this panel.
- **Permissions:** creating issues from findings needs the Vulnerability Management permission; from alert groups, the permission to manage alerts. Sharing a service connection, allowing public repositories and the auto-create rule need **Manage Integrations**.
- The issue endpoints are **session-only**: API keys cannot call `/api/git-issues`.

Nobody else's token is ever used for you. If your own token cannot be read, you are told so rather than given another one.

## Steps

1. **Check access.** Integrations → **GitHub & GitLab Issues** → **Check access**. The platform asks the provider whether the credential used for you can create issues and shows the answer. A fine-grained GitHub token is reported as *not verifiable* (GitHub does not report its permissions); give it *Issues: Read and write* and the first issue proves it.
2. **Create issues from findings.** Vulnerability Management → **All Occurrences**: open an occurrence and use **GitHub / GitLab Issue**, or select up to **25** occurrences and click **GitHub / GitLab issues…**. Choose the provider and the target — `owner/repo` or `group/project`. A code finding goes to its own repository when you leave the target empty; every other finding needs a target.
3. **Or from Wazuh alert groups.** Infra Command Center → Endpoint Security → **Alerts**: select alert groups and click **GitHub / GitLab issue…**, then enter the target.
4. **Wait for the result.** The request runs in the background; a large batch takes longer because GitHub asks for a pause between new issues. The result says whose account opened each issue (*created as …*).
5. **Optional, admins:** share your own connection as the team service connection, allow public or internal repositories, and turn on the **auto-create rule** (off by default) with a severity threshold and a default target.

## Which repositories are allowed

- The target must be **one of the team's repositories**: one with a completed scan for that provider, one registered in Code Command Center, one the GitHub App is installed on, or the default target an admin saved (which must itself be one of these). Anything else is refused. Issues opened with the team service connection only go to scanned, registered or GitHub App repositories.
- The target must be **private**. Public repositories — and GitLab *internal* projects, which every signed-in user of the instance can read — are refused unless an admin allowed them, and the auto-create rule never posts to them.

## What an issue contains

The finding's title, severity, source, location, description, remediation and fix, labelled `offload-security`, `severity:<level>` and `source:<module>`, with a link back to the platform when its public URL is configured. Text from findings is escaped, so it can never mention a user, link another issue or commit, or run a GitLab quick action. Labels are applied only if the credential may create labels in that repository; the result says when they were not.

One issue per finding (or alert-group episode) per repository: asking again returns the existing issue, two people clicking at once still open only one, and an interrupted attempt first looks for the issue it may have opened. The link shows on the occurrence and on the alert group, with the issue's state.

## Status sync — both directions

Every **15 minutes** (up to 200 issues per provider per run, oldest check first; the panel shows how many are still waiting), or now with **Refresh statuses**:

| Change | Result |
| --- | --- |
| Issue **closed** as completed | The finding or alert group is resolved — *Closed in GitHub by &lt;who&gt;* (or GitLab) |
| Issue closed as **not planned** (GitHub) | Nothing is resolved. The link shows *closed as not planned — decide in the platform* so a person decides |
| Issue **reopened** | Reopens only what an issue closed |
| Finding or alert group **resolved in the platform** (by a person, a re-scan, or automatically) while its issue is open | The issue is closed as completed, with a comment saying who resolved it and when |

The platform keeps your decisions: a finding changed in the platform after the issue moved is not overridden, and a finding marked false positive or accepted risk is never resolved by an issue — nor does marking it so close the issue. Reopening a finding in the platform does not reopen its issue.

## The auto-create rule

Off by default. When an admin turns it on, it opens issues only for findings **first seen after it was enabled** — never your existing backlog — at most **25 per run**, above the chosen severity. Code findings go to their own repository, others to the default target; a finding with no usable target is skipped and reported, and a failure that may clear (provider error, rate limit) is retried on the next run.

Sharing a service connection and allowing public repositories are recorded in the platform audit trail.

## If something goes wrong

- **"The connected GitHub token lacks the 'repo' scope …"** — edit or recreate the token with `repo`, then reconnect it in Git Connections. For GitLab, the token needs `api`.
- **"You have no GitHub connection …"** — connect your own account in Git Connections, or ask an admin to install the GitHub App with Issues: write or to share a service connection.
- **"… is not one of this team's … repositories"** — choose a repository the team scans or registered, or ask an admin to save it as the default target.
- **"… is public: security findings are not posted to non-private repositories …"** — use a private repository, or ask an admin to allow public / internal repositories.
- **"… did not confirm the issue …; it may or may not exist"** — retry; the next attempt looks for the issue first and never opens a second one.
- **Rate limit** — GitHub and GitLab rate limits stop the batch until the wait shown is over. Retry the items that were not sent afterwards; nothing is duplicated.

## Next steps

- [Jira](./jira.md) — the other two-way ticketing integration.
- [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) — where findings are ticketed from.
