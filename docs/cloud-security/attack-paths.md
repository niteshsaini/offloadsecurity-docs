---
title: "Attack Path Analysis"
sidebar_label: "Attack Path Analysis"
sidebar_position: 6
---

# Attack Path Analysis

Individual findings rarely tell the whole story. **Attack Path Analysis** connects them — it builds a graph of your environment and shows how an attacker could chain misconfigurations, vulnerabilities, and exposed resources together to reach a high-value asset. Instead of a flat list of issues, you see the *routes* that matter, so you can fix the one weak link that breaks an entire attack path.

![Security graph and attack paths](/img/screenshots/attack-paths.png)

## What it does

- **Builds a security graph** from your connected data — assets, findings, vulnerabilities, container images, and Kubernetes resources become nodes; relationships and exposures become edges.
- **Discovers attack paths** — chains of nodes that lead from an entry point (for example, an internet-exposed resource) to a sensitive target.
- **Maps to MITRE ATT&CK** — each step is labeled with the relevant technique so you can reason about attacker behavior.
- **Scores and prioritizes** — every path gets a risk score and an estimated **blast radius**, so you know which paths to cut first.
- **Recommends remediation** — highlights the highest-leverage node to remediate to break the most paths.

## How to use it

1. Open **Attack Path Analysis** from the Cloud & Infrastructure section.
2. Review the **security graph** — the overview shows total nodes and edges and the breakdown by type (findings, vulnerabilities, assets, and more).
3. Select a path to inspect its **steps**: the source, each hop, the techniques involved, and the target asset.
4. Use the **risk score** and **blast radius** to prioritize — focus on paths that reach your most critical assets.
5. Apply the recommended remediation, then re-scan; resolved findings drop out of the graph and shorten or eliminate the path.

:::tip[Tip]
Attack Path Analysis is only as complete as your connected data. The more you connect — cloud accounts, container registries, and Kubernetes clusters — the richer and more accurate the graph becomes.
:::

## Related

- **[Asset Inventory](./asset-inventory.md)** — the resource catalog the graph is built from.
- **[Cloud Security](./index.md)** — the posture findings that become graph nodes.
- **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)** — triage the vulnerabilities that appear in attack paths.
- **[Risk Management](../vulnerability-risk/risk-register.md)** — promote a critical path into a tracked risk.
