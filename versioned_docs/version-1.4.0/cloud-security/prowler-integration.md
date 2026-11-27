---
title: "Compliance & Benchmark Checks"
sidebar_label: "Compliance & Benchmark Checks"
sidebar_position: 5
description: "What the posture checks assess (CIS Benchmarks and provider best practices), how every finding maps to compliance frameworks, and how to read per-framework scores per account."
---

# Compliance & Benchmark Checks

Every cloud scan evaluates your configuration against hundreds of checks and reports each as **pass** or **fail**. A failing check becomes a finding; the pass/fail totals become **compliance scores** per framework, per account. This page explains what the checks cover and how to read the scores.

## What the checks assess

- **CIS Benchmarks.** Each provider is evaluated against the CIS Foundations Benchmark — root/privileged accounts without MFA, public storage, open security groups, disabled audit logging, unencrypted data stores, and so on.
- **Provider best practices.** Beyond CIS: hardening recommended by AWS, Google and Microsoft across identity, network, storage, compute, logging and encryption — including the AWS Foundational Security Best Practices set.
- **Framework mapping.** Every check carries the control IDs it satisfies in each framework it maps to. That mapping is what turns a technical failure ("S3 bucket public") into an audit statement ("PCI DSS 4.0 req. 1.3.1 not met on 5 resources").

Checks are grouped into six **categories** you can filter on: **IAM, Network, Storage, Compute, Logging, Encryption**. Each failing check is rated **Critical, High, Medium, Low** or **Informational** and includes the remediation steps and a reference link.

