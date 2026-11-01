---
title: "Managing Connected Accounts"
sidebar_label: "Managing Accounts"
sidebar_position: 2
description: "Review connected AWS, GCP and Azure accounts, test connections, rotate credentials, adjust scan regions, launch quick or full scans, act in bulk, and remove accounts cleanly."
---

# Managing Connected Accounts

Once accounts are connected you manage them from two places that show the same accounts through different lenses:

| View | Where | Best for |
| --- | --- | --- |
| **Accounts tab** | Cloud Security → **Accounts** | A card per account with last-scan time, live scan progress and one-click **Quick scan** / **Full scan**. Click a card to open its findings. |
| **Cloud Accounts** | Left navigation → **Cloud Accounts** (under *Management*) | **Manage Accounts** (the full table: search, filter, edit regions, test connections, bulk actions, export) and **Credentials & Health** (credential age, health checks, credential replacement). |

## The Accounts tab

![Cloud Security → Accounts: one card per connected account with provider, account ID, region, last scan and Quick / Full Scan buttons; the staging account shows a scan in progress](/img/screenshots/cloud-security/accounts-tab.webp)

Each card shows the account's **display name**, provider account ID, region, **Last Scan** date and a **status badge** (`Active`, or `Error` when the last connection check failed). While a scan is running the card shows *Scanning…* or *Queued* with a progress bar, and both scan buttons are disabled until it finishes — one scan per account at a time. A card whose scheduled scans were paused after repeated failures reads **Scheduled scans paused** (see [Account status and health](#account-status-and-health)).

**Click a card** to open the **Findings** tab already filtered to that account. Every other filter stays available, and the filter is kept in the URL, so the view can be bookmarked or shared.

- **Quick scan** — an incremental run over the account's full configured scope (for AWS with no saved regions, every enabled region).
- **Full scan** — the comprehensive run across the same scope.
- The **trash icon** removes the account after a confirmation.

