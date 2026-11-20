# API reference tooling

Two things are generated from the platform at each release tag and committed here:

| File | What | Used by |
| --- | --- | --- |
| `static/api/openapi/<version>.json` | The **published API reference**: every operation an API key can call, with the scope it needs (`x-offload-api-key-scope`). Session-only routes (the web UI's internal API) are left out. | `/api/reference/` (Redoc), and readers' tools |
| `tools/openapi/routes/<version>.txt` | Every route of the release, `METHOD /path` only (no schemas). | `check_doc_endpoints.py` |

## For each release

From a checkout of `offload-cspm` at the tag, with the backend's Python environment:

```bash
cd <offload-cspm at vX.Y.Z>/backend
python <docs-repo>/tools/openapi/export_api_key_surface.py \
  <docs-repo>/static/api/openapi/X.Y.Z.json X.Y.Z \
  --routes <docs-repo>/tools/openapi/routes/X.Y.Z.txt
```

Then add the version to `VERSIONS` in `static/api/reference/index.html` (newest first) and run the check:

```bash
python3 tools/openapi/check_doc_endpoints.py
```

It fails when a `METHOD /api/...` written in `docs/` (checked against the `CURRENT_RELEASE` route list) or in `versioned_docs/version-X/` (checked against `routes/X.txt`) is not a route of that release. It runs on every pull request (`.github/workflows/docs-checks.yml`).

Use a worktree for the platform checkout (`git worktree add --detach <dir> vX.Y.Z`) so you never switch someone's working branch.
