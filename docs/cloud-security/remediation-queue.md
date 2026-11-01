---
title: "Remediation Queue"
sidebar_label: "Remediation Queue"
sidebar_position: 6
description: "Track cloud findings you have handed to an owner — assignee, priority, due date and status — from creation to done."
---

# Remediation Queue

Resolving a finding in the platform does not fix the cloud; someone still has to change a bucket policy or a security group. The **Remediation Queue** is where that hand-off is tracked. Every task in it was created from a finding with the **Fix** action, so it stays linked to the check, the resource and the account it came from.

**Where:** Cloud Security → **Remediation Queue**.

![Remediation Queue: status tiles (Open 5, In progress, Done, Won't fix, Cancelled), filters, and a table of tasks with severity, priority, assignee, due date and status](/img/screenshots/cloud-security/remediation-queue.webp)

## Creating a task

1. On the **Findings** tab, expand a finding and select **Fix** (*Create Remediation Task*).
2. Under **Affected Resource**, pick the resource the task is for. A task targets one resource; when a check has many, the list shows the most recently detected ones and says how many there are in total.
3. Enter an **assignee** (email or name), a **priority**, a **due date** and any **notes** for the owner.
4. The task is created as **Open** and linked to the finding (check, resource, account).

**Fix** is not offered on findings raised by [custom policies](./custom-policies.md); track those in Vulnerability Management.

You can create tasks over the API as well — see [Cloud Security API](./api.md#remediation-tasks).

## Working the queue

The tiles count tasks per status; the table lists them **non-terminal first** (Open, In progress) so the work that still needs attention is always at the top. Filter by **status, severity, priority** or search by title, notes, resource ID or check ID.

Each row shows the finding title, the affected **resource ID**, **severity** (from the finding), and editable **priority**, **assignee**, **due date** and **status**. Changes save immediately.

| Status | Use it when |
| --- | --- |
| **Open** | Created, nobody has started. |
| **In progress** | The owner is working on it. |
| **Done** | The change is made. The next scan verifies it — if the check still fails, the finding stays open and you will see it on the Findings tab. |
| **Won't fix** | The owner decided not to change it. Pair this with a **suppression** on the finding so the risk is recorded as accepted, not ignored. |
| **Cancelled** | Created by mistake or superseded. |

:::note[Tasks vs. suppressions]
A **task** says "someone will fix this by a date". A **suppression** says "we accept this for a period". Use a task for anything you intend to change, and a suppression for accepted risk — the queue stays a true to-do list and the audit trail stays honest.
:::

Removing a cloud account closes its open tasks rather than deleting them, so the hand-off history stays.

## Related

- [Reviewing & Triaging Findings](./findings.md) — where tasks are created.
- [SLA Management](../vulnerability-risk/sla-management.md) — due dates driven by severity policies for the unified vulnerability view.
