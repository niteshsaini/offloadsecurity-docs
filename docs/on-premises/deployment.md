---
title: "Deployment & Operations"
sidebar_label: "Deployment & Operations"
sidebar_position: 1
description: "Install and run the platform inside your network — prerequisites and sizing, the Docker Compose stack of prebuilt images, first-run setup, TLS, upgrades by image tag, MongoDB backups, the environment variables that matter on-premises, and exactly what needs outbound access."
---

# Deployment & Operations

The on-premises platform is a **Docker Compose** stack of prebuilt images pulled from a private registry with a read-only token you are given at onboarding. No source code, no build step: pull, configure, start. The same images run the SaaS.

## Prerequisites

| Requirement | Minimum | Recommended |
| --- | --- | --- |
| Host | Linux x86-64 with Docker Engine and Compose v2; the workers need the Docker socket (scanners run as sibling containers) | A dedicated VM |
| CPU / RAM | 4 vCPU / 8 GB | 4+ vCPU / 16 GB (MongoDB alone is capped at 6 GB by default) |
| Disk | 80 GB | 100 GB+ — scan artefacts, evidence and backups grow |
| Network | Outbound HTTPS to the image registry and the endpoints in [What needs outbound access](#what-needs-outbound-access); inbound 80/443 from your users; inbound reachability from the host to whatever you want to scan | |
| Optional | A DNS name for the platform (TLS via Let's Encrypt or your own certificate); an SMTP relay; an OIDC identity provider; object storage (S3 / GCS / Azure / MinIO) for evidence and reports — local disk works | |

## The stack

| Service | Image | Role |
| --- | --- | --- |
| `frontend` | `offload-cspm-frontend` | Nginx serving the UI and proxying `/api` — the only service exposed (80 / 443; 3000 loopback) |
| `backend` | `offload-cspm-backend` | The API (8001, loopback only) |
| `celery-worker` · `celery-scan-worker` · `celery-code-worker` · `celery-long-worker` | `offload-cspm-backend` | Background work by queue — cloud, Kubernetes and container scans; native web / API / network scans; code scans; long-running jobs. Each mounts the Docker socket to run scanner containers |
| `celery-fix-worker` | `offload-cspm-fix-worker` | The agentic fix pipeline (opt-in) |
| `celery-beat` | `offload-cspm-backend` | The scheduler: recurring scans, feeds, syncs, retention, reports |
| `mongo` (7) · `redis` (7) | public images | Data store (loopback 27017) · cache, sessions, queue broker |
| `certbot` | `certbot/certbot` | Let's Encrypt renewal when `DOMAIN_NAME` is set |

Some scanner tools ship inside the backend image (nmap, Trivy, Syft, Grype); the rest run as sibling containers pulled from public registries on first use — OWASP ZAP, Nuclei, Prowler, testssl.sh — which is why the workers mount the Docker socket.

## Install

```bash
docker login ghcr.io -u <username>            # the read-only token from onboarding
cp .env.example .env                           # then edit — see the table below
mkdir -p data/mongo/db data/mongo/config data/mongo/backups
docker compose -f docker-compose.client.yml pull
docker compose -f docker-compose.client.yml up -d
docker compose -f docker-compose.client.yml ps  # every service healthy
```

Then open `http://<host>:3000` (or `https://<DOMAIN_NAME>`) and sign in as `admin@offloadsecurity.com` with `DEFAULT_ADMIN_PASSWORD` from `.env` (if you left it empty, the generated password is in the backend log). That account is the [platform administrator](../authentication/platform-administration.md); change its password immediately and enable MFA.

### First-run setup wizard

The **Platform Setup** wizard walks through *Service Connectivity* (MongoDB, Redis) → *Security Keys* → *Storage* → *Platform Settings* (name, public URL, environment) → *Email / SMTP* → *Admin Account* → *Complete*. It generates the encryption keys that protect stored credentials (`CLOUD_ENCRYPTION_KEY`, `INTEGRATION_ENCRYPTION_KEY`, `SECRET_KEY`, `WEBHOOK_SECRET`) and stores them in the platform's own configuration (`platform_config.generated_secrets`). Copy them into `.env` afterwards — `.env.example` carries the one-line extraction command — so a restore onto a fresh host can still read stored credentials. Any Admin can relaunch it later from the account menu; `PLATFORM_SETUP_COMPLETE=true` in `.env` locks it against reopening.

### The `.env` values that matter on-premises

| Variable | Purpose |
| --- | --- |
| `GHCR_OWNER` · `IMAGE_TAG` | Which images to pull; `IMAGE_TAG` pins the release (`latest` by default) |
| `REDIS_PASSWORD` · `SECRET_KEY` | Required |
| `DEFAULT_ADMIN_PASSWORD` | First-boot administrator password |
| `PUBLIC_APP_URL` · `DOMAIN_NAME` | The URL users (and SSO redirects, emails) use; setting `DOMAIN_NAME` switches Nginx to HTTPS with Let's Encrypt |
| `ALLOW_PRIVATE_SCAN_TARGETS=true` | Let scans and integrations reach RFC-1918 addresses. Loopback and link-local / cloud-metadata stay blocked regardless. Read by the backend **and** the workers |
| `SMTP_HOST` · `SMTP_PORT` · `SMTP_USER` · `SMTP_PASSWORD` · `SMTP_FROM` | Platform mail (invitations, resets, notifications); overrides anything teams configure |
| `OIDC_*` | Single sign-on — see [Signing In & Sessions](../authentication/session-management.md#single-sign-on-oidc) |
| `ALLOW_PUBLIC_REGISTRATION=false` | Keep it false; accounts come from invitations or SSO |
| `MONGO_MEM_LIMIT` · `MONGO_WT_CACHE_GB` | Size MongoDB to the host (6 GB / 3 GB by default) |
| `*_RETENTION_DAYS` | `SCAN_RETENTION_DAYS` 90 · `CLOUD_SCAN_RETENTION_DAYS` 180 · `CONTAINER_SCAN_RETENTION_DAYS` 180 · `REPORT_RETENTION_DAYS` 180 · `AUDIT_TRAIL_RETENTION_DAYS` 365 |
| `REMEDIATION_LIVE_EXECUTE` | Leave false until you want the Auto-Fix Engine to change cloud resources |
| `INTEGRATION_VERIFY_SSL` · `SMTP_CA_CERT` | Private-CA handling for integrations and mail |

## TLS

Set `DOMAIN_NAME` (and `PUBLIC_APP_URL=https://…`) and the front end serves 443 with a Let's Encrypt certificate renewed by the `certbot` service — which needs port 80 reachable from the internet for the challenge. Without `DOMAIN_NAME` the front end serves plain HTTP on port 3000 (loopback) and 80; air-gapped or internal-only installs terminate TLS on their own reverse proxy or load balancer in front of it.

## Upgrades

Releases are image tags. To move:

```bash
# in .env: IMAGE_TAG=<new tag>
docker compose -f docker-compose.client.yml pull
docker compose -f docker-compose.client.yml up -d
```

Take a backup first. Expect users to sign in again after the restart; scans that were running are re-queued or reaped by the fleet-health sweeps. Release notes for the tag list anything that needs an operator's hand.

## Backups

MongoDB is the system of record; evidence and report files live in the configured object storage (or the `data/` volumes when local).

```bash
docker compose -f docker-compose.client.yml exec -T mongo /usr/local/bin/backup.sh
# lists / restores:
docker compose -f docker-compose.client.yml exec mongo ls /backups/
docker compose -f docker-compose.client.yml exec mongo /usr/local/bin/restore.sh cspm_backup_<timestamp>
```

`backup.sh` writes a timestamped dump to `data/mongo/backups` and keeps the last 7 daily and 4 weekly; schedule it from the host's crontab (the script header has the line). `restore.sh` takes a safety backup before replacing data. Back up `.env` and the wizard-generated keys with the dumps — encrypted credentials are unreadable without them.

## What needs outbound access

| Destination | Why | If blocked |
| --- | --- | --- |
| `ghcr.io`, Docker Hub | Platform images; scanner images (ZAP, Nuclei, Prowler, testssl.sh) on first use | Pre-pull or mirror to an internal registry and point `GHCR_OWNER` / image references at it |
| Trivy and Grype vulnerability databases, Nuclei templates | Container, dependency and template-based scans stay current | Scans run on the bundled databases and age; mirror updates |
| The nine threat feeds (`cisa.gov`, `abuse.ch`, `otx.alienvault.com`, PhishTank, Blocklist.de, Spamhaus, OpenPhish) | Threat intelligence, KEV-based prioritisation | Feeds show *degraded*; import indicators via STIX instead |
| Cloud provider APIs (AWS, Azure, GCP) | Cloud posture scans, asset discovery | Those modules cannot run |
| Your SCM (GitHub, GitLab, Bitbucket, Azure DevOps) | Code scans, fix PRs | Use an internal SCM the host can reach |
| LLM provider (Anthropic, OpenAI, Google) — optional | AI features; Knowledge Base embeddings | Everything works in rule-based mode |
| Let's Encrypt — optional | Automatic TLS | Bring your own certificate / proxy |
| Your SMTP relay, Slack / Teams / PagerDuty / Jira endpoints | Notifications and integrations | Configure what you have |

Nothing about your findings is sent to Offload Security. Support works from logs and exports you choose to share.

## Health

`GET /api/health` is the liveness endpoint the front end and load balancers use; `docker compose ps` shows per-service health checks. The bundled monitoring (Prometheus, Grafana, Alertmanager, Loki) in the development compose file is optional on client installs; the platform's own scheduler and fleet-health sweeps recover stuck scans without it.

## Related

- [Platform Administration](../authentication/platform-administration.md) — the administrator account, Platform Setup, menu settings.
- [Production configuration](../adoption/production-configuration.md) — tuning and hardening checklist.
- [Troubleshooting & FAQ](./troubleshooting.md) — the failures operators actually hit.
