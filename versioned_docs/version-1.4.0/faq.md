---
title: "FAQ"
description: "Short answers to common questions about Offload Security: what it covers, how it secures your data, access and operations, and compliance."
sidebar_label: "FAQ"
sidebar_position: 13
---

# Frequently Asked Questions

## General

**What is Offload Security?**
A unified security platform: cloud posture (CSPM), code and container security, vulnerability management, Kubernetes, on-prem visibility, compliance automation, risk management, and privacy (DPDP) — all feeding one normalized findings model, one risk register, and one reporting layer. Start with [What is Offload Security](./introduction/index.md).

**Is it SaaS or on-premises?**
Both. The managed platform is the default; regulated customers can run the full platform **inside their own environment**, where data never leaves their network. See [On-Premises](./on-premises/index.mdx).

**Which cloud providers are supported?**
AWS, Google Cloud, and Azure — with read-only access wherever the provider supports it. Depth varies by provider: GCP can be onboarded by organization or folder, while AWS accounts and Azure subscriptions are connected one at a time (bulk scans, tests and deletes then work across them). See [Cloud Security](./cloud-security/index.md) and [permissions](./cloud-security/permissions.md).

**Can we keep our existing scanners and tools?**
Mostly by not needing them: the platform runs Prowler, Trivy, Grype, Syft, ZAP, Nuclei, nmap, testssl.sh, Kubescape, Polaris and the code scanners (OpenGrep, Bandit, Gitleaks, OSV, Checkov) itself, so their results are native findings. Of the tools you keep, [Wazuh](./on-premises/wazuh-integration.md) syncs agents, alerts and host CVEs in; [Greenbone OpenVAS](./on-premises/openvas-scanning.md) results are imported into Vulnerability Management; code scanners that export SARIF 2.1.0 can be imported in Code Command Center; SonarQube and Jenkins contribute summaries; Jira works two-way. The [Integration Catalog](./integrations/third-party.md) says, per tool, what flows.

**How are findings prioritized?**
Severity is normalized across sources, then enriched with exploit intelligence — findings on the **CISA KEV** list or with high **EPSS** scores are flagged so actively-exploited issues rise to the top — and with exposure, environment and asset context, including internet exposure of container and Kubernetes workloads. Critical findings can auto-promote into the [Risk Register](./vulnerability-risk/risk-management/index.md).

**Does the platform change our systems?**
Scanning is read-only. Remediation guidance — including AI suggestions — is advisory; people make the changes. Two opt-in exceptions exist: approved Auto-Fix Engine cloud actions (simulated unless the operator enables live execution) and agent-written fix pull requests (off by default; a pull request for a human to merge).

## Security

**How is our data protected?**
Team-scoped tenant isolation, credentials encrypted at rest under deployment-held keys, hashed session tokens and API keys, optional MFA and SSO, signed webhooks, rate-limited APIs, and a tamper-evident, hash-chained audit trail. The full picture is on [Trust & Security](./trust-and-security.md).

**How are our cloud credentials stored?**
Encrypted at rest (Fernet — AES-128-CBC with HMAC) under a key the deployment holds; decrypted only at the moment a scan runs; never returned by the API once saved. See [Trust & Security](./trust-and-security.md#credentials--secrets-handling).

**What do AI features see?**
Only data your team already has access to — finding and asset details, and for some features code snippets around a finding or the text of documents you uploaded to the Knowledge Base — and nothing tenant-derived is stored in shared caches. A team can configure its own provider (Anthropic, OpenAI or Google) and key, or use the deployment-wide key the operator set; with neither, the AI features are off and everything else works. See [how AI handles your data](./trust-and-security.md#how-ai-features-handle-your-data).

**Can we report a vulnerability in the platform?**
Yes — **security@offloadsecurity.com**. See the [responsible disclosure](./trust-and-security.md#responsible-disclosure) policy.

## Access and operations

**Can I create custom roles?**
Not today — six fixed roles per team (Admin, Security Manager, Security Analyst, Compliance Officer, Auditor, Viewer) plus scoped API keys. See [Roles, Teams & API Keys](./authentication/rbac-team-management.md).

**How do I sign in with our identity provider?**
The deployment operator configures OIDC (Okta, Entra ID, Google Workspace, Keycloak, Auth0…) and can enforce it; see [Signing In & Sessions](./authentication/session-management.md).

**What runs on our side in an on-premises install?**
A Docker Compose stack of prebuilt images on a host you own — API, web front end, several Celery worker pools, the beat scheduler, MongoDB, Redis, a Docker socket proxy for the scanner containers, and an encrypted backup service. The agentic-fix services start only if you enable their Compose profile. See [Deployment & Operations](./on-premises/deployment.md) and [Architecture](./architecture.md).

## Compliance

**Which frameworks are supported?**
A catalog of 27, including SOC 2, ISO 27001/27002/27017/27018/27701/42001, PCI DSS, NIST CSF / 800-53 / 800-171, CIS v8.1, CSA CCM, HIPAA, GDPR, NIS2, DORA, the EU AI Act, OWASP Top 10, CMMC Level 2, SEBI CSCRF and India's DPDPA — mapped through the SCF common-control backbone so one control satisfies many frameworks. The RBI Cyber Security Framework is not in the catalog. Full list: [Supported Frameworks](./compliance/supported-frameworks.md).

**Can it generate audit evidence?**
Yes — evidence is collected continuously and mapped to controls as work happens, then exported as audit-ready packages. Audit reports are frozen when issued and carry a SHA-256 fingerprint you can verify later. See [Evidence Hub](./compliance/evidence-hub.md) and [Audit Reports](./compliance/audit-reports.md).

**Does it help with India's DPDP Act?**
There's a dedicated module: readiness assessment, DPIAs, SDF obligations, vendor due diligence, and a breach workflow with DPB and CERT-In deadline tracking. See [DPDP Act (India)](./compliance/dpdp-privacy.md).

**Can it replace our spreadsheet risk register?**
Yes — risks are created manually or promoted automatically from critical findings, with ownership, treatment, review dates, and executive reporting. See [Risk Register](./vulnerability-risk/risk-management/index.md).

## Still have a question?

If it's about the platform's own security posture, check [Trust & Security](./trust-and-security.md); for anything else, contact your account team or support.
