---
title: "On-Premises Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 7
description: "The failures operators hit on-premises — a private target refused as SSRF, a Docker socket proxy that will not start, Wazuh and OpenVAS connections and syncs, feeds stuck at degraded behind a proxy, TLS that never issues, mail that never sends, backups that refuse to run, missing encryption keys — and answers to frequent questions about air-gapped installs and sizing."
---

# On-Premises Troubleshooting & FAQ

## Scanning internal targets

**"Target is not allowed: it targets a loopback, private/internal, or cloud-metadata address (SSRF protection)".**
Set `ALLOW_PRIVATE_SCAN_TARGETS=true` in `.env` and restart the backend **and** the workers (the worker runs the scan). Loopback, link-local and `169.254.169.254` stay blocked by design.

**The private hostname does not resolve.**
Scanner containers use the host's resolver. Make the host resolve internal names (or use IPs), then check `docker compose exec celery-scan-worker getent hosts portal.corp.local`.

**Scans of internal HTTPS sites fail on the certificate.**
A private CA is a TLS *finding*, not a scan failure, for web and TLS assessments. For integrations and mail, set `INTEGRATION_VERIFY_SSL` / `SMTP_CA_CERT` or paste the CA into the tool's `ca_cert` field.

**Scans queue forever / "no worker".**
The queue worker for that scan type is down or cannot reach Redis. Check `docker compose -f docker-compose.client.yml ps` for `celery-worker` (scan orchestration, native scans, syncs), `celery-scan-worker` (cloud scans, discovery), `celery-code-worker` (code, Kubernetes, container images) and `celery-long-worker` (App Scan / DAST and other long scans); logs with `docker compose -f docker-compose.client.yml logs --tail 200 <service>`. Stuck runs are reaped by the fleet-health sweeps and re-queued.

**Every Docker-backed scan fails; `docker-socket-proxy` restarts in a loop or is unhealthy.**
The workers reach Docker only through `docker-socket-proxy`. Check, in order: `DOCKER_GID` in `.env` matches `stat -c '%g' /var/run/docker.sock` (the default 996 is often wrong); `deployment/docker-socket-proxy/haproxy.cfg` exists next to the compose file and is world-readable (`chmod 644`); on SELinux hosts it carries `container_file_t`. Then `docker compose -f docker-compose.client.yml up -d --force-recreate docker-socket-proxy`.

**A scan is refused with a Docker API error after an upgrade.**
The release changed the proxy allowlist but the proxy still runs the old one — HAProxy reads `haproxy.cfg` only at start. Recreate it with `--force-recreate docker-socket-proxy`.

## Wazuh and OpenVAS

**Wazuh test: Manager OK, Indexer unreachable.**
Single-node Wazuh: leave the indexer fields blank (Manager host on 9200 is assumed). Split: fill `indexer_host` / port / credentials. Accepting the warning syncs agents only; alerts and vulnerabilities stay empty.

**Wazuh syncs time out, or panels say "not read — the sync ran out of time".**
The Wazuh server is usually overloaded (indexer heap, too many shards, alert volume). Open **Endpoint Security → Health** for the server's own findings and the noise advisor; the next sync retries.

**The bundled Wazuh manager will not start: "Set WAZUH_API_PASSWORD".**
Set `WAZUH_API_PASSWORD` in `.env` (8–64 characters with upper, lower, digit and symbol), or run `scripts/setup/docker-setup.sh --reconfigure` to generate one. If the API port fails to bind, `WAZUH_BIND` does not match the host's docker0 address (`ip -4 addr show docker0`).

**OpenVAS test fails on the port.**
The platform speaks GMP over TLS on **9390**. Port 9392 is Greenbone's web interface, which has no GMP; change the saved connection to 9390. Before 1.4.0 the integration only signed in to the web interface and imported nothing.

**OpenVAS: "The server's TLS certificate is not trusted".**
Paste the Greenbone server's certificate into the integration's **Ca Cert** field instead of turning off verification. For the bundled stack: `docker compose -f docker-compose.openvas.yml exec gmp-tls sed -n '/BEGIN CERT/,/END CERT/p' /certs/gmp.pem`.

**OpenVAS findings arrive without CVEs.**
On a fresh Greenbone install, restart `gvmd` once after the first feed load finishes: `docker compose -f docker-compose.openvas.yml restart gvmd`.

**OpenVAS sync marked "partial"; nothing resolves.**
More than 10,000 results in the tasks' latest reports, or a read failed. A partial read never resolves findings by design; split large tasks in Greenbone.

**Endpoint Security tab is missing from Infra Command Center.**
It appears once a Wazuh connection exists for the *active* team. Connect Wazuh, then reload.

## Egress, proxies and air gaps

**Threat feeds stay *degraded*; Trivy / Grype say the database is old.**
Both need outbound HTTPS from the worker containers. Behind a proxy, set `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` in the compose environment for the backend and workers. Without egress, import indicators via STIX and mirror the vulnerability databases into an internal registry on your own schedule.

**`docker compose pull` cannot reach `ghcr.io`.**
Log in with the read-only token from onboarding; behind a proxy configure the Docker daemon's proxy, not only the shell. Air-gapped sites pull on a connected host, `docker save` / `docker load`, and point the compose file at an internal registry.

