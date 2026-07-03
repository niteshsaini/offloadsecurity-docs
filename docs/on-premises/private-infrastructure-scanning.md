---
title: "Private Infrastructure & Internal URL/API Scanning"
sidebar_label: "Private Infrastructure Scanning"
sidebar_position: 2
---

# Private Infrastructure & Internal URL/API Scanning

Many of an organization's most sensitive applications are never exposed to the internet: internal admin panels, HR and finance systems, internal APIs and microservices, staging environments, and line-of-business apps reachable only on the corporate network or VPN. Because they're private, they're often *under*-tested — an external SaaS scanner simply can't reach them. Offload Security runs the same application security testing against these internal targets from inside your network.

## What you can scan

- **Internal web applications** — internal portals, dashboards, and line-of-business apps served on private hostnames or IPs.
- **Private APIs and microservices** — internal REST/HTTP services and service-to-service APIs that never leave the network.
- **Non-production environments** — staging, UAT, and pre-prod systems that hold real configurations and often weaker controls.
- **Internal endpoints and services** — any internal URL or host you can point the scanner at.

## What it checks for

The internal scanning capability applies the platform's application and network testing to private targets, including:

- **Web application weaknesses** — the OWASP-style issues surfaced by the platform's web scanning engines (see **[Security Scanning](../security-scanning/index.md)**).
- **API security issues** — authentication, authorization, and input-handling weaknesses in internal APIs.
- **Transport security** — SSL/TLS configuration on internal services.
- **Network exposure** — open ports and services on internal hosts.

Findings are normalized into the same schema as every other source, so an issue on an internal API looks and behaves like any other finding in the platform.

## Why it matters

- **Private doesn't mean safe.** "It's only on the internal network" is not a control. Once inside, an attacker (or a compromised endpoint) can reach these apps directly — and they're frequently the least-hardened systems you run.
- **Test what auditors and attackers actually target.** Internal financial, customer, and admin systems are prime targets. Testing them is often an explicit requirement in regulated environments.
- **Catch it before production risk becomes an incident.** Scanning internal and pre-prod systems moves discovery left, before a weakness reaches customers.

## How results flow

Internal application and API findings land in **[Vulnerability Management](../vulnerability-risk/vulnerability-management.md)** with severity, affected asset, and remediation guidance — deduplicated against other sources, tracked to SLA, and promoted into the **[Risk Register](../vulnerability-risk/risk-register.md)** and **[compliance evidence](../compliance/evidence-hub.md)** just like cloud and code findings.

:::tip Pair with discovery
Point internal scanning at the assets found by **[Internal Network Visibility](./internal-network-visibility.md)** so coverage keeps up automatically as the internal estate changes.
:::

## Related capabilities

- **[Internal Network Visibility](./internal-network-visibility.md)** — find the internal targets to scan.
- **[OpenVAS Scanning](./openvas-scanning.md)** — host-level vulnerability scanning to complement app/API testing.
- **[Security Scanning](../security-scanning/index.md)** — the underlying web, API, network, and SSL testing engines.
