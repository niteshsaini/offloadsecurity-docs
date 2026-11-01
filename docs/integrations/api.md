---
title: "Integrations API"
sidebar_label: "API"
sidebar_position: 13
description: "Catalog, wizard, sync, health and data endpoints; data collection health; Slack routing, notification preferences and the in-app center; webhook subscriptions; Jira and GitHub / GitLab issues; the audit-trail SIEM export; SMTP and channel tests — with the permission each one needs."
---

# Integrations API

Almost everything in this section is available over the REST API; the exception is GitHub & GitLab Issues, which is session-only. [API Reference](../api-reference/index.md) covers authentication and conventions. Swagger at `https://<your-host>/api/docs` is exhaustive, but is **off in production** unless the deployment sets `ENABLE_API_DOCS=true`.

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"
```

Send the key as `X-API-Key`; calls are scoped to the key's team.

## Catalog and connections

| Task | Endpoint | Notes |
| --- | --- | --- |
| Catalog | `GET /api/integrations/?category=&search=` | Every tool with `status` (`available` / `planned`), `capability` (`ingest` · `bidirectional` · `push` · `connect_test` · `listing`) and `capability_note` |
| Categories · stats | `GET /api/integrations/categories` · `GET /api/integrations/stats` | Categories that hold tools, with counts |
| Wizard template | `GET /api/integrations/templates/{tool_id}` · `GET /api/integrations/templates` | Required and optional fields per tool |
| Wizard | `POST /api/integrations/wizard/start?tool_id=` → `POST …/wizard/step` `{session_id, step, step_data}` (step 2 `step_data.credentials`, step 4 `step_data.monitoring.frequency_hours`) → `POST …/wizard/test-connection` `{session_id}` → `POST …/wizard/complete` `{session_id}` | **Manage Integrations**. Complete re-tests server-side and returns `connection_verified` |
| Test without saving | `POST /api/integrations/test-connection` `{tool_id, configuration}` | **Manage Integrations**. Refused for catalog-only tools |
| Connected tools | `GET /api/integrations/user-integrations` | The wizard store: `tool_id`, `status`, `sync_status`, `last_sync`, `health_status`, `error_message`. Any member |
| Sync now | `POST /api/integrations/sync/{tool_id}` | Returns a `job_id`; poll `GET /api/jobs/{job_id}`. **Manage Integrations** |
| Remove | `DELETE /api/integrations/user-integrations/{integration_id}` | **Manage Integrations** |
| Ingested data | `GET /api/integrations/data/{tool_id}` (`wazuh` · `greenbone-openvas` · `sonarqube` · `jenkins`) · `GET /api/integrations/wazuh/browse/{agents\|alerts\|vulnerabilities}?limit=&offset=` | Latest snapshot with `counts`, `data`, `synced_at`; Wazuh browse queries the live instance. **View Integrations** |
| Health | `GET /api/integrations/health-status` · `GET …/health-status/{integration_id}` · `POST /api/integrations/recheck/{integration_id}` | Latest recorded checks; recheck runs one now (**Manage Integrations**) |
| Request a tool | `POST /api/integrations/request-custom` `{tool_name, description, …}` | **Manage Integrations** |
| Data collection health | `GET /api/capability-health?stale_days=7` · `GET /api/capability-health/recovery?days=30` | Every source's state, reason and restore steps; detection and restore times. **View Integrations** |

## Notifications

| Task | Endpoint | Notes |
| --- | --- | --- |
| In-app center | `GET /api/notifications?unread_only=&skip=&limit=` · `GET /api/notifications/unread-count` · `POST /api/notifications/{notification_id}/read` · `POST …/{notification_id}/dismiss` · `POST /api/notifications/read-all` | Per-user read state |
| Team preferences | `GET /api/notifications/preferences` · `PUT /api/notifications/preferences` `{channels{email,slack,teams,google_chat,in_app,webhook,pagerduty}, muted_categories[], alerts{enabled, min_severity, channels{in_app,slack,teams,google_chat}}}` | PUT needs **Manage Integrations**; GET also returns `me` and `defaults_in_effect` |
| My preferences | `PUT /api/notifications/preferences/me` `{opted_out, muted_categories[]}` | Any member |
| Slack routing rules | `GET /api/notifications/slack/routing` · `POST …/slack/routing` `{name, category, severities[], sources[], webhook_url, channel_name, priority?, enabled?}` · `DELETE …/slack/routing/{rule_id}` | **Manage Integrations**; rules are returned with `webhook_url_masked` |
| Slack test · status · vocab | `POST …/slack/test` `{webhook_url, channel_name}` · `GET …/slack/status` · `GET …/slack/categories` | Categories, severities and source ids accepted by rules |
| Channel test | `POST /api/integration-config/notifications/test` `{channel: email\|slack\|teams\|all, message?}` · `GET …/notifications/status` | **Manage Integrations** |
| SMTP (config-route store) | `GET` · `POST /api/integration-config/smtp` `{smtp_host, smtp_port, smtp_username, smtp_password, from_email, use_tls}` · `POST …/smtp/test` | Alternative to the wizard for scripts; the wizard store is read when this is empty |
| Confluence publish | `POST /api/integration-config/confluence/publish-compliance-summary` | Publishes the compliance summary page to the connected space |

## Webhooks

| Task | Endpoint | Notes |
| --- | --- | --- |
| Subscriptions | `POST /api/webhooks` `{name, url, events[], secret?, headers?}` · `GET /api/webhooks` · `PUT /api/webhooks/{subscription_id}` `{…, enabled}` · `DELETE …/{subscription_id}` | Create returns `signing_secret` once when no `secret` is given. Reads need **View Integrations**; changes **Manage Integrations** |
| Rotate secret | `POST /api/webhooks/{subscription_id}/rotate-secret` | New secret, returned once. **Manage Integrations** |
| Test | `POST /api/webhooks/{subscription_id}/test` | One signed `webhook.test`; HTTP 502 when the receiver did not accept it. **Manage Integrations** |
| Delivery log | `GET /api/webhooks/{subscription_id}/deliveries?limit=50&offset=0&outcome=success\|failed` | One row per attempt, newest first; `metadata.total` for paging. **View Integrations** |
| Event types · policy | `GET /api/webhooks/event-types/list` · `GET /api/webhooks/capabilities` | Event catalogue with payload examples; limits, retry delays and timeout. **View Integrations** |

## Jira

| Task | Endpoint | Notes |
| --- | --- | --- |
| Tickets the platform created | `GET /api/integrations/jira/tickets?limit=` | Key, severity, source, status, `status_updated_at`. **View Integrations** |
| Sync status now | `POST /api/integrations/jira/tickets/sync-status` | Runs the Jira → platform pass immediately |
| Create for selected findings | `GET /api/vulnerabilities/jira/ticket-candidates?limit=` · `POST /api/vulnerabilities/jira/create-tickets` `{items: [...]}` (≤ 25) | High findings without a ticket; **Vulnerability Management** permission |
| Tickets for Wazuh alert groups | `POST /api/integrations/wazuh/alert-groups/tickets` | From Endpoint Security → Alerts |
| Jira (config-route store) | `GET` · `POST /api/integration-config/jira` `{base_url, auth_email, auth_token, default_project_key}` | Alternative to the wizard for scripts |

## GitHub & GitLab Issues

Session-only: these endpoints do not accept API keys. They back the [GitHub & GitLab Issues](./git-issues.md) panel.

| Task | Endpoint |
| --- | --- |
| Create from occurrences · from alert groups (≤ 25) | `POST /api/git-issues/occurrences` · `POST /api/git-issues/alert-groups` |
| Links · settings | `GET /api/git-issues/links` · `GET /api/git-issues/settings` |
| Check access | `POST /api/git-issues/check` |
| Admin settings | `PUT /api/git-issues/settings/auto-create` · `PUT …/settings/service-connection` · `PUT …/settings/public-targets` (**Manage Integrations**) |
| Refresh statuses | `POST /api/git-issues/sync` |

## Audit trail for a SIEM

| Task | Endpoint | Notes |
| --- | --- | --- |
| Pull the hash-chained audit trail | `GET /api/audit-trail/export/siem?after_seq=&limit=&format=jsonl\|cef` | Team admin session, or a team admin's API key with the `admin:audit` scope. See [SIEM Forwarding](./siem-forwarding.md#pull-the-audit-trail-instead) |

## Permissions

| Action | Permission |
| --- | --- |
| Read the catalog, templates, connected tools, health status | any authenticated team member |
| Read webhooks and their delivery log, data collection health | **View Integrations** |
| Read ingested data (`/data/{tool_id}`, Wazuh browse) and the platform's Jira tickets | **View Integrations** (`view_integrations`) — Security Manager, Security Analyst, Compliance Officer, Auditor |
| Connect, test, sync, reconfigure, remove; Slack routing rules; team notification preferences; create / change / test webhook subscriptions; GitHub & GitLab Issues admin settings; SMTP / Jira / Confluence config routes | **Manage Integrations** (`manage_integrations`) — Admin, Security Manager |
| Read notifications, mark read / dismiss, personal preferences | any authenticated team member |
| Create Jira tickets for selected findings | **Vulnerability Management** |

See [Authentication](../api-reference/authentication.md) for key scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
