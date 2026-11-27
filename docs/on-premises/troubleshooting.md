---
title: "On-Premises Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 7
description: "The failures operators hit on-premises — a private target refused as SSRF, a Docker socket proxy that will not start, Wazuh and OpenVAS connections, scans and syncs, installer warnings, quiet logs and API-key allowlists behind nginx, feeds stuck at degraded behind a proxy, TLS that never issues, mail that never sends, backups that refuse to run, missing encryption keys — and answers to frequent questions about air-gapped installs and sizing."
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
The queue worker for that scan type is down or cannot reach Redis. Check `docker compose -f docker-compose.client.yml ps` for `celery-worker` (scan orchestration, native scans, syncs, Docker housekeeping), `celery-maintenance-worker` (periodic sweeps, retention, notifications), `celery-scan-worker` (cloud scans, discovery), `celery-code-worker` (code, Kubernetes, container images) and `celery-long-worker` (App Scan / DAST and other long scans); logs with `docker compose -f docker-compose.client.yml logs --tail 200 <service>`. Stuck runs are reaped by the fleet-health sweeps and re-queued. `GET /api/health/integrity` (signed in) shows each queue lane under `scan_lanes`.

**Every Docker-backed scan fails; `docker-socket-proxy` restarts in a loop or is unhealthy.**
The workers reach Docker only through `docker-socket-proxy`. Check, in order: `DOCKER_GID` in `.env` matches `stat -L -c '%g' /var/run/docker.sock` (the default 996 is often wrong; the installer sets it on every run); `deployment/docker-socket-proxy/haproxy.cfg` and `create_guard.lua` exist next to the compose file and are world-readable (`chmod 644`); on SELinux hosts they carry `container_file_t`. Then `docker compose -f docker-compose.client.yml up -d --force-recreate docker-socket-proxy`.

**A scan is refused with a Docker API error after an upgrade.**
The release changed the proxy allowlist but the proxy still runs the old one — HAProxy reads `haproxy.cfg` and `create_guard.lua` only at start. Recreate it with `--force-recreate docker-socket-proxy`. The proxy also refuses some container creates by design (privileged, added capabilities, binds of protected host paths); the refusal names the reason.

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

**OpenVAS: starting or creating a scan fails with a Greenbone permission error.**
The Greenbone account in the integration has the **Observer** role, which can't create or start tasks. Give it the **User** role in Greenbone. In the platform, starting scans needs Run scans; editing, deleting, scheduling and credentialed scans need Manage scans.

**OpenVAS: a target is refused.**
Loopback, cloud-metadata and IPv4-in-IPv6 addresses are always refused. Private ranges are refused only if `OPENVAS_ALLOW_PRIVATE_TARGETS=false`. **Scan now** applies the same check to a task's existing targets.