**LLM features say "AI features are not available".**
Expected without egress to the provider. Everything else — feeds aside — works in rule-based mode.

## TLS, mail, identity

**Let's Encrypt never issues a certificate.**
`certbot` needs port 80 reachable from the internet for the HTTP challenge and `DOMAIN_NAME` to resolve to this host. Internal-only installs: leave `DOMAIN_NAME` empty and terminate TLS on your own proxy in front of port 3000 / 80.

**Invitations and password-reset links are not delivered.**
Platform mail is `SMTP_*` in `.env` or the Platform Setup Email step; the SMTP step's test authenticates to the relay. Until it works, the platform administrator can issue reset links directly from User Activity.

**SSO redirect lands on an error.**
The redirect URI registered at the provider must be `<PUBLIC_APP_URL>/api/auth/sso/callback`, and `PUBLIC_APP_URL` must be the URL users actually type (HTTPS if they use HTTPS). See [Signing In & Sessions](../authentication/session-management.md#single-sign-on-oidc).

## Data and upgrades

**After a restore, integrations and cloud accounts show decryption errors.**
Stored credentials are encrypted under `CLOUD_ENCRYPTION_KEY` / `INTEGRATION_ENCRYPTION_KEY`, which live in `.env`, not in the backup. Restore the `.env` that was in use when the data was written (installs migrated from an older release may still have a copy in the dump; see [Encryption keys](./deployment.md#encryption-keys)). Without the keys, re-enter the credentials.

**Saving credentials fails with "Encryption key not found", or the setup status says keys are missing from the host environment.**
The wizard's generated keys were never pasted into the host `.env`, or the stack was not recreated afterwards. Add the `KEY=value` lines and run `docker compose -f docker-compose.client.yml up -d` (`restart` does not re-read `.env`).

**The backend logs `LEGACY SECRET STORAGE` at CRITICAL on every start.**
Root keys still exist only in MongoDB from an older setup wizard. Move them out with `scripts.remove_db_persisted_setup_secrets` — see [Keep keys out of the database](./deployment.md#keep-keys-out-of-the-database).

**The `backup` service logs a failure and `/api/health/status` shows backup `failing` or `never_run`.**
Usually `BACKUP_AGE_RECIPIENT` is not set: the service refuses to write unencrypted backups. Set it to your age public key and run `docker compose -f docker-compose.client.yml up -d backup`; check with `docker compose -f docker-compose.client.yml logs backup`.

**Data disappears sooner than the documented retention.**
Old `*_RETENTION_DAYS=90|180|365` lines from an earlier `.env.example` override the 1.4.0 defaults. Remove them and recreate the stack; `GET /api/scan-retention/policies` lists any value still below its default under `overrides_below_promise`.

**MongoDB is using more memory than the host has.**
`MONGO_MEM_LIMIT` (6 GB) and `MONGO_WT_CACHE_GB` (3) are defaults for a 16 GB host; lower both together on smaller hosts.

**An upgrade left a scan mid-run.**
Expected; running scans are re-queued or reaped after the workers restart. Take a backup before every upgrade.

**`docker compose` refuses to start: "Set IMAGE_TAG in .env" (or `GHCR_OWNER`, `MONGO_ROOT_PASSWORD`, `REDIS_PASSWORD`, `SECRET_KEY`, `WEBHOOK_SECRET`).**
These are required from 1.4.0; there is no `latest` default. Set them in `.env`.

## Frequently asked questions

**Can the platform run fully air-gapped?**
The platform itself, yes — images loaded from an internal registry, no LLM provider, feeds imported via STIX, vulnerability databases mirrored. Cloud modules need reachability to the cloud provider APIs by definition, and Endpoint Security's Fix first shows fixed versions for Linux packages only from cached or reachable OSV advisories.

**Can the platform patch hosts for us?**
No. Fix first shows which package upgrade resolves which CVEs and the command to run; applying it is done on the host or through your own patch tooling.

**What sizes should I plan?**
4 vCPU / 16 GB / 100 GB serves a team scanning a handful of accounts, a few clusters and a few hundred images comfortably; container-image and DAST volume drives memory on the workers, and MongoDB grows with retention (`*_RETENTION_DAYS`, 730 days for scans and findings by default) and with local backups when no backup bucket is set.

**Is high availability supported?**
The compose stack is single-host. For HA, run MongoDB and Redis as external managed or replicated services (`MONGO_URL`, `CELERY_BROKER_URL`) and place the stateless services behind your load balancer; scope it with your implementation team.

**Does Offload Security see my data for support?**
No. Support works from logs and exports you choose to share; there is no telemetry channel from your install to Offload Security.

**Can I run scanners on another network segment than the platform?**
Not as a separate remote agent today. The workers run on the platform host, so the host needs a route to what it scans; a second, independent install per isolated segment is the pattern until remote workers exist.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers sign-in and module-level problems. When contacting support include `docker compose ps`, the failing service's last 200 log lines, the image tag, and — for scan problems — the scan id and target type (never the target's credentials).
