---
title: "SonarQube Integration"
sidebar_label: "SonarQube"
sidebar_position: 6
description: "Connect a SonarQube server to keep a per-team snapshot of its projects and open vulnerability issues alongside the platform's own code-security results — what is synced, how often, where to read it, and what is deliberately not imported."
---

# SonarQube Integration

Connect **SonarQube** and the platform keeps a current **snapshot** of what SonarQube knows about your code — the projects it analyses and the open vulnerability issues it has raised — next to the platform's own SAST, secrets, dependency and IaC results. It is a *pulls data in* integration: the connection test and every sync talk to your SonarQube server; SonarQube itself is never changed.

## What is synced

Every sync (the 30-minute global sync, or **Sync now** on the card) pulls, with the token you configured:

| SonarQube data | Snapshot content |
| --- | --- |
| **Projects** | Up to 100 projects visible to the token — key, name, last analysis |
| **Open vulnerability issues** | Up to 100 open issues of type *Vulnerability* at severity *Critical* / *Major* — rule, severity, project, component and line, message |

The snapshot is stored per team with counts and a `synced_at` time; the card shows *Connected & healthy* with the last sync.

**Where to read it:** `GET /api/integrations/data/sonarqube` returns the latest snapshot (`counts.projects`, `counts.issues`, `data.projects[]`, `data.issues[]`). It is a JSON view for dashboards and scripts; there is no dedicated SonarQube screen yet.

:::note[What is deliberately not done]
SonarQube issues are **not imported as platform findings** — they do not appear in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx), are not deduplicated against the platform's own SAST results and do not create alerts or tickets. The platform runs its own SAST / secrets / SCA / IaC engines on your repositories (see [Code Security](../security-scanning/code/index.md)); the SonarQube snapshot is context, not a second finding source. Treat the badge literally: *pulls data in*, as a snapshot.
:::

## Connect

**Integrations → SonarQube → Connect.**

| Field | Value |
| --- | --- |
| `server_url` | Your SonarQube server, e.g. `https://sonar.example.com` |
| `token` | A SonarQube **user token** (My Account → Security) with *Browse* on the projects you want in the snapshot |
| `project_key` *(optional)* | Restrict the snapshot to one project |
| `verify_ssl` · `ca_cert` *(optional)* | TLS verification and a private CA certificate for on-premises servers |

The connection test authenticates against the server before anything is saved. SonarQube Cloud works the same way with an organisation token; a server on a private network needs the platform deployed where it can reach it, or `ALLOW_PRIVATE_SCAN_TARGETS=true` on an on-premises install — see [On-Premises](../on-premises/index.mdx).

## Related

- [Code Security](../security-scanning/code/index.md) — the platform's own code scanners and where their findings go.
- [Connecting Tools](./connecting-tools.md) — the wizard, sync and health checks.
- [Integration Catalog](./third-party.md) — every tool and its capability.