What each scan type covers is explained in [Running Cloud Scans](./scan-orchestration.md#scan-types-and-regions).

## Manage Accounts

![Cloud Accounts → Manage Accounts: provider totals, search and provider filter, and a row per account with Regions, Test Connection, Quick Scan, Full Scan and Remove](/img/screenshots/cloud-security/manage-accounts.webp)

The header tiles count accounts per provider. Use the search box to match on **name, account ID, region, environment, status or provider**, narrow with the **All / AWS / GCP / Azure** filter, and sort by name or created date.

Per account row:

| Action | What it does |
| --- | --- |
| **Regions** | AWS only. Opens the region picker so you can change which regions future scans cover (including scheduled ones); you can add a region ID that is not in the list. Clear every region and save to go back to the default — every region enabled on the account. For GCP and Azure the window explains that the whole project or subscription is always scanned. |
| **Test Connection** | Re-runs the provider validation (the same check as onboarding) and updates the account's status. Use it after rotating a key or changing the role's trust policy. |
| **Quick Scan** / **Full Scan** | Start a scan. On an AWS account with no saved regions, the quick scan here covers `us-east-1` only and its button reads **Quick scan (us-east-1)**; with saved regions it covers those. This differs from the **Quick scan** on the Accounts tab, which is an incremental scan over the full scope. |
| **Remove** | Deletes the account after confirmation — see [Removing an account](#removing-an-account). |

Starting scans needs the **Create Cloud Scans** permission. Without it the scan buttons are disabled and say why.

### Bulk actions

Tick the checkbox on several rows (or **Select all** for the filtered list) to act on them together:

- **Start Scan** — a full scan per selected account. Bulk scans are staggered (about one account a minute by default) rather than started all at once, and selecting more than five accounts asks you to confirm first. Each still obeys the one-scan-per-account rule: the result reports which accounts were queued, skipped or failed.
- **Test / Sync** — tests the connection of every selected account; handy after an IAM change that touched many accounts.
- **Delete** — removes the selected accounts after a single confirmation.

At most **100 accounts** per bulk request. Selections are limited to rows currently visible, so a filter change can never widen a bulk action beyond what you can see.

:::note[Bulk scans and scan authorization]
Bulk **Start Scan** and Coverage **Scan now** do not ask for a scan authorization. If your deployment requires one, an account without a current authorization is counted as failed there — start its first scan from its own card. See [Scan authorization](./scan-orchestration.md#scan-authorization).
:::

### Export

**Export CSV** downloads the account list with provider, ID, regions, environment and status — useful as onboarding evidence for auditors ("these are the in-scope accounts").

## Credentials & Health

**Cloud Accounts → Credentials & Health** shows, per account, how long its stored credentials have been in use and the result of its last health check.

- **Credential age** is amber from **60 days** and red from **90 days**.
- **Run health check** tests the stored credentials without changing them. *Not checked* means no health check has run yet — it is not a pass.
- **Replace credentials** rotates them (below).

### Rotate an account's credentials

1. Create the new key, secret or role first, with the same permissions as the old one.
2. On **Credentials & Health**, select **Replace credentials** on the account, fill in the fields for its sign-in method (for example Role ARN and External ID, or tenant, client, secret and subscription IDs) and select **Save and test**.
3. Read the result: *Saved — the connection test passed*, or the reason it failed.
4. Revoke the old credentials in your cloud provider.

A passing replacement sets the account to **Active**, restarts its credential age and resumes scheduled scans that were paused after repeated failures. A failing replacement is still saved: the account shows **Error** until working credentials are saved, and its credential age is not reset. Replacing a cross-account role's Role ARN or External ID keeps any stored source access keys.

:::note[Only the person who added the account can rotate it]
For an account added by another user, the button reads *Added by another user*. Ask that user, or remove the account and add it again (removing deletes the account's scan data). Over the API, `PUT /api/cloud-accounts/{id}` with `{"credentials": { … }}` does the same; the response's `credential_test` gives the result.
:::

## Account status and health

| Status | Meaning | What to do |
| --- | --- | --- |
| **active** | Last validation succeeded; scans can run. | Nothing. |
| **pending** / **validating** | Onboarding in progress. | Wait, or finish the wizard. |
| **error** | The last connection test or scan failed to authenticate. | Fix the role, key or API enablement, then **Test Connection**. |
| **inactive** | Deliberately disabled (for example a retired GCP project). | Re-enable from the GCP organization view or reconnect. |
| **discovered** | Found by organization discovery but not yet onboarded. | Turn it on in the organization view. |

**Automatic pause after repeated failures.** If an account fails **three times in a row** (scheduled scans or health checks), the platform pauses its scheduled scans and records the reason, so a dead credential cannot generate a failing scan every night. The account shows **Scheduled scans paused** on Manage Accounts, its Cloud Security card and Credentials & Health, and **Alerts** shows *Scheduled scans paused: &lt;account&gt;*. Fix the cause, then either run a scan from the account card (when it succeeds the schedule resumes) or replace the credentials (new credentials that pass their test resume it). A health check alone does not resume it. Failures of scans you start by hand, and cancelled scans, never count toward the pause. Operators can change the threshold with `CLOUD_SCAN_MAX_CONSECUTIVE_FAILURES`.

## Duplicate prevention

An account is identified by **provider + provider account ID**. Adding the same AWS account or GCP project twice under the same owner is rejected, so you cannot accidentally double-scan or split findings across two records. If two teams need the same account, connect it in each team — dashboards stay isolated per team.

## Removing an account

Removing an account is a clean-up, not just a hide. The platform deletes the account record and then cascades:

- the account's **findings**, **compliance scores** and **scan history** are deleted,
- its open entries in **Vulnerability Management** and its open **remediation tasks** are closed (not deleted, so the audit trail stays),
- its **assets** are marked deleted in Asset Inventory,
- its **recurring schedules** are removed so nothing keeps firing.

Each removal is recorded (who, when, what was removed), and the frozen findings snapshots of its past scan runs are kept, so reports already issued for those runs remain reproducible.

If another team has the same provider account connected, the shared, provider-scoped data is kept for that team and only your account record and schedules go — the last team to remove it triggers the full cascade.

:::warning[Removal is permanent]
There is no undo for the deleted findings and scan history. If you only want to stop scanning for a while, pause the account's schedules in **Unified Scheduler** instead.
:::

## Related

- [Connecting Cloud Accounts](./connecting-accounts.md) — the wizard and provider setup.
- [Running Cloud Scans](./scan-orchestration.md) — quick vs full, regions, progress and status.
- [Troubleshooting](./troubleshooting.md) — connection errors and scans that will not start.
