---
title: "1.4.1-beta.5 Release Notes"
sidebar_label: "1.4.1-beta.5"
slug: "/release-notes/1.4.1-beta.5"
description: "Offload Security 1.4.1-beta.5 (13 November 2026, pre-release): credentialed OpenVAS scans, a Python dependency update that fixes CVE-2026-49272, and a new base image with fresh vulnerability databases."
---

# 1.4.1-beta.5 Release Notes

**Released:** 13 November 2026 · **Type:** Pre-release · **Image tag:** `1.4.1-beta.5` · **Previous pre-release:** [1.4.1-beta.4](./v1-4-1-beta-4.md) · **Built on:** 1.4.0

:::caution[Pre-release]
This beta is for testing, not for production. Credentialed scans are tested only against a simulated Greenbone; see [Known issues](#known-issues). The documentation pages describe 1.4.0 and may not yet cover what is new here.
:::

This beta is 1.4.1-beta.4 plus the two changes that were still in review then: credentialed OpenVAS scans and the Python dependency update. **If you skipped beta.4, read [its notes](./v1-4-1-beta-4.md) too.** Its upgrade notes (scanner networking, ECR, OpenVAS, change monitoring) all still apply.

## Install or upgrade

All six images are tagged `1.4.1-beta.5`. Download the one-file installer from the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.5). It uses the deploy files from this tag. Then run:

```bash
sudo bash offload-install-1.4.1-beta.5.sh --domain <your-domain>
```

Check the installer's SHA-256 before you run it: `2278d2299dfeb9fc081f8b1e8d5c86171bec5284dc1f6449a27c6d02309f8306`.

`/api/health` still reports `1.4.0`, because the version file is not changed for betas. Go by the image tag.

## Highlights

### Credentialed OpenVAS scans

- **Scan credentials:** store SSH, SMB, SNMP v2c/v3 and ESXi credentials for a team. Each secret is encrypted, and it is never shown again or written to logs.
- **Login result per host:** each host shows *authenticated*, *login failed* or *unauthenticated*.
- **A failed login does not close findings.** When a host's login fails, its earlier local-check findings stay open. Before, they were marked as fixed.
- **Package details:** package CVEs found by a local check now show the installed and the fixed package version.
- **Edit & re-run** repeats a scan setup.

### Python dependency update

About 120 minor and patch upgrades, including starlette 1.9, fastapi 0.141.1, pydantic 2.14.1, google-auth 2.62, litellm 1.100.4 and portalocker 4.4.1. It includes **oauthlib 4.0.1**, which fixes CVE-2026-49272 (High).

### Fresh vulnerability databases

The images use a new base image with the Trivy and Grype databases baked in again, so air-gapped installs can run Trivy scans.

## Upgrade notes

| Change | What to do |
| --- | --- |
| **Credentialed scans need `CLOUD_ENCRYPTION_KEY`** | Scan credentials are encrypted with the platform encryption key. The installer already generates it. On a hand-built `.env` without it, storing a scan credential is refused (HTTP 503) and nothing is saved. Scans without credentials are not affected. See [Encryption keys](../on-premises/deployment.md#encryption-keys). |
| **Credentials are copied to Greenbone** | Each stored credential is pushed to Greenbone as an `offload: …` credential. Deleting it in Offload clears the secret at once and scrubs or deletes the Greenbone copy. |
| **Larger first pull** | The backend and fix-worker images use the new base image, so the first pull after upgrading is bigger. |

## Known issues

- **Not tested against live services:**
  - **Credentialed scans** are tested only against a simulated Greenbone. On a beta instance, check: SSH with a password and with a key, SMB, a deliberately wrong password, SNMP, and deleting a credential.
  - **Carried over from beta.4:** the OpenVAS scan launch, ECR sign-in and bridge networking for scanner containers.
- **Areas to watch after the dependency update:** Checkov and Bandit scans, the AI fix worker, background tasks (starlette 1.9) and log rotation (portalocker). If one of them breaks, report it, so that package can be pinned back to its earlier version.

The full commit list is in the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.5).
