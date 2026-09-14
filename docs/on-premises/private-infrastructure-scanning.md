---
title: "Private Infrastructure & Internal URL/API Scanning"
sidebar_label: "Private Infrastructure Scanning"
sidebar_position: 3
description: "Point the platform's web, API, TLS, header and network scanners at targets that only resolve inside your network — what the operator must enable, how the worker reaches the target, and where the findings go."
---

# Private Infrastructure & Internal URL/API Scanning

The scanners that assess your public applications are the same ones that assess the internal ones; the only difference is reachability. On an on-premises install the scan workers run on your network, so an intranet portal, a staging API, an internal admin console or a database listener is a target like any other — once the operator has said so.

## What you can scan

| Target | Assessment | Engine |
| --- | --- | --- |
| Internal web applications (`https://portal.corp.local`, `http://10.20.30.40:8080`) | **Web Vulnerability** and **Nuclei** scans, authenticated where needed; or a full **App Scan** | OWASP ZAP, Nuclei |
| Private APIs (REST, GraphQL, service-to-service) | **API Security Testing** (OWASP API Top 10) and **API Discovery / Deep Scan** from a URL or an OpenAPI specification | native API scanner |
| Internal TLS endpoints | **SSL/TLS Security Test** — protocols, ciphers, certificate chain | testssl.sh |
| Any HTTP service | **Security Headers Check** | native analyzer |
| Hosts, ranges, CIDRs | **Network Discovery** — sweep, top-1000 ports, service / version detection | nmap |
| Internal container images and registries | Image scanning; private registries with credentials | Trivy, Syft / Grype — see [Container Security](../security-scanning/containers/index.md) |
| On-premises Kubernetes clusters | Cluster onboarding and scanning over a kubeconfig or the agent | see [Kubernetes Security](../security-scanning/kubernetes/index.md) |

## What the operator enables

1. **`ALLOW_PRIVATE_SCAN_TARGETS=true`** in `.env`, for the backend and the workers. Private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) become valid targets; loopback, link-local and cloud-metadata addresses (`169.254.169.254`) remain blocked whatever the setting.
2. **Name resolution** — the worker containers use the host's DNS; internal names must resolve there (or use IPs).
3. **Reachability** — the host running the stack needs a route and firewall path to the target segment. Scanner containers are siblings on the host's Docker network, so "can the host reach it" is the test.
4. **Private CAs** — set `INTEGRATION_VERIFY_SSL` / `SMTP_CA_CERT` for integrations and mail; scans of internal HTTPS services with a private certificate report the trust issue as a TLS finding rather than failing.

The target check resolves DNS, so a public name that points at a private address is treated as private; outbound connections the platform makes itself (webhooks, integrations) re-check at connection time against DNS rebinding.

## Where results go

Exactly where public-target findings go: the scan's own results page (with HTML / PDF / Word export and evidence screenshots for web scans), the unified findings lake behind [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) and [Triage](../vulnerability-risk/vulnerability-management/triage.md), SLAs, alerts, the [Risk Register](../vulnerability-risk/risk-management/index.md) and compliance evidence. An internal finding carries the same severity, KEV/EPSS enrichment and remediation guidance as an external one; what changes is the *internet-facing* signal in triage, which is false for it.

:::tip[Scan staging like production]
Pre-production copies hold production configuration with weaker controls and are the classic first foothold. A weekly web + API scan of staging, authenticated, catches the misconfiguration before the deploy that carries it to production.
:::

## Related

- [Scanning](../security-scanning/native-scans.md) — assessment types, authentication, rate limits.
- [Internal Network Visibility](./internal-network-visibility.md) — finding the targets first.
- [Deployment & Operations](./deployment.md) — the `.env` switches and network placement.
