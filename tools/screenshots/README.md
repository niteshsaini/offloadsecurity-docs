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
