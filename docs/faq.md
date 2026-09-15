---
title: "FAQ"
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
AWS, Google Cloud, and Azure — with read-only access wherever the provider supports it. Depth varies by provider (AWS and GCP include organization-level onboarding). See [Cloud Security](./cloud-security/index.md) and [permissions](./cloud-security/permissions.md).

**Can we keep our existing scanners and tools?**
Mostly by not needing them: the platform runs Trivy, Prowler, ZAP, Nuclei, nmap, testssl, Syft, Grype, kube-bench and the code scanners itself, so their results are native findings. Of the tools you keep, [Wazuh](./on-premises/wazuh-integration.md) syncs agents, alerts and host CVEs in; SonarQube and Jenkins contribute snapshots; Jira works two-way; [Greenbone / OpenVAS](./on-premises/openvas-scanning.md) is connected but its results stay in Greenbone today. The [Integration Catalog](./integrations/third-party.md) says, per tool, what flows.

**How are findings prioritized?**
Severity is normalized across sources, then enriched with exploit intelligence — findings on the **CISA KEV** list or with high **EPSS** scores are flagged so actively-exploited issues rise to the top. Critical findings can auto-promote into the [Risk Register](./vulnerability-risk/risk-management/index.md).

**Does the platform change our systems?**
Scanning is read-only. Remediation guidance — including AI suggestions — is advisory; people make the changes.

## Security

**How is our data protected?**
Team-scoped tenant isolation, credentials encrypted at rest under deployment-held keys, hashed session tokens and API keys, optional MFA and SSO, signed webhooks, rate-limited APIs, and a 365-day audit trail. The full picture is on [Trust & Security](./trust-and-security.md).

**How are our cloud credentials stored?**
Encrypted at rest (Fernet — AES-128-CBC with HMAC) under a key the deployment holds; decrypted only at the moment a scan runs; never returned by the API once saved. See [Trust & Security](./trust-and-security.md#credentials--secrets-handling).

**What do AI features see?**
Only data your team already has access to, and nothing tenant-derived is stored in shared caches. Each team configures its own provider (Anthropic, OpenAI or Google) and key; with none configured the AI features are off and everything else works. See [how AI handles your data](./trust-and-security.md#how-ai-features-handle-your-data).

**Can we report a vulnerability in the platform?**
Yes — **security@offloadsecurity.com**. See the [responsible disclosure](./trust-and-security.md#responsible-disclosure) policy.

## Access and operations

**Can I create custom roles?**
Not today — six fixed roles per team (Admin, Security Manager, Security Analyst, Compliance Officer, Auditor, Viewer) plus scoped API keys. See [Roles, Teams & API Keys](./authentication/rbac-team-management.md).

**How do I sign in with our identity provider?**
The deployment operator configures OIDC (Okta, Entra ID, Google Workspace, Keycloak, Auth0…) and can enforce it; see [Signing In & Sessions](./authentication/session-management.md).

**What runs on our side in an on-premises install?**
A Docker Compose stack of prebuilt images — API, web front end, workers, scheduler, MongoDB, Redis — on a host you own. See [Deployment & Operations](./on-premises/deployment.md).

## Compliance

**Which frameworks are supported?**
SOC 2, ISO 27001/27002/27701/42001, PCI DSS 4.0.1, NIST CSF 2.0 / 800-53 / 800-171, CIS v8.1, GDPR, HIPAA, OWASP, and India's DPDP Act, among others — mapped through a common-control backbone so one control satisfies many frameworks. Full list: [Supported Frameworks](./compliance/supported-frameworks.md).

**Can it generate audit evidence?**
Yes — evidence is collected continuously and mapped to controls as work happens, then exported as audit-ready packages. See [Evidence Hub](./compliance/evidence-hub.md).

**Does it help with India's DPDP Act?**
There's a dedicated module: readiness assessment, DPIAs, SDF obligations, vendor due diligence, and a breach workflow with DPB and CERT-In deadline tracking. See [DPDP Act (India)](./compliance/dpdp-privacy.md).

**Can it replace our spreadsheet risk register?**
Yes — risks are created manually or promoted automatically from critical findings, with ownership, treatment, review dates, and executive reporting. See [Risk Register](./vulnerability-risk/risk-management/index.md).

## Still have a question?

If it's about the platform's own security posture, check [Trust & Security](./trust-and-security.md); for anything else, contact your account team or support.
