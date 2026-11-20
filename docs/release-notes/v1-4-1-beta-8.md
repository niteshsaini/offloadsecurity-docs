---
title: "1.4.1-beta.8 Release Notes"
sidebar_label: "1.4.1-beta.8"
slug: "/release-notes/1.4.1-beta.8"
description: "Offload Security 1.4.1-beta.8 (19 November 2026, pre-release): the platform-admin console, read-only demo mode for a separate demo server, a new maintenance worker and memory defaults, retention and startup fixes, and security fixes."
---

# 1.4.1-beta.8 Release Notes

**Released:** 19 November 2026 · **Type:** Pre-release · **Image tag:** `1.4.1-beta.8` · **Previous pre-release:** [1.4.1-beta.7](./v1-4-1-beta-7.md) · **Built on:** 1.4.0

:::caution[Pre-release]
This beta is for testing, not for production. The current documentation describes this release. The [1.4.0 documentation](/1.4.0/) describes the last final release.
:::

:::warning[Read the upgrade notes first]
The compose files add a container and change memory defaults. Read [Upgrade notes](#upgrade-notes).
:::

## Install or upgrade

Download the one-file installer from the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.8), check its SHA-256 (`38014c157b8f1c022e8c592fab6b1ca2551626df2875b8d9b49732b74e0bf546`), then run:

```bash
sudo bash offload-install-1.4.1-beta.8.sh --domain <your-domain>
```

The images use a new base image with fresh vulnerability databases. `/api/health` still reports `1.4.0`; go by the image tag.

## Highlights

### Platform-admin console

New pages for the platform administrator; team admins don't see them. See [Platform Administration](../authentication/platform-administration.md).

- **User Activity:** reset a user's MFA, enforce MFA for the whole deployment, sign a user out everywhere, unlock an account, search and filter.
- **Teams & Users:** manage every team, its members and roles, with audit events. `GET /api/auth/users` is now scoped to the caller's teams.
- **Audit Log:** the API trail and authentication events, with filters, CSV export and hash-chain verification.
- **System Health:** one card per health source.
- **Security Policy:** password and lockout rules stored in the database, which can only be stricter than the built-in floor, plus an admin IP allowlist.
- **Access Review:** export every user's entitlements, sign off a review with a tamper-evident snapshot, and deactivate dormant users.
- **More than one platform admin:** grant, revoke and transfer the role. At least one usable admin always remains, and sensitive actions ask for your password again.

### Read-only demo mode

For a separate public demo server only: `DEMO_MODE=true` refuses every write, blocks reads with side effects, turns off AI and scheduled jobs, and shows a demo banner. Sample data is seeded and reset daily by `docker-compose.demo.yml`. **Customer installs leave `DEMO_MODE` unset, and nothing changes for them.**

### Changes for every install

- **Auditor role:** auditors can read Vulnerability Management and the triage queue (still read-only).
- **Compliance catalogue:** duplicate controls are merged at startup and a unique index prevents new ones.
- **Sessions and rate limits:** dead sessions are pruned at login, and IPv6 clients are rate-limited per /64.
- CORS preflight requests are no longer written to the audit trail.

### Fixes from a production health check

- **Workers:**
  - A new `celery-maintenance-worker` handles maintenance tasks. It has no Docker access.
  - Docker housekeeping moves to its own queue on the general worker.
  - Periodic tasks can no longer pile up.
  - SLA checks and vulnerability syncs no longer run twice at once.
- **Startup:** the orphan `team_id` repair no longer blocks the scheduler at boot. Collection stats use estimated counts.
- **Retention:** the nightly cycle drains its backlog in batches, records each cycle, and reports missing backups.
- **Performance:** indexes for the findings-lake sweeps, a bounded SLA walk, and in-app notification retention with duplicate suppression.
- **Kubernetes:** scans still waiting in the queue are no longer failed as "Scan lost". They wait up to `K8S_SCAN_QUEUE_MAX_HOURS` (24 h by default).

### Security fixes

- **Scanner image overrides:** only platform admins can set them. They must be the tool's own repository pinned by digest, and are re-checked when a scan runs.
- **Secret verdicts:**
  - Secrets from the supplementary scanner get verdicts.
  - Key-material names are no longer dismissed.
  - A same-line comment no longer hides a high-entropy value.
  - Stored reasons never quote the source line.
- **Response headers:** `X-XSS-Protection` is removed, `Cross-Origin-Resource-Policy: same-origin` is added, and the nginx version is hidden.
- **Dependencies:** dnspython 2.9.2 and OpenTelemetry 1.45.2, fixing the two CVEs listed in beta.7.

## Upgrade notes

| Change | What to do |
| --- | --- |
| **New container** | Run `docker compose up -d` after pulling. It creates `celery-maintenance-worker` and recreates the general, docker-control and beat containers. The installer does this. |
| **Mongo memory** | Keep `MONGO_WT_CACHE_GB` at most (`MONGO_MEM_LIMIT` − 1) ÷ 2: 3 for the default 8G limit, 4 for 10G, 7 for 16G. A 4 GB cache in an 8G limit gets the database killed for running out of memory. Defaults don't override values already set in `.env`. See [Deployment & Operations](../on-premises/deployment.md). |
| **Scheduler memory** | Source-built installs only (`docker-compose.yml`): if `.env` pins `SCHEDULER_MEM_LIMIT=1536M`, remove it or raise it; the new default is 2560M. The on-premises client stack runs the scheduler inside `backend`, so the setting has no effect there. |
| **Scanner image overrides** | An override that isn't the tool's own repository pinned by digest is ignored, and the pinned image runs instead. |

## Known issues

- **OpenVAS target check:** with private targets allowed, a host name that resolves to a cloud-metadata address is not blocked.
- **Demo mode:** a few pages show no demo notice when a write is blocked, though the write is still refused.
- **Usage analytics:** the PostHog key is hard-coded, so installs send product usage analytics to PostHog (US). A product decision is pending.

Full engineering record: `CHANGELOG.md` in the platform repository.
