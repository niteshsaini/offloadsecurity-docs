---
title: "API Reference"
sidebar_label: "Overview"
sidebar_position: 1
description: "Integrate with Offload Security programmatically: authentication, conventions, and task-oriented guides for cloud accounts, Kubernetes, scans, alerts, and vulnerabilities."
---

# API Reference

The Offload Security UI is built on a REST API. You can use the same API to
onboard cloud accounts and Kubernetes clusters, trigger scans, compare runs,
pull findings and vulnerabilities, and verify exported reports. This section
gets you from zero to a working integration and points you to the per-module
endpoint pages.

Two credentials exist, and they do not reach the same set of endpoints:

- **API keys** (`X-API-Key`) reach only the route families their scopes map to
  (scans, vulnerabilities, cloud, risks, reports, assessments, and the audit-trail
  SIEM export). Every other route refuses an API key with `403`.
- **Session tokens** (`Authorization: Bearer`) reach everything the signed-in
  user's team role allows, including alerts, webhooks and API key management.

See [Authentication](./authentication.md#what-an-api-key-can-reach) for the exact map.

## Base URL

Every endpoint is served under the `/api` prefix on your Offload Security host:

```
https://<your-offload-host>/api
```

The examples below use shell variables so you can copy and paste:

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"   # see Authentication
```

## Interactive reference (Swagger)

When enabled, the platform serves an interactive API explorer generated from
the running server. The UI assets are self-hosted under `/api/static/apidocs`,
so it works in air-gapped deployments.

| What | URL |
| --- | --- |
| Swagger UI (try requests in the browser) | `https://<your-offload-host>/api/docs` |
| ReDoc (reference view) | `https://<your-offload-host>/api/redoc` |
| OpenAPI schema (JSON, for Postman, Insomnia or codegen) | `https://<your-offload-host>/api/openapi.json` |

:::note[Off by default in production]
The schema, both UIs and their assets are controlled by `ENABLE_API_DOCS`. When
it is unset, they are on outside production and **off when
`ENVIRONMENT=production`**, which is the default in the client deployment. When
off, all four paths return `404`. To turn them on, set `ENABLE_API_DOCS=true` in
the backend environment and restart. The schema exposes the full route map, so
enable it only where that is acceptable.
:::

Where it is enabled, use Swagger UI for the exhaustive endpoint list. This
documentation focuses on authentication, conventions and common workflows.

## Quick start

1. **[Create an API key](./authentication.md)** in the platform and send it as the `X-API-Key` header.
2. Make your first call, listing vulnerability occurrences (needs the `vulnerabilities:read` scope):

```bash
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?limit=5" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

3. Explore the task guides below.

## What you can do

This section holds the cross-cutting material (keys, conventions, end-to-end
workflows) and deep dives on the most-automated surfaces. Every product section
also has its own **API page** listing that module's endpoints with the
permission each needs.

### Cross-cutting

| Guide | Covers |
| --- | --- |
| **[Authentication](./authentication.md)** | API keys, scopes, presets, what a key can reach, rotation, IP allowlists |
| **[Conventions](./conventions.md)** | Response shapes, pagination, errors, rate limits, IDs and timestamps |
| **[Workflows](./workflows.md)** | Recipes: onboard and scan an account, onboard and scan a cluster, triage alerts, export to a SIEM, gate CI, compare re-tests, pull the audit trail |

### By product area

| Area | API page | Also in this section |
| --- | --- | --- |
| Cloud Security: accounts, scans, findings, assets, identity and network, events, remediation | [Cloud Security API](../cloud-security/api.md) | [Cloud Accounts](./cloud-accounts.md) |
| App and Infrastructure Scanning: web, API and network scans, code, containers, Kubernetes, CI/CD | [Scanning API](../security-scanning/api.md) | [Scans & Results](./scans-and-results.md) · [Kubernetes](./kubernetes.md) |
| Vulnerabilities and Risk: occurrences, triage, risk exceptions, SLAs, alerts, risk register | [Vulnerabilities & Risk API](../vulnerability-risk/api.md) | [Vulnerabilities](./vulnerabilities.md) · [Alerts](./alerts.md) |
| Compliance and GRC: frameworks, scores, evidence, assessments, audit reports, DPDP | [Compliance & GRC API](../compliance/api.md) | |
| Reports and AI: executive dashboard, scheduled reports, exports, assistant, LLM providers | [Reports & AI API](../reports-and-ai/api.md) | |
| Integrations: catalog and wizard, notifications, Slack routing, webhooks, Jira | [Integrations API](../integrations/api.md) | |
| AI and Threat Intelligence: feeds, indicators, Command Center agents, AI governance, AIBOM, Knowledge Base | [AI & Threat Intelligence API](../ai-threat-intelligence/api.md) | |
| Platform Security: sign-in, MFA, SSO, teams, API keys, audit trail, platform admin | [Platform Security API](../authentication/api.md) | [Authentication](./authentication.md) |
| CI/CD: trigger scans and gate builds | [CLI & CI/CD](../cli-and-cicd.md) | [Workflows § 5](./workflows.md#5-trigger-a-scan-from-ci-and-fail-the-build-on-criticals) |

For anything not on those pages, the [Swagger UI](#interactive-reference-swagger)
is generated from the running server, where your administrator has enabled it.

## Conventions at a glance

- **Auth:** `X-API-Key: <key>` for automation, limited to the route families its scopes map to; or `Authorization: Bearer <session-token>` for everything the user's role allows.
- **Content type:** `application/json` for request bodies.
- **Tenancy:** every call is scoped to the caller's current team. You only see that team's data.
- **IDs:** opaque strings. Some carry a prefix (`osk_` API keys, `clus_` clusters, `alert_` alerts); cloud accounts and cloud scan runs use UUIDs. Do not parse them.

:::note[Response shapes vary by endpoint]
Most endpoints wrap results in a `{ "success": true, "data": … }` envelope, but
several return the payload directly (alerts, native scan results, cloud
accounts, Kubernetes clusters, native and cloud scan comparisons). Each guide shows the actual
response for its endpoints, and [Conventions](./conventions.md) explains the
patterns.
:::
