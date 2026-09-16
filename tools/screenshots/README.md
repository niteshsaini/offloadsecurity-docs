# Docs screenshot harness

Reproducible, headless screenshots of the product for the docs. One plan file
per docs section; re-run after UI changes and commit the refreshed images.

## What is here

| File | Purpose |
| --- | --- |
| `capture.js` | Playwright runner. Injects a session into `localStorage`, walks a plan, saves 1440×900 @2× PNGs. |
| `plan-cloud-security.json` | Capture plan for the Cloud Security section (tabs, wizard steps, dialogs). |
| `seed_cloud_security.py` | Deterministic fixture seeder: 4 accounts, ~30 scan runs, ~400 findings, compliance scores, remediation tasks, assets, cloud events, identity roster — shaped to the current read paths. |

## Run

Prerequisites: a local `offload-cspm` checkout with the frontend dev server running
(`npm start` in `frontend/`, proxying `/api` to a backend on current `main`), local
MongoDB/Redis (the compose stack), and Playwright from the frontend's `node_modules`.

```bash
# 1. seed fixtures for the default team (wipe + reinsert; idempotent)
MONGO_URL="mongodb://<user>:<pass>@localhost:27017/?authSource=admin" \
  ../offload-cspm/backend/.venv/bin/python tools/screenshots/seed_cloud_security.py

# 2. mint a session (admin login) and capture
SESSION_ID=<session id from POST /api/auth/login> \
BASE_URL=http://localhost:3001 \
PLAYWRIGHT_PATH=../offload-cspm/frontend/node_modules/playwright \
  node tools/screenshots/capture.js tools/screenshots/plan-cloud-security.json /tmp/shots

# 3. convert to WebP (1.5× of 1440×900, q88) into static/img/screenshots/<section>/
python3 - <<'EOF'
from PIL import Image; import glob, os
for f in glob.glob('/tmp/shots/*.png'):
    im = Image.open(f).convert('RGB'); im.thumbnail((2160, 1350))
    im.save(f"static/img/screenshots/cloud-security/{os.path.basename(f)[:-4]}.webp", 'WEBP', quality=88, method=6)
EOF
```

## Plan format

```json
{ "name": "findings-suppress-dialog",
  "url": "/dashboard?section=cloud-security",
  "clicks": ["Scanning", {"text": "Suppress", "exact": false}],
  "actions": [{"fill": {"placeholder": "owner@company.com", "value": "…"}}, {"check": "SOC2"}, {"scrollTop": true}],
  "delay": 2500 }
```

Clicks resolve visible `tab` → `button` → `link` roles by accessible name first, then visible text
(last match wins, which skips the sidebar). Use `actions` when fills and clicks must interleave.

## Rules

- Seed data must match **current** writer/read-path shapes — check the service that writes the
  collection before adding a fixture field.
- Never capture against production or customer data.
- Keep filenames stable; docs pages reference them by name.

## Section 2 — App & Infrastructure Scanning (2026-09-12)

`plan-security-scanning.json` captures the Scanning hub, Kubernetes, Container Security, Code Command Center and
Infra Command Center tabs. Unlike Cloud Security, this section used **real scans** rather than fixtures:

- Current backend source run *inside* the released image (all scanner binaries + `/data` volumes), with the
  Docker socket group added and a Celery worker for the `container_scans` queue — see the memory note
  `docs-section-rebuild-program` in the maintainer's Claude memory for the exact `docker run`.
- Native scans (ZAP quick, Nmap service detection, testssl, security headers), WAF test and load test against
  `offloadsecurity.com`; container full-analysis of `nginx:1.25.3`, `python:3.9-slim`, `node:18-alpine`, `alpine:3.17`;
  a code upload-scan of a deliberately vulnerable sample (`payments-api.zip`: SQLi, secrets, old deps, bad Terraform);
  SBOMs, an image policy from the *Production – Strict* template, and K8s compliance reports per cluster.
- Existing K8s/registry fixtures had their timestamps shifted to "recent" and registry sync errors cleared.

Steps in the plan use `actions` (fill/select/click) for the Dockerfile scan and the compliance form.

## Section 3 — Vulnerabilities & Risk (2026-09-13)

`plan-vulnerability-risk.json` captures Vulnerability Management (Triage queue, work item, How to fix, Accept Risk,
Raw findings by source, occurrence detail, dashboard), SLA Management (policies, breach dashboard, create-policy form),
Alerts (list + detail) and Risk Management (dashboard, register by category / all risks, new-risk form, import from
findings, treatment plans, controls, heat map, bulk import, appetite, KRIs, scenarios). Same environment as section 2.

Data prep that was needed:
- The Triage queue is only populated after `POST /api/vulnerabilities/sync?force_resync=true` followed by
  `POST /api/triage/score` (the lake and the scores are otherwise built on the 2-hourly / daily schedule).
- 671 noise alerts (scan/tool failures from the scanner work in section 2) were resolved so the list shows
  security alerts; KRIs, an appetite statement, scenarios, controls and treatment plans were created through the UI.
- `capture.js` gained two things this section relied on: `scrollY` now scrolls the tallest scrollable pane as well
  as the window (tab bodies scroll internally), and dropdown tabs are reached with
  `{"selector": "button:has-text('More')"}` followed by a text click.
- `risk-import` captures the auto-import preview, which takes several seconds — its step uses `delay: 9000`.
