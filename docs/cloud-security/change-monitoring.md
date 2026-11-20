---
title: "Cloud Change Monitoring"
sidebar_label: "Change Monitoring"
sidebar_position: 9.5
new_in: 1.4.1
description: "See every change made in your connected cloud accounts, who made it (a person, a pipeline, the provider's own automation or an unknown identity), whether it was expected, and review the unexplained changes that raise alerts."
---

# Cloud Change Monitoring

The **Changes** tab answers three questions about your cloud accounts: what changed, who changed it, and was it expected. It is built on the audit events your clouds already send to [Cloud Events](./cloud-events.md). A change made by an approved pipeline identity or by the provider's own automation is **expected**. Any other change is **unexplained**, and it raises an alert.

**Where:** Cloud Security → **Changes**.

## Before you begin

- [Cloud Events](./cloud-events.md#set-up-event-delivery) must be delivering for the accounts you want to watch. The Changes tab has no data source of its own.
- AWS routes created from the 1.4.0 instructions should be updated to the current EventBridge rule (see [Update an existing AWS rule](./cloud-events.md#update-an-existing-aws-rule)).
- To edit approved identities you need **Manage Cloud Accounts** (Admin or Security Manager). To review a change you need **Acknowledge Alerts** (Admin, Security Manager or Security Analyst). Anyone who can view the team's cloud data can read the tab.

## What counts as a change

Every audit event for a call that changed something gets a **change record**, whether or not the action is on the security event list. Before 1.4.1, actions outside that list were kept only as an event name and caller.

- **Not recorded:** read calls, failed calls (they changed nothing), and Azure's in-progress *Started* / *Accepted* phases. The *Succeeded* event that follows is recorded.
- **What the record holds:** the provider's event time, action, service, resource, region, account, source IP, user agent, the caller's identity details, and the request contents.
- **Secrets are removed** from the request before it is stored. Fields with names such as password, secret, token, private key or connection string are replaced, and the detail view shows how many fields were removed.
- **Large requests are cut, visibly.** A request over 16 KB is stored as its first 16 KB, and the detail view says so.
- **Requested, not before/after.** Cloud audit logs record what was asked for, not the value before the change. To see what was there before, compare a change with the **previous change to the same resource**, which the detail view shows.

Change records are kept as long as cloud events: 90 days by default.

## Who made the change

Each change is labelled with one of four kinds of caller:

| Label | Meaning |
| --- | --- |
| **Person** | A human: the AWS root user, IAM / Identity Center / federated users, SSO and console sessions, Google and Entra ID users, or a person impersonating a GCP service account. |
| **Pipeline** | The caller matches one of the account's **approved change identities**, such as a Jenkins role, a GitHub OIDC role or a Terraform service account. |
| **Cloud automation** | The provider acting on its own: AWS service calls and service-linked roles, Google service agents, Azure platform callers. |
| **Unknown identity** | A machine identity that is not on the approved list and is not the provider's automation. |

Two rules keep a person from hiding behind a pipeline identity. The **root user is always a person**, even if it is on the approved list. A **console session** in an approved role, or a **person impersonating** an approved GCP service account, is also labelled a person.

## Expected or unexplained

| Caller | Verdict | Severity |
| --- | --- | --- |
| Pipeline, cloud automation | **Expected** | Info. No alert. |
| Person, unknown identity | **Unexplained** | At least Medium; at least the severity the security event list gives that action. |
| AWS root user | **Unexplained** | Critical. |
| Caller cannot be read from the event | **Unexplained** | At least Medium. |

An analyst's review overrides the rule verdict (see [Review a change](#review-a-change)).

### Alerts for unexplained changes

Each unexplained change raises an alert on [Alerts](../vulnerability-risk/alerts.md) with the source **Cloud change**, titled *Unexplained cloud change: &lt;action&gt; on &lt;resource&gt;*. Each team that owns the account gets its own alert. New alerts follow your alert notification settings.

- **Bursts are grouped.** Changes by the same caller to the same resource in the same account within one hour share one alert. A person is grouped by their session, a machine by its role.
- **Alerts follow the verdict.** If a later approval or review makes a change expected, its alert is resolved. If a change becomes unexplained again, the alert reopens.
- **A failed alert is shown.** If the platform could not record the alert, the change's detail says *The alert for this unexplained change could not be recorded*, with the time. That change is not in Alerts, so review it on the Changes tab.

## Approve your pipeline identities

List the identities that are allowed to change each account, so their changes count as expected.

1. **Open the editor.** On **Changes**, select **Approved identities** and choose the cloud account.
2. **Enter one identity per line** as `pattern | label`, for example:
   ```text
   arn:aws:iam::*:role/jenkins-deployer | Jenkins
   arn:aws:iam::123456789012:role/github-actions-* | GitHub Actions
   terraform@my-project.iam.gserviceaccount.com | Terraform
   ```
   `*` matches any run of characters, and matching ignores case. For AWS, list the **role**, not a session: patterns are matched against the role behind an assumed-role session, never the session name the caller chooses. For GCP use the principal email; for Azure the caller or object ID, or the app ID for app callers.
3. **Select Save.** The confirmation says how many identities were saved and how many changes from the **last 7 days** were relabelled: how many are now expected, how many are now unexplained, and how many alerts were resolved.

Limits:

- At most 200 identities per account.
- Each pattern needs at least 8 characters besides `*`, so a pattern such as `arn*` that would approve almost every caller is refused.
- Relabelling covers at most 20,000 changes per save. Any older changes in the 7-day window that were not relabelled are counted in the message.
- If two people save the same list at once, the message says that a newer save took over relabelling.

New changes use the saved list on the next event; other backend workers pick it up within a minute.

## Read the Changes tab

- **Tiles:** **Changes** in the selected window, **Unexplained**, **Expected** and **Accounts changed**. Select a tile to filter the table by that status. A line under the tiles splits the changes by who made them. Changes received before labelling existed are counted as *Not labelled*.
- **Filters:** window (**Last 24 hours**, **Last 7 days**, **Last 30 days**), status, who (**Person**, **Pipeline**, **Cloud automation**, **Unknown identity**), cloud, account, and a search over resource, action and caller. Account matching ignores case, so an Azure subscription ID matches however the event spells it.
- **Table:** when, the change (action, cloud, account, region, resource), who (caller, label, and a **root** badge when applicable) and status with its severity. The table refreshes every minute.
- **Detail:** expand a row to see what was requested, the previous change to the same resource, who and how (caller, role, invoking service, impersonation chain, source IP, user agent, MFA when the provider reports it), the reasons for the label and the verdict, and the review history.

## Review a change

1. Expand the change.
2. Under **Review**, choose **Expected** or **Confirm unexplained**.
3. Enter a reason of at least 10 characters, such as the change ticket, and select **Save review**.

**Expected** resolves the change's alert. **Confirm unexplained** keeps it open, or reopens it if an earlier review had resolved it. Every review is kept with the reviewer and time, and the row shows **reviewed**.

## Check that it worked

Make a harmless change on a test account (for example, add and remove a tag) from the cloud console as yourself. Within a minute it should appear on **Changes** as a **Person** change marked **Unexplained**, and a **Cloud change** alert should appear on Alerts. Make the same change from your pipeline after approving its identity: it should appear as **Pipeline** and **Expected**.

## If something goes wrong

- **The tab is empty.** No change records have arrived for the window. Check that [Cloud Events](./cloud-events.md) shows recent events; if it doesn't, see [Troubleshooting](./troubleshooting.md#cloud-events).
- **GCP data changes are missing.** Admin Activity logs are always on, but Data Access logs, which hold data writes such as Cloud Storage object changes, are off by default for most services. Enable **Data Write** audit logs for those services (IAM & Admin → Audit Logs).
- **My pipeline's changes are still unexplained.** For AWS, approve the role ARN, not the assumed-role session ARN. A console session in the pipeline role is a person by design.
- **"Previous change" says no earlier change is stored.** Either the resource had no change in the retention window, or the event does not name a resource.

## Related

- [Real-Time Cloud Events](./cloud-events.md) — event delivery and the security event feed.
- [Cloud Security API](./api.md#cloud-events) — the change, approved-identity and review endpoints.
