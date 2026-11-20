---
title: "Authentication"
sidebar_label: "Authentication"
sidebar_position: 2
description: "Create and use Offload Security API keys: scopes, presets, which routes a key can reach, rotation, and the X-API-Key header."
---

# Authentication

Offload Security accepts two credentials:

| Method | Header | Best for |
| --- | --- | --- |
| **API key** *(recommended for automation)* | `X-API-Key: <key>` | CI/CD, scripts, SIEM pulls; limited to the route families its scopes map to |
| **Session token** | `Authorization: Bearer <token>` | The UI and anything an API key cannot reach (alerts, webhooks, key management) |

When a request carries `X-API-Key`, the key is checked first and the session
header is ignored. A request is authorized as the key's **owner**, using the
owner's current team role and team (re-resolved on each request, not the role
at the time the key was minted).

## Create an API key

API keys are created in the UI: open the user menu (top right) → **API Keys** →
**+ Create API Key**. You need the **Manage Integrations** team permission.

### Via the API

```
POST /api/api-keys
```

This call needs a **signed-in session** (`Authorization: Bearer`). API keys
cannot create, rotate or revoke keys: `/api/api-keys` is session-only for keys,
so a leaked key cannot mint a successor.

```bash
curl -s -X POST "$OFFLOAD_HOST/api/api-keys" \
  -H "Authorization: Bearer $OFFLOAD_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ci-pipeline",
    "scope_preset": "ci_cd_full",
    "expires_in_days": 90,
    "environment": "ci"
  }'
```

