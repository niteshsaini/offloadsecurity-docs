---
title: "Authentication"
sidebar_label: "Authentication"
sidebar_position: 2
description: "Create and use Offload Security API keys — scopes, presets, rotation, and the X-API-Key header."
---

# Authentication

Offload Security accepts two credentials on every request:

| Method | Header | Best for |
| --- | --- | --- |
| **API key** *(recommended for automation)* | `X-API-Key: <key>` | CI/CD, scripts, integrations |
| **Session token** | `Authorization: Bearer <token>` | Interactive / short‑lived UI sessions |

API keys are checked first. Everything below uses API keys.

## Create an API key

You can create a key in the **UI** (**Settings → API Keys → Create**) or over the API.

### Via the API

```
POST /api/api-keys
```

Requires the **Manage Integrations** team permission.

```bash
curl -s -X POST "$OFFLOAD_HOST/api/api-keys" \
  -H "X-API-Key: $OFFLOAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ci-pipeline",
    "scope_preset": "security_automation",
    "expires_in_days": 90,
    "rate_limit_per_minute": 120,
    "environment": "ci"
  }'
```

**Request body**

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `name` | string | — (**required**) | 1–128 chars |
| `description` | string | `""` | ≤ 512 chars |
| `scopes` | string[] | `null` | Explicit scopes (overrides `scope_preset`) |
| `scope_preset` | string | `null` | One of the presets below |
| `expires_in_days` | int | `90` | `0`–`365`; `0` = never expires |
| `ip_allowlist` | string[] | `null` | Restrict the key to these IPs (≤ 50) |
| `environment` | string | `production` | `production` / `staging` / `development` / `ci` |
| `rate_limit_per_minute` | int | `60` | `1`–`600` |
| `metadata` | object | `null` | Arbitrary key/values |

**Response** — the **full key is returned exactly once**. Store it securely; only a
prefix is retained afterward.

```json
{
  "success": true,
  "message": "API key created. Store it securely — it won't be shown again.",
  "data": {
    "key_id": "b1e7…",
    "api_key": "osk_Xy3f…<48 chars>…",
    "name": "ci-pipeline",
    "key_prefix": "osk_Xy3f8k2p",
    "scopes": ["scans:trigger", "scans:read", "scans:manage", "vulnerabilities:read", "vulnerabilities:manage", "cloud:read", "reports:read", "reports:generate"],
    "scope_preset": "security_automation",
    "environment": "ci",
    "rate_limit_per_minute": 120,
    "expires_at": "2026-09-29T12:00:00Z",
    "created_at": "2026-07-01T12:00:00Z"
  }
}
```

:::warning Store the key immediately
The plaintext `api_key` is shown **only** in this create response — the platform
stores just a SHA‑256 hash and the 12‑char prefix. If you lose it, rotate or
create a new one.
:::

## Use the key

Send it as `X-API-Key` on every request:

```bash
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?limit=5" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

## Scopes & presets

Grant a key only the scopes it needs. Fetch the live list any time:

```bash
curl -s "$OFFLOAD_HOST/api/api-keys/scopes" -H "X-API-Key: $OFFLOAD_API_KEY"
```

**Available scopes:** `scans:trigger`, `scans:read`, `scans:manage`,
`vulnerabilities:read`, `vulnerabilities:manage`, `assessments:read`,
`assessments:manage`, `cloud:read`, `cloud:manage`, `risks:read`, `risks:manage`,
`reports:read`, `reports:generate`, `admin:keys`, `admin:audit`.

**Presets:**

| Preset | Scopes |
| --- | --- |
| `ci_cd_basic` | `scans:trigger`, `scans:read` |
| `ci_cd_full` | `+ scans:manage`, `vulnerabilities:read` |
| `read_only` | `scans:read`, `vulnerabilities:read`, `assessments:read`, `cloud:read`, `risks:read`, `reports:read` |
| `security_automation` | `scans:*`, `vulnerabilities:read/manage`, `cloud:read`, `reports:read/generate` |
| `full_access` | all scopes |

:::note Two permission layers
Offload Security checks **both** your key's **scopes** *and* the key owner's
**team role** depending on the endpoint (e.g. onboarding a cloud account requires
the *Manage Cloud Accounts* team permission; listing vulnerabilities only
requires a valid key). If a call returns **403**, the key's scope or the owner's
team role is insufficient — widen the scope (or use `full_access`) and confirm
the owner's role. Each endpoint's exact requirement is visible in the
[Swagger UI](./index.md#interactive-reference-swagger).
:::

## Manage keys

| Action | Endpoint |
| --- | --- |
| List (masked) | `GET /api/api-keys` |
| Get one | `GET /api/api-keys/{key_id}` |
| Update | `PATCH /api/api-keys/{key_id}` |
| **Rotate** (new key, grace period) | `POST /api/api-keys/{key_id}/rotate` |
| **Revoke** | `DELETE /api/api-keys/{key_id}` |
| Usage analytics / audit log | `GET /api/api-keys/analytics`, `GET /api/api-keys/audit-log` |

Rotation returns a new key (shown once) and keeps the old one valid for a grace
period (`grace_period_hours`, default 48) so you can roll it out with zero
downtime.

## Errors

| Status | Meaning | Fix |
| --- | --- | --- |
| `401 Unauthorized` | Missing/invalid/expired key, or IP not in allowlist | Check the `X-API-Key` header and the key's status |
| `403 Forbidden` | Key scope or owner's team role insufficient | Grant the needed scope / role |
| `429 Too Many Requests` | Per‑key rate limit exceeded | Back off; raise `rate_limit_per_minute` |

See [Conventions](./conventions.md) for the full error format.
