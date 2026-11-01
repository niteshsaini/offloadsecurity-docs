---
title: "Import SARIF results"
sidebar_label: "SARIF Imports"
sidebar_position: 3.5
new_in: 1.4.0
description: "Import a SARIF 2.1.0 log from CodeQL, Semgrep, Checkmarx, Snyk Code or any other SARIF-producing scanner, in the page or from CI, so its results become findings beside the platform's own."
---

# Import SARIF results

If a team already runs a scanner the platform does not — CodeQL in GitHub Actions, a commercial SAST tool, an in-house linter — you can bring its results in as a SARIF 2.1.0 log. Each tool's results become findings next to the platform's own, de-duplicated on re-import, with the log's suppressions kept as decisions. One upload takes a minute; a CI step makes it automatic.

**Where:** Code Command Center → **SARIF Imports**.

## Before you begin

- The **Run Scans** permission. From CI, an API key with the `scans:trigger` scope whose owner has Run Scans.
- A SARIF **2.1.0** JSON log. Other versions and non-JSON bodies are refused.
- The repository URL your code scans already target (for example `https://github.com/acme/shop`). Findings are kept per repository URL **as entered**, so use the same spelling every time.

## Steps

1. **Choose the file.** Under *Import a SARIF log*, select the `.sarif` file.
2. **Name the repository.** Enter the repository URL. If you leave it empty, the log's `versionControlProvenance` is used; without either, the upload is refused.
3. **Name the branch (optional).** Leave **Branch** empty for the repository's default branch, or enter a branch and tick **This is the repository's default branch** when it is. Add the **Commit** if you have it.
4. **Say whether it is a complete run.** Tick **This log is a complete run of the tool over this repository and branch** only when the tool scanned the whole repository with its normal rules. Then findings that tool reported there before and no longer reports are resolved. Leave it off for a partial run (a subset of files or rules): nothing is resolved.
5. **Select Import SARIF.** The result shows, per tool in the log, how many findings were new, new and suppressed by the log, updated, reopened and resolved, plus results that were not imported (pass / not-applicable results, results marked absent from the baseline).

### From CI

The tab shows a ready `curl` command and a GitHub Actions step. Both post the log to the same endpoint:

```
POST /api/cicd/sarif/upload
```

```bash
curl --fail-with-body -sS -X POST \
  -H "X-API-Key: $OFFLOAD_API_KEY" \
  -H "Content-Type: application/sarif+json" \
  --data-binary @results.sarif \
  "https://<your-instance>/api/cicd/sarif/upload?repository=https://github.com/acme/shop&branch=main&default_branch=main&commit_sha=$GIT_SHA&full_run=true"
```

Set `full_run=true` only when the step ran the tool over the whole repository. On a pull-request branch the findings stay on that branch and never resolve the default branch's.

## Check that it worked

*Imported findings* on the same tab lists what arrived: severity, rule, CWE, file and lines, the tool and its version, the repository (and branch) and status. Filter by tool, repository, severity and status (**Open**, **Suppressed**, **Resolved**, **Other decisions**, **Any status**).

Imported findings are triaged — assigned, accepted, marked false positive — in Vulnerability Management's [Triage queue](../../vulnerability-risk/vulnerability-management/triage.md) with every other finding. The Code Command Center **Findings** tab shows the platform's own scans only.

## How results are mapped

| Topic | Behavior |
| --- | --- |
| **Severity** | The rule's `security-severity` when present (9.0+ critical, 7.0+ high, 4.0+ medium, above 0 low); else the tool's own severity word; else the SARIF level (error high, warning medium, note low, none info). |
| **CWE** | Read from rule tags (Semgrep `CWE-95: …`, CodeQL `external/cwe/cwe-089`), `properties.cwe`, rule relationships and result taxa. |
| **Re-import** | The same tool's log for the same repository and branch updates the same findings (the tool's fingerprints, or rule and location when it gives none). |
| **Cross-tool** | Two tools reporting the same issue become one finding only for dependency vulnerabilities (CVE + package) and IaC checks. SAST and secret findings from different tools stay separate. |
| **Resolution** | A complete run resolves a finding only when no other tool or platform scan still reports it. |
| **Secrets** | A secret's matched text is never stored. Results from secret scanners or with a credential CWE (for example CWE-798) keep no snippet or message; they are kept by a hash of the match. |

### Suppressions

Results the log suppresses (`suppressions[]` with status *accepted*, for example `# nosemgrep` or a CodeQL suppression) are imported as **Suppressed**, with the log's justification as the reason — but only while every tool that currently reports the finding suppresses it. A suppression that is *under review* or *rejected* leaves the finding open. If a later log no longer suppresses the result, the finding reopens.

A decision a person made is never changed by an import: false positive, accepted risk, a manual suppression, a reopen, or *in progress*.

### Branches

No branch, or the default branch, files results under the repository. Any other branch is kept as its own scope (`repository@branch`) and never resolves the default branch's findings. Findings that only SARIF imports report on a non-default branch get no SLA clock and are left out of the Triage queue and the SLA / overdue counts; this tab still lists them. A branch with no import for 30 days is treated as gone, and findings only imports reported there are resolved with the reason *branch scope stale*.

If you name a branch without saying whether it is the default, the platform uses the default branch an earlier import or a Git-connected code scan recorded. When neither exists, the results go under the repository as a whole, and a complete run is refused (400) until you supply `default_branch`.

## Limits

Over a limit the upload is **refused whole**, with the limit named; a log is never cut short.

| Limit | Default | Setting |
| --- | --- | --- |
| Body size | 10 MB (413) | `SARIF_UPLOAD_MAX_BYTES` |
| Results per upload | 50,000 (413) | `SARIF_INGEST_MAX_RESULTS` |
| Uploads parsed at once per API process | 2 (429) | `SARIF_UPLOAD_MAX_CONCURRENCY` |
| Time for the body to arrive | 300 s (408) | `SARIF_UPLOAD_BODY_TIMEOUT_SECONDS` |
| Uploads per hour per API key or user | 60 (429, when Redis is configured) | — |
| JSON nesting | 64 levels (400) | — |

## If something goes wrong

- **"… over the …-byte limit (SARIF_UPLOAD_MAX_BYTES)" or "… over the …-result ingest limit"** — nothing was imported. Split the log (one tool or one run per upload), or ask an administrator to raise the limit.
- **"unsupported SARIF version" or "body is not JSON"** — export the tool's results as SARIF 2.1.0 JSON.
- **"JSON nested deeper than 64 levels"** — the file is not a normal SARIF log; re-export it from the tool.
- **"repository is required"** — enter the repository, or include `versionControlProvenance` in the log.
- **"Nothing was resolved: …"** in the result — the upload was not marked a complete run, the tool reported a failed run, or the log names no tool. Reported findings were still imported.

## Next steps

- [Findings & Reports](./findings-and-reports.md) — the platform's own findings and lifecycle.
- [CI/CD & Automation](./ci-cd-and-automation.md) — put the import step next to your other pipeline jobs.
- [Scanning API](../api.md#code) — `GET /api/cicd/sarif/sources` lists the imported tools, repository scopes and the live limits.
