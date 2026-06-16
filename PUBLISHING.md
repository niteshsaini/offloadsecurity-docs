# Publishing the Documentation Wiki

This repo is a standalone [Docusaurus](https://docusaurus.io) site that serves the
public, customer-facing documentation for Offload Security (extracted from the
main application monorepo). This guide covers building and previewing it.

> **Hosting:** for the recommended self-hosted Docker deployment (and other
> options), see [HOSTING.md](HOSTING.md).

## Prerequisites

- Node.js 20+
- npm (a `package-lock.json` is committed)

## Local development & preview

```bash
npm ci          # install dependencies (first time only)
npm start       # live-reload dev server at http://localhost:3000
npm run build   # production build into ./build/
npm run serve   # serve the production build locally to verify before deploy
```

The build is configured to surface broken internal links and anchors
(`onBrokenLinks` / `onBrokenAnchors` in `docusaurus.config.ts`).

## Information architecture

- Pages live under `docs/`. The sidebar is **auto-generated** from the folder structure.
- Section order and labels come from `_category_.json` files in each folder;
  standalone top-level pages use `sidebar_position` in their frontmatter.
- Deep-technical / internal pages are grouped under **Architecture (Advanced)** and
  ordered last, keeping the customer journey up top.

## Screenshots

- Stored in `static/img/screenshots/` and referenced in pages as
  `/img/screenshots/<name>.png`.
- They were captured from a locally-running platform populated with realistic demo
  data, signed in as the admin user (`DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD`
  from your `.env`) at `http://localhost:3000`.
- To refresh a screenshot, sign in locally, navigate to the same route
  (`/dashboard`, or `/dashboard?section=<id>`), capture at ~1440×900, and overwrite
  the corresponding file. The pages reference the files by name, so no Markdown
  changes are needed.

## Deploy — GitHub Pages (recommended)

`.github/workflows/deploy-docs.yml` builds and publishes to GitHub Pages on every
push to `main` that touches `docs-site/**` (or via **Actions → Run workflow**).

One-time setup:

1. Repo **Settings → Pages → Build and deployment → Source: "GitHub Actions"**.
2. DNS: add a `CNAME` record `docs` → `<owner>.github.io` (e.g. `niteshsaini.github.io`).
3. The custom domain `docs.offloadsecurity.com` is provided by `static/CNAME`
   (copied into the build output). After the first successful deploy, tick
   **Enforce HTTPS** in the Pages settings.

## Deploy — Netlify (alternative)

`netlify.toml` is preconfigured (base `docs-site`, publish `build`, Node 20).
In Netlify: **Add new site → Import from Git → select this repo**; the config is
auto-detected. Set the custom domain under the site's **Domain settings**.

## Custom domain

`docs.offloadsecurity.com` is configured in two places — keep them in sync if it changes:

- `docusaurus.config.ts` → `url`
- `static/CNAME`
