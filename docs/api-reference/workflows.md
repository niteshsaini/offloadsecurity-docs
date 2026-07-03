---
title: "Workflows"
sidebar_label: "Workflows"
sidebar_position: 9
description: "End-to-end API recipes: onboard and scan a cloud account, onboard a cluster, triage alerts, and export vulnerabilities."
---

# Workflows

Copy‑paste recipes that stitch the endpoints together. All assume you've set
`OFFLOAD_HOST` and `OFFLOAD_API_KEY` (see [Authentication](./authentication.md)).

## 1. Onboard a cloud account and pull its first findings

```bash
# 1) Add the account (auto-starts an initial scan) and capture the scan id
RESP=$(curl -s -X POST "$OFFLOAD_HOST/api/cloud-accounts/" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "provider": "aws", "account_id": "123456789012", "account_name": "Prod",
        "credentials": { "access_key_id": "AKIA…", "secret_access_key": "…" } }')
SCAN_ID=$(echo "$RESP" | jq -r '.scan_run_id')
echo "Scan started: $SCAN_ID"

# 2) Poll cloud scan status
until [ "$(curl -s "$OFFLOAD_HOST/api/scan-management/status/$SCAN_ID" \
      -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.status')" = "completed" ]; do
  sleep 10; echo "…still running"
done

# 3) Pull the resulting vulnerabilities (highest risk first)
curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?source=cspm&status=open&limit=50" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq '.data.occurrences[] | {vulnerability_id, risk_assessment, asset_id}'
```

See [Cloud Accounts](./cloud-accounts.md) · [Scans & Results](./scans-and-results.md) · [Vulnerabilities](./vulnerabilities.md).

## 2. Onboard a Kubernetes cluster and scan it

```bash
# Encode the kubeconfig, onboard, then test connectivity
KUBECONFIG_B64=$(base64 -i ~/.kube/config | tr -d '\n')

CLUSTER=$(curl -s -X POST "$OFFLOAD_HOST/api/k8s/clusters" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d "{ \"name\": \"prod-gke\", \"provider\": \"gcp\", \"onboard_method\": \"kubeconfig\",
        \"credentials\": \"$KUBECONFIG_B64\" }")
CLUSTER_ID=$(echo "$CLUSTER" | jq -r '.id')

curl -s -X POST "$OFFLOAD_HOST/api/k8s/clusters/$CLUSTER_ID/test" -H "X-API-Key: $OFFLOAD_API_KEY"
```

See [Kubernetes](./kubernetes.md).

## 3. Triage critical alerts

```bash
# List open critical alerts
curl -s "$OFFLOAD_HOST/api/alerts?severity=critical&active_only=true&limit=50" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.items[] | "\(.alert_id)\t\(.title)"'

# Acknowledge one, then resolve it
curl -s -X POST "$OFFLOAD_HOST/api/alerts/$ALERT_ID/acknowledge" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "note": "Ack via automation" }'

curl -s -X PUT "$OFFLOAD_HOST/api/alerts/$ALERT_ID/status" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "status": "resolved", "reason": "Patched in release 2026.7.1" }'
```

See [Alerts](./alerts.md).

## 4. Export all open vulnerabilities to your SIEM (paginated)

```bash
SKIP=0; LIMIT=100
while : ; do
  PAGE=$(curl -s "$OFFLOAD_HOST/api/vulnerabilities/occurrences?status=open&skip=$SKIP&limit=$LIMIT" \
    -H "X-API-Key: $OFFLOAD_API_KEY")
  COUNT=$(echo "$PAGE" | jq '.data.occurrences | length')
  echo "$PAGE" | jq -c '.data.occurrences[]'   # → forward each to your SIEM
  [ "$COUNT" -lt "$LIMIT" ] && break
  SKIP=$((SKIP + LIMIT))
done
```

See [Vulnerabilities](./vulnerabilities.md) · [Conventions → Pagination](./conventions.md#pagination).

## 5. Trigger a scan from CI and fail the build on criticals

```bash
SCAN=$(curl -s -X POST "$OFFLOAD_HOST/api/native-scans/web-vulnerability" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{ "target_url": "'"$DEPLOY_URL"'", "scan_type": "standard" }')
SCAN_ID=$(echo "$SCAN" | jq -r '.scan_id')

until [ "$(curl -s "$OFFLOAD_HOST/api/native-scans/results/$SCAN_ID" \
      -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.scan_result.status')" = "completed" ]; do sleep 5; done

CRIT=$(curl -s "$OFFLOAD_HOST/api/native-scans/results/$SCAN_ID" -H "X-API-Key: $OFFLOAD_API_KEY" \
  | jq '[.scan_result.findings[] | select(.severity=="high" or .severity=="critical")] | length')
[ "$CRIT" -gt 0 ] && { echo "❌ $CRIT high/critical findings"; exit 1; } || echo "✅ clean"
```

For a turnkey GitHub Action and the dedicated CI/CD endpoints, see
[CLI & CI/CD](../cli-and-cicd.md).
