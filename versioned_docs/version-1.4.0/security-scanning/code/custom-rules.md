---
title: "Custom Rules"
sidebar_label: "Custom Rules"
sidebar_position: 8
description: "Add your own SAST, secret-detection and infrastructure-as-code rules to every code scan from a directory on the host — picked up on the next scan, no restart."
---

# Custom Rules

The bundled rule sets know the public mistakes. Your codebase has its own: an internal HTTP client that must not be bypassed, a token format only your systems issue, a Terraform module that must always set a tag. **Custom rules** add those checks to every scan the deployment runs, for all three rule-based engines.

| Engine | Directory | Format |
| --- | --- | --- |
| **SAST** (OpenGrep) | `sast/` | Semgrep rule files (`*.yml`, `*.yaml`) — rules from the Semgrep registry or an existing `.semgrep/` directory work unchanged |
| **Secrets** (Gitleaks) | `secrets/gitleaks.toml` | One Gitleaks configuration: extra rules and allowlists |
| **IaC** (Checkov) | `iac/` | Checkov YAML custom policies (`*.yml`, `*.yaml`) |

## Where the rules live

On the host that runs the platform, in the directory mounted read-only into the scanning containers — by default `./data/custom-rules` next to `docker-compose.yml` (override with `CODE_SCAN_CUSTOM_RULES_DIR` in `.env`):

```
custom-rules/
├── sast/       acme-http-client.yml
├── secrets/    gitleaks.toml
└── iac/        acme-required-tags.yaml
```

Rules apply to **every repository** scanned by the deployment. Repository-specific rules belong in the repository itself (a `.semgrep/` directory or `.gitleaks.toml`), which the engines honour as they always have.

## Hot reload

Every scan fingerprints the directory. If anything changed since the last scan, the rules are **re-validated and staged again**; otherwise the previous validated set is reused. Adding, editing or deleting a file is live on the **next scan** — no container restart, no image rebuild.

Validation is per file and a bad file is **quarantined, not fatal**: the valid ones still run, and the scan is never failed by a rule. This matters because one malformed YAML would otherwise make OpenGrep abort and silently zero the SAST results.

What the last scan used — and which files were rejected, with the reason — is one call away:

```
GET /api/code/scan-rules/custom                 # what the last scan used
GET /api/code/scan-rules/custom?refresh=true    # re-validate right now
```

```json
{
  "root": "/data/custom-rules", "mounted": true, "fingerprint": "364ae2a7c97e91d6",
  "sast":    {"files": 1, "rules": 2, "rule_ids": ["acme-no-raw-requests"], "active": true,
              "errors": [{"file": "engine-bad.yml", "error": "invalid rule engine-bad, engine-bad.yml:6:13: …"}]},
  "secrets": {"files": 1, "rules": 2, "errors": [], "active": true},
  "iac":     {"files": 1, "rules": 1, "errors": [], "active": true}
}
```

The same summary is stored with each scan report, so a report can state exactly which custom rules were in force.

## Writing rules

### SAST

Standard Semgrep syntax: a top-level `rules:` list; each rule needs `id`, `languages`, `message`, `severity` (`ERROR` / `WARNING` / `INFO`, or `CRITICAL` / `HIGH` / `MEDIUM` / `LOW`) and a `pattern`, `patterns`, `pattern-either` or `pattern-regex` — or, for `mode: taint`, `pattern-sources` and `pattern-sinks`.

```yaml
rules:
  - id: acme-no-raw-requests
    languages: [python]
    severity: WARNING
    message: Use acme.http.client instead of requests — it carries auth, retries and audit logging.
    pattern: requests.$METHOD(...)
    metadata: { category: security, owner: platform-security }
```

Findings from custom rules appear under **SAST** with the rule `id` as the identifier, and can be triaged like any other.

### Secrets

One file, named exactly `gitleaks.toml`, in Gitleaks configuration format. The platform **merges** it with the built-in rules and with the repository's own `.gitleaks.toml` when one exists, so list only what you add:

```toml
[extend]
useDefault = true                 # keep the built-in rules (assumed if omitted)
# disabledRules = ["generic-api-key"]

[[rules]]
id = "acme-service-token"
description = "Acme internal service token"
regex = '''\bacme_[a-z]{3}_[A-Za-z0-9]{32}\b'''
keywords = ["acme_"]

[[allowlists]]
description = "Test fixtures"
paths = ['''tests/fixtures/.*''']
```

Two things Gitleaks is strict about: write `[extend]` as a table header (not `extend.useDefault = true`), and remember that a regex with capture groups reports the **first group** as the secret unless `secretGroup` says otherwise. A repository whose own `.gitleaks.toml` already extends another file keeps that configuration as is — Gitleaks caps the extend chain at two levels, and the repository's committed configuration wins.

### IaC

Checkov YAML policies: `metadata` (`id`, `name`, `category`, `severity`) plus a `definition` over the resource attributes.

```yaml
metadata:
  id: "CKV2_ACME_1"
  name: "S3 buckets carry the cost-centre tag"
  category: "GENERAL_SECURITY"
  severity: "MEDIUM"
definition:
  cond_type: "attribute"
  resource_types: ["aws_s3_bucket"]
  attribute: "tags.cost_centre"
  operator: "exists"
```

## Related

- [Secret Detection](./secret-detection.md) — how the built-in and custom detectors are validated and triaged.
- [Running Code Scans](./running-code-scans.md) — the scan types the rules run in.
- [Scanning API](../api.md#code) — `GET /api/code/scan-rules/custom`.
