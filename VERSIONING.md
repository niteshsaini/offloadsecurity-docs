# Versioned documentation

The docs follow platform releases, the way Wazuh's docs do: a version selector
in the navbar, the current release at the site root, and earlier releases kept
under `/<version>/` with an "unmaintained version" banner.

## How it is wired

- `docs/` is **always the current release**. It is served at the root, so
  links into the docs (from the app, the website, search engines) never move.
- `CURRENT_RELEASE` in `docusaurus.config.ts` is the version the root
  describes. It drives the selector label ("1.4.0 (current)").
- Older releases live in `versioned_docs/version-X.Y.Z/` +
  `versioned_sidebars/` and are listed in `versions.json` — all three are
  created by the `docs:version` command, never by hand.
- Release notes are pages in `docs/release-notes/` (one per release),
  registered newest-first in `sidebars.ts`, plus a row in
  `docs/release-notes/index.md`.

## Shipping a new platform release (example: 1.4.0 → 1.5.0)

Do this **before** editing any page for 1.5.0 behaviour:

```bash
npm run docusaurus docs:version 1.4.0   # snapshot today's docs as 1.4.0
```

Then, in the same PR:

1. Set `CURRENT_RELEASE = '1.5.0'` in `docusaurus.config.ts`.
2. Add `docs/release-notes/v1-5-0.md` (copy the 1.4.0 page's structure:
   Highlights, Upgrade notes) and list it first in the Release Notes category in
   `sidebars.ts` and in the table in `docs/release-notes/index.md`.
3. Update pages in `docs/` for 1.5.0.
4. `npm run build` and check the selector shows 1.5.0 (current) + 1.4.0.

1.4.0 is then served at `/1.4.0/...` with a banner pointing to the latest.

## API reference (every release)

Export the published OpenAPI file and the route list for the new tag and add
the version to the reference page's menu: see `tools/openapi/README.md`.
`tools/openapi/check_doc_endpoints.py` (run on every pull request) then checks
that every endpoint the docs name exists in that release.

## Pre-releases (1.4.1-beta.N)

Customers run betas, so the root follows the **latest published pre-release**:

1. **Before the first docs change for a pre-release line**, snapshot the last
   final release (`docs:version 1.4.0`, or copy `docs/` to
   `versioned_docs/version-1.4.0/` plus `versions.json` and the sidebar JSON).
   Remove `release-notes/` from the snapshot and point its sidebar entry at
   `/release-notes`: release notes are version-independent and live only in
   the current docs.
2. In `docusaurus.config.ts` set `CURRENT_RELEASE` to the beta tag,
   `PRERELEASE = true` and `STABLE_RELEASE` to the last final release. The
   stable snapshot is then labelled "(stable)" without the "unmaintained"
   banner, and an announcement bar says which docs the reader is on.
3. Each published beta gets its own release-notes page
   (`docs/release-notes/v1-4-1-beta-N.md`) and a row in the index table. Bump
   `CURRENT_RELEASE` to the newest beta.
4. When the final release ships, set `CURRENT_RELEASE = '1.4.1'` and
   `PRERELEASE = false`. The previous final release's snapshot then gets the
   normal "unmaintained" banner.

## Patch releases (1.4.1)

No snapshot. Patch releases share their minor version's docs: add the release
notes entry and fix pages in place. Snapshot per **minor** version only, so the
selector stays short.

## Fixing a page in an older version

Edit the file under `versioned_docs/version-X.Y.Z/` directly. A fix that applies
to both should be made in both places.
