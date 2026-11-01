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

## Patch releases (1.4.1)

No snapshot. Patch releases share their minor version's docs: add the release
notes entry and fix pages in place. Snapshot per **minor** version only, so the
selector stays short.

## Fixing a page in an older version

Edit the file under `versioned_docs/version-X.Y.Z/` directly. A fix that applies
to both should be made in both places.
