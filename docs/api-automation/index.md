---
title: "API & Automation"
sidebar_label: "Overview"
sidebar_position: 0
---

# API & Automation

Everything Offload Security does in the UI is backed by a **REST API** — so anything you can do by clicking, you can also do programmatically. The API is how teams automate the platform: trigger scans from a pipeline, pull findings into another system, provision cloud accounts, export reports on a schedule, and feed security data into a SIEM, ticketing system, or BI dashboard.

This section explains how the API works, how to authenticate, and the common automation patterns. For the pipeline-specific workflow (gating releases on scan results), see **[CLI & CI/CD Integration](../cli-and-cicd.md)**.

## API basics

- **REST over HTTPS, JSON in and out.** Requests and responses are JSON.
- **Base URL** is your platform instance, with routes under `/api/` — for example `https://security.yourcompany.com/api/...`. Throughout these docs this is written as `$OFFLOAD_API_URL`.
- **Standard verbs** — `GET` to read, `POST` to create/trigger, `PUT`/`PATCH` to update, `DELETE` to remove.
- **Consistent response envelope.** Successful responses wrap their payload in a `data` object, so a status field is read as `.data.status`, results as `.data.results`, and so on. Errors return a non-2xx status with a JSON message.
- **Multi-tenant and scoped.** Every call runs in the context of a **team**, and only ever sees and affects that team's data — the same isolation that governs the UI.

## Authentication

Programmatic calls authenticate with an **API key**, sent in the **`X-API-Key`** header. Endpoints accept either a signed-in session **or** a valid API key, and each request is allowed only if the key's **scopes** cover the action — so you grant automation exactly the permissions it needs and nothing more.

```bash
curl -s "$OFFLOAD_API_URL/api/cicd/scan-types" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

- **Create and manage keys** in **Team Management → API Keys** — with a name, a scope preset, and optional expiry. See **[Roles, Teams & API Keys](../authentication/rbac-team-management.md)**.
- **Scope least privilege.** A pipeline that only triggers scans doesn't need a key that can manage accounts. Pick the narrowest preset that fits the job.
- **Keys are secrets.** Store them in your CI/CD secret store or a vault — never in source control. Rotate and revoke from the same screen; every key's usage is auditable.

:::warning Treat keys like passwords
An API key carries its scopes' permissions for your team. If a key is exposed, revoke it immediately and issue a new one.
:::

## The API reference

The platform is built on a standard **OpenAPI** foundation, so it publishes a machine-readable specification and an interactive reference you can use to explore every available endpoint, its parameters, and its response shape.

- **Interactive API reference** and the **OpenAPI (`openapi.json`) specification** are served from your platform instance (commonly at `/docs` and `/openapi.json`). Availability of the interactive docs endpoint can depend on your deployment's configuration — check with your administrator.
- Use the OpenAPI spec to **generate a client SDK** in your language of choice, or to keep an integration in sync as the API evolves.

:::tip This section vs. the API reference
These pages explain the *concepts and common workflows*. The interactive API reference is the *authoritative, always-current list of endpoints* for your version — use them together.
:::

## What you can automate

The API spans the same domains as the platform. Common resource families:

| Area | Automate |
|---|---|
| **Scanning** | Trigger web/API/network/container scans, poll status, fetch results (`/api/cicd/scans/...`). See **[CLI & CI/CD](../cli-and-cicd.md)**. |
| **Vulnerabilities & findings** | Pull the unified findings queue, filter by severity/status/source, push updates to another system. See **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)**. |
| **Cloud accounts** | Connect and manage AWS/Azure/GCP accounts and organizations, kick off cloud scans. See **[Cloud Security](../cloud-security/index.md)**. |
| **Assets** | Read the unified asset inventory across cloud and on-prem. |
| **Compliance & evidence** | Read control status, export evidence and audit data. See **[Compliance](../compliance/index.md)**. |
| **Reports** | Generate and download executive, compliance, and audit reports. |
| **Alerts & events** | Receive events via **[outbound webhooks](../integrations/notifications.md)** for near-real-time automation, or poll for them. |

The exact routes, parameters, and payloads for each are in the interactive API reference. For hands-on examples, continue to **[Automation Use Cases](./automation-use-cases.md)**.

## Two ways to integrate

1. **Pull (you call the API).** Your scripts, pipelines, or schedulers call the API to trigger work and read data — best for on-demand actions and periodic exports.
2. **Push (the platform calls you).** Subscribe to **[webhooks](../integrations/notifications.md)** so the platform sends you a signed JSON payload the moment an event occurs (a new finding, a scan completion, an SLA breach) — best for near-real-time SIEM/SOAR and ticketing automation.

Most automations use both: webhooks to react instantly, and the API to fetch detail and act.
