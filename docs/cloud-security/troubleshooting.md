---
title: "Cloud Security Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 13
description: "Fix the common Cloud Security problems — validation failures, scans that stay queued or come back partial, empty dashboards, findings that reappear — and answers to the questions teams ask most."
---

# Cloud Security Troubleshooting & FAQ

## Connection and validation

**Validation fails on AWS with `AccessDenied` / `not authorized to perform sts:AssumeRole`.**
The trust policy on your role does not allow the platform's principal, or the **External ID** differs from the one you entered. Re-check both in the role's *Trust relationships*; the wizard shows the exact principal and external ID to use. If you used access keys, confirm the user has `SecurityAudit` and `ReadOnlyAccess` attached.

**GCP validation fails with `PERMISSION_DENIED` or `API has not been used in project`.**
Enable the APIs listed in [Required Permissions](./permissions.md#bucket-a--read-only-scanning) (`cloudasset`, `cloudresourcemanager`, `compute`, `iam`, …) and grant the roles at project — or org — level. For organizations, run the readiness check first; it names each missing API and role.

**Azure validation fails with `AuthorizationFailed` or `invalid_client`.**
`invalid_client` means the client secret is wrong or expired — create a new secret and re-enter it. `AuthorizationFailed` means the service principal lacks `Reader` / `Security Reader` at the subscription scope.

**Test Connection passes but the account shows `error` later.**
Credentials were rotated or the role's policy changed after onboarding. Update the credential (over the API or by reconnecting) and run **Test Connection** again. Accounts whose scheduled scans failed three times in a row are paused until a scan succeeds — see [Automatic pause](./account-management.md#account-status-and-health).

## Scans

**The scan button is disabled / "A scan is already in progress".**
Only one scan runs per account at a time. Open **Cloud Scans** to see the running one; if it is stuck for far longer than its estimate, cancel it (`DELETE /api/cloud-scans/{run_id}`) and start again.

**A scan stays `queued`.**
Workers are busy or unavailable. On a self-hosted deployment check that the scan worker containers are running and healthy. Queued scans are picked up in order once a worker is free.

**The scan finished `partial`.**
Some jobs failed. Open the run and read its **warnings**: a region without permission, a disabled API, or API throttling. Fix the cause and re-scan; the successful jobs' results are already in.

**The scan finished `failed` immediately.**
Almost always authentication — the same causes as validation failures above. Run **Test Connection** to confirm.

**Findings count is much lower than expected.**
Check the run's **regions**: a quick scan without configured regions covers `us-east-1` only. Configure the account's regions (*Manage Accounts → Regions*) or run a **Full** scan.

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
Inventory is refreshed by discovery jobs. Trigger **Refresh Assets** on the account or wait for the next scheduled scan.

**The IAM Analysis tab says "No IAM findings available".**
The identity roster is populated by **Run IAM Analysis** (or the scheduled identity sweep). Run it on the account once; the roster, score and findings appear after it completes.

## Cloud events

**No events arrive.**
Check, in order: the route in your cloud targets the exact webhook URL shown in the in-app setup panel; the request carries the expected header (`x-amz-webhook-signature` / `x-goog-signature` / `x-webhook-signature`, or the GCP OIDC token); the platform has the matching `WEBHOOK_SECRET_<PROVIDER>` configured. A `401` in your cloud's delivery logs means a missing header, a `403` a wrong secret.

**Events arrive but no findings are created.**
Only catalogued, security-relevant events create findings; others are stored as *ignored*, and failed API calls as *skipped*. Trigger a known one (for example a security-group ingress change) to confirm the pipeline.

## Frequently asked questions

**Does the platform ever write to my cloud?**
No. Scans, discovery, IAM and network analyses and the *Cleanup Unused* recommendation are all read-only. The only outbound configuration you create is the event route for Cloud Events, and you create it yourself.

**Where are credentials stored?**
Encrypted at rest with a platform encryption key, in the platform's database. They are decrypted only inside scan workers at run time and are never returned by the API or shown in the UI. See [Trust & Security](../trust-and-security.md).

**How often should we scan?**
The defaults — daily incremental plus a weekly full baseline — are right for most teams. Add an on-demand **Full** scan before audits and after large infrastructure changes.

**Can we scan only some regions?**
Yes, on AWS: set the account's regions in the wizard or *Manage Accounts → Regions*. GCP projects and Azure subscriptions are always scanned whole.

**How do we handle 200 GCP projects or an AWS Organization?**
Connect the **GCP organization** (or a folder) once and let discovery onboard and maintain the projects. For AWS, connect each account with the cross-account role — the role and trust policy are identical, so it is one CloudFormation StackSet or Terraform module applied across the organization.

**Can findings flow into Jira, Slack or our SIEM?**
Yes — alerts and notifications are configured under Integrations; see [Notifications](../integrations/notifications.md) and [Third-Party Integrations](../integrations/third-party.md).

**Which permission do I need to resolve or suppress?**
**Manage Risks**. Viewing needs **View Scans**; connecting accounts needs **Manage Cloud Accounts**. See [RBAC & Team Management](../authentication/rbac-team-management.md).

**Is there a difference between a Quick and a Full scan's checks?**
No — both run the complete check set. They differ in default region footprint and expected duration. See [Scan types and regions](./scan-orchestration.md#scan-types-and-regions).

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers login, workers and deployment issues. For anything else, contact support with the **run ID** (from Cloud Scans) or the account's provider ID — both are on the scan detail dialog.
