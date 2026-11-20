---
title: "1.4.1-beta.6 Release Notes"
sidebar_label: "1.4.1-beta.6"
slug: "/release-notes/1.4.1-beta.6"
description: "Offload Security 1.4.1-beta.6 (14 November 2026, pre-release): App Scan refuses unsafe targets and no longer grades incomplete scans, per-tool time limits, honest scheduler runs, invitation revoke and user deactivation, and a stricter Content Security Policy."
---

# 1.4.1-beta.6 Release Notes

**Released:** 14 November 2026 · **Type:** Pre-release · **Image tag:** `1.4.1-beta.6` · **Previous pre-release:** [1.4.1-beta.5](./v1-4-1-beta-5.md) · **Built on:** 1.4.0

:::caution[Pre-release]
This beta is for testing, not for production. Nothing in it has been tested on a live instance yet; see [Known issues](#known-issues). The current documentation describes the latest pre-release, [1.4.1-beta.8](./v1-4-1-beta-8.md).
:::

This beta is 1.4.1-beta.5 plus five fixes from the 11 November end-to-end test report. **If you skipped beta.4 or beta.5, read [beta.4's notes](./v1-4-1-beta-4.md) and [beta.5's notes](./v1-4-1-beta-5.md) too.**

:::warning[Read the upgrade notes first]
App Scan grades can drop after this upgrade, and App Scan tools now have time limits and are cancelled when they stall. Read [Upgrade notes](#upgrade-notes).
:::

## Install or upgrade

All six images are tagged `1.4.1-beta.6`. They use the same base image as beta.5. Download the one-file installer from the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.6). It uses the deploy files from this tag. Then run:

```bash
sudo bash offload-install-1.4.1-beta.6.sh --domain <your-domain>
```

Check the installer's SHA-256 before you run it: `d829606b4a60eec6626363fc0df6f28360c3d6fdf97ab4f8aa664412eb64b4ad`.

The version file is not changed for betas, so go by the image tag. From this beta, an anonymous `/api/health` call no longer shows a version at all.

## Highlights

### App Scan

See [Run an App Scan](../security-scanning/app-scan.md).

- **Unsafe targets are refused when you start the scan.** A scan of a cloud-metadata address, `localhost`, a host name that doesn't resolve, or a private address (unless `ALLOW_PRIVATE_SCAN_TARGETS` is set) now returns HTTP 422, and no scan is created. The login, probe and OAuth token URLs are checked the same way. Before, the API answered 200 and the worker refused the scan later.
- **Incomplete scans are not graded.** If any requested tool failed or timed out, the scan shows **Incomplete — not graded** in the UI and in every report. A failed tool's controls count as errored, never as passed. Older partial scans are shown the same way.
- **Each tool has a time limit, and stalled tools are cancelled.** owasp_api and api_discovery get 2 hours each; every other tool gets 20 minutes. Auto-cancel of a stalled tool is now on by default. When owasp_api reaches its limit, the findings it already has are kept.
- **`http://` targets skip the TLS tools.** Those checks show as not applicable, and the scan can still be graded.
- **testssl scans can run in parallel.** Each run gets its own container name. Checkov had the same problem and is fixed too.
- **Duration estimates match the real limits:** about 10 minutes for Quick, up to 45 minutes for Standard and up to 11.5 hours for Full.

### Scheduler

See [Scan Management](../security-scanning/scan-management.md).

- **Run Now returns an execution ID.** The history record is written before the run starts, so you can follow the run in `/history`. If the job is skipped or queued, the UI says so.
- **Failures are no longer silent.** A failed history read returns HTTP 500 instead of an empty list. The hidden limit of 1,000 schedules is gone. Malformed history records are skipped and counted.
- **The start-time spread is shown**, for example "(cron 08:00 UTC · start spread up to 5 min)".

### Accounts, invitations and cleanup

- **Admins can revoke pending invitations** from the API or the UI. Accepting and revoking an invitation at the same moment is safe.
- **A platform admin can deactivate and reactivate users.** Deactivating a user revokes their sessions and API keys. You can't deactivate yourself, the platform admin, the last admin or a team's only admin. Users are not deleted, so the audit trail is kept.
- **SARIF sources can be removed** with `DELETE /api/cicd/sarif/sources?scope_key=…&scanner=…`. This needs the team Admin role, or an API key with `scans:manage`.
- **Permission errors (403) show plain role names**, for example "viewer" instead of "UserRole.VIEWER".
- **Anonymous health checks show less.** `/api/health` no longer shows the version, and `/api/health/ready` no longer shows error text.

### Frontend

- **Inline scripts are no longer allowed.** `'unsafe-inline'` is removed from the `script-src` Content Security Policy. The PostHog loader is now a separate file, and the development page `test-login.html` has been removed. The Swagger pages have their own hash-based policy.
- **KPI tiles are readable at phone width.**

## Upgrade notes

| Change | What to do |
| --- | --- |
| **App Scan grades can drop by up to 20 points** | This applies to complete scans too. Coverage now counts only the controls a tool actually tested, so expect a lower grade when you rescan. The drop is not a regression. |
| **App Scan time limits and auto-cancel** | Auto-cancel of stalled tools is now on, and each tool has a time limit. To tune them, set these in `.env`: `APP_SCAN_STALL_AUTO_CANCEL` (default `true`), `APP_SCAN_STALL_MINUTES` (default 15), `APP_SCAN_TOOL_BUDGET_S` (default 1200 seconds) and `APP_SCAN_TOOL_BUDGET_<TOOL>_S` for one tool, for example `APP_SCAN_TOOL_BUDGET_OWASP_API_S=7200`. The App Scan worker's size is set with `LONG_WORKER_CPUS` and `LONG_WORKER_MEM` (defaults 1.0 and 4G). All of these are described in `.env.example`. |
| **Content Security Policy** | If you added your own inline script to the frontend, it is now blocked. After upgrading, open the app and `/api/docs` and check the browser console for CSP errors. |

## Retest plan

On a beta instance, check these after upgrading:

1. Start an App Scan on `http://169.254.169.254/`, on `http://localhost:8000/` and on `https://x.example.invalid`. Each should return HTTP 422, and no scan should be created.
2. Run two App Scans with testssl at the same time. There should be no container-name conflict.
3. Run a Quick scan in which one tool times out. It should show **Incomplete — not graded** in the UI and in the PDF.
4. Stall a tool on purpose. It should be cancelled and its worker slot freed. Then run three Quick scans back to back; each should finish.
5. Click **Run Now** on a schedule. `/history` should show the returned execution ID reaching a final status.
6. Open the app and `/api/docs`. The browser console should show no CSP violations.
7. Clean up: revoke the pending test invitation, deactivate the test viewer user and remove the test SARIF sources.

## Known issues

- **Not yet tested on a live instance:** everything above, plus the items carried over from beta.4 and beta.5 (credentialed OpenVAS scans, OpenVAS scan launch, ECR sign-in, bridge networking for scanner containers).
- **Small follow-ups, none of them blockers:**
  - In the scheduler, a cancelled run can still overwrite a newer run's lock.
  - An invitation left half-accepted by a crash can't be revoked until it expires.
  - A tool cancelled together with its scan isn't tracked as abandoned.
- **Usage analytics:** the PostHog key is built into the frontend, so installs send usage analytics to PostHog (US region). A decision on this is pending.

The full commit list is in the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.6).
