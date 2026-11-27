---
title: "Custom Cloud Policies"
sidebar_label: "Custom Policies"
sidebar_position: 5.5
description: "Write your own cloud posture check as a JSON condition, have it evaluated against the cloud inventory after every scan, and triage its violations alongside Prowler findings."
new_in: 1.4.0
---

# Custom Cloud Policies

A custom policy is your own check — "every S3 bucket must carry an `owner` tag", "production databases must be encrypted" — evaluated against the cloud inventory that scans already collect. Violations become findings labeled **Custom policy**, next to the Prowler checks. Writing one takes a few minutes.

## Before you begin

- The **Manage Scans** permission to create, edit, enable or disable policies. Viewing them needs **View Scans**.
- At least one completed scan of an account of the provider you target, so the inventory holds resources to evaluate.
- The field you want to test. Expand a resource in [Asset Inventory](./asset-inventory.md) → **Detailed Inventory** to see its tags and metadata — those are the fields a condition can name.

## Steps

1. **Open the tab.** **Cloud Security → Custom Policies** → **New policy**.
2. **Describe the check.** Fill in **Name**, **Severity**, **Provider**, **Service** (for example `s3`), optional **Resource type**, **Description** and **Remediation**. Optionally add **Compliance references**, comma-separated; they appear as labels on the findings.
3. **Write the condition** as JSON describing what a **compliant** resource looks like:
   ```json
   {"field": "metadata.encrypted", "op": "eq", "value": true}
   ```
   Combine conditions with `{"all": [...]}`, `{"any": [...]}` and `{"not": ...}`:
   ```json
   {"all": [
     {"field": "tags.owner", "op": "exists"},
     {"field": "tags.env", "op": "in", "value": ["prod", "staging", "dev"]}
   ]}
   ```
   Operators: `eq`, `ne`, `in`, `not_in`, `gt`, `gte`, `lt`, `lte`, `contains`, `not_contains`, `starts_with`, `ends_with`, `exists`, `not_exists`. Fields are dotted paths into the inventory record (for example `tags.env` or `metadata.*`); they never index into lists.
4. **Save** with **Create policy**. The policy is evaluated against the current inventory straight away, and again after every completed scan.

## Check that it worked

Expand the policy in the list. For every connected account of that provider you see **State**, **Violations**, **Compliant**, **Not evaluated** and **Last evaluated**, plus how the last evaluation was allowed to resolve findings:

| Label | Meaning |
| --- | --- |
| **Complete inventory — resolution allowed** | The account's latest scan completed, so violations that disappeared are marked fixed. |
| **Partial inventory — nothing resolved** | The latest scan was partial: new violations are recorded, but nothing is closed. |
| **No inventory — nothing resolved** | There is no inventory for the account yet. |

**Not evaluated** means the inventory does not hold the field you named for that resource. It is never counted as compliant and never as a violation.

Violations appear on the **Findings** tab as groups labeled **Custom policy** with the policy name and its compliance references, and they are included in the CSV / Excel export.

## Working with custom-policy findings

Custom-policy findings live in the platform's unified findings store rather than the Prowler findings store, so the Findings tab's **Resolve All**, **Suppress…** and **Fix** buttons are not offered on them. Instead:

- **Triage** them in [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) — owner, status, risk exceptions and SLAs apply as for any other finding.
- **Edit** the policy to change what counts as compliant; it is re-evaluated on save.
- **Disable** the policy (or remove its condition) to retire its open findings. Deleting a policy is available over the API only (`DELETE /api/cspm/policies/custom/{id}`) and also retires its findings.

## If something goes wrong

- **"Condition must be valid JSON …"** — Check quotes and brackets; field names and strings need double quotes. A condition outside the supported language is rejected on save.
- **"You need the Manage Scans permission to change custom policies."** — Ask an administrator for that permission.
- **"Saved, but the evaluation could not be started"** — The policy is saved; it is evaluated after the next completed scan.
- **Everything is "Not evaluated"** — The field path does not exist in the inventory records for that service. Check the record in Asset Inventory and adjust the path.
- **"No condition — not evaluated"** — A policy without a condition is documentation only and is never evaluated.

## Next steps

- [Reviewing & Triaging Findings](./findings.md) — where custom-policy findings appear.
- [Cloud Security API](./api.md#custom-policies) — manage policies programmatically.
