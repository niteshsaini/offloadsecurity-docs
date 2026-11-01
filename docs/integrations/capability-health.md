---
title: "Data Collection Health"
sidebar_label: "Data Collection Health"
sidebar_position: 11
new_in: 1.4.0
description: "See which connected sources — cloud accounts, Kubernetes clusters, container registries, threat feeds, integrations and the GitHub App — have stopped delivering data, why, and how to restore them."
---

# Data Collection Health

A source that silently stops delivering data is worse than one that fails loudly: findings simply stop changing. The **Data collection health** panel lists every connected source of your team, says whether it is still collecting, names the reason when it is not, and gives the steps to restore it.

**Where:** **Integrations** → **Data collection health** (the first panel above the catalog). Reading it needs **View Integrations**.

## What it covers

| Source | Where its status comes from |
| --- | --- |
| Cloud accounts | Scan results and the account's pause state after repeated failures |
| Kubernetes clusters | The cluster's last scan and its last error |
| Container registries | The last registry sync and its errors |
| Threat feeds | The feed's last fetch and health |
| Integrations | The connection's health checks and syncs |
| GitHub App | The installation's status |

A source type that cannot be read is listed as unavailable, never dropped from the list.

## States

| State | Tile | Meaning |
| --- | --- | --- |
| **Lost** | Lost | The source has stopped collecting — for example rejected credentials, a removed permission, an unreachable cluster, an uninstalled App |
| **Stale** | Stale | No successful collection for 7 days |
| **Degraded** | Degraded | Collection runs but is partial |
| **Unknown** | Not yet collected | Nothing has been collected yet, so there is nothing to judge |
| **Healthy** | Healthy | Collecting normally |

Each impaired source carries a **category** saying why — `credentials`, `permissions`, `unreachable`, `partial`, `stale`, `paused`, `uninstalled`, `never_collected` and similar — the reason text, and the time of its last success.

## Restore a source

1. Open **Integrations**. The panel shows **Needs attention** by default; switch to **All sources** to see healthy ones too.
2. On an impaired source, click **How to restore** for the steps.
3. Click **Open** (or **Configure** for a source that was never set up) to go to the screen where it is fixed. For a cloud account, **Re-check** runs the credential check again now.
4. Click **Refresh** on the panel to read the result.

## Alerts and recovery times

Every **15 minutes** a background check records each source's state for every team. When a source becomes **lost**, one alert is raised; when it is restored, the restoration is recorded. From these transitions the platform measures *time to detect* and *time to restore*; the panel shows them, and `GET /api/capability-health/recovery?days=30` returns them. A loss that was already present the first time a source was observed is not counted toward detection time.

## API

| Task | Endpoint |
| --- | --- |
| Every source, normalized | `GET /api/capability-health?stale_days=7` |
| Detection and restore times | `GET /api/capability-health/recovery?days=30` |

Both need **View Integrations**.

## Related

- [Connecting Tools](./connecting-tools.md) — health checks and syncs of individual integrations.
- [Pull request scanning](../security-scanning/code/pull-request-scanning.md) — the GitHub App, including its **Webhook deliveries** panel.
- [Troubleshooting & FAQ](./troubleshooting.md).
