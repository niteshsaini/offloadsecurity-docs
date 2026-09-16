---
title: "Fix with Agent"
sidebar_label: "Fix with Agent"
sidebar_position: 9
description: "Let an agent clone the repository, fix a finding, open a pull request, and verify the fix on the merged commit — opt-in per deployment and per team, with honest verification outcomes."
---

# Fix with Agent

**AI Fix Suggestion** drafts a change for you to apply. **Fix with agent** goes further: an agent clones the repository into an isolated worker, makes the change, and opens a pull request — then, after the PR merges, the platform re-scans the merged commit and reports whether the finding is really gone. Because it touches your code, it is off until two switches are on.

## Enable it

### 1. Deployment (once)

The agent runs in its own worker, without access to the Docker socket, started only under the `agentic-fix` compose profile:

```bash
# .env
AGENTIC_FIX_ENABLED=true
```

```bash
docker compose --profile agentic-fix up -d celery-fix-worker
```

On the client compose file use `docker compose -f docker-compose.client.yml --profile agentic-fix up -d celery-fix-worker`. Without the profile the worker does not exist and agent runs stay queued.

The agent needs a model provider configured for the team ([AI Assistant](../../reports-and-ai/ai-assistant.md)); it reasons about the code with the same provider the assistant uses.

### 2. Team (each team that wants it)

Code Command Center → **Findings** shows a banner while agentic fixes are off for the team: *"Agentic fixes are switched off for this team."* A user with team-management rights switches them on there. Until then, **Fix with agent** is visible but disabled, with the reason in its tooltip, so nobody is left guessing why the button does nothing.

## Run a fix

1. Open a **SAST**, **dependency (SCA)**, **IaC** or **secret** finding in the Findings tab. For a secret the agent removes the hard-coded credential from the code; rotating it at the provider is still yours to do.
2. Select **Fix with agent**. The row reports *Agent run queued* and updates as the run progresses; starting a second run for the same finding while one is in flight is refused rather than duplicated.
3. The agent clones the repository at the finding's branch, applies a fix, and opens a **pull request** on the connected provider. The PR body links back to the finding; the finding's drawer links to the PR.
4. Review the PR like any other. Nothing is merged for you.

Agent runs need the **Execute Remediations** permission and a Git token with pull-request write access — the same requirements as [Fix PR](./findings-and-reports.md#fixing).

## Verification after merge

When the PR merges, the platform scans **that merged commit** and looks for the finding it set out to fix. The outcome is recorded on the finding:

| Outcome | Meaning |
| --- | --- |
| **verified fixed** | The scanner that produced the finding ran on the merged commit and the finding is gone. The finding is closed with the verification as evidence. |
| **still present** | The finding is still reported. The finding stays open and says so. |
| **verification inconclusive** | The verification scan could not prove anything: it ran on a different commit, its findings were truncated, or the scanner that produced the original finding did not complete. Nothing is closed. |

The last row is deliberate. A clean scan from a *different* scanner in the same family — say, OpenGrep completing while Bandit failed — proves nothing about a Bandit finding, and the platform will not mark it fixed on that basis. Re-run the scan; a completed run of the right scanner turns *inconclusive* into a verdict.

## Campaigns

Several findings of the same kind — a vulnerable dependency across many repositories, one rule across a service — can be fixed as a **campaign** from the API (`POST /api/agentic-fix/campaigns`), which queues one agent run per finding and tracks them together. See [Scanning API](../api.md#code).

## What the agent can and cannot do

- It works on a clone inside the fix worker; it has no access to the platform's Docker socket or to other teams' repositories.
- It opens pull requests only; it never pushes to a protected branch and never merges.
- Each run is bounded: 15 minutes for the fix (`AGENTIC_FIX_RUN_TIMEOUT_S`), 10 for verification (`AGENTIC_FIX_VERIFY_TIMEOUT_S`), two attempts (`AGENTIC_FIX_MAX_ATTEMPTS`). A run that fails is reported on the finding with the reason.

## Related

- [Findings & Reports](./findings-and-reports.md#fixing) — AI Fix Suggestion and manual Fix PR.
- [Vulnerability Management — Triage](../../vulnerability-risk/vulnerability-management/triage.md) — auto-fix from the triage queue uses the same agent.
- [Scanning API](../api.md#code) — `/api/agentic-fix/*`.
