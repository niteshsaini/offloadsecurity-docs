---
title: "Cloud Accounts API"
sidebar_label: "Cloud Accounts"
sidebar_position: 4
description: "Onboard AWS, GCP, and Azure accounts over the API: add, test connection, list, trigger a scan, and compare runs."
---

# Cloud Accounts API

Onboard a cloud account with read-only credentials, then let the platform scan
its posture. When the credentials validate, adding an account **auto-starts an
initial scan**.

> Required: an API key with **`cloud:manage`** for writes (`cloud:read` for
> reads), owned by a user with the **Manage Cloud Accounts** team permission.
> No preset except `full_access` includes `cloud:manage`; give the key that
> scope explicitly. See [Required Permissions](../cloud-security/permissions.md)
> for the cloud IAM roles the credentials themselves need.

## Add a cloud account

```
POST /api/cloud-accounts/
```

**Request body**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `provider` | string | ✓ | `aws` \| `gcp` \| `azure` |
| `account_id` | string | ✓ | AWS = 12-digit account number; GCP = project ID; Azure = subscription ID (GCP and Azure are lower-cased) |
| `account_name` | string | ✓ | Display name |
| `region` | string | — | Default region (optional) |
| `credentials` | object | ✓ | Provider-specific, see below |

**Credentials by provider**

| Provider | Required keys | Optional |
| --- | --- | --- |
| **AWS** | `access_key_id`, `secret_access_key` | `session_token`, `region` |
| **GCP** | `service_account_json` (the full service-account JSON, as a string) | — |
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

**Response `201 Created`** (returned directly, not in a `data` envelope)

```json
{
  "success": true,
  "message": "Cloud account created successfully. Initial security scan started automatically.",
  "validation_error": null,
  "id": "3f2b9c1e-…",
  "account_id": "my-gcp-project",
  "provider": "gcp",
  "account_name": "Production (GCP)",
  "display_name": "Production (GCP)",
  "region": "us-central1",
  "status": "active",
  "credential_id": "…",
  "auto_scan_initiated": true,
  "scan_run_id": "8d1c4f6a-…",
  "created_at": "2026-11-01T12:00:00+00:00"
}
```

- **`id`** is the platform's identifier for the account (a UUID). Every
  `/api/cloud-accounts/{account_id}` path below takes this `id`, not the
  provider's account number.
- **`scan_run_id`** identifies the initial scan; follow it with
  `GET /api/cloud-scans/{run_id}/status` (see [Workflows § 1](./workflows.md#1-onboard-a-cloud-account-and-pull-its-first-findings)).
- **Credentials that fail validation** do not reject the request: the account
  is saved with `status: "error"`, `validation_error` explains why, the message
  says so, and no scan starts (`auto_scan_initiated: false`). Fix the
  credentials and revalidate.

## Test credentials without saving

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

A failed test returns `200` with `"success": false` and the reason in `message`.

## List and read accounts

| Action | Endpoint | Scope |
| --- | --- | --- |
| List your team's accounts | `GET /api/cloud-accounts` | `cloud:read` |
| Read one | `GET /api/cloud-accounts/{account_id}` | `cloud:read` |
| Update name, region, scan regions (`regions`), credentials | `PUT /api/cloud-accounts/{account_id}` | `cloud:manage` |
| Revalidate credentials | `POST /api/cloud-accounts/{account_id}/revalidate` | `cloud:manage` |
| Delete (the deletion is audited; run snapshots are kept) | `DELETE /api/cloud-accounts/{account_id}` | `cloud:manage` |

```bash
curl -s "$OFFLOAD_HOST/api/cloud-accounts" -H "X-API-Key: $OFFLOAD_API_KEY"
```
```json
{ "success": true, "accounts": [ { "id": "3f2b9c1e-…", "provider": "gcp", "account_name": "Production (GCP)", "status": "active" } ], "total": 1, "meta": { } }
```

Account responses never include the stored secret, only a `credential_id`. If
some stored accounts could not be read, the response says so in `warning`
rather than returning a silently shorter list.

## Trigger a scan on demand

```
POST /api/cloud-accounts/{account_id}/scan
```
Re-scan an account any time (for example nightly). Needs `cloud:manage` on the
key and the owner's *Run Scans* and *Manage Cloud Accounts* permissions. An
optional body `{ "scan_type": "full", "regions": ["us-east-1"] }` overrides the
account's configured region scope for this run.

```bash
curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/3f2b9c1e-…/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```
```json
{ "success": true, "message": "Scan triggered successfully", "account_id": "3f2b9c1e-…", "scan_run_id": "8d1c4f6a-…", "task_id": "…" }
```

`GET /api/cloud-accounts/{account_id}/scan-history` lists the account's 20 most
recent scans.

## Compare two runs

*New in 1.4.0.*

```
GET /api/cloud-scans/{run_id}/compare?baseline={earlier_run_id}
```

Compares two runs of the same account from their **frozen snapshots**, so later
scans do not change the answer. Without `baseline`, the previous run of the
account that has a snapshot is used. Needs `scans:read`. The UI's **Compare**
action on a cloud scan run shows the comparison with the previous run; choosing
a different `baseline` is API-only.

```json
{
  "counts": { "new_failing": 3, "fixed": 7, "still_failing": 41, "not_reevaluated": 2 },
  "new_failing": [ ], "fixed": [ ], "still_failing": [ ], "not_reevaluated": [ ],
  "caveats": [ "The runs covered different regions (added: eu-west-1; removed: none)." ],
  "run": { "run_id": "8d1c4f6a-…", "status": "completed", "completed_at": "…" },
  "baseline": { "run_id": "51e0a7b2-…", "status": "completed", "completed_at": "…" }
}
```

`not_reevaluated` lists findings that were failing in the baseline and produced
no verdict this time; they are never counted as fixed. `caveats` flags a partial
run on either side and changed region coverage. Runs that predate snapshots
return `400`; when no earlier snapshotted run exists the response has
`"baseline": null` and a `detail` message.

A posture report for a single run is available as
`GET /api/export/cloud-posture?scan_run_id={run_id}` (PDF; `reports:read`).
Issued reports are fingerprinted; see
[Verify an exported report](./scans-and-results.md#verify-an-exported-report).

## Errors

| Status | Cause |
| --- | --- |
| `400` | Missing required fields, malformed `{account_id}` (not a UUID), or a failure while saving |
| `401` | Missing or invalid key |
| `403` | Key lacks `cloud:manage` / `cloud:read`, or the owner lacks *Manage Cloud Accounts* |
| `404` | Account not found in your team |
| `422` | Invalid `provider`, or `account_id` fails the provider format (AWS must be 12 digits) |

## Related

- [Required Permissions](../cloud-security/permissions.md): the IAM roles the credentials need
- [Connecting Cloud Accounts](../cloud-security/connecting-accounts.md): the UI flow
- [Scans & Results](./scans-and-results.md)
