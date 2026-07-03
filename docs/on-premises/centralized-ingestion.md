---
title: "Centralized Security Data Ingestion"
sidebar_label: "Centralized Ingestion"
sidebar_position: 5
---

# Centralized Security Data Ingestion

The point of on-premises support is not to add another dashboard — it's to remove one. Every internal capability the platform provides feeds a **single, correlated source of truth** that also holds your cloud, application, and container posture. This page explains what "centralized ingestion" actually means and why it's the difference between coverage and clarity.

## One dashboard, every source

Offload Security ingests and correlates:

- **Cloud posture** — AWS, Azure, GCP misconfigurations and native findings.
- **Application, API, code, and container** findings.
- **Internal-network discovery** and private URL/API scan results.
- **OpenVAS** internal vulnerability scans.
- **Wazuh** endpoint events, alerts, vulnerability state, SCA, and FIM.
- **Threat intelligence** and third-party scanner data via integrations.

All of it resolves against **one model** of assets, findings, controls, and evidence — so the internal database server, the CVE OpenVAS found on it, the Wazuh events from it, and the compliance control it supports are all connected.

## What unification changes

### One inventory
Cloud resources and internal assets live in the same **[Asset Inventory](../cloud-security/asset-inventory.md)**. An asset has one identity, whether it was discovered in a cloud account or on an internal subnet.

### One triage queue
Internal-host CVEs, cloud misconfigurations, application bugs, and Wazuh detections are deduplicated and prioritized together in **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)** and **[Alerts](../integrations/notifications.md)** — so analysts work one list, not six.

### One risk and compliance view
Findings from every source — cloud and on-prem alike — promote into the same **[Risk Register](../vulnerability-risk/risk-register.md)** and map to the same **[compliance controls](../compliance/index.md)**, producing one **[evidence vault](../compliance/evidence-hub.md)** and one set of **[reports](../vulnerability-risk/index.md)**.

## Correlation is the value

Separate tools can each be excellent and still leave you blind, because the risk that matters most often only appears when sources are combined:

- An **internal host** (Asset Inventory) with a **critical OpenVAS CVE** *and* **anomalous Wazuh activity** is a very different priority than any one of those signals alone.
- A **failed SCA compliance check** (Wazuh) on a host that also has an **open vulnerability** ties an operational finding directly to a control gap and its evidence.

Centralized ingestion is what makes those connections visible automatically, instead of requiring an analyst to notice them across three consoles.

## Data residency and control

Because the internal scanning and telemetry engines run **inside your network**, centralized ingestion does not mean shipping raw internal data to a third party by default. On-prem and hybrid deployments keep sensitive telemetry within your boundary while still delivering a unified view — a requirement for many banks, healthcare providers, and regulated enterprises. For deployment topologies and data-flow options, see **[Deployment](../infrastructure/deployment.md)**.

## The outcome

One place to answer the questions that matter:

- *What do we have?* — a complete inventory, cloud and internal.
- *What's wrong with it?* — every finding, deduplicated and prioritized.
- *How bad is it?* — risk, trended over time, across the whole estate.
- *Can we prove we're managing it?* — continuous, mapped evidence.

That is the promise of centralized ingestion: not more data, but one trustworthy picture of all of it.
