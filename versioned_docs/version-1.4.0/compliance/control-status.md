---
title: "How Control Status Is Decided"
sidebar_label: "How Status Is Decided"
sidebar_position: 1.5
description: "How the platform decides each SCF control's status from evidence, what a person's statement means to automation, how reviewed and derived scanner mappings differ, and how to read the Why this status panel and the status-basis API."
new_in: 1.4.0
---

# How control status is decided

Every SCF control carries a status for your team: `implemented`, `partial`, `planned`, `not_implemented`, `not_assessed` or `not_applicable`. In release 1.4.0 every status can be traced to what set it: a person, a piece of current evidence, or an active scan failure. This page explains the rules and how to check them for a single control.

## The rules

| Rule | What it means in practice |
| --- | --- |
| **Evidence decides automated status** | The engine maps an active scan failure to controls by **check ID**, never by matching words in a finding's title. Checks that map to no control are counted and listed on the sync timeline and in the audit report. |
| **A person's status is never changed by automation** | A status set by a person (a manual override, a status set through the API, an approved exception) is not changed by the engine, scan correlators, assessment mapping or evidence collectors. New evidence is still linked to the control. |
| **Contradictions are flagged, not resolved silently** | When active mapped scan failures contradict a status a person set to *implemented*, the control is marked **contradicted** for review. The status stays as the person set it. |
| **Implemented needs current evidence** | An *implemented* status that evidence put there holds only while at least one linked evidence item is current. When all of it lapses, the control returns to *not assessed*. |
| **Restoring needs evidence too** | When the failures behind an engine downgrade are resolved, the control is restored only on current evidence or a person's earlier attestation. Otherwise it becomes *not assessed*. |
| **A failed scan never improves a score** | A scan with tool failures, a paused account, or an image whose latest container scan failed is treated as unknown, not clean. |

### Reviewed and derived mappings

Scanner checks reach SCF controls in two ways:

| Mapping | Source | A failing check | A passing check |
| --- | --- | --- | --- |
| **Reviewed** | A hand-reviewed check-to-control table | Records a gap | Can mark the control implemented |
| **Derived** | Computed from the scanner's own framework tags (for Prowler: agreement between frameworks, or a corroborated NIST 800-53 / ISO 27001 pivot through the SCF crosswalk) | Records a gap | Earns no credit and never marks a control implemented |

Derived mappings are **fail-only**: they can add gaps and visibility but cannot raise a score. Kubernetes findings, Wazuh SCA results and Prowler checks without a reviewed mapping all use derived mappings. The **What cloud checks can and can't evidence** panel on the [Compliance Posture](./compliance-dashboard.md) tab shows, per cloud provider, how many Prowler checks have a reviewed mapping, a derived mapping or none, and why the unmapped ones are unmapped.

:::note
The derived Prowler-to-SCF table is computed at runtime from the pinned Prowler release and the SCF 2026.2 catalog. It is not shipped as a file.
:::

## Check why a control has its status

**Where:** **Compliance Posture** → *Evidence Hub* tab → open any control.

The control detail view includes a **Why this status** panel. It shows:

- **Basis**: one of the values in the table below.
- **Set by** / **Attested by**: who or what set the status, and when (**Decided** / **Last confirmed**).
- The latest status transition from the compliance audit log.
- For an engine downgrade: the failing checks, whether each mapping is reviewed or derived, and the finding counts.
- The linked evidence that is current now, with its source and validity. Evidence the platform could not read is counted separately.

If the panel cannot be loaded, it says "unavailable" rather than showing an empty panel.

| Basis | Meaning |
| --- | --- |
| Backed by current evidence | At least one current evidence item supports the status |
| Active scan failure on a mapped check | The engine set the status because a mapped check is failing now |
| Attested by a person | A person set the status |
| Attested by a person, contradicted by active scan failures (review) | A person set *implemented*, and mapped checks are failing now |
| No current evidence or attestation supports this status | Nothing current backs the status |
| Manual override | The control is locked by an override |
| Not assessed | Nothing evaluates this control yet |
| Marked not applicable | The control is out of scope |

The same information is available over the API:

```
GET /api/common-controls/control/{scf_id}/status-basis
```

The response is scoped to the caller's team. Evidence lists are bounded and report the true total next to them.

## Where contradictions and gaps show up

- **Drift Detection**: a *contradicted* drift when a contradiction starts, and a *cleared* drift when it resolves. See [Drift Detection](./drift-detection.md).
- **Audit Reports**: the Full Report includes an *Attested controls contradicted by scan failures* section and an *Active failing checks mapped to no control* section. See [Audit Reports](./audit-reports.md).
- **Evidence Hub**: items that do not earn credit (derived passes, stale results, failing checks) are labeled with the reason.

## Score method changes

The scoring and decision method has a version number. When it changes, the Compliance Engine trend and timeline mark the change point instead of plotting the re-decided statuses as a change in posture. Threshold breaches are not raised across a method change.

## Related

- [Compliance Posture](./compliance-dashboard.md): manual overrides and the implementation score.
- [Evidence Hub](./evidence-hub.md): the evidence behind each status.
- [Compliance & GRC API](./api.md#controls-and-posture): status-basis and audit-log endpoints.
