---
title: "Centralized Security Data Ingestion"
sidebar_label: "Centralized Ingestion"
sidebar_position: 6
description: "What is actually unified when cloud, code, container, Kubernetes, DAST, network and Wazuh data land on one platform — the shared asset inventory, the unified findings lake behind triage, one alert stream, one risk register and one evidence store — and where correlation happens automatically versus where it is still a person's job."
---

# Centralized Security Data Ingestion

The reason to run one platform instead of six tools is not the dashboard; it is that the tools' outputs become **one model** — assets, findings, alerts, risks, controls, evidence — with identity carried across sources. This page says, source by source, what actually converges, so that "single pane of glass" is a description and not a slogan.

## What each source contributes

| Source | Assets | Findings | Alerts | Evidence |
| --- | --- | --- | --- | --- |
| **Cloud scans** (AWS, Azure, GCP) | Every discovered resource, with identity and network context | Misconfigurations as cloud findings → unified findings | New / reopened critical and high findings | Control evidence auto-collected per framework |
| **Kubernetes** and **container** scans | Clusters, workloads, images, registries | Cluster misconfigurations, image CVEs → unified findings | Critical / high | Container and K8s compliance reports |
| **Code scans** (SAST, secrets, SCA, IaC) | Repositories | Code findings → unified findings; SBOMs → AIBOM | Critical / high | SBOMs, licence notices |
| **Web / API / TLS / network scans** (public or [private](./private-infrastructure-scanning.md)) | — | Scan findings → unified findings | Critical / high | Per-scan reports |
| **Wazuh** | Endpoints, correlated with their cloud VM | Host CVEs → vulnerability occurrences | Rule-level ≥ 7 detections | SCA / FIM browsed (not stored) |
| **Threat feeds** | — | Enrich findings (KEV, EPSS, indicators) | — | — |
| **Greenbone / OpenVAS**, catalog-only tools | — | Not imported today | — | — |

## What "unified" means, concretely

- **One inventory.** [Asset Inventory](../cloud-security/asset-inventory.md) holds cloud resources, Kubernetes clusters, repositories and Wazuh endpoints under one identity scheme; a Wazuh agent on an EC2 instance is the same asset the cloud scan discovered, not a duplicate. The security graph behind [Attack Paths](../cloud-security/attack-paths.md) is built from the same records.
- **One findings lake.** Every scanner writes into the unified findings store with a **fingerprint** (source, check, resource), so a re-scan updates a finding instead of creating another, a finding that disappears is reconciled as resolved, and the same CVE on an image and on a host are two occurrences of one vulnerability. [Triage](../vulnerability-risk/vulnerability-management/triage.md) scores across all of them with one formula — severity, KEV, EPSS, exposure, environment, age.
- **One alert stream.** Cloud, container, code, DAST and Wazuh events all pass through the same `record_alert` chokepoint into [Alerts](../vulnerability-risk/alerts.md), de-duplicated with occurrence counts, routed by the same [notification](../integrations/notifications.md) rules and SLAs.
- **One risk register and one evidence store.** Findings from any source promote into the [Risk Register](../vulnerability-risk/risk-management/index.md); compliance evidence from cloud, container and Kubernetes scans lands in the [Evidence Hub](../compliance/evidence-hub.md) against SCF controls, so a framework score reflects the whole estate the platform can see.

## Where correlation happens automatically — and where it does not

| Automatic today | Still a person's job |
| --- | --- |
| Wazuh endpoint ↔ cloud VM (hostname, then IP) | Wazuh host CVE ↔ OpenVAS result for the same host (OpenVAS is not imported) |
| Same finding across scans (fingerprint), same CVE across images and hosts (occurrences) | Same *application* across a code repository, its container image and its running workload — linked where names match, not asserted |
| KEV / EPSS / indicator enrichment on every finding | Reading a Wazuh SCA failure as evidence for a specific control (browse, then attach) |
| Finding ↔ alert ↔ SLA ↔ ticket lifecycle | Business context (owner, criticality) — set on assets by you, then used by SLAs and risk multipliers |

## Data residency

On an on-premises install every store above is yours: MongoDB and Redis on your host, evidence and reports in your object storage, scanners on your network. Nothing about your findings leaves unless you configure an outbound destination — a Slack channel, a Jira project, a webhook, an LLM provider — and those are per-team choices you can see in [Integrations](../integrations/index.md). The feeds and vulnerability databases the platform *pulls* carry nothing about you.

## Related

- [Unified data layer](../introduction/unified-data-layer.mdx) — the design behind the findings lake.
- [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) — where the unified queue is worked.
- [Deployment & Operations](./deployment.md) — where the stores live on-premises.