The check engine is [Prowler](https://github.com/prowler-cloud/prowler), pinned to version **5.44.0** (by image digest) in release 1.4.0 — earlier releases used 5.6.0. The platform runs it read-only against your account, normalizes the output, deduplicates it across runs, and keeps your triage decisions (see [Reviewing & Triaging Findings](./findings.md#what-happens-between-scans)). Each run records the Prowler version it actually reported and keeps the raw output per region with its SHA-256, and the run's [point-in-time report](./point-in-time-reports.md) prints both.

### Check results

| Result | How it is treated |
| --- | --- |
| **Pass** | Counts toward the score; a previously failing finding for that resource is resolved. |
| **Fail** | Opens (or keeps open) a finding and counts against the score. |
| **Manual** | Not assessed: neither pass nor fail, and it resolves nothing. Prowler 5.44 reports some permission-limited checks as *manual* where 5.6 reported *fail*. |
| **Error** (for example access denied) | Not assessed; the region is marked as having check errors, which makes the run **Partial**, and existing findings stay open. |

:::note[Upgrading from 5.6.0]
Prowler renamed or split some checks between 5.6.0 and 5.44.0 (including two AWS security-group checks). After the first 1.4.0 scan, findings for a renamed check resolve under the old key and reappear once under the new one.
:::

## Frameworks

| Framework | Where it appears |
| --- | --- |
| **CIS Benchmarks** (per provider version) | Finding filter, finding detail |
| **PCI DSS 4.0**, **SOC 2**, **ISO 27001:2022**, **NIST 800-53 rev 5**, **NIST CSF 2.0** | Finding filter, finding detail, Compliance tab |
| **HIPAA**, **GDPR**, **NIS2** | Finding detail, Compliance tab |
| **RBI Cyber Security Framework**, **CISA**, **AWS Foundational Security Best Practices** | Compliance tab |
| **MITRE ATT&CK** | Finding detail (technique tags) |

Availability depends on the provider: AWS has the broadest mapping (including NIST, HIPAA, GDPR, RBI, CISA and FSBP); GCP and Azure carry CIS, PCI DSS 4.0, ISO 27001, SOC 2 and MITRE ATT&CK, with NIS2 on Azure. Prowler does not provide NIST 800-53 for GCP or Azure. Where a framework is not mapped for a provider the underlying checks still run — only the label is missing.

### How cloud checks reach SCF controls

These are the *technical* controls. **Compliance Posture** combines them with policy, evidence and assessment controls from the Secure Controls Framework (SCF) catalog to give you the full framework view — see [Compliance Dashboard](../compliance/compliance-dashboard.md) and [Supported Frameworks](../compliance/supported-frameworks.md).

A Prowler check reaches an SCF control in one of three ways, in this order:

1. **Reviewed hand mapping** — a check-to-control pair reviewed against the SCF control's meaning.
2. **Framework consensus** — Prowler's own framework requirements for the check, resolved through the SCF catalog; a control is attributed only when at least three distinct frameworks agree.
3. **Corroborated pivot** — Prowler's NIST 800-53 rev 5 (or ISO 27001:2022) requirement resolved through the SCF crosswalk, kept only when a second framework of the check points to the same control and the pair is on the reviewed list.

Derived mappings (2 and 3) are **fail-only**: a failing check adds evidence and a gap to the control, but a passing one never marks a control implemented. A control is upgraded only when every mapped result for it in the scan passed and a hand-mapped check vouches for it; programme-level controls are never upgraded by a single cloud check. The derived mapping is computed by the platform at runtime and is not shipped as a table.

Not every check reaches a control. **Compliance Posture** shows a section titled **What cloud checks can and can’t evidence**, with a table per provider — how many Prowler checks are mapped, and why each unmapped one is not (for example "Tagged only to frameworks the SCF doesn't map"). Use it to see which parts of a framework the cloud scans cannot evidence.

## The Compliance tab

**Cloud Security → Compliance** turns the pass/fail results into scores.

![Compliance tab: average score 72%, 10 frameworks, tier cards for Regional & Cloud and Global Standards with per-framework pass counts and percentages](/img/screenshots/cloud-security/compliance-tab.webp)

**Score** = passed ÷ (passed + failed) checks mapped to that framework, for the account(s) selected. Checks reported as *manual* or that errored are not assessed and do not count either way; suppressed or accepted findings are counted as exceptions, and resolved ones are not counted. The header tiles summarize the **average score**, the number of frameworks with data, and how many fall in each band:

| Band | Score | Read it as |
| --- | --- | --- |
| **Critical** | below 25% | Systemic gap — usually logging, encryption or identity baselines missing across the account. |
| **Needs work** | 25–70% | Typical for a newly connected account. Work the Critical/High findings first; the score follows. |
| **Good** | above 70% | Baseline in place; remaining failures are individual resources. |

Frameworks are grouped into three tiers — **Global Standards** (SOC 2, ISO 27001, NIST CSF, NIST 800-53), **Industry-Specific** (PCI DSS, HIPAA, GDPR, NIS2) and **Regional & Cloud** (RBI, CISA, AWS FSBP). Use **Account** to score a single account, **Show** to list only frameworks with findings or only critical ones, and **Category** to focus on one tier. Each framework card shows *passed / total* and the percentage.

Scores are recomputed from the latest finished scan of each account, so a fix that clears findings moves the score on the next run. For a score frozen at one run — for an auditor — use that run's [point-in-time report](./point-in-time-reports.md).

## Using scores well

1. **Pick the framework you are accountable for** — e.g. PCI DSS 4.0 for the payments account — and note its score per account.
2. On the **Findings** tab, filter **Framework = PCI-DSS** and **Severity = Critical/High**: that list is the shortest path to raising the score.
3. Record accepted risks as **suppressions with a reason** so the auditor sees a decision, not an ignored failure.
4. Re-run a **Full scan** before the review so the score reflects current state, then export findings (CSV/Excel) or generate a report.

:::tip[Same checks, wider region set]
A **Full** scan does not run more checks than a **Quick** scan — it covers more regions (see [Scan types and regions](./scan-orchestration.md#scan-types-and-regions)). If a score looks too good, make sure the run covered every region you use.
:::

## Related

- [Reviewing & Triaging Findings](./findings.md) — filter by framework, resolve, suppress.
- [Running Cloud Scans](./scan-orchestration.md) — keeping scores current.
- [Compliance Dashboard](../compliance/compliance-dashboard.md) — the organization-wide framework view.