**Request body**

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `name` | string | (**required**) | 1–128 chars; must be unique among your active keys |
| `description` | string | `""` | Up to 512 chars |
| `scopes` | string[] | `null` | Explicit scopes; overrides `scope_preset` |
| `scope_preset` | string | `null` | One of the presets below. With neither field set, the key gets `ci_cd_basic` |
| `expires_in_days` | int | `90` | `0`–`365`; `0` = never expires |
| `ip_allowlist` | string[] | `null` | Up to 50 entries; exact IP addresses (matched as strings, no CIDR ranges) |
| `environment` | string | `production` | Label: `production` / `staging` / `development` / `ci` |
| `rate_limit_per_minute` | int | `60` | `1`–`600`. Recorded on the key; see the note under [Rate limits](./conventions.md#rate-limits) |
| `metadata` | object | `null` | Arbitrary key/values (repo, pipeline name) |

Each user can hold up to **25 active keys**.

**Response.** The full key is returned exactly once. Store it securely; only a
prefix is retained afterward.

```json
{
  "success": true,
  "message": "API key created. Store it securely — it won't be shown again.",
  "timestamp": "2026-11-01T12:00:00.000000+00:00",
  "data": {
    "key_id": "b1e7…",
    "api_key": "osk_Xy3f…",
    "name": "ci-pipeline",
    "description": "",
    "key_prefix": "osk_Xy3f8k2p",
    "scopes": ["scans:trigger", "scans:read", "vulnerabilities:read"],
    "scope_preset": "ci_cd_full",
    "environment": "ci",
    "ip_allowlist": [],
    "rate_limit_per_minute": 60,
    "expires_at": "2027-01-30T12:00:00+00:00",
    "created_at": "2026-11-01T12:00:00+00:00"
  }
}
```

:::warning[Store the key immediately]
The plaintext `api_key` (`osk_` followed by 64 URL-safe characters) is shown
**only** in this create response. The platform stores a SHA-256 hash and the
12-character prefix. If you lose it, rotate the key or create a new one.
:::

## Use the key

Send it as `X-API-Key` on every request:

```bash
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?limit=5" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

## Scopes and presets

Grant a key only the scopes it needs. Fetch the live list (any signed-in user):

```
GET /api/api-keys/scopes
```

**Available scopes:** `scans:trigger`, `scans:read`, `scans:manage`,
`vulnerabilities:read`, `vulnerabilities:manage`, `assessments:read`,
`assessments:manage`, `cloud:read`, `cloud:manage`, `risks:read`, `risks:manage`,
`reports:read`, `reports:generate`, `admin:keys`, `admin:audit`.

The `admin:` scopes are kept only when the key's owner has the **admin** role;
for anyone else they are silently dropped from the key.

**Presets:**

| Preset | Scopes |
| --- | --- |
| `ci_cd_basic` | `scans:trigger`, `scans:read` |
| `ci_cd_full` | `scans:trigger`, `scans:read`, `vulnerabilities:read` |
| `read_only` | `scans:read`, `vulnerabilities:read`, `assessments:read`, `cloud:read`, `risks:read`, `reports:read` |
| `security_automation` | `scans:trigger`, `scans:read`, `scans:manage`, `vulnerabilities:read`, `vulnerabilities:manage`, `cloud:read`, `reports:read`, `reports:generate` |
| `full_access` | All scopes (`admin:` scopes only for an admin owner) |

The CI presets deliberately omit `scans:manage`: that scope can relax the CI
gate policy and admission/image policies, and a pipeline key must not be able
to loosen its own gate. No preset except `full_access` includes `cloud:manage`,
which onboarding a cloud account needs.

## What an API key can reach

Scopes are enforced centrally, by URL family and HTTP method. A read (`GET`)
needs the family's read scope; `POST`, `PUT`, `PATCH` and `DELETE` need its
write scope. **Any route not in this table refuses API keys with `403`**,
whatever scopes the key holds.

| Route family (prefix) | Read scope | Write scope |
| --- | --- | --- |
| `/api/native-scans`, `/api/cloud-scans`, `/api/cicd`, `/api/ci`, `/api/code`, `/api/code-scan`, `/api/secrets`, `/api/iac`, `/api/app-scan`, `/api/api-scan`, `/api/k8s`, `/api/kubernetes`, `/api/container`, `/api/container-security`, `/api/container-registries`, `/api/scans`, `/api/pipeline`, `/api/lightweight-scans`, `/api/missing-tools`, `/api/gcp-scanner` | `scans:read` | `scans:trigger` |
| `/api/scan-*` (for example `/api/scan-management`) | `scans:read` | `scans:manage` |
| `/api/vulnerabilities`, `/api/triage` | `vulnerabilities:read` | `vulnerabilities:manage` |
| `/api/assessments`, `/api/compliance-*` | `assessments:read` | `assessments:manage` |
| `/api/cloud-accounts`, `/api/cloud`, `/api/cloud-credentials`, `/api/cspm`, `/api/unified-cloud-security`, `/api/advanced-cspm`, `/api/gcp/org`, `/api/ciem`, `/api/assets` | `cloud:read` | `cloud:manage` |
| `/api/risk-management`, `/api/risk-exceptions`, `/api/risk-scoring` | `risks:read` | `risks:manage` |
| `/api/reports`, `/api/premium-reports`, `/api/export` | `reports:read` | `reports:generate` |
| `/api/audit-trail` (SIEM export and chain verification only) | `admin:audit` | `admin:audit` |
| `/api/api-keys/admin` | `admin:keys` | `admin:keys` |

Families reviewed and kept **session-only** for API keys include
`/api/alerts`, `/api/api-keys`, `/api/webhooks`, `/api/integrations`,
`/api/notifications`, `/api/teams`, `/api/dashboard`, `/api/ai`, `/api/evidence`,
`/api/threat-intelligence` and `/api/platform`. Call them with a session token.

A few writes inside `scans:trigger` families need `scans:manage` instead:
changing the CI gate policy (`/api/ci/gate/policy`), container-image and K8s
admission policies, a code secret verdict, and a K8s finding status. Checking an
image against policy (`…/policies/validate-image`) stays on `scans:trigger`.

:::note[Two permission layers]
A key needs the **scope** for the route family **and** its owner needs the
**team permission** the endpoint checks. For example, onboarding a cloud
account needs `cloud:manage` on the key and the *Manage Cloud Accounts* team
permission on the owner. Some endpoints inside a mapped family accept only a
session (for example `GET /api/vulnerabilities/stats`); those answer `401` to
a key. The guides in this section say which endpoints are key-accessible.
:::

Enforcement is controlled by `API_KEY_SCOPE_MODE` (`enforce` by default;
`warn` logs without blocking, `off` disables it). Keys created before scopes
existed were given explicit scopes at upgrade, derived from their recorded usage.

## Manage keys

All of these need a signed-in session. Writes need **Manage Integrations**.

| Action | Endpoint |
| --- | --- |
| List your keys (masked) | `GET /api/api-keys` (`include_revoked`, `environment` filters) |
| Get one | `GET /api/api-keys/{key_id}` |
| Update name, scopes, allowlist, rate limit, environment, metadata | `PATCH /api/api-keys/{key_id}` |
| **Rotate** (new key, grace period) | `POST /api/api-keys/{key_id}/rotate` |
| **Revoke** (irreversible) | `DELETE /api/api-keys/{key_id}` |
| Revoke several | `POST /api/api-keys/bulk-revoke` (`key_ids` or `environment`) |
| Usage analytics / audit log | `GET /api/api-keys/analytics`, `GET /api/api-keys/audit-log` |

Rotation returns a new key (shown once) and keeps the old one valid for
`grace_period_hours` (default `48`, range `0`–`168`) so you can roll it out
without downtime.

## Errors

| Status | Meaning | Fix |
| --- | --- | --- |
| `401 Unauthorized` | Missing, invalid, expired or revoked key; IP not in the allowlist; or a session-only endpoint called with a key | Check the `X-API-Key` header, the key's status, or use a session |
| `403 Forbidden` | Key lacks the route family's scope, the route is session-only for keys, or the owner's team role lacks the permission | The message names the missing scope or says the route is session-only |
| `429 Too Many Requests` | Rate limit exceeded | Back off; see [Rate limits](./conventions.md#rate-limits) |

See [Conventions](./conventions.md) for the error format.
