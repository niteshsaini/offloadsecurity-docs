---
title: "Deployment & Operations"
sidebar_label: "Deployment & Operations"
sidebar_position: 1
description: "Install and run the platform inside your network — prerequisites and sizing, the Docker Compose stack of prebuilt images, first-run setup and encryption keys, TLS, upgrades by image tag, encrypted backups, data retention, audit-trail integrity, the environment variables that matter on-premises, and exactly what needs outbound access."
---

# Deployment & Operations

The on-premises platform is a **Docker Compose** stack of prebuilt images pulled from a private registry with a read-only token you are given at onboarding. No source code, no build step: pull, configure, start. The same images run the SaaS.

## Prerequisites

| Requirement | Minimum | Recommended |
| --- | --- | --- |
| Host | Linux x86-64 with Docker Engine and Compose v2. Scanners run as sibling containers, reached through a restricted Docker API proxy that mounts the host's Docker socket | A dedicated VM |
| CPU / RAM | 4 vCPU / 8 GB | 4+ vCPU / 16 GB (MongoDB alone is capped at 6 GB by default) |
| Disk | 80 GB | 100 GB+ — scan artefacts, evidence, retention (730 days by default) and local backups grow |
| Network | Outbound HTTPS to the image registry and the endpoints in [What needs outbound access](#what-needs-outbound-access); inbound 80/443 from your users; reachability from the host to whatever you want to scan | |
| Optional | A DNS name for the platform (TLS via Let's Encrypt or your own certificate); an SMTP relay; an OIDC identity provider; S3-compatible storage for off-host backups; object storage (S3 / GCS / Azure / MinIO) for evidence and reports — local disk works | |

## The stack

| Service | Image | Role |
| --- | --- | --- |
| `frontend` | `offload-cspm-frontend` | Nginx serving the UI and proxying `/api` — the only service exposed (80 / 443; 3000 loopback) |
| `backend` | `offload-cspm-backend` | The API (8001, loopback only) and the in-process schedulers. Has **no** Docker access |
| `celery-worker` | `offload-cspm-backend` | General queue: scan orchestration, compliance, threat feeds, integration syncs (Wazuh, OpenVAS), maintenance |
| `celery-scan-worker` | `offload-cspm-backend` | Cloud scans and per-region asset discovery |
| `celery-code-worker` | `offload-cspm-backend` | Code, Kubernetes and container-image scans |
| `celery-long-worker` | `offload-cspm-backend` | Multi-hour native scans (App Scan / DAST, web, domain recon) |
| `celery-docker-control-worker` | `offload-cspm-backend` | Short Docker questions an API request waits on (is an image cached, cancel a scan container, Hadolint, Cosign verify) |
| `celery-beat` | `offload-cspm-backend` | The Celery scheduler: recurring scans, feeds, syncs, retention, reports |
| `docker-socket-proxy` | `haproxy` (public) | With `agent-launcher`, the only holder of the host Docker socket. Forwards only the Docker API calls the workers need |
| `backup` · `backup-init` | `offload-backup` · `alpine` | Scheduled, encrypted backups of MongoDB and the file volumes (see [Backups](#backups)); `backup-init` prepares the backup directory once |
| `mongo` (7) · `redis` (7) | public images | Data store (loopback 27017) · cache, sessions, queue broker |
| `certbot` | `certbot/certbot` | Let's Encrypt renewal when `DOMAIN_NAME` is set |
| `celery-fix-worker` · `agent-launcher` · `agent-egress` · `agent-sandbox` | `offload-cspm-fix-worker` · `offload-cspm-backend` · `offload-agent-egress` · `offload-agent-sandbox` | The agentic fix pipeline. Started **only** with the `agentic-fix` compose profile — see [Agentic fix services](#agentic-fix-services-opt-in) |

Some scanner tools ship inside the backend image (nmap, Trivy, Syft, Grype); the rest run as sibling containers pulled from public registries on first use — OWASP ZAP, Nuclei, Prowler, testssl.sh. The workers start them through `docker-socket-proxy` on an internal network with no route out; the web-facing backend and the scheduler cannot reach Docker at all.

:::note[What the proxy does and does not do]
The proxy removes Docker from the web tier and blocks most of the Docker API (exec, build, volumes, swarm, secrets, system and more). It does not inspect the body of a container-create request, so it narrows what a compromised worker can do but does not sandbox the workers.
:::

## Install

The bundle you receive contains `docker-compose.client.yml`, `.env.example` and `deployment/docker-socket-proxy/haproxy.cfg`. Keep `haproxy.cfg` at that path next to the compose file, world-readable (`chmod 644`); on SELinux-enforcing hosts give it a container label (`chcon -t container_file_t deployment/docker-socket-proxy/haproxy.cfg`). Without it the proxy restarts in a loop and every Docker-backed scan fails.

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

The **Platform Setup** wizard walks through *Service Connectivity* (MongoDB, Redis) → *Security Keys* → *Storage* → *Platform Settings* (name, public URL, environment) → *Email / SMTP* → *Admin Account* → *Complete*. Any Admin can relaunch it later from the account menu; `PLATFORM_SETUP_COMPLETE=true` in `.env` locks it against reopening.

The *Security Keys* step can generate the encryption keys that protect stored credentials (`CLOUD_ENCRYPTION_KEY`, `INTEGRATION_ENCRYPTION_KEY`). It shows them once as paste-ready `KEY=value` lines with a copy button and asks you to confirm before you leave the step. **Paste them into the host `.env` and recreate the stack** (`docker compose -f docker-compose.client.yml up -d` — `docker compose restart` does not re-read `.env`). Until you do, only the backend process holds the keys: the workers and scheduler cannot decrypt credentials, and the keys are lost when the backend container is recreated. The wizard summary, `GET /api/health/status` and `/api/setup/status` flag keys still missing from the host environment. You can also generate the keys yourself and put them in `.env` before first start.

:::warning[The keys are not stored in the database]
From 1.4.0 the platform never keeps these keys in MongoDB, which holds the ciphertext they protect. If you lose `.env`, stored cloud and integration credentials cannot be decrypted. Keep a copy of `.env` in your secret store, separate from database backups.
:::

### The `.env` values that matter on-premises

| Variable | Purpose |
| --- | --- |
| `GHCR_OWNER` · `IMAGE_TAG` | Which images to pull. Both are **required** — `IMAGE_TAG` is the release you run (e.g. `1.4.0`); there is no `latest` default, so an install never drifts onto an unreleased build |
| `DOCKER_GID` | The host's docker group ID (`stat -c '%g' /var/run/docker.sock`), so the restricted Docker socket proxy the scan workers use can open the socket. Defaults to 996, which is wrong on many hosts |
| `REDIS_PASSWORD` · `MONGO_ROOT_PASSWORD` · `SECRET_KEY` · `WEBHOOK_SECRET` | Required; compose refuses to start without them |
| `CLOUD_ENCRYPTION_KEY` · `INTEGRATION_ENCRYPTION_KEY` | Fernet keys that encrypt stored credentials — from the setup wizard or generated yourself. See [Encryption keys](#encryption-keys) |
| `DEFAULT_ADMIN_PASSWORD` | First-boot administrator password |
| `PUBLIC_APP_URL` · `DOMAIN_NAME` | The URL users (and SSO redirects, emails) use; setting `DOMAIN_NAME` switches Nginx to HTTPS with Let's Encrypt |
| `ALLOW_PRIVATE_SCAN_TARGETS=true` | Let scans reach RFC-1918 addresses (default false). Loopback and link-local / cloud-metadata stay blocked regardless. Read by the backend **and** the workers. Also allows private integration endpoints |
| `ALLOW_PRIVATE_INTEGRATION_TARGETS` | Integrations (Jira, Wazuh, Greenbone, SonarQube, …) may reach private addresses. **Default true**; set false only where every integration endpoint is public |
| `SCAN_MAX_NETWORK_HOSTS` | Largest range one nmap scan may cover (default 4096 addresses, a /20) |
| `SCAN_REQUIRE_AUTHORIZATION` | `true` makes every scan carry an authorization attestation (default false: scans are recorded as "authorization not recorded") |
| `SMTP_HOST` · `SMTP_PORT` · `SMTP_USER` · `SMTP_PASSWORD` · `SMTP_FROM` | Platform mail (invitations, resets, notifications); overrides anything teams configure |
| `OIDC_*` | Single sign-on — see [Signing In & Sessions](../authentication/session-management.md#single-sign-on-oidc) |
| `ALLOW_PUBLIC_REGISTRATION=false` | Keep it false; accounts come from invitations or SSO |
| `MONGO_MEM_LIMIT` · `MONGO_WT_CACHE_GB` | Size MongoDB to the host (6 GB / 3 GB by default; keep the cache at least 1 GB below the limit) |
| `WEB_CONCURRENCY` | API worker processes (default 1). See [API worker processes](#api-worker-processes) |
| `*_RETENTION_DAYS` | How long data is kept. See [Data retention](#data-retention) |
| `BACKUP_*` | Scheduled encrypted backups. See [Backups](#backups) |
| `REQUIRE_EXTERNALIZED_SECRETS` | `auto` (default), `true` or `false`. See [Encryption keys](#encryption-keys) |
| `AUDIT_CHAIN_HMAC_KEY` · `AUDIT_HEAD_WITNESS_*` | Audit-trail signing key and the optional external head witness. See [Audit trail integrity](#audit-trail-integrity) |
| `REMEDIATION_LIVE_EXECUTE` | Leave false until you want the Auto-Fix Engine to change cloud resources |
| `AGENTIC_FIX_ENABLED` · `AGENTIC_FIX_RUNNER` | Agentic fix pipeline, off by default (`false` / `none`). See [Agentic fix services](#agentic-fix-services-opt-in) |
| `WAZUH_API_USERNAME` · `WAZUH_API_PASSWORD` · `WAZUH_BIND` | Only for the bundled Wazuh stack — see [Wazuh Integration](./wazuh-integration.md#the-bundled-wazuh-stack) |
| `OPENVAS_ADMIN_USER` · `OPENVAS_ADMIN_PASSWORD` · `OPENVAS_BIND` | Only for the bundled Greenbone stack — see [OpenVAS Scanning](./openvas-scanning.md#the-bundled-greenbone-stack) |
| `INTEGRATION_VERIFY_SSL` · `INTEGRATION_CA_BUNDLE` · `SMTP_CA_CERT` | Private-CA handling for integrations and mail |

## TLS

Set `DOMAIN_NAME` (and `PUBLIC_APP_URL=https://…`) and the front end serves 443 with a Let's Encrypt certificate renewed by the `certbot` service — which needs port 80 reachable from the internet for the challenge. Without `DOMAIN_NAME` the front end serves plain HTTP on port 3000 (loopback) and 80; air-gapped or internal-only installs terminate TLS on their own reverse proxy or load balancer in front of it.

## Upgrades

Releases are image tags (`1.4.0`, …). Read the [release notes](../release-notes/index.md) for the target version first — its **Upgrade notes** list any `.env` changes and new services — and use the documentation for that version (version selector, top right). To move:

```bash
# in .env: IMAGE_TAG=<new version>, e.g. IMAGE_TAG=1.4.0
docker compose -f docker-compose.client.yml pull
docker compose -f docker-compose.client.yml up -d
```

Take a backup first. Upgrade every backend and worker container together (one `up -d` does this). Expect users to sign in again after the restart; scans that were running are re-queued or reaped by the fleet-health sweeps.

If a release changes `deployment/docker-socket-proxy/haproxy.cfg`, copy the new file into place and recreate the proxy — Compose does not watch that file, and HAProxy reads it only at start:

```bash
docker compose -f docker-compose.client.yml up -d --force-recreate docker-socket-proxy
```

:::warning[Old retention lines in `.env`]
A `.env` copied from an `.env.example` before 1.4.0 pins the old short retention windows (90 / 180 / 365 days). An explicit value always wins, so data keeps being deleted early until you remove those lines. See [Data retention](#data-retention).
:::

## Backups

MongoDB is the system of record; evidence, Knowledge Base uploads, scan archives, stored scan results and custom rules live on file volumes (or in the configured object storage).

The `backup` service (from 1.4.0) runs with the stack. Every `BACKUP_INTERVAL_HOURS` (default 24; first run 10 minutes after start) it dumps MongoDB, archives the customer-data file volumes, encrypts both to the [age](https://age-encryption.org) public key in `BACKUP_AGE_RECIPIENT`, and either uploads them to S3-compatible storage (`BACKUP_S3_BUCKET`, `BACKUP_S3_ENDPOINT`, `BACKUP_S3_ACCESS_KEY_ID` / `BACKUP_S3_SECRET_ACCESS_KEY`) or, without a bucket, keeps them in `data/mongo/backups` on the same host with a warning on every run. Runs older than `BACKUP_RETENTION_DAYS` (default 14) are deleted, always keeping the newest `BACKUP_MIN_KEEP` (default 3) successful runs and the newest run whose restore-verify passed.

**With no recipient set the service refuses to back up** rather than writing plaintext, unless you opt in with `BACKUP_ALLOW_UNENCRYPTED=true` (not recommended).

```bash
# 1. Make a key pair OFF the server; keep the private key in your password manager or HSM.
age-keygen -o offload-backup.key        # prints "Public key: age1..."
# 2. In .env: BACKUP_AGE_RECIPIENT=age1...  (comma-separate several for key escrow)
#    and, for off-host copies, BACKUP_S3_BUCKET / BACKUP_S3_ENDPOINT / BACKUP_S3_ACCESS_KEY_ID / BACKUP_S3_SECRET_ACCESS_KEY
# 3. Apply and watch the first run:
docker compose -f docker-compose.client.yml up -d backup
docker compose -f docker-compose.client.yml logs -f backup
# Take a backup now instead of waiting:
docker compose -f docker-compose.client.yml run --rm backup once
```

Give the backup credentials **write-only** access to a dedicated bucket with versioning or object lock; the application containers share `.env`, so assume a compromised host can read them. With write-only credentials set `BACKUP_RETENTION_DAYS=0` and let a bucket lifecycle rule handle retention.

**Prove a backup restores.** `restore-verify` decrypts the newest archive into a throwaway MongoDB inside the backup container (in RAM, `BACKUP_VERIFY_SCRATCH_SIZE`, default 2 GB) and checks the file archive, without touching production:

```bash
docker compose -f docker-compose.client.yml run --rm \
  -v /secure/offload-backup.key:/run/secrets/age.key:ro \
  -e BACKUP_AGE_IDENTITY_FILE=/run/secrets/age.key \
  backup restore-verify
```

The service also runs restore-verify on a schedule (`BACKUP_VERIFY_INTERVAL_HOURS`, default 168; `0` = off), but only if it can read a private key (`BACKUP_AGE_IDENTITY_FILE`) — use a dedicated verify key pair for that, not your escrow key. Without one, scheduled verifies are recorded as skipped.

**Monitoring.** `GET /api/health/status` (unauthenticated) reports `components.backup` as `healthy`, `failing`, `overdue` or `never_run`; the full record is on `GET /api/health/backup` for the platform administrator. A backup that is not healthy makes the overall status `degraded`.

**What the backup does not cover.** The dump is not point-in-time on the default standalone MongoDB (a write during the dump can appear in one collection and not another); run MongoDB as a single-node replica set for a consistent snapshot. And the backup never contains `.env`: keep `.env`, with the encryption keys, in your secret store. Without those keys, restored credentials cannot be decrypted.

A full restore (stop the application services, `mongorestore` the decrypted archive, unpack the file archive from the **same** timestamp into the volumes, start the stack) is a deliberate, data-replacing operation; follow the procedure shipped in the release's deployment guide or ask support.

## Data retention

MongoDB TTL indexes and daily retention sweeps delete data automatically. From 1.4.0 the shipped defaults are:

| Data | Variable(s) | Default |
| --- | --- | --- |
| Scan results and scan runs | `SCAN_RETENTION_DAYS`, `SCAN_RUN_RETENTION_DAYS`, `CONTAINER_SCAN_RETENTION_DAYS` | 730 days |
| Findings (cloud, Kubernetes, code; resolved unified findings) | `FINDING_RETENTION_DAYS` and per-store variables | 730 days |
| Native scan records | `NATIVE_SCAN_RETENTION_DAYS` | 365 days |
| Compliance records and compliance audit log | `COMPLIANCE_RETENTION_DAYS`, `COMPLIANCE_DRIFT_TTL_DAYS`, `COMPLIANCE_AUDIT_LOG_RETENTION_DAYS` | 1825 days (5 years) |
| AI-agent and Kubernetes credential-access audit | `AGENT_AUDIT_RETENTION_DAYS`, `K8S_CREDENTIAL_AUDIT_RETENTION_DAYS` | 1825 days |
| Evidence | `EVIDENCE_RETENTION_YEARS` | 7 years |
| Reports | `REPORT_RETENTION_DAYS` | 180 days |
| Alerts · system and cloud events | `ALERT_RETENTION_DAYS` · `SYSTEM_EVENT_RETENTION_DAYS`, `CLOUD_EVENT_RETENTION_DAYS` | 90 days |

The API audit trail and authentication events have no TTL. The legacy `container_scans` and `cloud_scans` collections never had a working TTL; turning one on would delete old data, so it is opt-in (`ENABLE_LEGACY_SCAN_TTLS=true`, default false).

A value you set always wins, lower ones included. Values below 1 are ignored; a value below its default logs a startup warning and is listed as `overrides_below_promise` in `GET /api/scan-retention/policies`. Change a window by editing `.env` and running `docker compose -f docker-compose.client.yml up -d`.

**Upgrading from 1.3.x:** remove old `*_RETENTION_DAYS=90|180|365` lines copied from an earlier `.env.example` unless you chose them on purpose. With the longer defaults MongoDB keeps growing for up to 24 months after the upgrade before it levels off — size the disk for it (`du -sh ./data/mongo/db`).

## Encryption keys

### Keep keys out of the database

Installs set up by the wizard in releases before 1.4.0 may still hold their root keys in MongoDB, next to the credentials they encrypt. In 1.4.0 such an install keeps running, with a CRITICAL `LEGACY SECRET STORAGE` log on every start and `components.secret_storage.status: warning` in `GET /api/health/status`. `REQUIRE_EXTERNALIZED_SECRETS` controls this:

| Value | Behavior |
| --- | --- |
| `auto` (default) | Strict for new installs and installs whose keys are all in the environment; a legacy install whose keys are only in MongoDB keeps working with the warning |
| `true` | Never read secrets from MongoDB; refuse to start if one exists only there |
| `false` | Temporary opt-out; keep reading legacy secrets from MongoDB |

The next release is planned to make strict the default, so move the keys now with the bundled script (each step is safe to re-run; nothing is deleted until the purge):

```bash
C="docker compose -f docker-compose.client.yml exec backend"
$C python -m scripts.remove_db_persisted_setup_secrets                          # report (dry run, no values printed)
$C python -m scripts.remove_db_persisted_setup_secrets --export-env <path>      # write KEY=value lines to a 0600 file
# add the lines to the host .env, then: docker compose -f docker-compose.client.yml up -d
$C python -m scripts.remove_db_persisted_setup_secrets --rewrap-k8s-keys --yes  # re-wrap Kubernetes credential keys
$C python -m scripts.remove_db_persisted_setup_secrets --purge --yes            # verify, then remove the database copies
# finally set REQUIRE_EXTERNALIZED_SECRETS=true in .env and run up -d again
```

The export path must be on a volume mounted into the backend container; delete the export file once the values are in your secret store. Database backups taken before the purge still contain the key — if any may have left your control, rotate it (below).

### Rotate the credential key

`CLOUD_ENCRYPTION_KEY_PREVIOUS` holds old key value(s), comma-separated, used only to decrypt while stored credentials are re-encrypted under the new key (including Kubernetes cluster credential keys derived from it):

1. Generate a new key: `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
2. In `.env`, set `CLOUD_ENCRYPTION_KEY=<new>` and `CLOUD_ENCRYPTION_KEY_PREVIOUS=<old>`, then `docker compose -f docker-compose.client.yml up -d`.
3. Dry run, then apply:
   ```bash
   docker compose -f docker-compose.client.yml exec backend python -m scripts.reencrypt_credentials
   docker compose -f docker-compose.client.yml exec backend python -m scripts.reencrypt_credentials --apply --yes
   ```
4. Re-run the dry run until it reports 0 tokens under the old key and 0 old-key data keys, then remove `CLOUD_ENCRYPTION_KEY_PREVIOUS` and run `up -d` again.

## Audit trail integrity

Every mutating API call is appended to a per-team, hash-chained audit trail; compliance control history and authentication events are chained too. `GET /api/audit-trail/verify` reports whether a chain is intact, edited or truncated — see [Audit Trail](../authentication/audit-trail.md).

- Set a dedicated `AUDIT_CHAIN_HMAC_KEY` (for example `openssl rand -hex 32`). If it is unset the key is derived from `SECRET_KEY`, so rotating `SECRET_KEY` would rotate the audit key too. To rotate, move the old value to `AUDIT_CHAIN_HMAC_KEY_PREVIOUS` and restart every backend and worker container.
- **External head witness (opt-in, off by default).** Someone with database write access can wipe the newest entries and leave nothing in the database to contradict it. A witness keeps a signed copy of each chain's head outside the database, every 15 minutes:
  - `AUDIT_HEAD_WITNESS_DIR=/path` — append-only JSON-lines files. The shipped compose file does not mount a witness directory: add the same mount to `backend` (verify reads it) and `celery-worker` (the task writes it) in an extra compose file passed with a second `-f`, ideally on a remote or append-only (`chattr +a`) mount; a witness on the database host's own disk only protects against someone who has the database but not the host. Files rotate every `AUDIT_HEAD_WITNESS_SEGMENT_LINES` lines (default 5000).
  - `AUDIT_HEAD_WITNESS_SYSLOG=udp://host:514` (or `tcp://host:port`) — one RFC 5424 line per chain per run to your SIEM; compare there and alert when a chain's `seq` goes down.

  Without a witness, verify says so in its `disclosures`.

## API worker processes

The backend runs one API process by default (`WEB_CONCURRENCY=1`), so one slow PDF render or aggregation can delay other requests. `WEB_CONCURRENCY=auto` (`min(4, CPU limit)` — 2 with the shipped `cpus: '2.0'`) or an explicit count runs several uvicorn workers; schedulers stay leader-elected to one process and shared state (rate limits, MFA challenges, scan bookkeeping) lives in Redis. Each worker is a full copy of the app (~0.5–1 GB): keep `WEB_CONCURRENCY` × 1 GB under the backend's 4 GB memory limit. Multi-worker mode is built but has not been validated on every deployment shape — enable it deliberately and watch memory after `docker compose -f docker-compose.client.yml up -d backend`.

## Agentic fix services (opt-in)

The agentic fix pipeline is **off by default** (`AGENTIC_FIX_ENABLED=false`, `AGENTIC_FIX_RUNNER=none`) and its four services start only under the `agentic-fix` compose profile:

| Service | Role |
| --- | --- |
| `celery-fix-worker` | Runs fix jobs, one at a time; holds no Docker socket |
| `agent-launcher` | Starts each sandbox container on the fix worker's behalf; set `AGENT_LAUNCHER_TOKEN` in `.env` |
| `agent-sandbox` | Pull-only image the launcher runs per job, on an internal network with no route out |
| `agent-egress` | The sandboxes' only exit; allows `AGENT_EGRESS_ALLOW` (default the Anthropic and OpenAI APIs and PyPI) |

```bash
docker compose -f docker-compose.client.yml --profile agentic-fix pull
docker compose -f docker-compose.client.yml --profile agentic-fix up -d
```

Enabling it also needs `AGENTIC_FIX_ENABLED=true`, `AGENTIC_FIX_RUNNER=sandbox`, an LLM provider, and a per-team opt-in. See [Agentic fixes](../security-scanning/code/agentic-fixes.md).

## What needs outbound access

| Destination | Why | If blocked |
| --- | --- | --- |
| `ghcr.io`, Docker Hub | Platform images; scanner images (ZAP, Nuclei, Prowler, testssl.sh) on first use | Pre-pull or mirror to an internal registry and point `GHCR_OWNER` / image references at it |
| Trivy and Grype vulnerability databases, Nuclei templates | Container, dependency and template-based scans stay current | Scans run on the bundled databases and age; mirror updates |
| Threat feeds (`cisa.gov`, `abuse.ch`, `otx.alienvault.com`, Blocklist.de, Spamhaus, OpenPhish) | Threat intelligence, KEV-based prioritization | Feeds show *degraded*; import indicators via STIX instead |
| `api.first.org` (EPSS), `services.nvd.nist.gov` (NVD) | Exploit-probability and CVSS enrichment | Findings carry less enrichment |
| `api.osv.dev` and OSV advisory data | Fixed versions for Linux host packages in Endpoint Security **Fix first**; dependency enrichment | Host CVEs show "fix data pending" or the last cached advisories |
| `api.deps.dev` | Licence enrichment for code scans | More components show an unknown licence |
| Cloud provider APIs (AWS, Azure, GCP) | Cloud posture scans, asset discovery | Those modules cannot run |
| Your SCM (GitHub, GitLab, Bitbucket, Azure DevOps) | Code scans, fix PRs | Use an internal SCM the host can reach |
| LLM provider (Anthropic, OpenAI, Google) — optional | AI features; Knowledge Base embeddings; the agentic fix sandbox via `agent-egress` | Everything else works in rule-based mode |
| Let's Encrypt — optional | Automatic TLS | Bring your own certificate / proxy |
| `registry.community.greenbone.net` — only with the bundled Greenbone stack | Greenbone engine and vulnerability-feed images | The bundled stack cannot load its feed; mirror the images |
| S3-compatible backup storage — optional | Off-host backups | Backups stay on the host's disk |
| Your SMTP relay, Slack / Teams / PagerDuty / Jira endpoints | Notifications and integrations | Configure what you have |

Wazuh and Greenbone OpenVAS are reached on your own network, not the internet. Nothing about your findings is sent to Offload Security. Support works from logs and exports you choose to share.

## Health

| Endpoint | Use |
| --- | --- |
| `GET /api/health` · `GET /api/health/live` | Liveness for load balancers |
| `GET /api/health/ready` | Readiness — what the backend container's health check uses |
| `GET /api/health/status` | Component summary without authentication: backup, secret storage and more; `overall_status` turns `degraded` when one is not healthy |

`docker compose -f docker-compose.client.yml ps` shows per-service health checks. Prometheus, Grafana and Alertmanager are available as an optional overlay (`docker-compose.client-observability.yml`); backup alerts such as `BackupMissed` route only when it runs. The platform's own scheduler and fleet-health sweeps recover stuck scans without it.

## Related

- [Platform Administration](../authentication/platform-administration.md) — the administrator account, Platform Setup, menu settings.
- [Production configuration](../adoption/production-configuration.md) — tuning and hardening checklist.
- [Release notes 1.4.0](../release-notes/v1-4-0.md) — upgrade notes for this release.
- [Troubleshooting & FAQ](./troubleshooting.md) — the failures operators actually hit.
