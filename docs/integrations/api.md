---
title: "Integrations API"
sidebar_label: "API"
sidebar_position: 10
description: "Catalog, wizard, sync, health and data endpoints; Slack routing, notification preferences and the in-app center; webhook subscriptions; Jira tickets; SMTP and channel tests — with the permission each one needs."
---

# Integrations API

Everything in this section is available over the REST API. [API Reference](../api-reference/index.md) covers authentication and conventions; Swagger at `https://<your-host>/api/docs` is exhaustive.

```bash
export OFFLOAD_HOST="https://your-instance.example.com"
export OFFLOAD_API_KEY="osk_xxxxxxxxxxxxxxxxxxxx"
```

Send the key as `X-API-Key`; calls are scoped to the key's team.

## Catalog and connections

| Task | Endpoint | Notes |
| --- | --- | --- |
| Catalog | `GET /api/integrations/?category=&search=` | Every tool with `status` (`available` / `planned`), `capability` and `capability_note` |
| Categories · stats | `GET /api/integrations/categories` · `GET /api/integrations/stats` | Categories that hold tools, with counts |
| Wizard template | `GET /api/integrations/templates/{tool_id}` · `GET /api/integrations/templates` | Required and optional fields per tool |
| Wizard | `POST /api/integrations/wizard/start?tool_id=` → `POST …/wizard/step` `{session_id, step, step_data}` (step 2 `step_data.credentials`, step 4 `step_data.monitoring.frequency_hours`) → `POST …/wizard/test-connection` `{session_id}` → `POST …/wizard/complete` `{session_id}` | **Manage Integrations**. Complete re-tests server-side and returns `connection_verified` |
| Test without saving | `POST /api/integrations/test-connection` `{tool_id, configuration}` | **Manage Integrations** |
| Connected tools | `GET /api/integrations/user-integrations` | The wizard store: `tool_id`, `status`, `sync_status`, `last_sync`, `health_status`, `error_message`. Any member |
| Sync now | `POST /api/integrations/sync/{tool_id}` | Returns a `job_id`; poll `GET /api/jobs/{job_id}`. **Manage Integrations** |
| Remove | `DELETE /api/integrations/user-integrations/{integration_id}` | **Manage Integrations** |
| Ingested data | `GET /api/integrations/data/{tool_id}` (`wazuh` · `sonarqube` · `jenkins`) · `GET /api/integrations/wazuh/browse/{agents\|alerts\|vulnerabilities}?limit=&offset=` | Latest snapshot with `counts`, `data`, `synced_at`; Wazuh browse queries the live instance. **View Integrations** |
| Health | `GET /api/integrations/health-status` · `GET …/health-status/{integration_id}` · `POST /api/integrations/recheck/{integration_id}` | Latest recorded checks; recheck runs one now (**Manage Integrations**) |
| Request a tool | `POST /api/integrations/request-custom` `{tool_name, description, …}` | **Manage Integrations** |

## Notifications

| Task | Endpoint | Notes |
| --- | --- | --- |
| In-app center | `GET /api/notifications?unread_only=&skip=&limit=` · `GET /api/notifications/unread-count` · `POST /api/notifications/{notification_id}/read` · `POST …/{notification_id}/dismiss` · `POST /api/notifications/read-all` | Per-user read state |
| Team preferences | `GET /api/notifications/preferences` · `PUT /api/notifications/preferences` `{channels{email,slack,teams,in_app,webhook,pagerduty}, muted_categories[], alerts{enabled, min_severity, channels{in_app,slack,teams}}}` | PUT needs **Manage Integrations**; GET also returns `me` and `defaults_in_effect` |
| My preferences | `PUT /api/notifications/preferences/me` `{opted_out, muted_categories[]}` | Any member |
| Slack routing rules | `GET /api/notifications/slack/routing` · `POST …/slack/routing` `{name, category, severities[], sources[], webhook_url, channel_name}` · `DELETE …/slack/routing/{rule_id}` | **Manage Integrations**; rules are returned with `webhook_url_masked` |
| Slack test · status · vocab | `POST …/slack/test` `{webhook_url, channel_name}` · `GET …/slack/status` · `GET …/slack/categories` | Categories, severities and source ids accepted by rules |
| Channel test | `POST /api/integration-config/notifications/test` `{channel: email\|slack\|teams\|all, message?}` · `GET …/notifications/status` | **Manage Integrations** |
| SMTP (config-route store) | `GET` · `POST /api/integration-config/smtp` `{smtp_host, smtp_port, smtp_username, smtp_password, from_email, use_tls}` · `POST …/smtp/test` | Alternative to the wizard for scripts; the wizard store is read when this is empty |
| Confluence publish | `POST /api/integration-config/confluence/publish-compliance-summary` | Publishes the compliance summary page to the connected space |

## Webhooks

| Task | Endpoint | Notes |
| --- | --- | --- |
| Subscriptions | `POST /api/webhooks` `{name, url, events[], secret?, headers?}` · `GET /api/webhooks` · `PUT /api/webhooks/{subscription_id}` `{…, enabled}` · `DELETE …/{subscription_id}` | Create / update / delete need **Manage Integrations** |
| Test · log · events | `POST /api/webhooks/{subscription_id}/test` · `GET …/{subscription_id}/deliveries?limit=` · `GET /api/webhooks/event-types/list` | Deliveries newest first with `status_code`, `success`, `timestamp` |

## Jira

| Task | Endpoint | Notes |
| --- | --- | --- |
| Tickets the platform created | `GET /api/integrations/jira/tickets?limit=` | Key, severity, source, status, `status_updated_at`. **View Integrations** |
| Sync status now | `POST /api/integrations/jira/tickets/sync-status` | Runs the Jira → platform pass immediately |
| Create for selected findings | `GET /api/vulnerabilities/jira/ticket-candidates?limit=` · `POST /api/vulnerabilities/jira/create-tickets` `{items: [...]}` (≤ 25) | High findings without a ticket; **Vulnerability Management** permission |
| Jira (config-route store) | `GET` · `POST /api/integration-config/jira` `{base_url, auth_email, auth_token, default_project_key}` | Alternative to the wizard for scripts |

## Permissions

| Action | Permission |
| --- | --- |
| Read the catalog, templates, connected tools, health status | any authenticated team member |
| Read ingested data (`/data/{tool_id}`, Wazuh browse) and the platform's Jira tickets | **View Integrations** (`view_integrations`) — Security Manager, Security Analyst, Compliance Officer, Auditor |
| Connect, test, sync, reconfigure, remove; Slack routing rules; team notification preferences; webhook subscriptions; SMTP / Jira / Confluence config routes | **Manage Integrations** (`manage_integrations`) — Admin, Security Manager |
| Read notifications, mark read / dismiss, personal preferences | any authenticated team member |
| Create Jira tickets for selected findings | **Vulnerability Management** |

See [Authentication](../api-reference/authentication.md) for key scopes and [Conventions](../api-reference/conventions.md) for pagination, error shapes and rate limits.
