---
title: "Welcome to Offload Security"
sidebar_label: "Welcome"
sidebar_position: 0
slug: "/"
---

# Offload Security

**Offload Security is a unified CNAPP, vulnerability management and compliance platform that consolidates findings across cloud, code, containers, Kubernetes, applications, on-premises infrastructure and existing security tools into one governed risk view.** It brings cloud security, vulnerability management, container and Kubernetes security, code and supply-chain security, compliance and risk (GRC), threat intelligence, and AI-driven security operations together in a single, multi-tenant platform — so your team works from one source of truth instead of a dozen disconnected tools.

This documentation helps you **onboard, configure, and operate** the platform end to end — whether you're connecting your first cloud account or rolling it out across a security organization.

:::tip New here?
- **Understand the "why"** → **[Introduction](./introduction/index.md)**: what Offload Security is, the problem it solves, and why to choose it over fragmented tools.
- **Cover your private infrastructure** → **[On-Premises & Private Infrastructure](./on-premises/index.md)**: internal-network visibility, OpenVAS scanning, and the Wazuh integration.
- **See it for your sector** → **[Solutions by Industry](./industries/index.md)**, including a detailed **[Banking & Financial Services](./industries/banking-financial-services.md)** breakdown.
- **Just get running** → jump straight to **[Getting Started](./getting-started.md)**.
:::

---

## What you can do with it

Offload Security is organized into five areas that map directly to the product's left-hand navigation.

### 🛡️ Core Security
Run and review security testing from one place.
- **Dashboard** — security posture, metrics, and recent activity at a glance.
- **Scanning** — web (OWASP ZAP, Nuclei), network (Nmap), SSL/TLS (testssl.sh), and API security testing.
- **Code Command Center** — SAST (OpenGrep, Bandit, Checkov), secrets detection (GitLeaks), and SBOM-based open-source **license compliance**.
- **Vulnerability Management** — triage, risk scoring, SLA tracking, deduplication, and remediation guidance.
- **Security Reports** — executive, compliance, and audit reports in PDF, HTML, and Excel.

### ☁️ Cloud & Infrastructure
Continuously assess everything you run in the cloud.
- **Cloud Security (CSPM)** — AWS, Azure, and GCP misconfiguration scanning with native findings ingestion (GuardDuty, GCP Security Command Center, Azure Defender).
- **Container Security** — image scanning across ECR, GCR, ACR, and Docker Hub, with SBOMs, signature verification, and secret detection in layers.
- **Kubernetes Security** — cluster scanning (kube-bench, Polaris, Kubescape, Trivy) mapped to the MITRE ATT&CK Container Matrix.
- **Asset Inventory** — a live catalog of cloud resources across accounts and regions.
- **Attack Path Analysis** — graph-based discovery of exploitable paths to high-value assets.

### 📋 Compliance & Risk
Turn findings into audit-ready governance.
- **Compliance Posture** — track frameworks (SOC 2, ISO 27001, NIST CSF, PCI-DSS, and more) with control status and drift detection.
- **Risk Management** — an enterprise risk register with treatment plans and SLAs, auto-minted from findings.
- **Assessments** — guided, auto-scored assessments (OWASP ASVS 5.0, NIST CSF 2.0, NIST SSDF, SOC 2, SAMM, and others).
- **Audit Reports** & **DPDP Compliance** — evidence packages and India DPDP data-protection tracking.

### 🧠 Threat & Intelligence
Add context and automation to detection.
- **Threat Intelligence** — multi-feed ingestion (CISA KEV, NVD, OTX) with IOC correlation against your assets.
- **AI Governance** — EU AI Act risk-tier classification and governance controls for your AI systems.
- **Security Command Center (AI-SOC)** — AI-assisted incident correlation and prioritization.

### ⚙️ Management
Configure, integrate, and administer.
- **Account Setup**, **Integrations** (Slack, webhooks, CI/CD), **Unified Scheduler**, **Knowledge Base**, and **Team Management** (roles, API keys).

---

## Who this is for

| Audience | Where to focus |
|---|---|
| **Security engineers & analysts** | Scanning, Vulnerability Management, Container/K8s, Threat Intelligence |
| **CISOs & security leaders** | Dashboard, Risk Management, Compliance, Reports |
| **Compliance officers & auditors** | Compliance Posture, Assessments, Audit Reports |
| **DevSecOps teams** | CLI & CI/CD integration, Code Command Center, Container Security |
| **Platform operators (self-hosting)** | Onboarding & Setup, Reference, Operations |

---

## Start here

1. **[Getting Started](./getting-started.md)** — sign in and take a tour of the dashboard and core concepts.
2. **Connect your environment** — add a [cloud account](./cloud-security/account-management.md) (AWS, Azure, GCP), a container registry, or a Kubernetes cluster.
3. **Run your first scan** and review findings in [Vulnerability Management](./vulnerability-risk/vulnerability-management.md).
4. **Automate it** — wire scans into your pipeline with [CLI & CI/CD integration](./security-scanning/scan-management.md).

:::note A note on accuracy
This documentation describes capabilities that exist in the platform today. Where a feature requires specific configuration, prerequisites, or permissions, those are called out explicitly so you can plan accordingly.
:::

## Need help?

- Visit [offloadsecurity.com](https://offloadsecurity.com) for the platform.
- See the **[Glossary](./glossary.md)** for key terms used throughout this documentation.
