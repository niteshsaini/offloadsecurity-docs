---
title: "1.4.1-beta.4 Release Notes"
sidebar_label: "1.4.1-beta.4"
slug: "/release-notes/1.4.1-beta.4"
description: "Offload Security 1.4.1-beta.4 (12 November 2026, pre-release): run OpenVAS scans from the platform, cloud change monitoring, ECR sign-in as the linked account, bridge networking for scanner containers, and the upgrade steps operators need."
---

# 1.4.1-beta.4 Release Notes

**Released:** 12 November 2026 · **Type:** Pre-release · **Image tag:** `1.4.1-beta.4` · **Previous pre-release:** 1.4.1-beta.3 · **Built on:** 1.4.0

:::caution[Pre-release]
This beta is for testing, not for production. It was built to be tested on a beta instance. Some features are tested only against simulated services, which are listed under [Known issues](#known-issues). The current documentation describes the latest pre-release, [1.4.1-beta.8](./v1-4-1-beta-8.md).
:::

:::warning[Read the upgrade notes first]
This beta changes how scanner containers reach the network. Read [Upgrade notes](#upgrade-notes) before upgrading, especially if you scan `localhost` targets or rely on instance-role sign-in.
:::

## Install or upgrade

All six images are tagged `1.4.1-beta.4`. Download the one-file installer from the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.4). It uses the deploy files from this tag. Then run:

```bash
sudo bash offload-install-1.4.1-beta.4.sh --domain <your-domain>
```

Check the installer's SHA-256 before you run it: `949917c454d0d5fc8c266b63b21f6174a22c9bb78098e02830c2af170cdc14c9`.

`/api/health` still reports `1.4.0`, because the version file is not changed for betas. Go by the image tag.

## Highlights

### Run OpenVAS scans from the platform

- **Infra Command Center → Network VAPT (OpenVAS):** start or stop existing Greenbone tasks, or create a new scan for hosts, IP addresses and CIDR ranges.
- **Endpoint 360:** each host shows its OpenVAS scan state and has a **Trigger Network VAPT scan** action.
- **Endpoint Security → OpenVAS coverage:** a new tab lists scanned, not scanned, in-progress and failed endpoints, with a coverage percentage. You can scan one host, a selection, or up to 100 unscanned hosts at a time.
- **Results** are imported within minutes of a scan finishing.
- **Vulnerability Management** has its own OpenVAS source tab and badge.

See [OpenVAS Vulnerability Scanning](../on-premises/openvas-scanning.md) for connecting Greenbone.

### Cloud change monitoring

The new **Changes** tab shows every cloud write event, who made it and whether it was expected. Unexplained changes raise alerts, and you can approve identities you know about. See [Cloud Events](../cloud-security/cloud-events.md).

### Containers and SBOM

- **ECR registries sign in as the linked AWS account**, with keys or an assumed cross-account role, and the account number is checked. The platform's own AWS identity is no longer used silently.
- **Container policy "Require signature"** is now verified with Cosign in both CI gates. Before, it was reported as not evaluated.
- **SBOM Reports** are shown as a repository → branch → report tree.

### Platform

- **Scanner containers no longer use host networking.** Prowler, nmap, nuclei, testssl, kube-hunter and kube-bench now use Docker bridge networking. kube-bench no longer runs with `--pid=host`, and the scan sidecars no longer get the host Docker socket.
- **nginx sees the real client IP behind a load balancer** when `NGINX_REAL_IP_FROM` is set.

## Upgrade notes

Take a backup before upgrading (see [Backups](../on-premises/deployment.md#backups)).

| Change | What to do |
| --- | --- |
| **Scanner networking** | `SCANNER_DOCKER_NETWORK` now defaults to `bridge`. This changes three things. **(1)** `localhost` or `127.0.0.1` in an nmap, nuclei or testssl target now means the scanner container, not the host. **(2)** Cloud scans that sign in with an instance role or managed identity (IMDS) may fail, because IMDSv2 with hop limit 1 does not reach a bridge container. **(3)** SBOM and container scans of images that exist only in the host's Docker store now need those images in a registry. To roll back, set `SCANNER_DOCKER_NETWORK=host` in `.env`. The Docker proxy still allows host networking by default. |
| **ECR sign-in** | A cross-account role with a wrong trust policy or external ID now fails outright. Keys that sign in to a different account than the linked one are refused. An ECR registry that only worked through the host's own AWS identity needs `CSPM_ALLOW_PLATFORM_IDENTITY=true` in `.env`. Set it only if this deployment scans its own AWS account. |
| **OpenVAS scan launch** | The Greenbone account Offload uses needs the **User** role, because an Observer account can't create or start tasks. Starting scans needs the Run scans permission. Private targets are allowed by default (`OPENVAS_ALLOW_PRIVATE_TARGETS=true`). Loopback, cloud-metadata and IPv4-in-IPv6 addresses are always refused. Finished scans are imported every `OPENVAS_COMPLETION_CHECK_MINUTES` minutes (default 5; 0 turns it off). |
| **Cloud change monitoring** | On first start the backend adds a unique index on change events. It removes the change record from duplicate rows and keeps the earliest. ECS services are now stored as `cluster/service`, so the first change to each service after the upgrade shows no previous change. |
| **Require signature** | CI gates whose policy requires a signature start one Cosign container per gate. Air-gapped installs need the pinned `COSIGN_IMAGE` available locally. |
| **Behind a load balancer** | Set `NGINX_REAL_IP_FROM` to the balancer's own subnets, never a whole VPC CIDR. `0.0.0.0/0` is refused. |

## Known issues

- **Trivy needs internet access.** The vulnerability database baked into the image expired on 2 November, and the base image is the same as in beta.3. Each new worker downloads a fresh database, so Trivy scans fail on offline or air-gapped installs. Fixed in [1.4.1-beta.5](./v1-4-1-beta-5.md).
- **oauthlib 4.0.0 (CVE-2026-49272, High)** is still in the image. The platform does not import it directly; it comes in through another dependency. Fixed in [1.4.1-beta.5](./v1-4-1-beta-5.md).
- **Not tested against live services:** the OpenVAS scan launch and ECR sign-in are tested only against simulated Greenbone and AWS. The new scanner networking has not run against real targets. These are the main things to check on a beta instance.
- **Not in this beta:** credentialed OpenVAS scans and the Python dependency update. Both are in [1.4.1-beta.5](./v1-4-1-beta-5.md).

The full commit list is in the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.4).
