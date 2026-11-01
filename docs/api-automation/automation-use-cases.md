---
title: "Automation Use Cases"
description: "Common automation workflows with the Offload Security API: gate a release on a scan, pull findings into other systems, react to webhooks, provision cloud accounts and schedule report exports."
sidebar_label: "Automation Use Cases"
sidebar_position: 1
---

# Automation Use Cases

This page shows common ways teams drive Offload Security programmatically. The
calls authenticate with the `X-API-Key` header (see **[API & Automation](./index.md)**).
Each example names the key scopes it needs; the [API Reference](../api-reference/index.md)
has the full parameters and response shapes.

:::note[Set these first]
```bash
export OFFLOAD_API_URL="https://security.yourcompany.com"
export OFFLOAD_API_KEY="osk_...your key..."   # user menu → API Keys
```
:::

## 1. Trigger a scan and gate a release

The most common automation: run a scan from CI/CD and fail the build if it
doesn't meet your bar. Trigger with `POST /api/cicd/scans/trigger`, poll
`.../status`, then read the gate decision from `.../results`. Scopes:
`scans:trigger`, `scans:read` (the `ci_cd_basic` preset).

```bash
SCAN_ID=$(curl -s -X POST "$OFFLOAD_API_URL/api/cicd/scans/trigger" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"scan_type":"nuclei","target":"https://staging.example.com","fail_on_severity":"high"}' \
  | jq -r '.data.scan_id')

# poll until terminal
while : ; do
  STATUS=$(curl -s "$OFFLOAD_API_URL/api/cicd/scans/$SCAN_ID/status" \
    -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.data.status')
  case "$STATUS" in completed|failed) break ;; esac
  sleep 10
done

# read the gate decision (null while the scan is still running)
GATE=$(curl -s "$OFFLOAD_API_URL/api/cicd/scans/$SCAN_ID/results" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.data.gate_passed')

[ "$GATE" = "true" ] || { echo "Security gate failed"; exit 1; }
```

The full pipeline recipe (GitHub Action, every supported scan type, SARIF
output) is in **[CLI & CI/CD Integration](../cli-and-cicd.md)**.

## 2. Pull findings into another system

Export the normalized vulnerability occurrences on a schedule into a data
warehouse, a BI dashboard or a spreadsheet. The list is offset-paged
(`skip` + `limit`, at most 100 per page) and wrapped in `data`. Scope:
`vulnerabilities:read`.

```python
import os, time, requests

BASE = os.environ["OFFLOAD_API_URL"]
HEADERS = {"X-API-Key": os.environ["OFFLOAD_API_KEY"]}

def get_occurrences(params=None, limit=100):
    params = dict(params or {}, skip=0, limit=limit)
    while True:
        r = requests.get(f"{BASE}/api/vulnerabilities/occurrences",
                         headers=HEADERS, params=params, timeout=60)
        r.raise_for_status()
        page = r.json()["data"]["occurrences"]
        yield from page
        if len(page) < limit:
            break
        params["skip"] += limit
        time.sleep(1)  # this path allows 60 requests per minute per client IP

# Every open occurrence with a base CVSS of 7.0 or higher
for occ in get_occurrences({"status": "open", "severity_min": 7.0}):
    print(occ["occurrence_id"], occ["vulnerability_id"],
          occ["risk_assessment"].get("priority_rank"), occ.get("asset_id"))
```

Use `priority=P1` (triage-engine priority) instead of `severity_min` to export
by priority. Other key-accessible lists use their own paging; for example
`GET /api/cspm/findings` for cloud misconfigurations (`cloud:read`).

## 3. React to events in near real time (webhooks)

Don't poll for events: **subscribe to webhooks** so the platform pushes a signed
JSON payload when something happens, such as `scan.completed`,
`finding.created`, `alert.created`, `alert.resolved` or `sla.breached`.
Configure the subscription in **Integrations → [Webhooks](../integrations/webhooks.md)**
(managing subscriptions needs a signed-in session; API keys cannot), then
handle deliveries.

