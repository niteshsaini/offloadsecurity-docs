---
title: "API Reference"
sidebar_label: "Overview"
sidebar_position: 1
description: "Integrate with Offload Security programmatically — authentication, conventions, and task-oriented guides for cloud accounts, Kubernetes, scans, alerts, and vulnerabilities."
---

# API Reference

Everything you can do in the Offload Security UI, you can do over its REST API —
onboard cloud accounts and Kubernetes clusters, trigger scans, pull findings and
vulnerabilities, and read or act on alerts. This section gets you from zero to a
working integration.

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

| Guide | Onboard / read |
| --- | --- |
| **[Authentication](./authentication.md)** | Create & manage API keys, scopes, rotation |
| **[Conventions](./conventions.md)** | Response shapes, pagination, errors, rate limits |
| **[Cloud Accounts](./cloud-accounts.md)** | Add AWS/GCP/Azure accounts, test connection, trigger a scan |
| **[Kubernetes](./kubernetes.md)** | Onboard a cluster with a kubeconfig, list, connectivity test |
| **[Scans & Results](./scans-and-results.md)** | Trigger scans, poll status, fetch results |
| **[Alerts](./alerts.md)** | List, read, acknowledge, assign, resolve |
| **[Vulnerabilities](./vulnerabilities.md)** | List occurrences, group by CVE, filter & triage |
| **[Workflows](./workflows.md)** | End‑to‑end recipes stitching the above together |

## Conventions at a glance

- **Auth:** `X-API-Key: <key>` (recommended for automation) or `Authorization: Bearer <session-token>`.
- **Content type:** `application/json` for request bodies.
- **Multi‑tenancy:** every call is scoped to the API key's team — you only ever see your team's data.
- **IDs:** resources use prefixed IDs (`osk_…` API keys, `clus_…` clusters, `occur_…` vulnerability occurrences, `alert_…` alerts).

:::note Response shapes vary by endpoint
Most endpoints wrap results in a `{ "success": true, "data": … }` envelope, but a
few return the payload directly. Each guide shows the **actual** response for that
endpoint, and [Conventions](./conventions.md) explains the patterns. When in
doubt, check the live [Swagger UI](#interactive-reference-swagger).
:::
