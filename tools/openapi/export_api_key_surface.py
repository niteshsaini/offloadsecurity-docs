#!/usr/bin/env python3
"""Export the public API reference: the OpenAPI operations an API key can call.

Run from the platform repo's backend/ directory at a release tag, with the
backend's Python environment:

    cd <offload-cspm checkout at vX.Y.Z>/backend
    python <docs-repo>/tools/openapi/export_api_key_surface.py <out.json> <version> [--routes <routes.txt>]

--routes also writes every route of the release (`METHOD /path`, no schemas)
for tools/openapi/check_doc_endpoints.py.

What counts as public: the routes whose dependency tree reaches an API-key
authenticator (the same walk as the platform's
tests/unit/test_api_key_route_scope_coverage.py) AND that a key scope grants
(core.auth_standard.required_api_key_scope). Session-only routes are the web
UI's internal API and are deliberately left out. Each operation carries
`x-offload-api-key-scope`, the scope a key needs for it.
"""
import json
import os
import re
import secrets
import sys

os.environ.setdefault("TESTING", "true")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SKIP_TOOL_VERIFICATION", "1")
os.environ.setdefault("MONGO_URL", "mongodb://127.0.0.1:1/x")
from cryptography.fernet import Fernet  # noqa: E402

for k in ("CLOUD_ENCRYPTION_KEY", "INTEGRATION_ENCRYPTION_KEY", "CREDENTIAL_ENCRYPTION_KEY"):
    os.environ.setdefault(k, Fernet.generate_key().decode())
for k in ("SECRET_KEY", "WEBHOOK_SECRET"):
    os.environ.setdefault(k, secrets.token_hex(32))
sys.path.insert(0, os.getcwd())

import server  # noqa: E402
from fastapi.dependencies.utils import get_dependant  # noqa: E402
from core.auth_standard import require_auth_or_api_key, required_api_key_scope  # noqa: E402

try:
    from routes.cicd_scan_routes import authenticate_api_key
    targets = {require_auth_or_api_key, authenticate_api_key}
except ImportError:  # older releases
    targets = {require_auth_or_api_key}
try:
    from tests._route_introspection import iter_routes
except ImportError:
    def iter_routes(app):
        return list(app.routes)


INTERNAL = re.compile(
    r"\b(used to|it was|before this|previously|legacy|regression|review|TODO|FIXME|"
    r"hack|workaround|bug|W\d+-\d+|PR|#\d{3,})\b", re.I)


def public_summary(doc: str) -> str:
    """The public part of a route docstring: up to three sentences of its
    first paragraph, stopping at the first one that reads like a note for
    maintainers (history, review ids, workarounds)."""
    para = " ".join(doc.strip().split("\n\n")[0].split())
    out = []
    for sentence in re.split(r"(?<=[.!?])\s+", para):
        if not sentence or INTERNAL.search(sentence) or len(out) == 3:
            break
        out.append(sentence)
    return " ".join(out)


def reaches(dep):
    return any(s.call in targets or reaches(s) for s in dep.dependencies)


out_path, version = sys.argv[1], sys.argv[2]
routes_path = sys.argv[sys.argv.index("--routes") + 1] if "--routes" in sys.argv else None
keep = {}
for r in iter_routes(server.app):
    endpoint = getattr(r, "endpoint", None)
    if endpoint is None:
        continue
    dep = getattr(r, "dependant", None) or get_dependant(path=r.path, call=endpoint)
    hit = reaches(dep) or any(
        x.dependency in targets or reaches(get_dependant(path=r.path, call=x.dependency))
        for x in (getattr(r, "dependencies", None) or [])
    )
    if not hit:
        continue
    for m in getattr(r, "methods", None) or ():
        if m in ("HEAD", "OPTIONS"):
            continue
        scope = required_api_key_scope(r.path, m)
        if scope:
            keep[(m.lower(), r.path)] = scope

full = server.app.openapi()
if routes_path:
    with open(routes_path, "w") as f:
        f.write("\n".join(sorted(f"{m.upper()} {p}" for p, o in full.get("paths", {}).items() for m in o)) + "\n")
paths = {}
for path, ops in full.get("paths", {}).items():
    for method, op in ops.items():
        scope = keep.get((method, path))
        if not scope:
            continue
        op = dict(op)
        op["x-offload-api-key-scope"] = scope
        op["security"] = [{"ApiKeyAuth": []}]
        # Only the first paragraph of the route's docstring is published: the
        # rest is often implementation notes for maintainers, not API docs.
        first = public_summary(op.get("description") or "")
        op["description"] = (first + "\n\n" if first else "") + \
            f"API-key scope required: `{scope}`."
        paths.setdefault(path, {})[method] = op

# Keep only the component schemas the kept operations reference (transitively).
schemas = full.get("components", {}).get("schemas", {})
used, todo = set(), [json.dumps(paths)]
while todo:
    for name in re.findall(r"#/components/schemas/([^\"]+)", todo.pop()):
        if name not in used and name in schemas:
            used.add(name)
            todo.append(json.dumps(schemas[name]))

spec = {
    "openapi": full.get("openapi", "3.1.0"),
    "info": {
        "title": "Offload Security API",
        "version": version,
        "description": (
            "The operations an API key can call in Offload Security " + version + ". "
            "Authenticate with the `X-API-Key` header; each operation lists the key "
            "scope it needs (`x-offload-api-key-scope`). Routes not listed here are "
            "the web interface's internal API: they accept only a signed-in session "
            "and may change without notice. Paths are relative to your own "
            "deployment, e.g. https://offload.example.com."
        ),
    },
    "servers": [{"url": "https://{host}", "variables": {"host": {"default": "offload.example.com"}}}],
    "paths": dict(sorted(paths.items())),
    "components": {
        "schemas": {k: schemas[k] for k in sorted(used)},
        "securitySchemes": {"ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"}},
    },
}
with open(out_path, "w") as f:
    json.dump(spec, f, indent=1, sort_keys=False)
n_ops = sum(len(v) for v in paths.values())
print(f"{version}: {len(paths)} paths, {n_ops} operations, {len(used)} schemas "
      f"(of {len(full.get('paths', {}))} paths in the full app)")
