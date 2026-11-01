---
title: "Fix with Agent"
sidebar_label: "Fix with Agent"
sidebar_position: 9
status: opt-in
description: "Let an agent fix a finding in an isolated sandbox, check the fix with the platform's own scanner and the repository's tests, and open a pull request — off by default, enabled per deployment and per team."
---

# Fix with Agent

**AI Fix Suggestion** drafts a change for you to apply. **Fix with agent** goes further: an agent clones the repository, reproduces the finding, makes the change inside a throwaway sandbox, re-checks it with the platform's own scanner and the repository's tests, and opens a pull request. After the PR merges, the platform re-scans the merged commit and reports whether the finding is really gone.

Because it touches your code, it is **off by default** and needs two switches: one for the deployment, one for each team.

## Enable it

### 1. Deployment (an administrator, once)

The agent runs on its own fix worker, started only under the `agentic-fix` compose profile. With the profile's default runner (`sandbox`), the agent and the repository's own tests run in throwaway **sandbox containers**:

- read-only root filesystem with a temporary `/tmp`, all Linux capabilities dropped, no privilege escalation, memory / CPU / process limits;
- only the scrubbed workspace mounted — no platform credentials in the environment; the model key is passed on stdin;
- an internal network whose only exit is the **agent-egress** proxy, which allows connections only to `AGENT_EGRESS_ALLOW` (by default the Anthropic and OpenAI APIs and PyPI) and always refuses private, loopback and cloud-metadata addresses.

The fix worker itself holds **no Docker socket**. It asks the **agent-launcher** service — the only component with the socket — to start a sandbox; the launcher accepts only "run the sandbox on this workspace" and builds the container itself, so a caller cannot choose an image, mount, capability or network.

```bash
# .env
AGENTIC_FIX_ENABLED=true
AGENT_LAUNCHER_TOKEN=<a long random value>
```

```bash
docker compose -f docker-compose.client.yml --profile agentic-fix pull
docker compose -f docker-compose.client.yml --profile agentic-fix up -d
```

This starts `celery-fix-worker`, `agent-launcher` and `agent-egress`; the `agent-sandbox` image is the one each run uses. Without the profile the worker does not exist and agent runs stay queued — the Findings tab then says nothing is consuming the fix queue.

| Setting | Default | Meaning |
| --- | --- | --- |
| `AGENTIC_FIX_ENABLED` | `false` | Master switch. |
| `AGENTIC_FIX_RUNNER` | `sandbox` on the fix worker (`none` elsewhere) | `none` fails every run with a clear error. `openhands_local` is a development-only in-process runner that also needs `AGENTIC_FIX_ALLOW_INPROCESS=true`; the Findings tab warns when it is in use. |
| `AGENT_LAUNCHER_TOKEN` | — | Shared secret between the fix worker and the launcher; the launcher refuses everything without it. |
| `AGENT_EGRESS_ALLOW` | `.anthropic.com,.openai.com,pypi.org,files.pythonhosted.org` | Where a sandbox may connect. Add your package registries if the repository's tests install from them. |
| `AGENTIC_FIX_SANDBOX_MEMORY` / `_CPUS` / `_PIDS` / `_TMP` | `2g` / `2` / `512` / `1g` | Per-sandbox limits. |

The agent needs a model provider configured for the team ([AI Assistant](../../reports-and-ai/ai-assistant.md)); it reasons about the code with the same provider the assistant uses.

### 2. Team (each team that wants it)

Code Command Center → **Findings** shows a banner while agentic fixes are off for the team: *"Agentic fixes are switched off for this team."* A user with team-management rights selects **Enable for this team** there (API: `POST /api/ai-agents/triage/auto-fix/settings`). Until then, **Fix with agent** is visible but disabled, with the reason in its tooltip. When the deployment is not set up, the Findings tab says why (*"Fix with agent is unavailable. …"*), naming the missing setting.

## Run a fix

1. Open a **SAST**, **dependency (SCA)**, **IaC** or **secret** finding in the Findings tab. For a secret the agent removes the hard-coded credential from the code; rotating it at the provider is still yours to do.
2. Select **Fix with agent**. For a dependency row in *Group by fix*, **Upgrade with agent** runs one upgrade of the package and opens one pull request that closes all of that group's CVEs.
3. Follow the chip on the row: *agent queued → cloning → reproducing → working → verifying → opening PR*. Starting a second run for the same finding while one is in flight is refused rather than duplicated.
4. The run ends with **verified PR**, **unverified PR**, *agent blocked (no PR)* or *agent failed* (hover for the reason; **retry** starts a new run). The PR body links back to the finding; the finding's drawer links to the PR.
5. Review the PR like any other. Nothing is merged for you.

