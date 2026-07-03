---
title: "Internal Network Visibility"
sidebar_label: "Internal Network Visibility"
sidebar_position: 1
---

# Internal Network Visibility

You cannot secure what you cannot see — and for most organizations the least-visible part of the estate is the internal network. Assets appear and disappear as teams stand up servers, connect devices, and deploy internal services, often without central tracking. Internal Network Visibility gives you a continuously updated inventory of what actually exists behind the firewall, so it can be assessed and governed like everything else.

## What it does

- **Discovers internal assets.** Identifies hosts, services, and internal applications reachable inside your network segments — including systems that no cloud console or external scanner will ever list.
- **Builds a living inventory.** Discovered internal assets join the same **[Asset Inventory](../cloud-security/asset-inventory.md)** as your cloud resources, so you have one catalog spanning cloud and on-prem instead of two.
- **Surfaces open services and exposure.** Enumerates listening services and ports on internal hosts, highlighting unexpected exposure inside the perimeter (lateral-movement risk, forgotten services, shadow IT).
- **Feeds downstream assessment.** Once an internal asset is known, it becomes a target for **[OpenVAS vulnerability scanning](./openvas-scanning.md)** and **[private URL/API scanning](./private-infrastructure-scanning.md)**, and a subject for **[Wazuh endpoint monitoring](./wazuh-integration.md)**.

## Why it matters

- **Internal is where lateral movement happens.** Once an attacker has a foothold, the internal network is their playground. Visibility into internal services and their weaknesses is what limits blast radius.
- **Shadow IT and drift.** Internal environments change constantly. Continuous discovery catches the database someone spun up "temporarily" and the service that was supposed to be decommissioned.
- **Audit scope accuracy.** Auditors ask what's in scope. A complete, current internal inventory answers that question with data instead of guesswork.

## How it fits the unified picture

Internal assets are first-class citizens in the platform. A vulnerability found on an internal host is triaged in the same **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)** queue as a cloud misconfiguration, promoted into the same **[Risk Register](../vulnerability-risk/risk-register.md)**, and counted toward the same **[compliance](../compliance/index.md)** controls. There is no separate "internal" dashboard to reconcile.

:::note Network reachability
Internal discovery and scanning run from within your network so they can reach private segments. Which segments are in scope, and how the scanner is positioned, is part of deployment planning handled during onboarding.
:::

## Related capabilities

- **[Private Infrastructure & Internal URL/API Scanning](./private-infrastructure-scanning.md)** — test the internal apps and APIs you discover.
- **[OpenVAS Scanning](./openvas-scanning.md)** — vulnerability-scan internal hosts.
- **[Wazuh Integration](./wazuh-integration.md)** — add endpoint-level security telemetry.
