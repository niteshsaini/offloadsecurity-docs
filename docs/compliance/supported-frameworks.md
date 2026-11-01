---
title: "Supported Frameworks"
description: "The compliance frameworks Offload Security supports, mapped through the Secure Controls Framework (SCF 2026.2) so evidence for one control advances every framework that references it."
sidebar_label: "Supported Frameworks"
sidebar_position: 8
---

# Supported Frameworks

The compliance engine is built on the **Secure Controls Framework (SCF), release 2026.2** as a common-control backbone: you implement a control once, and it maps out to every framework that references it. That's why evidence collected for one framework automatically advances the others. The bundled catalog is **1,534 controls in 34 domains, mapped across 27 frameworks**. These 27 are the frameworks you can activate and score; other regimes (for example RBI directions) are not selectable frameworks.

## Framework catalog

All 27 frameworks below are mapped through the SCF 2026.2 backbone, so a single control satisfies every framework that references it. Ten are active by default (ISO 27001, ISO 27002, SOC 2, PCI DSS 4.0.1, NIST CSF 2.0, NIST 800-53 r5, CIS v8.1, HIPAA, GDPR, OWASP Top 10). A platform administrator activates frameworks per team from the **Frameworks** tile on [Compliance Posture](./compliance-dashboard.md#framework-activation).

| Framework | Domain |
|---|---|
| **SOC 2** (AICPA Trust Services Criteria) | Service-organization trust |
| **CIS Controls v8.1** | Baseline cyber hygiene |
| **ISO/IEC 27001:2022** | Information security management |
| **ISO/IEC 27002:2022** | Security controls |
| **ISO/IEC 27017:2015** | Cloud security controls |
| **ISO/IEC 27018:2025** | Cloud PII protection |
| **ISO/IEC 27701:2025** | Privacy information management |
| **ISO/IEC 42001:2023** | AI management systems |
| **CSA CCM 4.1.0** | Cloud controls matrix |
| **NIST AI RMF (AI 100-1)** | AI risk management |
| **NIST Privacy Framework** | Privacy |
| **NIST SP 800-53 Rev 5** | Security & privacy controls |
| **NIST SP 800-171 Rev 2** | Controlled unclassified information |
| **NIST SP 800-171 Rev 3** | Controlled unclassified information |
| **NIST SSDF (SP 800-218)** | Secure software development |
| **NIST CSF 2.0** | Cybersecurity framework |
| **OWASP Top 10 (2025)** | Application security |
| **PCI DSS 4.0.1** | Payment-card security |
| **CMMC 2.0 Level 2** | Defense supply-chain maturity |
| **HIPAA** | US healthcare privacy & security |
| **EU AI Act** | AI regulation |
| **EU DORA (2023)** | Financial-sector operational resilience |
| **EU GDPR** | EU data protection |
| **EU NIS2 (2022)** | EU network & information security |
| **EU NIS2 Annex (2024)** | NIS2 sector annex |
| **India DPDP Act, 2023** | India data protection |
| **SEBI CSCRF (2024)** | India securities-market cyber resilience |

Several of these also have **dedicated, guided modules** on top of the SCF mapping:

| Framework | Dedicated module |
|---|---|
| **India DPDP Act, 2023** | [DPDP Act (India) Privacy](./dpdp-privacy.md) — readiness, DPIA, SDF classification, vendor due diligence, breach workflow with statutory DPB / CERT-In deadlines |
| **EU AI Act**, **NIST AI RMF**, **ISO 42001** | [AI Governance](../ai-threat-intelligence/ai-governance.md) — risk-tier classification, model discovery, prompt-injection testing, assessments, ISO 42001 Statement of Applicability |

Every framework also has a **Statement of Applicability** (one row per requirement, rolled up from the mapped SCF controls) in its drill-down on Compliance Posture. For ISO 27001 it covers clauses 4–10 and the Annex A controls.

## How mappings work in practice

- **One control, many frameworks.** Marking an SCF control implemented updates the posture of every mapped framework at once — the Compliance Posture page shows the per-framework effect.
- **Evidence reuse.** Evidence attached in the [Evidence Hub](./evidence-hub.md) is control-mapped, so a single artifact (say, your access-review export) counts toward SOC 2, ISO 27001, and NIST CSF simultaneously.
- **Scan findings map to controls by check ID.** Cloud (Prowler), container and Kubernetes scan failures, and Wazuh SCA results, link to the controls they affect, so technical drift shows up as compliance drift. Prowler checks use a reviewed mapping where one exists; otherwise a mapping derived from Prowler's own framework tags through the SCF crosswalk. Derived mappings, and all Kubernetes and Wazuh mappings, are fail-only: they record gaps but never mark a control implemented. See [How control status is decided](./control-status.md#reviewed-and-derived-mappings).

:::tip[Start with one anchor framework]
Pick the framework your customers or regulators actually ask for (commonly SOC 2 or ISO 27001), get it green, and let the SCF mappings pull the others along — rather than assessing everything at once.
:::

## Related

- [Compliance & GRC overview](./index.md)
- [Compliance Posture](./compliance-dashboard.md)
- [Assessments](./interactive-assessments.md)
- [DPDP Act (India) Privacy](./dpdp-privacy.md)
