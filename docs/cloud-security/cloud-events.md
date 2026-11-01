---
title: "Real-Time Cloud Events"
sidebar_label: "Cloud Events"
sidebar_position: 9
description: "Stream CloudTrail, Google Cloud Audit Log and Azure Activity Log events to Offload Security so security-relevant changes surface in seconds, not at the next scan."
---

# Real-Time Cloud Events

Scans tell you the state of an account every day. **Cloud Events** tells you the moment it changes. Your cloud pushes audit events to your team's platform webhook; the platform keeps the security-relevant ones, enriches them with who did what from where, raises a finding for each, and shows them on a live feed.

**Where:** Cloud Security → **Cloud Events**.

![Real-Time Cloud Events: totals for the last window (44 events, 8 critical, 10 high, 3 providers), provider and severity filters, a Hide-noise toggle, and a feed of enriched events such as CloudTrail Logging Stopped and NSG Rule Modified](/img/screenshots/cloud-security/cloud-events.webp)

## What you get

- **Curated, not raw.** Only events that matter for security are kept — roughly **270 AWS**, **220 GCP** and **155 Azure** event types across identity, network, storage, logging, encryption, compute and database. Everything else is recorded as ignored, and failed API calls are skipped because they changed nothing.
- **Enriched.** Each event shows the **actor / principal**, **source IP**, **user agent / client**, **service**, **region**, **account or project**, the **affected resource**, the **permissions** involved and a plain-language **What happened** summary. The **raw audit log** is one click away.
- **A finding per event.** Each security-relevant event creates a real-time finding (severity from the event catalogue) next to your scan findings, so *CloudTrail logging stopped* or *S3 bucket policy made public* is triaged in the same place as everything else.
- **Noise control.** IAM policy changes that only touch provider service agents are marked as noise; **Hide noise** (on by default) keeps the feed readable while the events remain searchable.

## Set up event delivery

Delivery is **push-based**: you create one event route in each cloud that targets the platform webhook. Every delivery must carry your **team's webhook token**, which binds the event to your team; an event is accepted only for cloud accounts your team has onboarded. The scanning role needs no additional permission; the person creating the route needs the usual admin rights for EventBridge, Pub/Sub or Event Grid. The in-app setup panel on the **Cloud Events** tab shows your instance's exact URLs.

### 1. Generate the team webhook token

On **Cloud Events**, open the setup panel and select **Generate token** (needs **Manage Cloud Accounts**). The token is shown **once** — copy it now; afterwards only a short hint is displayed. **Rotate token** replaces it immediately: routes still using the old token stop delivering until you update them.

### 2. Create the route in each cloud

| Cloud | Route | Webhook |
| --- | --- | --- |
| **AWS** | CloudTrail → **EventBridge rule** → API destination. Create an EventBridge *connection* with authorization type **API Key**, key name `x-offload-webhook-token` and your token as the value. | `POST https://<your-host>/api/cloud-events/webhook/aws` |
| **AWS via SNS** | SNS HTTPS subscriptions cannot send headers, so subscribe the URL with the token in the path. | `POST https://<your-host>/api/cloud-events/webhook/aws/<team token>` |
| **GCP** | Cloud Audit Logs → **Logging sink** → Pub/Sub topic → **push subscription** to the URL with the token. | `POST https://<your-host>/api/cloud-events/webhook/gcp/<team token>` |
| **Azure** | Activity Log → **Event Grid** system topic → event subscription (endpoint type *Webhook*) to the URL with the token. The subscription validation handshake is handled automatically. | `POST https://<your-host>/api/cloud-events/webhook/azure/<team token>` |

The token can be sent either in the URL path or in the `x-offload-webhook-token` header, for any provider.

### Authenticating the webhook

| Check | When it applies |
| --- | --- |
| **Team webhook token** | Always. A missing token is rejected with `401`; an unknown token with `401`. |
| **GCP OIDC token** | When the operator sets `GCP_PUBSUB_OIDC_AUDIENCE`, enable OIDC authentication on the push subscription with that audience; requests without the OIDC token are rejected. |
| **SNS certificate chain** | SNS pushes are verified with the SNS signing certificate. |

:::warning[The shared webhook URL is off by default]
Earlier releases accepted events on a shared, token-less URL authenticated by deployment-wide secrets (`WEBHOOK_SECRET_AWS`, `WEBHOOK_SECRET_GCP`, `WEBHOOK_SECRET_AZURE`). That path is now **rejected** unless the operator sets the deprecated `CSPM_CLOUD_EVENT_ALLOW_GLOBAL_SECRET=true`, in which case the team is taken from the account ID in the payload. On that shared path, `CSPM_CLOUD_EVENT_STRICT_AUTH` (default `true`) rejects unsigned requests and SNS deliveries need the topic in the `CSPM_AWS_SNS_TOPIC_ARN` allowlist. If your routes still use the shared URL, generate a team token and move them to the per-team URL before upgrading.
:::

:::tip[Test with a harmless event]
After wiring AWS, add and remove an ingress rule on a test security group — `AuthorizeSecurityGroupIngress` / `RevokeSecurityGroupIngress` events show within seconds. On GCP, add and remove a viewer binding on a sandbox project; on Azure, change a tag on a resource group.
:::

## Reading the feed

The feed auto-refreshes every 30 seconds. Filter by **provider** and **severity**; the tiles show totals for the current window and how many providers are actively sending. Select an event for the full detail — identity, client, permissions, the change summary and the raw log.

Real-time findings carry a `rt_` identifier and appear on the **Findings** tab alongside scan findings; the next scheduled scan does not overwrite them.

Events are visible to your team only. When the same provider account is connected by several teams, each owning team sees its events. If the feed cannot load, the tab says so instead of showing an empty feed.

## Related

- [Required Permissions — Bucket C](./permissions.md#bucket-c--cloud-events-auditactivity-streaming) — the one-time setup rights per cloud.
- [Reviewing & Triaging Findings](./findings.md) — where event-driven findings are worked.
- [Notifications](../integrations/notifications.md) — routing critical events to Slack, Teams, email or a SIEM.
