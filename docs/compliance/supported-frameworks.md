---
title: "Supported Frameworks"
sidebar_label: "Supported Frameworks"
sidebar_position: 6
---

# Supported Frameworks

The compliance engine is built on the **Secure Controls Framework (SCF)** as a common-control backbone: you implement a control once, and it maps out to every framework that references it. That's why evidence collected for one framework automatically advances the others.

## Framework catalog

Frameworks mapped through the SCF backbone:

| Framework | Domain |
|---|---|
| **SOC 2** (AICPA Trust Services Criteria) | Service-organization trust |
| **ISO/IEC 27001:2022** | Information security management |
| **ISO/IEC 27002:2022** | Security controls |
| **ISO/IEC 27701** | Privacy information management |
| **ISO/IEC 42001:2023** | AI management systems |
| **PCI DSS 4.0.1** | Payment-card security |
| **NIST CSF 2.0** | Cybersecurity framework |
| **NIST SP 800-53 Rev 5** | Security & privacy controls |
| **NIST SP 800-171 Rev 2 / Rev 3** | Controlled unclassified information |
| **NIST Privacy Framework** | Privacy |
| **CIS Controls v8.1** | Baseline cyber hygiene |
| **OWASP Top 10 (2021)** | Application security |
| **EU GDPR** | EU data protection |
| **HIPAA** | US healthcare privacy & security |

Additional frameworks with dedicated assessment modules:

| Framework | Where |
|---|---|
| **India DPDP Act, 2023** | [DPDP Act (India) Privacy](./dpdp-privacy.md) — readiness, DPIA, SDF, vendor due diligence, breach workflow |
| **EU AI Act** & **NIST AI RMF** | [AI Governance](../ai-threat-intelligence/ai-governance.md) — risk-tier classification, FRIA, assessments |
| **OWASP ASVS 5.0** | Application security verification assessments |
| **OWASP API Security Top 10** | API security assessments |
| **NIST SSDF** | Secure software development |
| **OWASP SAMM** | Software assurance maturity |
| **DevSecOps maturity** | Pipeline & practice maturity |
| **Insider threat** | Insider-risk program assessment |

## How mappings work in practice

- **One control, many frameworks.** Marking an SCF control implemented updates the posture of every mapped framework at once — the compliance dashboard shows the per-framework effect.
- **Evidence reuse.** Evidence attached in the [Evidence Hub](./evidence-hub.md) is control-mapped, so a single artifact (say, your access-review export) counts toward SOC 2, ISO 27001, and NIST CSF simultaneously.
- **Scan findings map to controls.** Cloud, code, container, and Kubernetes findings link to the controls they affect, so technical drift shows up as compliance drift.

:::tip[Start with one anchor framework]
Pick the framework your customers or regulators actually ask for (commonly SOC 2 or ISO 27001), get it green, and let the SCF mappings pull the others along — rather than assessing everything at once.
:::

## Related

- [Compliance & GRC overview](./index.md)
- [Compliance Dashboard](./compliance-dashboard.md)
- [Interactive Assessments](./interactive-assessments.md)
- [DPDP Act (India) Privacy](./dpdp-privacy.md)
