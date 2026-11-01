---
title: "Evidence Hub"
sidebar_label: "Evidence Hub"
sidebar_position: 4
description: "Every artifact behind every control in one canonical store: auto-collected scan evidence, raw AWS, GCP and Azure API captures, Wazuh fleet results, policy acknowledgements, documents and screenshots, with coverage by SCF domain, freshness, a review queue, the reason each status holds, renewal prompts and per-framework auditor packages."
---

# Evidence Hub

Posture says *what* you claim; evidence is *why an auditor should believe you*. The Evidence Hub collects that proof from everything the platform already does, lets you add what it cannot see, and tells you which controls still have nothing behind them.

**Where:** left navigation → **Compliance Posture** → *Evidence Hub* tab.

![Evidence Hub: framework-aware mode with 10 active frameworks; tiles for total controls, with evidence (46.7% coverage), auto-collected, manual evidence, no evidence; evidence coverage by SCF domain](/img/screenshots/compliance/evidence-hub.webp)

## Where evidence comes from

| Source | How it gets here | Typical quality score |
| --- | --- | --- |
| **Scan evidence**: cloud posture (Prowler), Kubernetes, container, vulnerability and web scans | Written automatically as scans correlate to controls, and by **Collect All Evidence** | 85–95 |
| **API evidence**: raw, read-only cloud API responses. AWS: S3 encryption, logging, versioning and public-access block, EBS default encryption, RDS encryption / public access / backups, IAM summary and password policy, Access Analyzer, security groups, VPC flow logs, CloudTrail, GuardDuty, Config, Security Hub, KMS rotation. GCP: project IAM bindings, firewall rules, Cloud SQL, GKE, audit-log sinks, Cloud Storage buckets. Azure: storage accounts, NSGs, SQL servers, Key Vaults, Defender plans, AKS. | **Collect API Evidence** for all connected accounts, or per account | scan-grade |
| **Wazuh fleet evidence**: Wazuh SCA (configuration assessment) results per check across your agents | The Wazuh sync, when the [Wazuh integration](../integrations/wazuh.md) is connected | gaps only (see below) |
| **Policy acknowledgements**: a campaign asking team members to acknowledge a policy version | [Policy Acknowledgement](./policy-attestation.md) in the Knowledge Base | credited only when complete |
| **Assessment answers** | Each answered assessment question is evidence for the controls it maps to | 75 |
| **Knowledge-base documents** | Policies and procedures uploaded to the [Knowledge Base](../ai-threat-intelligence/knowledge-base.md) and mapped to controls | 70 |
| **Manual uploads**: documents, screenshots, configs, policies, certificates, reports | **Quick Upload** or the **Evidence Wizard** | 60–70 |

Evidence is **deduplicated** by content: one artifact is stored once and linked to every control it satisfies (the *Avg Controls / Item* tile on the posture page). Sensitive values in API captures are **masked** before storage.

All of it lives in **one evidence store** per team, which every score, counter, review and export reads. If the platform finds evidence from an earlier release that it cannot attribute to a team, the tab shows a notice; platform administrators can assign each listed item to their current team (audited).

### What earns credit

Not every item linked to a control counts toward its status or score. An item earns credit only while it is **current** and its result supports the control:

- **Failing checks** are recorded as gaps, not credit.
- **Derived mappings** are fail-only: a pass through a derived mapping is shown but never credited. All Wazuh SCA mappings and Kubernetes findings are derived, so Wazuh and Kubernetes evidence can add gaps and visibility but never raise a score. Stale Wazuh results (an agent that has not re-run the check) are not evaluated, and agents that do not report are never counted as passing.
- **Manual uploads** are linked without changing status. Approval in the review queue can promote the control to *partial*; rejection reverts that.
- **Expired, superseded, rejected, pending-review or unapproved** items earn nothing.
- **API evidence** for a resource type with no resources is *not evaluated*, never a pass. Permission denied or a disabled API is a collection error, never a pass or a fail. An account without its own credentials collects nothing; the platform never falls back to its own cloud credentials.

Each evidence item that does not earn credit is labeled with the reason (for example *a pass through a derived mapping — shown, never credited*).

## Coverage

The **Coverage** view is the honest number: of the controls in scope for your active frameworks, how many have at least one evidence item — overall and **by SCF domain**, with *with gaps only* / *fully covered* filters. Click a tile to list the controls behind it; click a control to see its evidence and add a comment.

![Evidence coverage by domain with per-domain percentages and counts](/img/screenshots/compliance/evidence-hub-domains.webp)

