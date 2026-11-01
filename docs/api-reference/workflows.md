---
title: "Workflows"
sidebar_label: "Workflows"
sidebar_position: 9
description: "End-to-end API recipes: onboard and scan a cloud account, onboard and scan a cluster, triage alerts, export vulnerabilities, gate CI, compare re-tests, and pull the audit trail."
---

# Workflows

Copy-and-paste recipes that combine the endpoints. All assume you've set
`OFFLOAD_HOST` and `OFFLOAD_API_KEY` (see [Authentication](./authentication.md)),
and that `jq` is installed. Each recipe names the key scopes it needs; give the
key exactly those with explicit `scopes` when no preset fits.

## 1. Onboard a cloud account and pull its first findings

Scopes: `cloud:manage`, `scans:read`, `vulnerabilities:read`. Owner permission:
*Manage Cloud Accounts*.

```bash
# 1) Add the account (auto-starts an initial scan when the credentials validate)
RESP=$(curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "provider": "aws", "account_id": "123456789012", "account_name": "Prod",
        "credentials": { "access_key_id": "AKIA…", "secret_access_key": "…" } }')
echo "$RESP" | jq '{id, status, validation_error, scan_run_id}'
SCAN_ID=$(echo "$RESP" | jq -r '.scan_run_id // empty')
[ -n "$SCAN_ID" ] || { echo "No scan started: fix the credentials and revalidate"; exit 1; }

# 2) Poll the cloud scan until it reaches a terminal status
while : ; do
  STATUS=$(curl -s "$OFFLOAD_HOST/api/scan-management/status/$SCAN_ID" \
    -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.status')
  case "$STATUS" in completed|partial|failed|cancelled) break ;; esac
  sleep 15; echo "…$STATUS"
done
echo "Scan finished: $STATUS"

# 3) Pull the resulting vulnerabilities (highest priority first)
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?source=cspm&status=open&limit=50" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq '.data.occurrences[] | {vulnerability_id, risk_assessment, asset_id}'
```

A `partial` run finished with some checks missing; treat its results as
incomplete. See [Cloud Accounts](./cloud-accounts.md) · [Scans & Results](./scans-and-results.md) · [Vulnerabilities](./vulnerabilities.md).

## 2. Onboard a Kubernetes cluster and scan it

Scopes: `scans:trigger`, `scans:read`. Owner permissions: *Manage Container
Security*, *Run Scans*.

```bash
# Encode the kubeconfig, onboard, test connectivity, then start a scan
KUBECONFIG_B64=$(base64 -i ~/.kube/config | tr -d '\n')

CLUSTER=$(curl -s -X POST "$OFFLOAD_HOST/api/k8s/clusters" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d "{ \"name\": \"prod-gke\", \"provider\": \"gcp\", \"onboard_method\": \"kubeconfig\",
        \"credentials\": \"$KUBECONFIG_B64\" }")
CLUSTER_ID=$(echo "$CLUSTER" | jq -r '.cluster_id')

curl -s -X POST "$OFFLOAD_HOST/api/k8s/clusters/$CLUSTER_ID/test" -H "X-API-Key: $OFFLOAD_API_KEY" | jq '{success, message}'

SCAN_ID=$(curl -s -X POST "$OFFLOAD_HOST/api/k8s/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d "{ \"cluster_id\": \"$CLUSTER_ID\" }" | jq -r '.scan_id')

while : ; do
  SCAN=$(curl -s "$OFFLOAD_HOST/api/k8s/scan/$SCAN_ID" -H "X-API-Key: $OFFLOAD_API_KEY")
  case "$(echo "$SCAN" | jq -r '.status')" in completed|failed|timeout|cancelled) break ;; esac
  sleep 15
done
echo "$SCAN" | jq '{status, scan_health, outcome, findings_count}'
```

See [Kubernetes](./kubernetes.md).

## 3. Triage critical alerts

Alerts are **session-only**: API keys get `403`. Use a session token from a
signed-in user with *Acknowledge Alerts* and *Manage Alerts*.

```bash
# List open critical alerts
curl -s "$OFFLOAD_HOST/api/alerts?severity=critical&active_only=true&limit=50" \
  -H "Authorization: Bearer $OFFLOAD_SESSION_TOKEN" | jq -r '.items[] | "\(.alert_id)\t\(.title)"'

# Acknowledge one, then resolve it (a new alert cannot go straight to resolved)
curl -s -X POST "$OFFLOAD_HOST/api/alerts/$ALERT_ID/acknowledge" \
  -H "Authorization: Bearer $OFFLOAD_SESSION_TOKEN" -H "Content-Type: application/json" \
  -d '{ "note": "Ack via automation" }'

curl -s -X PUT "$OFFLOAD_HOST/api/alerts/$ALERT_ID/status" \
  -H "Authorization: Bearer $OFFLOAD_SESSION_TOKEN" -H "Content-Type: application/json" \
  -d '{ "status": "resolved", "reason": "Patched in release 2026.11.1" }'
```

