---
title: "Automation Use Cases"
sidebar_label: "Automation Use Cases"
sidebar_position: 1
---

# Automation Use Cases

This page shows common ways teams drive Offload Security programmatically. All calls authenticate with the `X-API-Key` header (see **[API & Automation](./index.md)**), and responses wrap their payload in a `data` object. The exact routes and parameters for your version are in the interactive API reference; the examples below show the shape of each workflow.

:::note Set these first
```bash
export OFFLOAD_API_URL="https://security.yourcompany.com"
export OFFLOAD_API_KEY="ofsk_...your key..."   # created in Team Management → API Keys
```
:::

## 1. Trigger a scan and gate a release

The most common automation: run a scan from CI/CD and fail the build if it doesn't meet your bar. The scan API is `POST /api/cicd/scans/trigger`, then poll `.../status` and read `.../results`:

```bash
SCAN_ID=$(curl -s -X POST "$OFFLOAD_API_URL/api/cicd/scans/trigger" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"scan_type":"nuclei","target":"https://staging.example.com","fail_on_severity":"high"}' \
  | jq -r '.data.scan_id')

# poll until terminal, then read the gate decision
GATE=$(curl -s "$OFFLOAD_API_URL/api/cicd/scans/$SCAN_ID/results" \
  -H "X-API-Key: $OFFLOAD_API_KEY" | jq -r '.data.gate_passed')

[ "$GATE" = "true" ] || { echo "Security gate failed"; exit 1; }
```

The full pipeline recipe — polling loop, GitHub Action, and all supported scan types — is in **[CLI & CI/CD Integration](../cli-and-cicd.md)**.

## 2. Pull findings into another system

Export the unified findings queue on a schedule — into a data warehouse, a BI dashboard, or a spreadsheet — so security data lives wherever your organization reports from. This is a paginated `GET` against the findings/vulnerabilities endpoints (see the API reference for the exact path and filters):

```python
import os, requests

BASE = os.environ["OFFLOAD_API_URL"]
HEADERS = {"X-API-Key": os.environ["OFFLOAD_API_KEY"]}

def get_all(path, params=None):
    params = dict(params or {}); params.setdefault("page", 1)
    while True:
        r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=60)
        r.raise_for_status()
        body = r.json().get("data", {})
        items = body.get("items", body if isinstance(body, list) else [])
        if not items:
            break
        yield from items
        params["page"] += 1

# Example: every open critical/high finding (see the API reference for the exact route + filters)
for finding in get_all("/api/vulnerabilities/occurrences",
                        {"status": "open", "severity": "critical,high"}):
    print(finding["id"], finding["severity"], finding.get("asset_name"))
```

Point the same helper at reports, assets, or compliance endpoints to export those instead.

## 3. React to events in near real time (webhooks)

For instant automation, don't poll — **subscribe to webhooks** so the platform pushes a signed JSON payload the moment something happens (a new finding, a scan completion, an SLA breach). Configure the subscription in **[Notifications → Webhooks](../integrations/notifications.md)**, then handle deliveries:

```python
# minimal receiver: verify the signature, then act
import hmac, hashlib, os
SECRET = os.environ["OFFLOAD_WEBHOOK_SECRET"].encode()

def handle(request):
    sig = request.headers.get("X-Signature", "")
    expected = hmac.new(SECRET, request.body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return 401
    event = request.json()
    if event["type"] == "sla.breached":
        open_incident(event["data"])      # e.g. page on-call, open a ticket
    return 200
```

This is the backbone of SIEM/SOAR and ticketing automation: webhooks trigger the workflow, and the API fetches any extra detail you need.

## 4. Provision cloud accounts and kick off scans

Onboarding many cloud accounts (or GCP org projects) by hand is slow. Script it: connect the account, then trigger its first scan — all through the Cloud Security endpoints (see the API reference for exact routes):

```bash
# connect a cloud account, then trigger a scan for it
ACCOUNT_ID=$(curl -s -X POST "$OFFLOAD_API_URL/api/cloud-accounts" \
  -H "X-API-Key: $OFFLOAD_API_KEY" -H "Content-Type: application/json" \
  -d '{"provider":"aws","name":"prod","credentials":{ ... }}' | jq -r '.data.account_id')

curl -s -X POST "$OFFLOAD_API_URL/api/cloud-accounts/$ACCOUNT_ID/scan" \
  -H "X-API-Key: $OFFLOAD_API_KEY"
```

See **[Cloud Security](../cloud-security/index.md)** for the onboarding model these endpoints drive.

## 5. Export reports on a schedule

Generate an executive or compliance **[report](../vulnerability-risk/index.md)** and download it (PDF/HTML/Excel) from a nightly or pre-audit job, then post it to a shared drive or email it — no one has to log in and click Export.

## Good practices

- **Least-privilege keys.** Give each automation its own scoped key; revoke it when the job is retired.
- **Be idempotent and poll politely.** Use the `status` endpoint with a sensible interval and a timeout; don't hammer the API in a tight loop.
- **Handle pagination.** List endpoints are paged — always loop until you've read every page (as in example 2).
- **Prefer webhooks for "react to X."** Polling for events wastes calls; a webhook fires exactly when the event happens.
- **Check the response envelope.** Read payloads from `.data`, and treat any non-2xx status as a failure to handle.

For the authoritative list of endpoints and their exact parameters, use the interactive **API reference** described in **[API & Automation](./index.md)**.
