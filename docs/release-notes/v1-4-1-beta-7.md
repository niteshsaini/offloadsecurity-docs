---
title: "1.4.1-beta.7 Release Notes"
sidebar_label: "1.4.1-beta.7"
slug: "/release-notes/1.4.1-beta.7"
description: "Offload Security 1.4.1-beta.7 (15 November 2026, pre-release): OpenVAS task controls (create-only, edit, delete, scheduled runs), scheduler and invitation hardening, and App Scan tool cleanup."
---

# 1.4.1-beta.7 Release Notes

**Released:** 15 November 2026 · **Type:** Pre-release · **Image tag:** `1.4.1-beta.7` · **Previous pre-release:** [1.4.1-beta.6](./v1-4-1-beta-6.md) · **Built on:** 1.4.0

:::caution[Pre-release]
This beta is for testing, not for production. If you skipped earlier betas, read their notes too.
:::

## Install or upgrade

Download the one-file installer from the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.7), check its SHA-256 (`2616b0a230fd8866044bdbc665ca374ebfca8bb53cd629d5bb439aa647484ba7`), then run:

```bash
sudo bash offload-install-1.4.1-beta.7.sh --domain <your-domain>
```

It uses the same base image as beta.5 and beta.6.

## Highlights

### OpenVAS task controls

See [OpenVAS Scanning](../on-premises/openvas-scanning.md).

- **Create a task without starting it:** untick **Start the scan now**. The API field is `start_now`, default `true`. The authorization attestation is asked for when the task starts.
- **Edit a task:** name, comment, scan config, scanner, hosts, excluded hosts, port list and credentials, via `PATCH /api/integrations/greenbone-openvas/tasks/{id}`.
  - Edits are refused while the task is queued or running, and for tasks not created from Offload.
  - A host change creates a new target and moves the old one to Greenbone's trashcan.
- **Delete a task** to Greenbone's trashcan, where it can be restored. Stop it first. Findings already imported stay open and are marked source-removed.
- **Schedule recurring OpenVAS scans** with the `openvas` type in the Unified Scheduler, or **Schedule…** on a task.
- **Permissions:** editing, deleting and scheduling need manage-scans; starting needs run-scans.

### Scheduler

- Overlapping runs no longer overwrite each other's lock or record; the cron lock is atomic.
- A queued **Run Now** is no longer left stuck, and run counters count each run once.
- Code Command Center shows queued and skipped runs as such.

### Invitations

- An invitation stuck mid-accept can be revoked.
- A failed registration rolls back cleanly.
- Older invitations can be declined.

### App Scan

- A tool cancelled with its scan is tracked and cleaned up. The wait for leftover tools is capped by `APP_SCAN_ABANDONED_DRAIN_S` (300 s by default, 10–3600).
- A tool that won't stop no longer survives: that worker process is restarted after the task.
- `api_discovery` keeps the endpoints it found when it hits its time limit, and the scan is graded Incomplete.

## Upgrade notes

- **App Scan worker restarts:** a worker may restart after an App Scan whose tool wouldn't stop. A log line says why, and the task result is kept. Leave `CELERY_WORKER_MAX_MEMORY_PER_CHILD_KB` unset.
- **OpenVAS edit and delete need manage-scans.** Analysts who can run scans can't edit, delete or schedule tasks.

## Known issues

- **OpenVAS target check:** with private targets allowed (the on-premises default), a host name that resolves to a cloud-metadata address is not blocked, because only Greenbone resolves the name.
- **Dependencies:** dnspython and opentelemetry-api had known CVEs. Fixed in [beta.8](./v1-4-1-beta-8.md).
- **Usage analytics:** the PostHog key is hard-coded, so installs send product usage analytics to PostHog (US). A product decision is pending.

Full engineering record: `CHANGELOG.md` in the platform repository.
