---
title: "Kubernetes API"
sidebar_label: "Kubernetes"
sidebar_position: 5
description: "Onboard a Kubernetes cluster with a kubeconfig over the API, list clusters, test connectivity, start a scan, and compare two scans."
---

# Kubernetes API

Onboard any cluster (EKS, GKE, AKS or on-prem) with **read-only** credentials,
then scan it. The kubeconfig is safety-validated and stored encrypted.

> Required: an API key with **`scans:trigger`** for writes (`scans:read` for
> reads); the `/api/k8s` family maps to the scan scopes. The key's owner needs
> **Manage Container Security** to onboard and test clusters and **Run Scans**
> to start scans. See [Required Permissions](../cloud-security/permissions.md)
> for the in-cluster RBAC the credentials need.

## Onboard a cluster

```
POST /api/k8s/clusters
```

The `credentials` field is your **base64-encoded kubeconfig**. Encode it first:

```bash
export KUBECONFIG_B64=$(base64 -i ~/.kube/config | tr -d '\n')
```

**Request body**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | string | ✓ | Unique within your team (1–255 chars) |
| `provider` | string | ✓ | `aws` \| `gcp` \| `azure` \| `on-prem` \| `other` |
| `onboard_method` | string | ✓ | Use `kubeconfig` |
| `credentials` | string | ✓ | **Base64-encoded** kubeconfig. It is always parsed and validated as a kubeconfig, so a token goes inside a kubeconfig `user` entry |
| `project` | string | — | Groups clusters in the UI |
| `rbac_mode` | string | — | `minimal` (default) or `extended` |
| `api_server` | string | — | API server URL (also deduplicated per team) |
| `metadata` | object | — | Arbitrary key/values |

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

**Response `201 Created`**, a cluster object (returned directly):

```json
{
  "cluster_id": "clus_9f2a4c1b7e3d5a60",
  "name": "production-gke",
  "project": "platform",
  "provider": "gcp",
  "onboard_method": "kubeconfig",
  "rbac_mode": "minimal",
  "api_server": "https://34.x.x.x",
  "status": "pending",
  "metadata": { },
  "created_by": "…",
  "created_at": "2026-11-01T12:00:00Z",
  "has_credentials": true
}
```

Onboarding is metadata-only: no live connection is made and **no scan starts**.
The cluster stays `pending` until you test it or scan it. Check the HTTP status
(`201`) rather than looking for a `success` field.

:::warning[Kubeconfig safety validation]
The platform **rejects** kubeconfigs that use `exec:` credential plugins,
`cmd:`-based token sources, `tokenFile` / `token-file` references, or
`insecure-skip-tls-verify: true` (the first three would run commands or read
files on the scanner). Such a kubeconfig returns **400 `Unsafe kubeconfig: …`**.
Use a static token or client-certificate kubeconfig, or a service-account token.
:::

Many clusters at once: `POST /api/k8s/clusters/bulk-import` (up to 200 per
request by default, runs as a background job, optional paced `auto_scan`).

## List clusters

```
GET /api/k8s/clusters?provider=gcp&page=1&page_size=50
```

Filters: `provider`, `status` (`active` / `pending` / `scanning` / `error` /
`degraded`). Paging: `page` and `page_size` (max `500`).

```json
{ "clusters": [ { "cluster_id": "clus_…", "name": "production-gke", "status": "active" } ],
  "total": 12, "page": 1, "page_size": 50, "summary": { } }
```

`summary` (page 1 only) counts every matching cluster, not just the page.

## Test connectivity

Probe a stored cluster. Returns the live version, node count and namespaces:

```
POST /api/k8s/clusters/{cluster_id}/test
```
```bash
curl -s -X POST "$OFFLOAD_HOST/api/k8s/clusters/clus_9f2a4c1b7e3d5a60/test" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```
```json
{ "success": true, "message": "Successfully connected to cluster",
  "details": { "version": "1.28.0", "nodes": 10, "namespaces": 25 } }
```

## Start a scan

```
POST /api/k8s/scan
```

| Field | Type | Notes |
| --- | --- | --- |
| `cluster_id` | string | **Required** |
| `scanners` | string[] | Default `["trivy", "polaris", "kubescape"]`. `kube-bench` is accepted but always reports not applicable for a remotely scanned cluster |
| `severity_filter` | string[] | `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` (any case) |
| `namespace_filter` | string[] | Limit to these namespaces |
| `engagement` | object | Authorization attestation, kept as the cluster's standing authorization. See [Engagement record](./scans-and-results.md#engagement-record) |

Returns **`202`** with `{ "scan_id", "cluster_id", "status": "pending", … }`. If
a scan of that cluster is already running, the response is **`200`** with that
scan instead of starting a second one.

Poll `GET /api/k8s/scan/{scan_id}` until `status` is `completed`, `failed`,
`timeout` or `cancelled`. A degraded scan is stored as `completed`: check
`scan_health` (`ok` / `degraded` / `failed`), `outcome` (`complete` / `partial`
/ `failed`) and `successful_scanners` before trusting the result.

## Compare two scans

:::note[New in 1.4.0 · API-only]
There is no UI for this comparison in 1.4.0.
:::

```
GET /api/k8s/scans/{scan_id}/compare?base={earlier_scan_id}
```

Finding-level comparison of two scans of one cluster, from each scan's frozen
findings. Without `base`, the previous completed scan of the cluster is used.
Needs `scans:read`. Response (in the `data` envelope):

| Field | Meaning |
| --- | --- |
| `counts` | `new`, `fixed`, `triaged`, `not_reevaluated`, `persisting` |
| `new` / `fixed` | Findings that appeared or disappeared |
| `triaged` | Gone because a user suppressed or accepted the finding, not fixed |
| `not_reevaluated` | Gone, but the later scan could not have seen it (its scanner failed, or the namespace was denied or out of scope); never counted as fixed |

Lists are complete (no cap), and each scan's frozen findings file is checked
against its SHA-256 first. Returns `404` when a scan (or the `base` scan for
this cluster) is not found in your team, and `409` when a scan has no frozen
findings, a frozen file fails its SHA-256 check, or there is no earlier
completed scan to compare with.

## Errors

| Status | Cause |
| --- | --- |
| `400` | Invalid base64, `Unsafe kubeconfig: …` (see above), or `Scan not authorized: …` (engagement) |
| `403` | Key lacks the scope, or owner lacks *Manage Container Security* / *Run Scans* |
| `404` | Cluster or scan not found in your team |
| `409` | A cluster with that `name` (or `api_server`) already exists in your team; or a cluster that was discovered but not imported |

## Related

- [Kubernetes Security](../security-scanning/kubernetes/index.md): what the scans cover
- [Required Permissions](../cloud-security/permissions.md)