Agent runs need the **Execute Remediations** permission and a Git token that can push branches and open pull requests — the same requirements as [Fix PR](./findings-and-reports.md#fixing).

## What is checked before the PR

The platform's scanners decide, not the agent:

| Moment | Check | If it fails |
| --- | --- | --- |
| **Before the agent** | The finding must reproduce in the fresh clone with the scanner that reported it. | The run stops — no model spend on a finding that is not there. |
| **After the agent** | The same scanner must no longer report the finding, and the repository's test suite (when one is found) must pass. | Finding still present → no PR. |

Every check is recorded as *passed*, *failed* or *skipped*. A PR is labelled **verified** only when the checks actually ran and passed; a skipped check (no test suite, scanner unavailable) gives an **unverified PR** — review those with extra care. Post-fix checks run on a disposable copy of the workspace, so nothing the tests write can reach the pull request.

Each run also records the sandbox image, a bounded log of what the agent ran and saw, and the SHA-256 of the patch that went into the PR. A transient failure (network, model rate limit, Docker daemon) is retried once from a fresh clone; earlier attempts are kept and the chip shows *agent retrying · attempt N*.

### Tell the agent how to run your tests

Test detection looks for a suite at the repository root and one level down, and picks the suite that holds the finding's file. A monorepo or a suite that needs setup should say how in **`.offload/agentic-fix.yml`** on the branch being fixed:

```yaml
version: 1
tests:
  workdir: backend                 # relative to the repository root
  setup: pip install --user -q -r requirements.txt
  command: python -m pytest -x -q -p no:cacheprovider
  select: related                  # all | related
  related: ["tests/**/test_*{stem}*.py"]
  env: {TESTING: "true"}
  timeout_s: 900
```

| Field | Meaning |
| --- | --- |
| `workdir` | Existing directory inside the repository where the tests run. |
| `setup` | Optional command run before the tests. |
| `command` | Required. The test command (string or list). |
| `select` | `all` runs the whole suite; `related` runs only test files matching the stems of the files the agent changed. No match → the step is *skipped* (unverified), never *passed*. |
| `related` | Globs containing `{stem}`, used with `select: related`. |
| `env` | Up to 30 extra environment variables; sandbox plumbing such as `PATH`, `HOME` and proxy variables cannot be overridden. |
| `timeout_s` | Test timeout, at least 30 seconds. |

The file is read from the clone **before** the agent runs, so the agent cannot rewrite its own gate. It is validated strictly (no symlink, at most 64 KB, `workdir` inside the repository); an invalid file blocks the run before any model spend, with the reason.

## Verification after merge

When the PR merges, the platform scans **that merged commit** and looks for the finding it set out to fix. The outcome is recorded on the finding:

| Outcome | Meaning |
| --- | --- |
| **verified fixed** | The scanner that produced the finding ran on the merged commit and the finding is gone. The finding is closed with the verification as evidence. |
| **still present** | The finding is still reported. The finding stays open and says so. |
| **verification inconclusive** | The verification scan could not prove anything: it ran on a different commit, its findings were truncated, or the scanner that produced the original finding did not complete. Nothing is closed. |

The last row is deliberate. A clean scan from a *different* scanner in the same family — say, OpenGrep completing while Bandit failed — proves nothing about a Bandit finding, and the platform will not mark it fixed on that basis. Re-run the scan; a completed run of the right scanner turns *inconclusive* into a verdict.

## Campaigns (API only)

Several findings in **one repository** can be fixed as a **campaign** — `POST /api/agentic-fix/campaigns` — which queues one agent run per finding and tracks them together. A campaign takes at most 10 findings (`AGENTIC_FIX_CAMPAIGN_MAX`); anything over the cap is recorded on the campaign as dropped, never silently ignored. There is no campaign screen. See [Scanning API](../api.md#code).

## What the agent can and cannot do

- It works on a clone inside a sandbox with no platform credentials, no Docker access and no network beyond the egress allowlist.
- It opens pull requests only; it never pushes to a protected branch and never merges.
- Each run is bounded: 15 minutes for the fix (`AGENTIC_FIX_RUN_TIMEOUT_S`), 10 for verification (`AGENTIC_FIX_VERIFY_TIMEOUT_S`), two attempts (`AGENTIC_FIX_MAX_ATTEMPTS`), 30 agent iterations (`AGENTIC_FIX_MAX_ITERATIONS`). Each sandbox has its own lifetime limit, and sandboxes or workspaces left behind by a crashed worker are cleaned up. A run that fails is reported on the finding with the reason.

## Related

- [Findings & Reports](./findings-and-reports.md#fixing) — AI Fix Suggestion and manual Fix PR.
- [Upgrade Impact](./upgrade-impact.md) — which dependency upgrade to hand the agent.
- [Vulnerability Management — Triage](../../vulnerability-risk/vulnerability-management/triage.md) — auto-fix from the triage queue uses the same agent.
- [Scanning API](../api.md#code) — `/api/agentic-fix/*`.
