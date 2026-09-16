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
| *(no badge)* | Not validated: no validator for this detector, or the provider could not give a definitive answer (network, rate limit, wrong region). | Treat as live until you know otherwise. |

Validators exist for AWS access-key pairs and for GitHub, GitLab, Slack, Stripe, SendGrid, npm, OpenAI, Anthropic, Hugging Face, DigitalOcean, Heroku, Cloudflare, Terraform Cloud, Datadog, New Relic, Sentry, Mailgun, Discord, Telegram, Linear, Postman, Square and Mailchimp tokens. Validation only ever contacts a fixed host per provider — it never derives a host from the secret text — and a validation failure is reported as *not validated*, never as *inactive*.

- **Regional providers.** Datadog keys are bound to a site; a key from the EU site answers "forbidden" on the US site exactly like a revoked one. Set `DATADOG_SITE` (for example `datadoghq.eu` or `us3.datadoghq.com`) on the deployment to validate against your site; without it, such keys stay *not validated* rather than being called inactive.
- **Air-gapped deployments.** `SECRET_VALIDATION_ENABLED=false` turns outbound validation off; detection is unaffected.

## Push protection

The same detectors are available as an API for pre-commit hooks and CI steps, so a secret is caught before it reaches the remote:

```bash
curl -s --fail -X POST https://<your-host>/api/secrets/push-protection/scan \
  -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --arg c "$(git diff --cached)" '{content: $c, filename: "staged", fail_on_block: true}')"
```

| Field | Default | Purpose |
| --- | --- | --- |
| `content` | — | The diff or file content to scan (up to 5 MB). |
| `filename` | `input` | A label for the report. |
| `validate` | `false` | Also confirm whether each match is live. Detection alone is enough to block; validation adds the badge. |
| `fail_on_block` | `false` | Return **HTTP 422** instead of 200 when a secret is found, so `curl --fail` gates the step on its own. |

The response lists `findings` (masked) and `blocked`. A pre-commit hook that runs this on the staged diff stops the commit; a CI step stops the build.

## Triage

A secret finding follows the same [lifecycle](./findings-and-reports.md#lifecycle) as any other. Two habits keep the list honest:

- **Rotate first, resolve second.** Removing a live secret from the code closes the finding on the next scan, but the credential is still valid until it is rotated at the provider.
- **False positive with evidence.** Test fixtures and sample keys are the usual false positives; record the reason so the decision survives re-scans and reviews.

## Related

- [Custom Rules](./custom-rules.md) — add detectors for your own token formats and allowlist known fixtures.
- [Pull Request Review](./pull-request-review.md) — new secrets flagged inline on the pull request.
- [Scanning API](../api.md#code) — endpoints.