Each delivery body is `{ "event_id", "event_type", "timestamp", "data" }`. It
carries `X-Offload-Timestamp` and `X-Offload-Signature-V1`, where the signature
is `v1=` + hex HMAC-SHA256 of `"<timestamp>." + <raw body>` with the
subscription's signing secret (shown once when you create the subscription).
Reject stale timestamps to block replays:

```python
# minimal receiver: verify the signature and timestamp, then act
import hashlib, hmac, json, os, time
SECRET = os.environ["OFFLOAD_WEBHOOK_SECRET"].encode()

def handle(request):
    ts = request.headers.get("X-Offload-Timestamp", "")
    sig = request.headers.get("X-Offload-Signature-V1", "")
    if not ts.isdigit() or abs(time.time() - int(ts)) > 300:
        return 401
    expected = "v1=" + hmac.new(SECRET, ts.encode() + b"." + request.body,
                                hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig.encode(), expected.encode()):
        return 401
    event = json.loads(request.body)
    if event["event_type"] == "sla.breached":
        open_incident(event["data"])      # e.g. page on-call, open a ticket
    return 200
```

This is the backbone of SIEM, SOAR and ticketing automation: webhooks trigger
the workflow, and the API fetches any extra detail you need.

## 4. Provision cloud accounts and kick off scans

Onboarding many cloud accounts by hand is slow. Script it: connect the
account, which starts its first scan when the credentials validate, and
re-scan it later on demand. Scopes: `cloud:manage` (not in any preset except
`full_access`; add it explicitly). Owner permission: *Manage Cloud Accounts*.

```bash
# connect a cloud account; the response's "id" is the platform's account ID
ACCOUNT=$(curl -s -X POST "$OFFLOAD_API_URL/api/cloud-accounts/" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"provider":"aws","account_id":"123456789012","account_name":"prod",
       "credentials":{"access_key_id":"AKIA…","secret_access_key":"…"}}')
echo "$ACCOUNT" | jq '{id, status, validation_error, scan_run_id}'
ID=$(echo "$ACCOUNT" | jq -r '.id')

# later: trigger another scan for it
curl -s -X POST "$OFFLOAD_API_URL/api/cloud-accounts/$ID/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

See **[Cloud Accounts API](../api-reference/cloud-accounts.md)** and
**[Cloud Security](../cloud-security/index.md)** for the onboarding model.

## 5. Export reports on a schedule

Download a report from a nightly or pre-audit job and post it to a shared
drive, so no one has to sign in and click Export. For example, the Cloud
Security Posture report for one scan run, reproduced from that run's frozen
snapshot (scope `reports:read`):

```bash
curl -s -o posture.pdf -D headers.txt \
  "$OFFLOAD_API_URL/api/export/cloud-posture?scan_run_id=$RUN_ID" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
grep -i '^x-content-sha256' headers.txt   # the fingerprint the platform recorded
```

Every issued report is fingerprinted. Anyone can later confirm a copy is
unmodified with `GET /api/native-scans/exports/verify?sha256=…` (scope
`scans:read`); see [Verify an exported report](../api-reference/scans-and-results.md#verify-an-exported-report).

## Good practices

- **Least-privilege keys.** Give each automation its own scoped key; revoke it when the job is retired.
- **Be idempotent and poll politely.** Poll status with a sensible interval and an overall timeout, and stop on every terminal status (`failed` and `partial` as well as `completed`).
- **Handle pagination.** List endpoints are paged; loop until you have read every page (as in example 2).
- **Respect rate limits.** Limits are per client IP (60 requests per minute on the vulnerability and findings paths, 100 elsewhere). Back off on `429` and honor `Retry-After`.
- **Prefer webhooks for "react to X".** A webhook fires when the event happens; polling wastes calls.
- **Check the response shape.** Read enveloped payloads from `.data`, and treat any non-2xx status as a failure to handle.

For the endpoints and their parameters, see the **[API Reference](../api-reference/index.md)**.