**OpenVAS: saving a scan credential fails with HTTP 503.**
`CLOUD_ENCRYPTION_KEY` is missing from the host `.env`; nothing was saved. Add the key and recreate the stack. See [Encryption keys](./deployment.md#encryption-keys).

**OpenVAS: hosts show "Login failed" or "Login not confirmed".**
The credential was refused or Greenbone could not confirm the login, so only remote checks ran and the host is *Not assessed locally*. Its earlier local-check findings stay open. Check the account, password or key, the SSH port or SMB domain, and that the service is reachable from the Greenbone scanner, then use **Edit & re-run this scan setup**.

**OpenVAS: Edit or Delete is missing on a task.**
Only tasks created from the platform that are not running can be edited or deleted. Tasks created in Greenbone itself can only be started and stopped; Endpoint 360 host tasks can be deleted but not edited.

**OpenVAS: a scan finished but its findings are not in the platform yet.**
Finished scans are imported within `OPENVAS_COMPLETION_CHECK_MINUTES` (default 5), and by the 30-minute sync. With the Manage integrations permission, the Network VAPT page imports them at once when it sees the scan finish.

**Endpoint Security tab is missing from Infra Command Center.**
It appears once a Wazuh connection exists for the *active* team. Connect Wazuh, then reload.

## Installer

**The installer says the certificate request failed.**
The platform is running but HTTPS is not, so the UI is not reachable from outside. Point the domain at the server, open ports 80 and 443, and run the same installer again; re-runs keep `.env`.

**The installer warns that `DEFAULT_ADMIN_PASSWORD` fails the password rules, and sign-in returns 401.**
An older installer generated a password the backend rejects, so no admin was created. Set a stronger `DEFAULT_ADMIN_PASSWORD` in `.env` (12+ characters with upper, lower, digit and symbol; avoid `$`, `#` and quotes), then `docker compose -f docker-compose.client.yml up -d --force-recreate backend`. The backend creates the admin at startup only while it has no users; if sign-in already works, ignore the warning.

**The installer warns that `CLOUD_ENCRYPTION_KEY` / `INTEGRATION_ENCRYPTION_KEY` are blank.**
The keys may exist only in MongoDB from an older setup wizard. The installer never generates new ones on an upgrade. Export them as described in [Keep keys out of the database](./deployment.md#keep-keys-out-of-the-database).

**After an upgrade there are `*.bak-<tag>` files in the install directory.**
You had edited those deploy files; the installer kept your copies (mode 600) before replacing them. Carry your changes into the new files, or into `.env`, then run `up -d`.

## Logs, proxies and monitoring

**`docker compose logs` shows almost nothing.**
`LOG_LEVEL` defaults to `ERROR`, so only failures are logged. Set `LOG_LEVEL=INFO` in `.env` and run `docker compose -f docker-compose.client.yml up -d` while you troubleshoot; set it back afterwards.

**A CI/CD API key with an IP allowlist gets 403 on every request.**
Behind the bundled nginx the backend sees nginx's address, not your runner's, unless `TRUSTED_PROXIES` names nginx's exact address. See [Client addresses behind nginx](./deployment.md#client-addresses-behind-nginx). A key whose `last_used_ip` equals your proxy's address is the sign. Keys past their rotation grace also stop working on `/api/cicd/*` and are revoked within the hour; move the pipeline to the successor key.

**The observability overlay (Prometheus, Grafana, Alertmanager) refuses to start.**
`GRAFANA_ADMIN_PASSWORD` is not set; there is no shared default. The installer fills it in; on a manual install use `openssl rand -hex 16`. See [Upgrading to 1.4.1](./deployment.md#upgrading-to-141) for an existing Grafana.

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

**The `backup` service logs a failure and `/api/health/status` (signed in) shows backup `failing` or `never_run`.**
Usually `BACKUP_AGE_RECIPIENT` is not set: the service refuses to write unencrypted backups. Set it to your age public key and run `docker compose -f docker-compose.client.yml up -d backup`; check with `docker compose -f docker-compose.client.yml logs backup`.

**Data disappears sooner than the documented retention.**
Old `*_RETENTION_DAYS=90|180|365` lines from an earlier `.env.example` override the 1.4.0 defaults. Remove them and recreate the stack; `GET /api/scan-retention/policies` lists any value still below its default under `overrides_below_promise`.

**MongoDB is OOM-killed, or uses more memory than the host has.**
`MONGO_MEM_LIMIT` (8G) and `MONGO_WT_CACHE_GB` (3) are the defaults for a 16 GB host. Keep the cache at or below (limit − 1) ÷ 2, for example 3 in an 8G limit, because MongoDB also uses memory outside the cache. Values in `.env` override the defaults, so a `.env` that pins 4 with an 8G limit needs changing. Lower both together on smaller hosts. See [Memory and worker sizing](./deployment.md#memory-and-worker-sizing).

**Retention overrides set through the API are not applied.**
Before 1.4.1, `PUT /api/scan-retention/policies/{name}` changed only the API process's memory. From 1.4.1 the override is stored and the workers apply it; set it again after upgrading if it was lost on a restart.

**Old scan data takes several nights to be summarized and archived after upgrading.**
Expected. The nightly retention cycle now drains the backlog in batches up to a per-cycle budget (see [Data retention](./deployment.md#data-retention)); a backlog left by the old 100-documents-a-night limit clears over the following nights.

**An upgrade left a scan mid-run.**
Expected; running scans are re-queued or reaped after the workers restart. Take a backup before every upgrade.

**A Kubernetes scan waiting in the queue shows "Scan lost".**
From 1.4.1 a queued Kubernetes scan is not counted as lost until a worker has picked it up or its queue deadline passes: `K8S_SCAN_QUEUE_MAX_HOURS` (default 24) after it was queued. Raise it in `.env` if large fleet-wide scans wait longer.

**`/api/health` reports version 1.4.0 on a 1.4.1 beta.**
Expected: the version file is not changed for pre-releases. Go by the image tag (`IMAGE_TAG` in `.env`).

**`docker compose` refuses to start: "Set IMAGE_TAG in .env" (or `GHCR_OWNER`, `MONGO_ROOT_PASSWORD`, `REDIS_PASSWORD`, `SECRET_KEY`, `WEBHOOK_SECRET`).**
These are required from 1.4.0; there is no `latest` default. Set them in `.env`.

## Frequently asked questions

**Can the platform run fully air-gapped?**
The platform itself, yes — images loaded from an internal registry, no LLM provider, feeds imported via STIX, vulnerability databases mirrored. Each release's images carry Trivy and Grype databases from the image build, so container scans work offline, with findings as current as that build. Cloud modules need reachability to the cloud provider APIs by definition, and Endpoint Security's Fix first shows fixed versions for Linux packages only from cached or reachable OSV advisories. What works in each mode is in [Air-gapped, restricted-egress and connected installs](./deployment.md#air-gapped-restricted-egress-and-connected-installs).

**Can the platform patch hosts for us?**
No. Fix first shows which package upgrade resolves which CVEs and the command to run; applying it is done on the host or through your own patch tooling.

**What sizes should I plan?**
4 vCPU / 16 GB / 100 GB serves a team scanning a handful of accounts, a few clusters and a few hundred images comfortably; container-image and DAST volume drives memory on the workers, and MongoDB grows with retention (`*_RETENTION_DAYS`, 730 days for scans and findings by default) and with local backups when no backup bucket is set.

**Is high availability supported?**
The compose stack is single-host. For HA, run MongoDB and Redis as external managed or replicated services (`MONGO_URL`, `CELERY_BROKER_URL`) and place the stateless services behind your load balancer; scope it with your implementation team.

**Does Offload Security see my data for support?**
No. Support works from logs and exports you choose to share; the server sends nothing about your findings to Offload Security. One exception to note: the web UI loads PostHog analytics in users' browsers, which send usage analytics to PostHog's US region. Block `us.i.posthog.com` if your policy requires it; see [What needs outbound access](./deployment.md#what-needs-outbound-access).

**Can I run scanners on another network segment than the platform?**
Not as a separate remote agent today. The workers run on the platform host, so the host needs a route to what it scans; a second, independent install per isolated segment is the pattern until remote workers exist.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers sign-in and module-level problems. When contacting support include `docker compose ps`, the failing service's last 200 log lines, the image tag, and — for scan problems — the scan id and target type (never the target's credentials).
