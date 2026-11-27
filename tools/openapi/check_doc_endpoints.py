#!/usr/bin/env python3
"""Fail when the docs name an API endpoint the release does not have.

Every `METHOD /api/...` written in the docs (inline code or a one-line code
block) must match a route of the release those docs describe:

  docs/                         -> tools/openapi/routes/<CURRENT_RELEASE>.txt
  versioned_docs/version-X.Y.Z/ -> tools/openapi/routes/X.Y.Z.txt

The route lists are exported from the platform at the release tag (see
tools/openapi/README.md). A literal segment in the docs may stand in for a
path parameter (`/soa/iso_27001` matches `/soa/{framework}`). Paths
abbreviated with `…` or `...` are skipped.

Usage: python3 tools/openapi/check_doc_endpoints.py   (from the repo root)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROUTES = os.path.join(ROOT, "tools", "openapi", "routes")
ENDPOINT = re.compile(
    r"`(GET|POST|PUT|PATCH|DELETE)\s+(/api/[^`\s]*)`|^(GET|POST|PUT|PATCH|DELETE)\s+(/api/\S+)",
    re.M,
)


def segments(path):
    path = path.split("?")[0].split("[")[0].rstrip("/")
    path = re.sub(r"\{[^}]+\}", "{}", path)
    path = re.sub(r"<[^>]+>", "{}", path)
    return path.split("/")


def load_routes(version):
    f = os.path.join(ROUTES, f"{version}.txt")
    if not os.path.exists(f):
        sys.exit(f"missing route list {f} - export it from the platform at that tag")
    out = []
    for line in open(f):
        method, _, path = line.strip().partition(" ")
        if path:
            out.append((method, segments(path)))
    return out


def seg_match(route_seg, doc_seg):
    """A route segment may be a parameter ({}) or contain one ({}.svg)."""
    if route_seg == doc_seg or route_seg == "{}" or doc_seg == "{}":
        return True
    if "{}" in route_seg:
        pattern = "^" + re.escape(route_seg).replace(re.escape("{}"), "[^/]+") + "$"
        return re.match(pattern, doc_seg) is not None
    return False


def matches(method, segs, routes):
    return any(
        m == method and len(t) == len(segs)
        and all(seg_match(a, b) for a, b in zip(t, segs))
        for m, t in routes
    )


def current_release():
    cfg = open(os.path.join(ROOT, "docusaurus.config.ts")).read()
    return re.search(r"const CURRENT_RELEASE = '([^']+)'", cfg).group(1)


def check(doc_root, version):
    routes = load_routes(version)
    bad = []
    for f in sorted(glob.glob(os.path.join(doc_root, "**", "*.md*"), recursive=True)):
        text = open(f).read()
        for m in ENDPOINT.finditer(text):
            method, path = (m.group(1) or m.group(3)), (m.group(2) or m.group(4))
            if "…" in path or "..." in path:
                continue
            if not matches(method, segments(path), routes):
                line = text.count("\n", 0, m.start()) + 1
                bad.append(f"{os.path.relpath(f, ROOT)}:{line}: {method} {path} is not a route in {version}")
    return bad


problems = check(os.path.join(ROOT, "docs"), current_release())
for d in sorted(glob.glob(os.path.join(ROOT, "versioned_docs", "version-*"))):
    problems += check(d, os.path.basename(d)[len("version-"):])
print("\n".join(problems) or "All documented endpoints exist in their release.")
sys.exit(1 if problems else 0)
