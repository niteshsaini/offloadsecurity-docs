---
title: "Collect policy acknowledgements"
sidebar_label: "Policy Acknowledgement"
sidebar_position: 4.5
description: "Publish a version of a policy from the Knowledge Base to team members or roles, track who acknowledged it, and use a complete campaign as evidence for the SCF controls it maps to."
new_in: 1.4.0
---

# Collect policy acknowledgements

Publish one version of a policy document for acknowledgement, track who has read and acknowledged it, and turn a complete campaign into compliance evidence. This takes a few minutes to set up; the campaign then runs until its due date.

## Before you begin

- **Manage Assessments** permission to publish a policy version, send reminders and manage recipients; **Export Reports** to export the record. Any team member who is a recipient can acknowledge.
- The policy must already be in the [Knowledge Base](../ai-threat-intelligence/knowledge-base.md) with document type **policy**, **SOP**, **security playbook**, **incident response** or **training material**.
- Decide which SCF controls the acknowledgement evidences. The default is **HRS-05.7** (Policy Familiarization & Acknowledgement) and **GOV-02** (publishing security documentation).

## Steps

1. **Open the campaign form.** Left navigation → **Knowledge Base** → **Policy Acknowledgement** tab → *Publish a policy version for acknowledgement*.
2. **Choose the policy document.** Search by title and select it. The platform records the SHA-256 of the file so every acknowledgement is tied to these exact bytes.
3. **Enter a version label** (for example `v2.1`) and a **due date**. The default due date is 14 days from today.
4. **Choose the audience.** Tick roles under *Publish to roles* (Admins, Security managers, Security analysts, Compliance officers, Auditors, Viewers), individual members, or both.
5. **Confirm the SCF controls** this acknowledgement evidences, then click **Publish**.

Publishing a new version of the same policy supersedes the previous active campaign: its pending acknowledgements become *superseded*, and its evidence stops counting until the new version is complete.

## What recipients do

Each recipient sees the policy under **My policy acknowledgements**, clicks **Read this version** (the file is served from the platform and re-hashed on every read), then **I have read and accept this policy**. The record keeps who acknowledged, when, which version and SHA-256, the network address and the user agent. If the document changed after publishing, the acknowledgement is refused.

:::note
A forwarded client address is recorded as unverified unless the platform's `TRUSTED_PROXIES` setting names your reverse proxy.
:::

## Check that it worked

The tab shows four tiles: **Waiting for my acknowledgement**, **Active policy versions**, **Counting toward controls** and **Overdue acknowledgements**. In *Policy acknowledgement campaigns* each campaign lists recipients, **Completion**, **Team coverage**, due date and status.

| Measure | Calculation |
| --- | --- |
| **Completion** | Acknowledged ÷ counted recipients, rounded down (99 of 100 is 99%). The publisher's own acknowledgement is recorded but not counted. |
| **Team coverage** | Active team members covered by the audience ÷ active team members. |

## When it counts as evidence

Each campaign is one item in the evidence store, linked to its SCF controls.

| Campaign state | Evidence |
| --- | --- |
| Complete **and** covers every active team member | Earns credit for 365 days from completion |
| In progress, or audience does not cover the whole team | Not evaluated, no credit |
| Overdue | Shown as a failing check (a gap); it does not change any control status by itself |
| Superseded by a newer version | No credit |

Membership changes are re-evaluated daily. A member who leaves the team drops out of the count. A member who joins later is added (for role-based audiences) and has 30 days to acknowledge; credit is kept until then and withheld afterwards until they acknowledge.

## Manage recipients and reminders

- **Recipients** lists each recipient with status, acknowledgement time and IP address.
- **Remind** sends an in-app and email reminder now. Reminders are also sent daily for each campaign, at most once per its reminder interval (3 days by default).
- **Remove** a recipient takes them out of the completion count; they still count for team coverage, so credit stays withheld.
- **Exempt** a recipient, with a reason, takes them out of both completion and coverage.
- Deleting the policy document cancels its active campaigns.
- **CSV** and **PDF** download the acknowledgement record, with every row.

Every publish, acknowledgement, reminder, removal, exemption and supersession is written to the team's hash-chained compliance audit log.

## If something goes wrong

- **The policy is not in the document list.** Only the document types listed under *Before you begin* can be published. Change the document type in the Knowledge Base.
- **Completion is 100% but the campaign does not count toward controls.** Team coverage is below 100%: the audience does not include every active member. Add the missing roles or members, or exempt members with a reason.
- **A recipient cannot acknowledge.** The document file changed after publishing. Publish a new version.

## Next steps

- [Evidence Hub](./evidence-hub.md): see the campaign as evidence on its controls.
- [How control status is decided](./control-status.md): how evidence credit affects status.
