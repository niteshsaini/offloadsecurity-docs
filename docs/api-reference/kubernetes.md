---
title: "Kubernetes API"
sidebar_label: "Kubernetes"
sidebar_position: 5
description: "Onboard a Kubernetes cluster with a kubeconfig over the API, list clusters, and run a connectivity test."
---

# Kubernetes API

Onboard any cluster (EKS/GKE/AKS or on‑prem) with **read‑only** credentials, then
scan it. The kubeconfig is safety‑validated and stored encrypted.

> Required permission: **Manage Container Security**. See
> [Required Permissions → Kubernetes](../cloud-security/permissions.md) for the
> in‑cluster RBAC the credentials need.

## Onboard a cluster

```
POST /api/k8s/clusters
```

The `credentials` field is your **base64‑encoded kubeconfig** (or token). Encode it first:

```bash
export KUBECONFIG_B64=$(base64 -i ~/.kube/config | tr -d '\n')
```

**Request body**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | string | ✅ | Unique within your team (1–255 chars) |
| `provider` | string | ✅ | `aws` \| `gcp` \| `azure` \| `on-prem` \| `other` |
| `onboard_method` | string | ✅ | `kubeconfig` \| `token` |
| `credentials` | string | ✅ | **Base64‑encoded** kubeconfig or token |
| `project` | string | ➖ | Groups clusters in the UI |
| `rbac_mode` | string | ➖ | Permission profile — default `minimal` |
| `api_server` | string | ➖ | API server URL (also deduplicated per team) |
| `metadata` | object | ➖ | Arbitrary key/values |

```bash
curl -s -X POST "$OFFLOAD_HOST/api/k8s/clusters" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d "{
    \"name\": \"production-gke\",
    \"provider\": \"gcp\",
    \"onboard_method\": \"kubeconfig\",
    \"credentials\": \"$KUBECONFIG_B64\",
    \"project\": \"platform\"
  }"
```

**Response `201 Created`** — a cluster object:

```json
{
  "id": "clus_9f2a…",
  "name": "production-gke",
  "provider": "gcp",
  "status": "active",
  "api_server": "https://34.x.x.x",
  "created_at": "2026-07-01T12:00:00Z"
}
```

:::note[Treat any 2xx as success]
Onboarding returns **201** with the cluster object. Don't gate success on a
`success: true` field here — check the HTTP status.
:::

:::warning[Kubeconfig safety validation]
The platform **rejects** kubeconfigs that use `exec:` credential plugins,
`cmd:`‑based token sources, or file token references (they'd run arbitrary
commands on the scanner). Such a kubeconfig returns **400 `Unsafe kubeconfig: …`**.
Use a static token or client‑cert kubeconfig, or a service‑account token.
:::

## List clusters

```
GET /api/k8s/clusters?provider=gcp
```
```bash
curl -s "$OFFLOAD_HOST/api/k8s/clusters" -H "X-API-Key: $OFFLOAD_API_KEY"
```

## Test connectivity

Probe a stored cluster — returns live version, node count, and namespaces:

```
POST /api/k8s/clusters/{cluster_id}/test
```
```bash
curl -s -X POST "$OFFLOAD_HOST/api/k8s/clusters/clus_9f2a/test" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

## Errors

| Status | Cause |
| --- | --- |
| `400` | Invalid base64, or `Unsafe kubeconfig: …` (see above) |
| `403` | Key owner lacks *Manage Container Security* |
| `409` | A cluster with that `name` (or `api_server`) already exists in your team |

## Related

- [Kubernetes Security](../security-scanning/kubernetes-security.md) — what the scans cover
- [Required Permissions (GCP)](../cloud-security/permissions.md)
