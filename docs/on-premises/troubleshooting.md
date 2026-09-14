---
title: "On-Premises Troubleshooting & FAQ"
sidebar_label: "Troubleshooting & FAQ"
sidebar_position: 7
description: "The failures operators hit on-premises — a private target refused as SSRF, a worker that cannot start scanner containers, feeds stuck at degraded behind a proxy, TLS that never issues, mail that never sends, a restore that loses encrypted credentials — and answers to frequent questions about air-gapped installs and sizing."
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
The queue worker for that scan type is down or cannot reach Redis. `docker compose ps` for `celery-scan-worker` (web / API / network), `celery-worker` (cloud, K8s, container), `celery-code-worker`; logs with `docker compose logs --tail 200 <service>`. Stuck runs are reaped by the fleet-health sweeps and re-queued.

**Container / DAST scans fail with "permission denied" on the Docker socket.**
Workers need `/var/run/docker.sock` mounted read-only and the container user in the socket's group. On hardened hosts (rootless Docker, SELinux) map the socket group id into the compose file.

## Wazuh and OpenVAS

**Wazuh test: Manager OK, Indexer unreachable.**
Single-node Wazuh: leave the indexer fields blank (Manager host on 9200 is assumed). Split: fill `indexer_host` / port / credentials. Accepting the warning syncs agents only.

**OpenVAS test fails on the default port.**
Older builds pre-filled 9390 (the GMP TLS socket); the platform signs in to the Greenbone web API on **9392**. Fixed in the current release — set 9392 if your saved connection still says 9390.

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
Stored credentials are encrypted under the keys the setup wizard generated. They must be restored with the database — from `.env` (if you copied them there as the wizard instructed) or from the `platform_config` document in the dump. Without them, re-enter the credentials.

**MongoDB is using more memory than the host has.**
`MONGO_MEM_LIMIT` (6 GB) and `MONGO_WT_CACHE_GB` (3) are defaults for a 16 GB host; lower both together on smaller hosts.

**An upgrade left a scan mid-run.**
Expected; running scans are re-queued or reaped after the workers restart. Take a backup before every upgrade.

## Frequently asked questions

**Can the platform run fully air-gapped?**
The platform itself, yes — images loaded from an internal registry, no LLM provider, feeds imported via STIX, vulnerability databases mirrored. Cloud modules need reachability to the cloud provider APIs by definition.

**What sizes should I plan?**
4 vCPU / 16 GB / 100 GB serves a team scanning a handful of accounts, a few clusters and a few hundred images comfortably; container-image and DAST volume drives memory on the workers, and MongoDB grows with retention (`*_RETENTION_DAYS`).

**Is high availability supported?**
The compose stack is single-host. For HA, run MongoDB and Redis as external managed or replicated services (`MONGO_URL`, `CELERY_BROKER_URL`) and place the stateless services behind your load balancer; scope it with your implementation team.

**Does Offload Security see my data for support?**
No. Support works from logs and exports you choose to share; there is no telemetry channel from your install to Offload Security.

**Can I run scanners on another network segment than the platform?**
Not as a separate remote agent today. The workers run on the platform host, so the host needs a route to what it scans; a second, independent install per isolated segment is the pattern until remote workers exist.

## Still stuck?

The platform-wide [Troubleshooting](../troubleshooting.md) page covers sign-in and module-level problems. When contacting support include `docker compose ps`, the failing service's last 200 log lines, the image tag, and — for scan problems — the scan id and target type (never the target's credentials).
