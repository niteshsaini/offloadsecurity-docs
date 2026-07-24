---
title: "Cloud Accounts API"
sidebar_label: "Cloud Accounts"
sidebar_position: 4
description: "Onboard AWS, GCP, and Azure accounts over the API — add, test connection, list, and trigger a scan."
---

# Cloud Accounts API

Onboard a cloud account with read‑only credentials, then let the platform scan
its posture. Adding an account **auto‑starts an initial scan**.

> Required permission: **Manage Cloud Accounts** (works with an `X-API-Key` whose
> owner has that team role). See [Required Permissions](../cloud-security/permissions.md)
> for the cloud IAM roles the credentials themselves need.

## Add a cloud account

```
POST /api/cloud-accounts/
```

**Request body**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `provider` | string | ✅ | `aws` \| `gcp` \| `azure` |
| `account_id` | string | ✅ | AWS = 12‑digit account number; GCP = project id; Azure = subscription id |
| `account_name` | string | ✅ | Friendly display name |
| `region` | string | ➖ | Default region (optional) |
| `credentials` | object | ✅ | Provider‑specific — see below |

**Credentials by provider**

| Provider | Required keys | Optional |
| --- | --- | --- |
| **AWS** | `access_key_id`, `secret_access_key` | `session_token`, `region` |
| **GCP** | `service_account_json` (the full service‑account JSON, as a string) | — |
| **Azure** | `client_id`, `client_secret`, `tenant_id` | — |

**Example (GCP)**

```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/" \
  -H "X-API-Key: $OFFLOAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gcp",
    "account_id": "my-gcp-project",
    "account_name": "Production (GCP)",
    "region": "us-central1",
    "credentials": {
      "service_account_json": "{\"type\":\"service_account\",\"project_id\":\"my-gcp-project\", ... }"
    }
  }'
```

**Example (AWS)**

```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "provider": "aws",
    "account_id": "123456789012",
    "account_name": "Production (AWS)",
    "credentials": { "access_key_id": "AKIA…", "secret_access_key": "…" }
  }'
```

**Response `201 Created`**

```json
{
  "success": true,
  "message": "Cloud account created successfully. Initial security scan started automatically.",
  "id": "acc_…",
  "account_id": "my-gcp-project",
  "provider": "gcp",
  "account_name": "Production (GCP)",
  "region": "us-central1",
  "status": "active",
  "credential_id": "cred_…",
  "auto_scan_initiated": true,
  "scan_run_id": "scan_…",
  "created_at": "2026-07-01T12:00:00Z"
}
```

Capture `scan_run_id` to follow the initial scan (see [Scans & Results](./scans-and-results.md)).

## Test credentials without saving

Validate credentials before committing them:

```
POST /api/cloud-accounts/test-connection
```
```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/test-connection" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "provider": "aws", "account_id": "123456789012",
        "credentials": { "access_key_id": "AKIA…", "secret_access_key": "…" } }'
```
```json
{ "success": true, "message": "Connection successful", "details": { } }
```

## List & read accounts

```
GET  /api/cloud-accounts            # list your team's accounts
GET  /api/cloud-accounts/{account_id}
PUT  /api/cloud-accounts/{account_id}    # update name/region/credentials
DELETE /api/cloud-accounts/{account_id}
```

```bash
curl -s "$OFFLOAD_HOST/api/cloud-accounts" -H "X-API-Key: $OFFLOAD_API_KEY"
```
```json
{ "success": true, "accounts": [ { "id": "acc_…", "provider": "gcp", "account_name": "Production (GCP)", "status": "active" } ], "total": 1 }
```

Account responses never include the stored secret — only a `credential_id`.

## Trigger a scan on demand

```
POST /api/cloud-accounts/{account_id}/scan
```
Re‑scan an account any time (e.g. nightly in CI). Returns a scan id to poll.

```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/acc_123/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

`GET /api/cloud-accounts/{account_id}/scan-history` lists past scans for the account.

## Errors

| Status | Cause |
| --- | --- |
| `400` | Missing required credential keys, or connection test failed |
| `403` | Key owner lacks the *Manage Cloud Accounts* role |
| `422` | Invalid `provider`, or `account_id` fails provider format (AWS must be 12 digits) |

## Related

- [Required Permissions (GCP)](../cloud-security/permissions.md) — the IAM roles the credentials need
- [Connecting Cloud Accounts](../cloud-security/connecting-accounts.md) — the UI flow
- [Scans & Results](./scans-and-results.md)
