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
Both. The managed platform is the default; regulated customers can run the full platform **inside their own environment**, where data never leaves their network. See [On-Premises](./on-premises/index.md).

**Which cloud providers are supported?**
AWS, Google Cloud, and Azure — with read-only access wherever the provider supports it. Depth varies by provider (AWS and GCP include organization-level onboarding). See [Cloud Security](./cloud-security/index.md) and [permissions](./cloud-security/permissions.md).

**Can we keep our existing scanners and tools?**
Yes — that's the point of the unified model. Findings from tools like Trivy, Prowler, ZAP, Grype, Syft, and kube-bench can be ingested via API, and SIEM/scanner integrations like [Wazuh](./on-premises/wazuh-integration.md) and [OpenVAS](./on-premises/openvas-scanning.md) feed the same dashboards. See [Integrations](./integrations/index.md).

**How are findings prioritized?**
Severity is normalized across sources, then enriched with exploit intelligence — findings on the **CISA KEV** list or with high **EPSS** scores are flagged so actively-exploited issues rise to the top. Critical findings can auto-promote into the [Risk Register](./vulnerability-risk/risk-register.md).

**Does the platform change our systems?**
Scanning is read-only. Remediation guidance — including AI suggestions — is advisory; people make the changes.

## Security

**How is our data protected?**
Team-scoped tenant isolation, envelope-encrypted credentials, signed webhooks, rate-limited APIs, and audit trails. The full picture is on [Trust & Security](./trust-and-security.md).

**How are our cloud credentials stored?**
Encrypted at rest with envelope encryption; decrypted only at the moment a scan runs; never returned by the API once saved. See [Trust & Security](./trust-and-security.md#credentials--secrets-handling).

**What do AI features see?**
Only data your team already has access to, and nothing tenant-derived is stored in shared caches. Model providers are configurable in enterprise deployments. See [how AI handles your data](./trust-and-security.md#how-ai-features-handle-your-data).

**Can we report a vulnerability in the platform?**
Yes — **security@offloadsecurity.com**. See the [responsible disclosure](./trust-and-security.md#responsible-disclosure) policy.

## Compliance

**Which frameworks are supported?**
SOC 2, ISO 27001/27002/27701/42001, PCI DSS 4.0.1, NIST CSF 2.0 / 800-53 / 800-171, CIS v8.1, GDPR, HIPAA, OWASP, and India's DPDP Act, among others — mapped through a common-control backbone so one control satisfies many frameworks. Full list: [Supported Frameworks](./compliance/supported-frameworks.md).

**Can it generate audit evidence?**
Yes — evidence is collected continuously and mapped to controls as work happens, then exported as audit-ready packages. See [Evidence Hub](./compliance/evidence-hub.md).

**Does it help with India's DPDP Act?**
There's a dedicated module: readiness assessment, DPIAs, SDF obligations, vendor due diligence, and a breach workflow with DPB and CERT-In deadline tracking. See [DPDP Act (India)](./compliance/dpdp-privacy.md).

**Can it replace our spreadsheet risk register?**
Yes — risks are created manually or promoted automatically from critical findings, with ownership, treatment, review dates, and executive reporting. See [Risk Register](./vulnerability-risk/risk-register.md).

## Still have a question?

If it's about the platform's own security posture, check [Trust & Security](./trust-and-security.md); for anything else, contact your account team or support.
