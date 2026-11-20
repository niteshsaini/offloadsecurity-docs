---
title: "Secret Detection"
sidebar_label: "Secret Detection"
sidebar_position: 7
description: "How leaked credentials are found in code and git history, confirmed live against the provider, and stopped before they are pushed."
---

# Secret Detection

A leaked credential is the one finding whose severity depends on a fact the scanner cannot see: **does it still work?** Secret detection in the Code Command Center answers that — and looks where a plain tree scan does not, in git history — so the finding you act on first is the one that is actually open.

Secrets are part of **Full Code Security** and of the **Secrets Scan** type ([Running Code Scans](./running-code-scans.md)); nothing here needs enabling.

## What is detected

Gitleaks runs over the source tree with its built-in rules, the platform's supplementary rules, and your own ([Custom Rules](./custom-rules.md)). The supplement covers credential formats the pinned Gitleaks release does not know, including current **Anthropic** and **OpenAI** API keys (project-scoped and legacy formats). Secret values are **masked** everywhere they are shown (first and last three characters only); the finding carries the detector, the file and line.

## Git history

A secret that was committed and later deleted is still in the repository's history, and history is what an attacker clones. Every scan **deepens the clone** (the last **200** commits by default) and runs Gitleaks over that history. A secret found in history but no longer at HEAD is reported as **history only**, with the commit that introduced it — and it is validated like any other secret, because a rotated-but-leaked key still matters if it was never rotated.

Deployment settings: `SECRETS_HISTORY_DEPTH` (commits; `0` disables the deepen), `SECRETS_HISTORY_ENABLED=false` to skip history entirely.

## Live validation

Each detected secret is checked against its provider with a **read-only call** the provider treats as harmless (an identity or token-info endpoint — nothing is created, listed or changed). The result is shown on the finding:

| Badge | Meaning | Do |
| --- | --- | --- |
| **verified live** | The provider accepted the credential during the scan. | Rotate now; then triage the finding. |
| **inactive** | The provider rejected it — already rotated or never valid. | Remove it from the code so the finding closes; no emergency. |
| **not checked:** *reason* | No verdict, with the reason: *inconclusive* (the provider was unreachable, rate-limited or ambiguous), *no check for this type*, *checks off* (validation disabled on the deployment), *over scan limit*, or *no result* (for example a scan from before checks existed). | Treat as live until you have rotated it. |

Validators exist for about 40 providers — among them GitHub, GitLab, Slack, Stripe, SendGrid, npm, OpenAI, Anthropic, Hugging Face, DigitalOcean, Heroku, Cloudflare, Terraform Cloud, Datadog, New Relic, Sentry, Mailgun, Discord, Telegram, Linear, Postman, Square and Mailchimp — plus AWS access-key pairs. Validation only ever contacts a fixed host per provider — it never derives a host from the secret text — only the verdict is stored, never the credential, and a validation failure is reported as *not checked*, never as *inactive*.

| Limit | Default | Setting |
| --- | --- | --- |
| Secrets validated per scan | 200 (the rest show *not checked: over scan limit*) | `SECRET_VALIDATION_MAX` |
| AWS key pairs validated per scan | 5 | `SECRET_VALIDATION_AWS_MAX_PAIRS` |

- **Regional providers.** Datadog keys are bound to a site; a key from the EU site answers "forbidden" on the US site exactly like a revoked one. Set `DATADOG_SITE` (for example `datadoghq.eu` or `us3.datadoghq.com`) on the deployment to validate against your site; without it, such keys stay *not validated* rather than being called inactive.
- **Air-gapped deployments.** `SECRET_VALIDATION_ENABLED=false` turns outbound validation off (secrets then show *not checked: checks off*); detection is unaffected.

### Secret verdicts

Each secret also carries a **verdict** — *Confirmed secret*, *Likely secret*, *Likely false positive* or *Not a secret* — with a confidence and the reason; open the finding to see why. A reviewer can override the verdict, with a reason. While a verdict marks a secret as not actionable (for example *Likely false positive*), automated fixes, tickets and the release gate skip it until someone overrides the verdict.

## Push protection

The same detectors are available for pre-commit / pre-push hooks and CI steps, so a secret is caught before it reaches the remote. There is no screen for this; it works through the hooks and the API.

**The hook kit** ships with the platform (ask your administrator for it). Set `OFFLOAD_API_URL` and `OFFLOAD_API_KEY` (an API key with scan permission) in your shell profile and run the kit's `install.sh` from the repository root: it installs pre-commit and pre-push hooks and keeps hooks you already had. The kit also has GitHub Actions and GitLab CI snippets; set the same two values as CI secrets and make the job a required check.

Push protection **fails closed**: only an explicit *clean* answer lets a change through. An unreachable platform, a timeout, or a change over the size limit blocks it. Hooks that are installed but not configured allow the change with a warning; the CI snippet fails instead. To override deliberately, set `OFFLOAD_PUSH_PROTECTION_BYPASS` to a reason for that one command — the bypass is reported to the platform as a team alert. `git push --no-verify` skips the hook and leaves no record; the CI check still catches it.

Or call the API directly:

```bash
curl -s --fail -X POST https://<your-host>/api/secrets/push-protection/scan \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --arg c "$(git diff --cached)" '{content: $c, filename: "staged", fail_on_block: true}')"
```

| Field | Default | Purpose |
| --- | --- | --- |
| `content` | — | The diff or file content to scan (up to 16 MB by default, `PUSH_PROTECTION_MAX_CONTENT_BYTES`). |
| `filename` | `input` | A label for the report. |
| `validate` | `false` | Also confirm whether each match is live. Detection alone is enough to block; validation adds the badge. |
| `fail_on_block` | `false` | Return **HTTP 422** instead of 200 when the verdict is not *clean*, so `curl --fail` gates the step on its own. |

The response carries a `verdict` — `clean`, `blocked`, or `too_large` (over the size limit and **not scanned**, so also `blocked: true`) — plus the masked `findings`. Content over the limit is never reported as clean; the hooks split large pushes into smaller requests.

## Triage

A secret finding follows the same [lifecycle](./findings-and-reports.md#lifecycle) as any other. Two habits keep the list honest:

- **Rotate first, resolve second.** Removing a live secret from the code closes the finding on the next scan, but the credential is still valid until it is rotated at the provider.
- **False positive with evidence.** Test fixtures and sample keys are the usual false positives; record the reason so the decision survives re-scans and reviews.

## Related

- [Custom Rules](./custom-rules.md) — add detectors for your own token formats and allowlist known fixtures.
- [Pull Request Review](./pull-request-review.md) — new secrets flagged inline on the pull request.
- [Scanning API](../api.md#code) — endpoints.
