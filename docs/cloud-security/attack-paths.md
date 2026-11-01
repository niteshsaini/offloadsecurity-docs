---
title: "Attack Path Analysis"
sidebar_label: "Attack Path Analysis"
sidebar_position: 11
description: "Explore the security graph built from your cloud, identity, container and Kubernetes data, find attack paths and toxic combinations mapped to MITRE ATT&CK, check any node's blast radius, and find the fixes that cut the most paths."
---

# Attack Path Analysis

Individual findings rarely tell the whole story. A public instance is one finding; an over-privileged role attached to it is another; a customer database that role can read is a third. **Attack Path Analysis** connects them — it builds a graph of your environment and shows the *routes* an attacker could take, so you can fix the one link that breaks a whole path instead of working three tickets in isolation.

**Where:** left navigation → **Attack Path Analysis** (under *Cloud & Infrastructure*).

![Security Graph & Attack Paths: 37 nodes, 38 edges, 13 publicly exposed, tiles for critical paths and toxic combinations, graph node distribution by type and relationship types](/img/screenshots/cloud-security/attack-paths.webp)

## How it works

1. **The security graph** holds what the platform already knows — cloud assets and findings, identities and their evaluated access from [identity analysis](./identity-and-network.md#iam-analysis), internet reachability verdicts, container images and their vulnerabilities, Kubernetes namespaces and workloads — as **nodes** (cloud resource, data store, identity, network, vulnerability, finding, container image, k8s cluster / namespace, service) and **edges** (`has_finding`, `connects_to`, `has_access`, `can_escalate_to`, `runs_as`, `contains`, `runs_on`, `has_vulnerability`, …). It is rebuilt automatically after every completed scan; **Sync Graph** rebuilds it on demand.
2. **Run Attack Path Analysis** searches for routes of up to **5 hops** from an entry point — an internet-exposed resource, the Internet node, or an external (cross-account) principal — to a data store, and evaluates **20 toxic-combination rules** — for example *public resource with an identity path to a data store*, *public data store with a high/critical finding*, *container with a critical CVE on a public-facing host*, *admin IAM identity with a high/critical finding*, *cross-account trust to an external entity*, *public Kubernetes cluster with a critical finding*. Each path's steps are annotated with **MITRE ATT&CK** tactics and techniques.
3. **Analytics** rank what to fix: **choke points** (the edges most attack paths pass through), **blast radius** (everything reachable from a node), **root-cause groups** (findings that share one underlying cause) and a **remediation** plan you can simulate.

The graph is only as complete as the data behind it. Connect cloud accounts, container registries and Kubernetes clusters, and let identity analysis and the reachability refresh run on key accounts, and the paths get sharper.

:::note[Paths are not recomputed automatically]
The graph syncs after each scan, but the path analysis runs when you start it. Run it again after significant changes. The line under the header says which analysis you are looking at (*Showing the analysis from …*) and turns amber when it is more than a day old.
:::

## The tabs

| Tab | What you see |
| --- | --- |
| **Overview** | Node and edge counts, how many nodes are **publicly exposed**, critical paths and toxic combinations found, the node distribution by type, relationship types, the finding-severity breakdown and the **highest attack surface** (most-connected assets). |
| **Graph Explorer** | An interactive canvas of the graph — see [Graph Explorer](#graph-explorer) below. |
| **Attack Paths** | Each detected path: entry point → hops → target, its severity and score, MITRE tactics/techniques per step, and the affected assets. Click a row to draw the path; **Load more** pages through every stored path. |
| **Choke Points** | Edges ranked by how many paths (and critical paths) they carry, with blast-radius buttons for either end — remove the top one and several paths disappear at once. |
| **Remediation** | The shortest list of fixes that breaks the critical paths, ordered by how many still-open critical paths each one breaks. Untick a fix to simulate the result without it. |
| **Toxic Combinations** | The matched toxic-combination rules grouped by severity, with the resources involved. If some rules failed to evaluate, the tab says so. |
| **Blast Radius** | Pick any node to see everything reachable from it and the findings there — the "if this box is popped, what else is exposed?" view. |
| **Root Cause Groups** | One CVE or one misconfiguration shared by many resources, so one fix closes many findings. |

### Graph Explorer

The **Graph Explorer** tab draws the graph so you can investigate it directly.

- **Filters** (applied on the server): node type, cloud, account, **only internet-exposed**, **only with findings**, and a search on name, ID or ARN. The counts show how many nodes are drawn, how many matched, and how many the graph holds. The canvas draws at most **1,000 nodes**; when more match, it says so and asks you to narrow the filters — nothing is dropped silently.
- **Markers**: internet-exposed nodes and nodes with findings are marked. Evaluated identity edges are drawn solid; assumed (heuristic) ones dashed.
- **Node panel**: click a node for its details, its linked findings (*N of total*), a link to the owning module (Asset Inventory, Vulnerability Management, Container Security or Kubernetes), its edges with their evidence, and its **blast radius** with a depth control — highlighted on the canvas with counts by type. Reachable nodes outside the current view are counted, not dropped.

### Identity edges and their evidence

Identity edges (`has_access`, `can_escalate_to`) come from [identity analysis](./identity-and-network.md#how-effective-permissions-are-evaluated). Each one carries evidence chips in the node panel:

| Chip | Meaning |
| --- | --- |
| **evaluated** | Derived from the policies themselves — AWS identity and resource policies, permission boundaries and SCPs (cross-account included); GCP IAM (inherited bindings, custom roles, deny policies); Azure RBAC (role definitions, deny assignments), including managed-identity takeover. |
| **not evaluated · &lt;reason&gt;** / **assumed** | Inferred from flags and role names, or from policies that could not be read completely. Treat these as leads to verify, not proof. |
| **conditional · &lt;keys&gt;** | The grant has conditions; they are listed, not simulated. |
| **cross-account · store in &lt;account&gt;** | A principal in one AWS account can reach a store in another. |
| **via organization share · &lt;org&gt;** | The edge exists because the resource's policy shares it with an AWS organization. |
| **one of N targets (strongest kept)** | The edge stands for several targets and only the strongest is drawn. |

Paths that cross an identity edge are marked *identity hop · heuristic* in the Attack Paths list.

## Reading a path

- **Score** = the sum of the findings on the path's nodes (by default critical 40, high 20, medium 10, low 5 each). **40 or more is critical**, 20 or more is high.
- A **Crown jewel** or **High value** badge grades the target by its criticality, data classification, sensitive tags (such as PII or PCI) and resource type (databases and secret stores rank high).
- A resource that [network reachability](./identity-and-network.md#internet-reachability) **verified as not reachable** from the internet is not used as an entry point, even if a finding mentions public exposure. Public access granted by a resource policy (anyone) still counts.
- An amber notice appears when an entry-point / data-store pair reached the per-pair route limit, or the search ran out of its work budget; the list and counts may then be missing paths, and the notice gives the count.

### Why 0 critical attack paths?

When the analysis finds no critical path, the **Why 0 critical attack paths?** box explains it from the analysis's own diagnostics. It checks, in turn, and names the first one missing: entry points in the graph, data stores in the graph, a route from an entry point to a data store within 5 hops, and whether the riskiest route reaches the critical threshold (*"… the riskiest one scores N; a critical path needs 40."*). An empty result is never presented as proof that nothing exists.

## Using it

1. Make sure the graph is current — it syncs after each scan; choose **Sync Graph** from the **Analysis** menu in the header after onboarding new sources.
2. Choose **Run Attack Path Analysis** from the same menu (needs the **Manage Risks** permission). It runs in the background; start on the **Overview** tile counts, then open **Attack Paths**.
3. For the top path, check **Choke Points** and **Remediation** — the fix that cuts the most paths is usually cheaper than fixing every finding along one path.
4. Apply the fix in the owning module and your cloud, re-scan, and re-run the analysis: resolved findings drop out of the graph and the path shortens or disappears.
5. Promote a path you cannot fix quickly into the [Risk Register](../vulnerability-risk/risk-management/index.md) so it is tracked and owned.

:::tip[Blast radius for incident response]
During an incident, search for the compromised asset in **Graph Explorer** (or pick it in **Blast Radius**) to get the identities, data stores and networks reachable from it — a ready-made containment scope.
:::

## If something looks wrong

- **"Graph is empty"** — Choose **Sync Graph**, then **Run Attack Path Analysis**. If it stays empty, no scan results exist yet.
- **"No analysis run yet"** — Choose **Run Attack Path Analysis** from the Analysis menu.
- **"the graph has no entry point …"** — Nothing in the graph is internet-exposed and no external principal exists. Check that cloud scans ran, and that network reachability and identity analysis have run for the accounts.
- **"This analysis was stored before full path sets were kept …"** — Run the analysis again to list every path.
- **Identity edges missing or old** — If identity analysis did not complete for an account, its edges are from an older run or missing; Cloud Security → **IAM Analysis** shows the last attempt's outcome.

## Related

- [Asset Inventory](./asset-inventory.md) — the resource catalog the graph is built from.
- [Identity & Network Posture](./identity-and-network.md) — identity analysis and internet reachability populate the identity and exposure layers of the graph.
- [Container Security](../security-scanning/containers/index.md) and [Kubernetes Security](../security-scanning/kubernetes/index.md) — the image and cluster layers.
- [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) — triage the vulnerabilities that appear in paths.
