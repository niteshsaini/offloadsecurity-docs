---
title: "Cloud Security Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 13
description: "Fix the common Cloud Security problems — validation failures, scans that stay queued or come back partial, empty dashboards, findings that reappear — and answers to the questions teams ask most."
---

# Cloud Security Troubleshooting & FAQ

## Connection and validation

**Validation fails on AWS with `AccessDenied` / `not authorized to perform sts:AssumeRole`.**
The trust policy on your role does not allow the platform's principal, or the **External ID** differs from the one you entered. Re-check both in the role's *Trust relationships*; ask your platform administrator which AWS principal the deployment runs as. If you used access keys, confirm the user has `SecurityAudit` and `ReadOnlyAccess` attached.

**A scan is refused because the identity belongs to a different AWS account.**
Every AWS scan verifies with `sts:GetCallerIdentity` that the role or keys reached the 12-digit account you entered. The credentials belong to another account — replace them under **Cloud Accounts → Credentials & Health** (see [Rotate an account's credentials](./account-management.md#rotate-an-accounts-credentials)).

**GCP validation fails with `PERMISSION_DENIED` or `API has not been used in project`.**
Enable the APIs listed in [Required Permissions](./permissions.md#bucket-a--read-only-scanning) (`cloudasset`, `cloudresourcemanager`, `compute`, `iam`, …) **on the service account's own project** and grant the roles at project — or org — level. For organizations, run **Check readiness** first; it names each missing API and role and shows the command to fix it.

**Azure validation fails with `AuthorizationFailed` or `invalid_client`.**
`invalid_client` means the client secret is wrong or expired — create a new secret and re-enter it. `AuthorizationFailed` means the service principal lacks `Reader` / `Security Reader` at the subscription scope.

**Test Connection passes but the account shows `error` later.**
Credentials were rotated or the role's policy changed after onboarding. Replace the credential under **Cloud Accounts → Credentials & Health** (it is tested straight away) or run **Test Connection** again after fixing the role. Accounts that failed three times in a row show **Scheduled scans paused** until a scan succeeds or working credentials are saved — see [Automatic pause](./account-management.md#account-status-and-health).

**"The health check could not run: The stored credentials could not be decrypted…"**
The saved credentials can no longer be read (for example after the platform's encryption key changed). Replace the credentials.

**"Replace credentials" is disabled ("Added by another user").**
Only the user who added an account can replace its credentials. Ask that user, or remove and re-add the account (removing deletes its scan data).

## Scans

**The scan button is disabled / "A scan is already in progress".**
Only one scan runs per account at a time. Open **Cloud Scans** to see the running one; if it is stuck for far longer than its estimate, cancel it (`DELETE /api/cloud-scans/{run_id}`) and start again. On Manage Accounts the scan buttons are also disabled when your role lacks the **Create Cloud Scans** permission; the button says so.

**"Authorization required" appears, or a scan is refused with "no current authorization is recorded for this account".**
Your deployment requires a recorded authorization before a cloud account is scanned (`SCAN_REQUIRE_AUTHORIZATION`). Tick *I am authorized to test this target*, optionally add a reference and an end date, and select **Record and start scan**. It covers the account's scheduled scans until the end date. Bulk scans and Coverage **Scan now** do not prompt — start the first scan from the account card. See [Scan authorization](./scan-orchestration.md#scan-authorization).

**A scan stays `queued`.**
Workers are busy or unavailable. On a self-hosted deployment check that the scan worker containers are running and healthy. Queued scans are picked up in order once a worker is free.

**The scan finished `partial`.**
A job failed, Prowler reported check errors in a region (for example access denied), or a region returned nothing it could verify. Open the run, or download its [point-in-time report](./point-in-time-reports.md), which lists each region and job that was not tested or incomplete. Fix the cause and re-scan; the successful jobs' results are already in, and nothing was marked fixed for the parts that failed.

**The scan finished `failed` immediately.**
Almost always authentication — the same causes as validation failures above. Run **Test Connection** to confirm.

**Findings count is much lower than expected.**
Check the run's **region scope** (printed in its report). The Manage Accounts quick scan of an AWS account with no saved regions covers `us-east-1` only — its button reads *Quick scan (us-east-1)*. Full and incremental scans cover every enabled region unless regions are configured; if the enabled-region lookup failed, the run fell back to 13 common regions and its report says so.

**Some findings disappeared after upgrading to 1.4.0, then came back.**
Prowler was upgraded from 5.6.0 to 5.44.0, which renamed or split some checks. Findings for a renamed check resolve under the old key and reappear once under the new one. Some permission-limited checks now report *manual* instead of *fail*.

## Dashboards and data

**Cloud Security looks empty.**
In order: (1) you are in the right **team** (account menu, top-right); (2) at least one account is connected and **active**; (3) at least one scan has finished — the Coverage tab's *Not covered* tile tells you which accounts have never been scanned.

**Coverage shows an account as *Not covered* although it was scanned.**
Only **completed** or **partial** runs count. A failed run does not. Check **Cloud Scans** for the account's last run status.

**A finding I resolved came back.**
Resolve records your claim; the next scan verifies it. If the misconfiguration is still present, the finding reopens. Fix the resource, or — if you accept the risk — **suppress** it with a reason and an expiry instead.

**A suppressed finding reappeared.**
Its suppression window ended (or the resource re-failed after a permanent suppression was lifted). Re-suppress with a longer window if the risk is still accepted; the reason and history are kept.

**Compliance scores show `Frameworks: 0`.**
Scores are computed from the latest **finished** scan; a brand-new account has none until its first run completes. Also make sure the account filter on the Compliance tab is not set to an account that has not been scanned.

**Asset Inventory does not show a resource I just created.**
Inventory is refreshed by discovery jobs. Trigger **Refresh Assets** on the account or wait for the next scheduled scan. Short-lived types (snapshots, pods, jobs and similar) are never stored.

**The encryption card reads "Not assessed".**
No encryptable asset could be assessed yet — wait for the next discovery, or check the read permissions in [Required Permissions](./permissions.md#encryption-at-rest-and-exposure). Assets whose encryption could not be read show the reason in their expanded row.

**The IAM Analysis tab says "No IAM findings available".**
The identity roster is populated by **Run IAM Analysis** or the daily identity sweep. Run it on the account once; the roster, score and findings appear after it completes.

**IAM Analysis shows an amber "last attempt failed" notice.**
The last identity analysis of that account failed or completed partly, so an older complete result is shown. Common causes are a missing read permission (shown as *Not evaluated* with the permission to grant) or the time budget running out on a very large account.

**SCPs show as "Not evaluated".**
A member account cannot read its own SCPs. Onboard the organization's management account or a delegated administrator in the same team with the Organizations read permissions — see [Required Permissions](./permissions.md#identity-analysis-ciem).

**A custom policy shows only "Not evaluated".**
The field path in its condition does not exist in the inventory records. Check the record in Asset Inventory and adjust the path — see [Custom Cloud Policies](./custom-policies.md).

## Cloud events

**No events arrive.**
Check, in order: your team has a webhook token (**Cloud Events** setup panel); the route targets the per-team URL shown there, or sends the token in the `x-offload-webhook-token` header; the token has not been rotated since the route was created; for GCP with OIDC configured, the push subscription sends the OIDC token. A `401` in your cloud's delivery logs means a missing or unknown token (or a missing OIDC token); routes that still use the old shared URL without a token are rejected with `401` — see [Real-Time Cloud Events](./cloud-events.md#set-up-event-delivery).

**Events arrive but no findings are created.**
Only catalogued, security-relevant events create findings; others are stored as *ignored*, and failed API calls as *skipped*. Events for a cloud account your team has not onboarded are stored as *rejected*. Trigger a known one (for example a security-group ingress change) on an onboarded account to confirm the pipeline.

## Frequently asked questions

**Does the platform ever write to my cloud?**
No. Scans, discovery, identity and network analyses and the *Cleanup Unused* recommendation are all read-only. The only outbound configuration you create is the event route for Cloud Events, and you create it yourself.

**Where are credentials stored?**
Encrypted at rest with a platform encryption key, in the platform's database. They are decrypted only inside scan workers at run time and are never returned by the API or shown in the UI. See [Trust & Security](../trust-and-security.md).

**How often should we scan?**
The defaults — daily incremental plus a weekly full baseline — are right for most teams. Add an on-demand **Full** scan before audits and after large infrastructure changes.

**Can we scan only some regions?**
Yes, on AWS: set the account's regions in the wizard or *Manage Accounts → Regions*. With none set, AWS scans cover every region enabled on the account. GCP projects and Azure subscriptions are always scanned whole.

**How do we handle 200 GCP projects or an AWS Organization?**
Connect the **GCP organization** (or a folder) once and let discovery onboard and maintain the projects. AWS accounts and Azure subscriptions are connected one by one: deploy the identical role with one CloudFormation StackSet or Terraform module across the organization, then add each account in the wizard and scan them with bulk **Start Scan**. A run's report lists AWS Organization members and Azure subscriptions visible to the credential that are not onboarded or not assessed.

**Can findings flow into Jira, Slack or our SIEM?**
Yes — alerts and notifications are configured under Integrations; see [Notifications](../integrations/notifications.md) and [Third-Party Integrations](../integrations/third-party.md).

**Which permission do I need to resolve or suppress?**
**Manage Risks**. Viewing needs **View Scans**; connecting accounts needs **Manage Cloud Accounts**; starting scans needs **Create Cloud Scans**; custom policies need **Manage Scans**. See [RBAC & Team Management](../authentication/rbac-team-management.md).

**Is there a difference between a Quick and a Full scan's checks?**
No — both run the complete check set. They differ in default region footprint. See [Scan types and regions](./scan-orchestration.md#scan-types-and-regions).

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment issues. For anything else, contact support with the **run ID** (from Cloud Scans) or the account's provider ID — both are on the scan detail dialog.
