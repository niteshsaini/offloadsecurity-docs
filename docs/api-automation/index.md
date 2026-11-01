---
title: "API & Automation"
description: "How the Offload Security REST API works: authentication with API keys, the API reference, and what you can automate, from scans in CI to exports into a SIEM, ticketing or BI tool."
sidebar_label: "Overview"
sidebar_position: 0
---

# API & Automation

The Offload Security UI is backed by a **REST API**, so much of what you do by
clicking you can also do programmatically. Teams use the API to trigger scans
from a pipeline, pull findings into another system, provision cloud accounts,
export reports on a schedule, and feed security data into a SIEM, ticketing
system or BI dashboard.

This section explains how the API works, how to authenticate, and the common
automation patterns. For the pipeline-specific workflow (gating releases on
scan results), see **[CLI & CI/CD Integration](../cli-and-cicd.md)**.

## API basics

- **REST over HTTPS, JSON in and out.**
- **Base URL** is your platform instance, with routes under `/api/`, for example `https://security.yourcompany.com/api/...`. These pages write the instance address as `$OFFLOAD_API_URL`.
- **Standard verbs:** `GET` to read, `POST` to create or trigger, `PUT` / `PATCH` to update, `DELETE` to remove.
- **Response envelope.** Most endpoints wrap their payload in `{ "success": true, "data": … }`, so a value is read as `.data.<field>`. Some return the payload directly (alerts, native scan results, cloud accounts, Kubernetes clusters); the [API Reference](../api-reference/conventions.md#response-envelope) shows each shape. Errors return a non-2xx status with `{ "success": false, "error": { "code", "message" } }`.
- **Team-scoped.** Every call runs in the context of a **team** and only sees and affects that team's data, the same isolation that governs the UI.

## Authentication

Programmatic calls authenticate with an **API key**, sent in the **`X-API-Key`**
header. Each request is allowed only if the key's **scopes** cover the route
family and its owner's team role allows the action, so you grant automation
exactly the permissions it needs.

```bash
curl -s "$OFFLOAD_API_URL/api/cicd/scan-types" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

- **Create and manage keys** from the user menu (top right) → **API Keys**, with a name, a scope preset, and an optional expiry. See **[Roles, Teams & API Keys](../authentication/rbac-team-management.md)** and **[Authentication](../api-reference/authentication.md)**.
- **Not every endpoint takes a key.** Keys reach only the route families their scopes map to (scans, vulnerabilities, cloud, risks, reports, assessments, and the audit-trail SIEM export). Alerts, webhooks, integrations, teams and API key management are session-only and refuse keys with `403`. See [What an API key can reach](../api-reference/authentication.md#what-an-api-key-can-reach).
- **Scope least privilege.** A pipeline that only triggers scans doesn't need a key that can manage accounts. Pick the narrowest preset that fits the job.
- **Keys are secrets.** Store them in your CI/CD secret store or a vault, never in source control. Rotate and revoke them from the same screen; key creation, rotation and revocation are recorded in the key audit log.

:::warning[Treat keys like passwords]
An API key carries its scopes' permissions for your team. If a key is exposed, revoke it immediately and issue a new one.
:::

## The API reference

The platform can serve its own interactive reference, generated from the
running server and self-hosted on your instance (no external dependencies, so
it works in air-gapped deployments):

| What | Where on your instance |
|---|---|
| **Swagger UI**: browse and try endpoints | `https://<your-offload-host>/api/docs` |
| **ReDoc**: reference view | `https://<your-offload-host>/api/redoc` |
| **OpenAPI schema (JSON)**: import into Postman or Insomnia, or generate a client | `https://<your-offload-host>/api/openapi.json` |

:::note[Off by default in production]
These pages are controlled by `ENABLE_API_DOCS`. Unset, they are on outside
production and **off when `ENVIRONMENT=production`** (the client deployment's
default), in which case all of them return `404`. An administrator can set
`ENABLE_API_DOCS=true` and restart the backend to turn them on.
:::

For curated, task-oriented endpoint guides (authentication, conventions, cloud
accounts, Kubernetes, scans, vulnerabilities, alerts and copy-paste workflows),
see the **[API Reference](../api-reference/index.md)** section.

:::note[This section vs. the API reference]
These pages explain the *concepts and common workflows*. The API Reference
section, and the interactive reference where it is enabled, list the endpoints
and parameters for your version.
:::

## What you can automate

The API spans the same domains as the platform. Common resource families:

| Area | Automate |
|---|---|
| **Scanning** | Trigger web, API, network and container scans, poll status, fetch results, compare a run with the previous one. CI gating: `/api/cicd/scans/...`, see **[CLI & CI/CD](../cli-and-cicd.md)**. |
| **Vulnerabilities and findings** | Pull the normalized findings, filter by severity, status, priority or source, manage risk exceptions. See **[Vulnerabilities API](../api-reference/vulnerabilities.md)**. |
| **Cloud accounts** | Connect AWS, Azure and GCP accounts, kick off cloud scans, compare runs. See **[Cloud Accounts API](../api-reference/cloud-accounts.md)**. |
| **Assets** | Read the asset inventory (`cloud:read`). |
| **Compliance and evidence** | Read assessment and compliance data (`assessments:read`). Evidence routes are session-only. See **[Compliance](../compliance/index.md)**. |
| **Reports** | Download reports, such as the Cloud Security Posture PDF for a scan run, and verify an exported report's SHA-256. |
| **Audit trail** | Pull the hash-chained audit trail into a SIEM (`admin:audit`, team admin key). |
| **Alerts and events** | Receive events through **[outbound webhooks](../integrations/webhooks.md)** for near-real-time automation. Reading alerts over the API needs a signed-in session. |

For hands-on examples, continue to **[Automation Use Cases](./automation-use-cases.md)**.

## Two ways to integrate

1. **Pull (you call the API).** Your scripts, pipelines or schedulers call the API to trigger work and read data. Best for on-demand actions and periodic exports.
2. **Push (the platform calls you).** Subscribe to **[webhooks](../integrations/webhooks.md)** so the platform sends you a signed JSON payload when an event occurs (a new finding, a completed scan, an alert created or resolved, an SLA breach). Best for near-real-time SIEM, SOAR and ticketing automation.

Most automations use both: webhooks to react, and the API to fetch detail and act.
