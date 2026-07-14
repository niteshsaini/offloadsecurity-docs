---
title: "India Regulatory Readiness"
sidebar_label: "India Regulatory Readiness"
sidebar_position: 8
---

# India Regulatory Readiness

Indian regulated entities answer to a specific stack of obligations: **RBI** directions for banks and NBFCs, **SEBI's Cybersecurity and Cyber Resilience Framework (CSCRF)** for securities-market entities, **CERT-In** directions on incident reporting, and the **DPDP Act, 2023** for personal data. This page maps those obligations to the platform capabilities that support them.

## RBI-regulated entities (banks, NBFCs, payment players)

RBI's directions on outsourcing of IT services shape what regulated entities must demand of any technology vendor — and what they must be able to demonstrate themselves.

| Obligation | How the platform supports it |
|---|---|
| **Data localization** — regulated data stored in India per applicable directions | [On-premises / private deployment](../on-premises/index.md): the platform runs entirely inside your environment, so scan data, findings, evidence, and reports never leave your network or the country |
| **Incident reporting on tight clocks** — REs report incidents to RBI within hours, which means vendors and internal teams must surface incidents immediately | Real-time [alerts](../integrations/notifications.md) to Slack/Teams/email/webhooks, plus the [DPDP breach workflow](../compliance/dpdp-privacy.md) with deadline watchdogs for CERT-In-style reporting windows |
| **Vendor oversight without audit fatigue** — RBI permits reliance on recognized third-party certifications and structured due diligence | [Vendor due-diligence questionnaires](../compliance/dpdp-privacy.md), continuous [evidence collection](../compliance/evidence-hub.md), and audit-ready [reports](../vulnerability-risk/index.md) for your own supervisory examinations |
| **IT & cyber risk governance** — a board-visible risk process | The [Risk Register](../vulnerability-risk/risk-register.md) with ownership, treatment, and executive reporting |

## SEBI CSCRF (securities-market entities)

CSCRF tiers regulated entities — from Market Infrastructure Institutions down to self-certification REs — with obligations scaled to the tier, and requires cyber audits and VAPT to be performed by **CERT-In-empanelled auditing organizations**.

How the platform fits:

- **Continuous compliance between audits.** CSCRF's control expectations (asset inventory, vulnerability management, logging, access control) map onto the platform's [compliance engine](../compliance/index.md) and [supported frameworks](../compliance/supported-frameworks.md), so the annual audit confirms a posture you maintain continuously rather than assembling annually.
- **VAPT evidence in one place.** Findings from your VAPT providers and scanners are ingested alongside the platform's own scans ([third-party integrations](../integrations/third-party.md), [OpenVAS](../on-premises/openvas-scanning.md)), tracked to closure in the [Risk Register](../vulnerability-risk/risk-register.md) — closure evidence auditors ask for.
- **Smaller REs.** For mid-size, small, and self-certification REs, the platform's compliance automation and reporting does the heavy lifting of demonstrating conformance without a large internal team.

:::note[Audits stay with empanelled firms]
CSCRF audits and VAPT must be conducted by CERT-In-empanelled organizations. The platform is the system of record that makes those audits fast — it does not replace the empanelled auditor.
:::

## CERT-In directions

CERT-In's directions require reporting of specified cyber incidents on very short timelines. The platform's [breach-incident workflow](../compliance/dpdp-privacy.md) tracks **CERT-In reportability**, generates **draft report text**, checks it for **completeness**, and raises **approaching-deadline and overdue alarms** so the window is met with a documented trail.

## DPDP Act, 2023

The [DPDP module](../compliance/dpdp-privacy.md) covers readiness assessment, DPIAs, Significant Data Fiduciary obligations, vendor due diligence, and the dual-track breach notification workflow (Data Protection Board + CERT-In).

## Typical deployment for Indian regulated entities

1. **Private deployment** inside your network for data residency ([On-Premises](../on-premises/index.md)).
2. **Connect the estate** — cloud accounts, repositories, clusters, registries, plus [Wazuh](../on-premises/wazuh-integration.md) and [OpenVAS](../on-premises/openvas-scanning.md) for on-prem visibility.
3. **Anchor compliance** on your primary framework and let the [SCF mappings](../compliance/supported-frameworks.md) carry the rest.
4. **Wire the clocks** — alert routing and the breach workflow configured before an incident, not during one.
5. **Stand up the audit trail** — evidence hub, audit packs, and scheduled reports for examiners.

## Related

- [Banking & Financial Services](./banking-financial-services.md)
- [Fintech](./fintech.md)
- [DPDP Act (India) Privacy](../compliance/dpdp-privacy.md)
- [Trust & Security](../trust-and-security.md)
