---
title: "Jira"
sidebar_label: "Jira"
sidebar_position: 4
description: "The two-way Jira integration — critical findings become tickets automatically, high findings on request, ticket status closes or reopens the finding and resolving the finding transitions the ticket — plus the Jira tab, the status-sync cadence and the transitions used."
---

# Jira

Jira is the platform's only **two-way** integration. Findings become tickets — critical ones automatically, high ones when an analyst asks — and the two stay in step: closing the ticket in Jira resolves the finding, resolving the finding in the platform transitions the ticket, and a ticket reopened in Jira reopens the finding. Remediation stays provable on both sides.

## Connect

**Integrations → Jira → Connect.** The wizard asks for:

| Field | Value |
| --- | --- |
| `base_url` | Your Jira Cloud site, e.g. `https://acme.atlassian.net` |
| `auth_email` · `auth_token` | The account the platform acts as and an **API token** created for it |
| `default_project_key` | The project tickets are created in (e.g. `SEC`) |

The connection test calls `/rest/api/3/myself` with those credentials. Use a dedicated account that can create and transition issues in the target project; the labels the platform adds (`auto-created`, `security`, the severity) make its tickets easy to filter.

## Tickets from findings

| Path | When | Who |
| --- | --- | --- |
| **Automatic** | Every new **critical** finding — cloud findings the moment they are created, other sources (Kubernetes, container, code, IaC, API, domain) on the next vulnerability sync, capped at 50 new tickets per sync so a first connection does not flood the project | Nobody; happens once Jira is connected |
| **On request** | **High** findings without a ticket, selected in Vulnerability Management → *Raw findings* → **Create Jira Tickets** (up to 25 per action), or **Create Jira Ticket** on a single occurrence | Anyone with the Vulnerability Management permission |

A ticket's summary is `[SEVERITY] <finding title>`; the description carries the severity, source module, resource and the finding's own description. One finding gets one ticket — a finding that already has a key is skipped, and the key is shown on the occurrence.

## Status sync — both directions

- **Jira → platform.** Every 15 minutes (`JIRA_STATUS_SYNC_INTERVAL_MINUTES`) the platform reads the status category of each open ticket. A ticket moved to a **done** category resolves the linked finding (occurrence and unified finding) with the ticket as the recorded reason; a ticket moved back to *new* / *in progress* reopens a finding that Jira had closed. **Sync status now** on the Jira tab runs the same pass immediately.
- **Platform → Jira.** Resolving a finding — by reconciliation (the scanner no longer sees it), by a triage decision, or by an analyst — transitions the ticket through the first available of `Done`, `Resolve`, `Close`; reopening uses `Reopen`, `To Do`, `Backlog`. Override the names for a custom workflow with `JIRA_RESOLVED_TRANSITION` / `JIRA_REOPENED_TRANSITION` (comma-separated). If none of the transitions exists in the project's workflow, the ticket is left as is and the log says which names were tried.

## The Jira tab

**Where:** Vulnerability Management → **Jira** tab (it appears once Jira is connected for the team).

Every ticket the platform created, newest first, with its key, severity, source, current Jira status and when the status last changed — the same list as `GET /api/integrations/jira/tickets`. It is the answer to "which of our findings are actually being worked on".

:::tip[One project per team]
Connections are per team and so is `default_project_key`. Teams that share a Jira site but own different services should each connect with their own project, so ticket volume and ownership stay separate.
:::

## Related

- [Vulnerability Management](../vulnerability-risk/vulnerability-management/index.mdx) — where tickets are created on request and where the ticket key shows.
- [Triage](../vulnerability-risk/vulnerability-management/triage.md) — decisions that resolve findings, and therefore tickets.
- [Integrations API](./api.md#jira) — ticket list and sync endpoints.
