---
title: "Check where an image runs and whether a fix has rolled out"
sidebar_label: "Image Rollout"
sidebar_position: 4
new_in: 1.4.0
description: "Find the Kubernetes workloads that run a container image, matched by digest, and confirm that every running container has moved to the fixed build."
---

# Check where an image runs and whether a fix has rolled out

The **Rollout** tab joins an image to the running containers recorded by your Kubernetes cluster scans. It answers two questions: *where does this image run?* and *has the fixed build replaced the old one everywhere?* A check takes a few seconds.

## Before you begin

- Role with **View Scans**.
- The clusters that run the image are onboarded in [Kubernetes Security](../kubernetes/onboarding-clusters.md) and were scanned recently. Running images are recorded by cluster scans; a snapshot older than 48 hours (`K8S_RUNNING_SNAPSHOT_MAX_AGE_HOURS`) does not count as current.
- For the rollout check: the fixed image has been scanned, or you know its digest (`sha256:…`).

## Steps

1. **Open Container Security → Rollout.**
2. **Enter the image**, for example `registry/team/app:1.4`.
3. **Optional: enter the target digest** of the fixed build. Without it, the digests from the image's latest completed scan are used — the index digest and its platform digests.
4. **Select Check.**

## Check that it worked

The first line says where the image runs:

| Result | Meaning |
| --- | --- |
| **Running in N workload(s) · matched by digest** | Exact match on the content digest. Exposed workloads are counted. |
| **… matched by tag only** | No digest match; the tag may point at another build. |
| **Not running in any scanned cluster.** | Every cluster has a complete, current snapshot and none runs the image. |
| **Unknown: …** | No cluster has reported its running images yet, or a snapshot is incomplete. Never read this as "not running". |

Below it, the rollout status:

- **Rollout complete** — every running container of the image's repository runs the target build.
- Otherwise, the containers still on another build are listed with cluster, namespace and workload, plus any whose digest is unknown, and the ones already on the target.

Workloads are reported as their Deployment (not the ReplicaSet), so a rollout in progress does not look like a new workload.

## How this feeds triage

The same running-workload data sets the **workload exposure** of container and Kubernetes findings in the triage score:

| Verdict | When | Effect on priority |
| --- | --- | --- |
| **Exposed** | Running, and a LoadBalancer or NodePort Service, Ingress, externally attached Gateway API / Istio / OpenShift route, external IP, `hostNetwork` or `hostPort` reaches it from outside the cluster | Raised |
| **Not exposed** | Running, complete snapshot, nothing routes to it | — |
| **Not running** | Complete, current snapshots and nothing runs it | Lowered |
| **Not evaluated** | Anything the platform could not see | Unchanged — unknown never lowers priority |

The Triage queue shows *running · N workloads · N exposed*, *not deployed* or *deployment unknown* on each finding, and the score's drivers name the exposure path. See [Triage](../../vulnerability-risk/vulnerability-management/triage.md).

## If something goes wrong

- **"No completed scan of this image, so there is no target build to compare against; give a target digest."** — Scan the new image first, or paste its digest into **Target digest**.
- **Always "Unknown"** — No onboarded cluster has a current running-image snapshot. Scan the clusters, then check again.
- **More than 500 clusters** — Only the first 500 are read; an image that is not found among them shows *Unknown*, not *Not running*.
- Images running outside Kubernetes clusters onboarded in this platform are not seen.

## Next steps

- [Image Scanning — a moved tag supersedes](./image-scanning.md#moved-tag) — why the old build's findings stay visible until it is gone.
- [Kubernetes Security — Scanning & Findings](../kubernetes/scanning-and-findings.md) — keep cluster snapshots current.