**Framework-aware mode** (the strip of active frameworks at the top) restricts everything on this tab to controls those frameworks reference.

### Why this status

Opening a control shows its evidence, comments and a **Why this status** panel: who or what set the status and when, the latest transition, the failing checks behind an engine downgrade, and which linked evidence is current now. See [How control status is decided](./control-status.md).

## Freshness

![Evidence Freshness: fresh, expiring within 14 days, stale and expired counts](/img/screenshots/compliance/evidence-hub-freshness.webp)

Evidence ages. Manual evidence carries a **valid-until** date; assessments carry a validity window; scan evidence is superseded by the next scan. Freshness splits all of the team's evidence items into four buckets that add up to the total: **Fresh**, **Expiring within** the window, **No expiry set** (current until archived or revoked) and **Expired / retired** (expired, archived, revoked or superseded; earns no credit). Expired evidence stops supporting its controls and appears as an *Evidence Expired* [drift](./drift-detection.md).

## Smart breakdown

![Smart Breakdown: evidence by source, type and quality band](/img/screenshots/compliance/evidence-hub-smart.webp)

Each evidence item carries a **quality score** — the source's base score (CSPM scan 95, vulnerability scan 90, container / Kubernetes / security scan 85, assessment 75, knowledge base or policy 70, manual 60) adjusted by type (scan result 1.0, assessment 0.9, policy 0.85, config 0.8, document 0.75, attestation 0.65, screenshot 0.5, email 0.4). The breakdown shows where your evidence is strong and where a framework leans on screenshots.

## Review queue

![Review Queue: pending evidence reviews with Approve and Reject](/img/screenshots/compliance/evidence-hub-review.webp)

Auto-collected evidence enters as **auto_collected**; before an audit you move it to **pending_review** and a reviewer marks it **approved** (audit-ready) or **rejected** (needs replacement). The queue lists what is waiting, with the controls each item supports. The person who uploaded an item cannot review it, expired or superseded items cannot be approved, and items replaced by a newer version leave the queue (the queue says how many were hidden).

## API evidence

![API Evidence: capture status per connected cloud account and Collect API Evidence](/img/screenshots/compliance/evidence-hub-api.webp)

This is the evidence auditors like most: the raw API response, not a scanner's interpretation. **Collect API Evidence** walks every connected AWS, GCP and Azure account (read-only calls, per-resource where it matters), masks secrets, deduplicates and links each capture to the SCF controls it proves. Each capture records the verdict and the per-resource fields that decided it. The tab shows totals for compliant and non-compliant captures, the last collection run per account, and a notice naming any connected provider for which no API evidence is collected.

## Renewals

![Renewals: evidence from the previous audit cycle due for renewal](/img/screenshots/compliance/evidence-hub-renewals.webp)

Manual evidence from the last cycle — the access-review export, the pen-test report, the tabletop minutes — is remembered and surfaced when it is a year old (configurable 30–730 days), with a one-click renewal prompt so the second audit is not a rediscovery of the first.

## Adding evidence yourself

![Upload Manual Evidence: SCF control IDs, title, evidence type, description, file](/img/screenshots/compliance/evidence-hub-upload.webp)

**Quick Upload** takes a title, an evidence type (document, screenshot, config, policy), one or more **SCF control IDs** and the file. The **Evidence Wizard** starts from the other end — pick a framework, see its controls without evidence, and upload against each.

![Interactive Evidence Upload wizard: choose a framework, then controls needing evidence](/img/screenshots/compliance/evidence-hub-wizard.webp)

## Auditor package

**Download auditor package** (per framework, at the bottom of the tab, and under **Evidence bundle** on the [Audit Reports](./audit-reports.md) page) produces a ZIP organised **by control**: a `README.txt` and `executive_summary.json`, then one folder per SCF control with `control_info.json` and the evidence grouped in four layers — **L1 governance** (policies), **L2 technical** (scan results and API captures), **L3 operational** (assessment answers) and **L4 monitoring** (alerts and logs). It is the thing you hand to the auditor instead of a shared drive.

## Related

- [Compliance Posture](./compliance-dashboard.md) — the scores this evidence supports.
- [Audit Reports](./audit-reports.md) — attestable PDF and CSV reports for controls, findings, drift and remediation.
- [How control status is decided](./control-status.md) — the rules behind credit and status.
- [Compliance & GRC API](./api.md#evidence) — evidence, collection, capture, review and renewals over REST.