To react to alerts without polling, subscribe to the `alert.created`,
`alert.updated` and `alert.resolved` webhook events. See [Alerts](./alerts.md#receive-alert-events-by-webhook).

## 4. Export all open vulnerabilities to your SIEM (paginated)

Scope: `vulnerabilities:read`.

```bash
SKIP=0; LIMIT=100
while : ; do
  PAGE=$(curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?status=open&skip=$SKIP&limit=$LIMIT" \
    -H "X-API-Key: $OFFLOAD_API_KEY")
  COUNT=$(echo "$PAGE" | jq '.data.occurrences | length')
  echo "$PAGE" | jq -c '.data.occurrences[]'   # forward each to your SIEM
  [ "$COUNT" -lt "$LIMIT" ] && break
  SKIP=$((SKIP + LIMIT))
  sleep 1   # /api/vulnerabilities is limited to 60 requests per minute per client IP
done
```

Open-status lists exclude occurrences under an approved risk exception; add
`&excepted=include` to export them too (they are labeled). See
[Vulnerabilities](./vulnerabilities.md) · [Conventions → Pagination](./conventions.md#pagination).

## 5. Trigger a scan from CI and fail the build on criticals

Scopes: `scans:trigger`, `scans:read` (the `ci_cd_basic` preset).

```bash
SCAN=$(curl -s -X POST "$OFFLOAD_HOST/api/native-scans/web-vulnerability" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "target_url": "'"$DEPLOY_URL"'", "scan_type": "standard" }')
SCAN_ID=$(echo "$SCAN" | jq -r '.scan_id')

for i in $(seq 1 360); do   # up to 30 minutes
  RESULT=$(curl -s "$OFFLOAD_HOST/api/native-scans/results/$SCAN_ID" -H "X-API-Key: $OFFLOAD_API_KEY")
  STATUS=$(echo "$RESULT" | jq -r '.scan_result.status')
  case "$STATUS" in completed|partial|failed) break ;; esac
  sleep 5
done

[ "$STATUS" = "completed" ] || { echo "Scan did not complete (status: $STATUS)"; exit 1; }
CRIT=$(echo "$RESULT" | jq '[.scan_result.findings[] | select((.severity // "" | ascii_downcase) == "high" or (.severity // "" | ascii_downcase) == "critical")] | length')
if [ "$CRIT" -gt 0 ]; then echo "FAIL: $CRIT high/critical findings"; exit 1; else echo "PASS: no high/critical findings"; fi
```

For a built-in pass/fail gate (`fail_on_severity`, `gate_passed`), a GitHub
Action and SARIF output, use the dedicated CI/CD endpoints; see
[CLI & CI/CD](../cli-and-cicd.md).

## 6. Compare a re-test with the previous run

*New in 1.4.0.* Scope: `scans:read`.

```bash
# What changed since the last run of the same tool on the same target?
curl -s "$OFFLOAD_HOST/api/native-scans/results/$SCAN_ID/compare" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq '{counts, caveats, new: [.new[] | {severity, title, location}]}'

# Or against a specific earlier run
curl -s "$OFFLOAD_HOST/api/native-scans/results/$SCAN_ID/compare?baseline=$EARLIER_SCAN_ID" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq '.counts'
```

Cloud runs, code scans, Kubernetes scans and container images have equivalent
endpoints; see [Scans & Results → Compare with an earlier run](./scans-and-results.md#compare-with-an-earlier-run).

## 7. Pull the audit trail into a SIEM

*New in 1.4.0 · API-only.* The platform audit trail is hash-chained per team.
A SIEM can pull it incrementally with a cursor and check continuity itself.

Scope: `admin:audit`. The key's owner must be a **team admin** (the `admin:`
scopes are dropped for any other role); a team admin reads only their own
team's chain.

```bash
AFTER=0
while : ; do
  curl -s -D headers.txt "$OFFLOAD_HOST/api/audit-trail/export/siem?after_seq=$AFTER&limit=500" \
    -H "X-API-Key: $OFFLOAD_API_KEY" >> audit.jsonl
  AFTER=$(grep -i '^x-audit-next-after-seq:' headers.txt | tr -d '\r' | awk '{print $2}')
  grep -qi '^x-audit-has-more: true' headers.txt || break
done
```

| Parameter | Notes |
| --- | --- |
| `after_seq` | Cursor: return entries with `seq` greater than this. Persist the last `X-Audit-Next-After-Seq` between runs |
| `limit` | `1`–`5000`, default `500` |
| `format` | `jsonl` (default; each line carries `seq`, `prev_hash` and `hash`) or `cef` (ArcSight CEF) |
| `store` | `api` (default, the platform API trail), `compliance` (control-state history) or `auth` (sign-in events; platform admin only) |

Check the chain on the platform side with `GET /api/audit-trail/verify`
(`status`: `ok`, `broken`, `truncated` or `empty`). Very large chains are
verified as a background job: the response carries a `job_id` to poll at
`GET /api/audit-trail/verify/jobs/{job_id}`. Entries written before the chain
existed are not in this export. Each pull is itself recorded in the audit trail.
See [Audit Trail](../authentication/audit-trail.md).
