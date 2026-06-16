---
title: "Notifications"
sidebar_label: "Notifications"
sidebar_position: 1
---

# Notifications

Notifications keep your team informed the moment something important happens — a new critical finding, a scan that failed, an SLA about to breach, or a change in your compliance posture. Offload Security can deliver these alerts to **Slack**, **email**, **Microsoft Teams**, and your own **webhook endpoints**, and you choose exactly which events trigger an alert on each channel.

## What it does

- **Sends alerts to the channels your team already uses** — Slack, email (SMTP), Microsoft Teams, and outbound webhooks for your own automation or SIEM.
- **Lets you choose what triggers an alert** — by event type (for example, new findings, scan failures, SLA warnings), by severity (critical/high/medium/low/info), and by the part of the platform the event came from (cloud, Kubernetes, registry, code scanning, and more).
- **Routes the right alert to the right place** — send critical security alerts to one Slack channel and routine scan completions to another.
- **Shows in-app alerts** in real time in the platform's notification center, so signed-in users see updates without leaving the screen.
- **Verifies delivery before you rely on it** — every channel has a **test** action, and webhooks keep a delivery log.

Notifications are **team-scoped**: each team configures its own channels and rules, and only sees its own alerts. Connection details and secrets are stored **encrypted**.

:::note Who can configure this
Setting up channels and rules requires the **Manage Integrations** permission (Admins have it by default). See **[Roles & Team Management](../authentication/rbac-team-management.md)**.
:::

## Notification channels

| Channel | How alerts arrive | Best for |
|---|---|---|
| **Slack** | Posts a message to a Slack channel via an incoming webhook | Team-wide, real-time alerting |
| **Email (SMTP)** | Sends email through your mail server | Digests, audit trails, recipients without Slack |
| **Microsoft Teams** | Posts an Adaptive Card to a Teams channel via a webhook | Teams-based organizations |
| **Webhooks** | Sends a signed JSON payload to a URL you control | SIEM/SOAR, ticketing, and custom automation |
| **In-app** | Appears in the notification center inside the platform | Signed-in users working in the UI |

## How to set up Slack

1. In Slack, create an **Incoming Webhook** for the channel you want alerts in, and copy its webhook URL.
2. In the platform, open **Integrations**, find **Slack**, and select **Connect**.
3. Paste the **webhook URL**, then choose **Test Connection** to send a test message to the channel.
4. Select **Save Configuration**.

### Route specific alerts to specific channels

For finer control, you can add **routing rules** so different kinds of alerts land in different Slack channels. Each rule maps a combination of category, severity, and source to a channel's webhook:

- **Category** — choose one:
  - **Security Alerts** — findings from cloud, Kubernetes, registry, and code scanning.
  - **System Notifications** — scan completions, scheduled-job results, and configuration changes.
  - **System Errors** — service issues, task failures, and connectivity problems.
- **Severities** *(optional)* — limit the rule to specific severities (`critical`, `high`, `medium`, `low`, `info`). Leave empty to match all.
- **Sources** *(optional)* — limit the rule to specific modules (for example, `cspm`, `kubernetes`, `registry`, `code_scan`, `compliance`). Leave empty to match all.
- **Channel** — the Slack webhook URL and a display name (for example, `#security-critical`).

**Example:** send only critical and high security alerts to `#security-critical` by creating a rule with category **Security Alerts**, severities `critical, high`, and that channel's webhook.

:::tip Default channel
If no rule matches an alert, it goes to your default Slack channel (configured during setup). Use rules to peel off high-priority alerts, and let everything else fall through to the default.
:::

## How to set up email (SMTP)

1. In **Integrations**, find the **SMTP / Email** option and select **Connect**.
2. Enter your mail-server details:

   | Field | What to enter |
   |---|---|
   | **SMTP Server** | Your mail host, e.g. `smtp.gmail.com` |
   | **SMTP Port** | Usually `587` for STARTTLS |
   | **Username / Email** | The account that sends the mail |
   | **Password / App Password** | The account password, or an app-specific password |
   | **From Email Address** | The sender shown to recipients (defaults to the username if left blank) |
   | **Use TLS (STARTTLS)** | Enable for an encrypted connection (recommended) |

3. Select **Test Connection** to confirm the platform can reach your mail server and authenticate.
4. Select **Save Configuration**.

:::tip Use an app password
Many providers (such as Gmail and Microsoft 365) block plain account passwords for SMTP. Generate an **app password** in your provider's security settings and use that instead.
:::

## How to set up Microsoft Teams

1. In Teams, add an **Incoming Webhook** connector to the target channel and copy its URL.
2. In **Integrations**, connect **Microsoft Teams** and paste the **webhook URL**.
3. Use the **test** action to confirm a card arrives in the channel, then save.

## How to set up webhook subscriptions

Webhooks let you forward platform events as JSON to any HTTPS endpoint — your SIEM, a serverless function, or an internal service.

1. In **Integrations**, open **Webhooks** and create a subscription.
2. Provide:
   - **Name** — a label for the subscription.
   - **URL** — the HTTPS endpoint that receives the payload.
   - **Events** — one or more event types to subscribe to (see below). You can use wildcards such as `finding.*` to match a whole group, or `*` for all events.
   - **Signing secret** *(optional)* — used to sign each payload (HMAC) so your endpoint can verify it came from Offload Security.
   - **Custom headers** *(optional)* — extra HTTP headers to include with each delivery.
3. Use **Test delivery** to send a sample event, and check the **delivery log** to confirm it was received.

:::warning Use a reachable, public HTTPS endpoint
Webhook URLs must point to a routable address. Private, internal, or cloud-metadata addresses are rejected for security reasons. Make sure the endpoint is reachable from the platform before relying on it.
:::

## Choosing what events trigger alerts

These are the event types you can subscribe to (for webhooks) and that drive Slack, email, and Teams alerts:

| Event | Fires when |
|---|---|
| `finding.created` | A new finding is detected |
| `finding.resolved` | A finding is marked resolved |
| `finding.excepted` | A finding exception is approved |
| `scan.started` / `scan.completed` / `scan.failed` | A scan starts, finishes, or fails |
| `sla.warning` | An SLA is approaching its deadline |
| `sla.breached` | An SLA deadline is missed |
| `compliance.drift_detected` | Your compliance posture changes |
| `exception.requested` / `exception.approved` / `exception.rejected` | A risk exception moves through review |
| `user.login` / `user.mfa_enabled` | A user signs in or enables MFA |

Out of the box, the platform automatically alerts on the events that matter most — **critical and high-severity findings**, **SLA warnings and breaches**, **compliance drift**, and **scan failures** — so you get useful alerts even before you add any custom rules. Use Slack routing rules and webhook subscriptions to broaden, narrow, or redirect these as your team prefers.

## Verify your setup

- Use **Test Connection** (Slack, email, Teams) or **Test delivery** (webhooks) on each channel and confirm the message arrives.
- Check the notification channel status in **Integrations** to see which channels are configured.
- For webhooks, review the **delivery log** to confirm events are reaching your endpoint and to troubleshoot failures.

:::tip Start narrow, then expand
Begin with one channel and the default alerts, confirm they land correctly, then add routing rules and webhook subscriptions for additional teams, severities, or destinations.
:::

## Related

- **[Third-party integrations](./third-party.md)** — connect ticketing, SIEM, and other external tools.
- **[Integrations overview](./index.md)** — all of the platform's connectivity options.
- **[Roles & Team Management](../authentication/rbac-team-management.md)** — who can configure integrations and notifications.
- **[CI/CD integration](../infrastructure/testing-cicd.md)** — gate pipelines on scan results.
