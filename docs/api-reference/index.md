---
title: "API Reference"
sidebar_label: "Overview"
sidebar_position: 1
description: "Integrate with Offload Security programmatically — authentication, conventions, and task-oriented guides for cloud accounts, Kubernetes, scans, alerts, and vulnerabilities."
---

# API Reference

Everything you can do in the Offload Security UI, you can do over its REST API —
onboard cloud accounts and Kubernetes clusters, trigger scans, pull findings and
vulnerabilities, read or act on alerts, manage compliance evidence, drive
integrations and administer teams. This section gets you from zero to a working
integration and points you to the per-module endpoint pages.

## Base URL

Every endpoint is served under the `/api` prefix on your Offload Security host:

```
https://<your-offload-host>/api
```

The examples below use a shell variable so you can copy‑paste:

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"   # see Authentication
```

## Interactive reference (Swagger)

The platform ships a **live, always‑current** interactive API explorer generated
from the running server:

| What | URL |
| --- | --- |
| Swagger UI (try requests in the browser) | `https://<your-offload-host>/api/docs` |
| ReDoc (clean reference view) | `https://<your-offload-host>/api/redoc` |
| OpenAPI schema (JSON — import into Postman/Insomnia/codegen) | `https://<your-offload-host>/api/openapi.json` |

Use the Swagger UI for the **exhaustive** endpoint list and to experiment. This
documentation focuses on **authentication, conventions, and the common
workflows** — the things Swagger alone doesn't explain.

## Quick start

1. **[Create an API key](./authentication.md)** in the platform and send it as the `X-API-Key` header.
2. Make your first call — list vulnerabilities:

```bash
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?limit=5" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

3. Explore the task guides below.

## What you can do

This section holds the **cross-cutting** material — keys, conventions, end-to-end workflows — and deep dives on the most-automated surfaces. Every product section also has its own **API page** listing that module's endpoints with the permission each needs; those are the exhaustive per-area references.

### Cross-cutting

| Guide | Covers |
| --- | --- |
| **[Authentication](./authentication.md)** | Create & manage API keys, scopes, presets, rotation, IP allowlists |
| **[Conventions](./conventions.md)** | Response shapes, pagination, errors, rate limits, IDs and timestamps |
| **[Workflows](./workflows.md)** | End-to-end recipes: onboard an account and pull findings, onboard a cluster, triage alerts, export to a SIEM, gate CI |

### By product area

| Area | API page | Also in this section |
| --- | --- | --- |
| Cloud Security — accounts, scans, findings, assets, identity & network, events, remediation | [Cloud Security API](../cloud-security/api.md) | [Cloud Accounts](./cloud-accounts.md) |
| App & Infrastructure Scanning — web / API / network scans, code, containers, Kubernetes, CI/CD | [Scanning API](../security-scanning/api.md) | [Scans & Results](./scans-and-results.md) · [Kubernetes](./kubernetes.md) |
| Vulnerabilities & Risk — occurrences, triage, SLAs, alerts, risk register | [Vulnerabilities & Risk API](../vulnerability-risk/api.md) | [Vulnerabilities](./vulnerabilities.md) · [Alerts](./alerts.md) |
| Compliance & GRC — frameworks, scores, evidence, assessments, audit reports, DPDP | [Compliance & GRC API](../compliance/api.md) | |
| Reports & AI — executive dashboard, scheduled reports, exports, assistant, LLM providers | [Reports & AI API](../reports-and-ai/api.md) | |
| Integrations — catalog and wizard, notifications, Slack routing, webhooks, Jira | [Integrations API](../integrations/api.md) | |
| AI & Threat Intelligence — feeds, indicators, Command Center agents, AI governance, AIBOM, Knowledge Base | [AI & Threat Intelligence API](../ai-threat-intelligence/api.md) | |
| Platform Security — sign-in, MFA, SSO, teams, API keys, audit trail, platform admin | [Platform Security API](../authentication/api.md) | [Authentication](./authentication.md) |
| CI/CD — trigger scans and gate builds | [CLI & CI/CD](../cli-and-cicd.md) | [Workflows § 5](./workflows.md) |

For anything not on those pages, the live [Swagger UI](#interactive-reference-swagger) is generated from the running server and is always complete.

## Conventions at a glance

- **Auth:** `X-API-Key: <key>` (recommended for automation) or `Authorization: Bearer <session-token>`.
- **Content type:** `application/json` for request bodies.
- **Multi‑tenancy:** every call is scoped to the API key's team — you only ever see your team's data.
- **IDs:** resources use prefixed IDs (`osk_…` API keys, `clus_…` clusters, `occur_…` vulnerability occurrences, `alert_…` alerts).

:::note[Response shapes vary by endpoint]
Most endpoints wrap results in a `{ "success": true, "data": … }` envelope, but a
few return the payload directly. Each guide shows the **actual** response for that
endpoint, and [Conventions](./conventions.md) explains the patterns. When in
doubt, check the live [Swagger UI](#interactive-reference-swagger).
:::
