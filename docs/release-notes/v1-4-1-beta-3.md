---
title: "1.4.1-beta.3 Release Notes"
sidebar_label: "1.4.1-beta.3"
slug: "/release-notes/1.4.1-beta.3"
description: "Offload Security 1.4.1-beta.3 (9 November 2026, pre-release): security fixes from a full-repository scan, org-admin vs platform-admin roles, Container Quick Scan on the scan worker, fixes for 20 defects found on 1.4.0, and installer fixes."
---

# 1.4.1-beta.3 Release Notes

**Released:** 9 November 2026 · **Type:** Pre-release · **Image tag:** `1.4.1-beta.3` · **Previous pre-release:** [1.4.1-beta.1](./v1-4-1-beta-1.md) · **Built on:** 1.4.0

:::caution[Pre-release]
This beta is for testing, not for production. 1.4.1-beta.2 was not published.
:::

:::warning[Read the upgrade notes first]
Grafana needs a password, some kubeconfigs are now refused, and CI/CD API keys enforce IP allowlists and rotation. Read [Upgrade notes](#upgrade-notes).
:::

## Install or upgrade

Download the one-file installer from the [GitHub release](https://github.com/offloadsecurity/offload-cspm/releases/tag/v1.4.1-beta.3), check its SHA-256 (`a03654765d65674850cd46b3af7d4caa30e69a26802af344b788f6a86f9663f7`), then run:

```bash
sudo bash offload-install-1.4.1-beta.3.sh --domain <your-domain>
```

`/api/health` still reports `1.4.0` because the version file is unchanged for betas. Go by the image tag.

## Highlights

### Security fixes

From a full-repository security scan:

- A scanned repository's `.checkov.yaml` can no longer run code. Repository-supplied Checkov external checks are not honored.
- An uploaded kubeconfig can no longer run commands: `exec`, `auth-provider` and file-path credentials are refused at upload and at use.
- Path traversal and symlink tricks inside a scanned repository are confined to the scan workspace.
- Uploaded evidence can no longer render HTML or SVG inside the app.
- Assessment updates can no longer rewrite ownership or scores.
- Invitations can no longer create a platform administrator.

### Admin roles

Someone invited as an admin becomes an **organization admin**. Only the **platform administrator** (the first account) can enable modules, change tiers or reopen the setup wizard. See [Platform Administration](../authentication/platform-administration.md).

### Container Quick Scan works on customer installs

Quick Scan now runs on the scan worker instead of the API service, so it no longer fails with *Cannot connect to the Docker daemon*. See [Image Scanning](../security-scanning/containers/image-scanning.md).

### Fixes for 20 defects found on 1.4.0

- **Containers:** an honest risk score, scan-type label and posture trend.
- **Kubernetes:** Findings by Category shows categories; triage shows the cluster name.
- **Code:** partial npm resolution is a disclosed coverage gap, not a failed tool. The overview's severity donut matches the findings tile.
- **Triage:** package work items are keyed on the package name, so one CVE on one image is one work item. App Scan header findings have titles and correct severities.
- **Risk:** control scores, Next Due dates and the Untreated count are fixed.
- **Compliance:** manual overrides produce drift. Evidence freshness tiles add up to the total. Threshold alerts reach Teams. DPDP logs DPIA, SDF and vendor-assessment actions.
- **Executive dashboard:** Critical Gaps counts the full set.
- **Threat intelligence and AI:** the report format is honored and report times are in UTC. AI Governance coverage counts bias tests and assessments. The prompt-injection test is followed to completion. The Knowledge Base "AI Ready" chip needs a provider, and tags are shown.
- **KEV enrichment** works again.

### Installer

The installer now:

- sets the Docker group from the host's socket;
- generates an admin password the backend accepts;
- ships every file the compose files mount;
- keeps a backup of any config file you changed before replacing it;
- keeps the observability overlay running across upgrades.

## Upgrade notes

| Change | What to do |
| --- | --- |
| **Grafana needs a password** | Set `GRAFANA_ADMIN_PASSWORD` in `.env`. Without it only Grafana stays down. |
| **Kubeconfigs refused** | Kubeconfigs that use an `auth-provider` (gcp/oidc/azure), `exec` or file paths are refused. Re-upload a token or client-certificate kubeconfig. The cluster card shows **Kubeconfig refused**. |
| **CI/CD API keys** | Keys past their rotation grace stop working on `/api/cicd/*` and are revoked within the hour. IP allowlists are enforced there for the first time. Set `TRUSTED_PROXIES` behind nginx, or allowlisted keys may get 403. |
| **Risks merged under `vuln:unknown`** | They are not split automatically. In the backend container run `python scripts/repair_risk_unknown_dedup.py` (dry run), then with `--apply`. |
| **Setup wizard** | Reopening it is platform-admin only. To recover lost keys, restore them in the host `.env` and recreate the services. |

## Known issues

- **Trivy's baked vulnerability database had expired.** Workers download a fresh one, so Trivy scans need internet access until a newer base image. This was fixed in [beta.5](./v1-4-1-beta-5.md).
- **oauthlib 4.0.0 (CVE-2026-49272)** is in the image as a transitive dependency; the platform does not use it. Fixed in a later base image.

Full engineering record: `CHANGELOG.md` in the platform repository.
