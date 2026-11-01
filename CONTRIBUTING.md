# Writing the Offload Security docs

Conventions for pages in `docs/`. The site is customer-facing: it documents
what the platform does **today**, in the release named by `CURRENT_RELEASE`
(see [VERSIONING.md](VERSIONING.md)).

## Voice

- Professional and precise, not marketing. Short paragraphs, `##` / `###`.
- Every claim must be true of the current release. If a feature is off by
  default, behind a flag, or catalog-only, say so where it is described.
- American spelling for UI words that match the product; keep product names
  exactly as the UI shows them.
- Every page has front matter `title`, `sidebar_label` and a one-sentence
  `description` (used for search snippets, link previews and `/llms.txt`).

## Page types

| Type | Use for | Shape |
| --- | --- | --- |
| **Section overview** (`<section>/index`) | What the section covers and how its parts fit | Intro, how it fits together, prerequisites. "Pages in this section" cards are added automatically — don't hand-maintain a full link list. |
| **Task guide** | Doing one thing: connect, configure, run, deploy | The template below. |
| **Concept** | How something works (scoring, data model) | Explanation + a diagram where it helps (Mermaid). |
| **Reference** | Fields, endpoints, variables, permissions | Tables. One line per row. |
| **Troubleshooting & FAQ** | Symptoms | `## Area`, then **bold symptom** + the fix in one or two lines. |

### Task guide template

```md
---
title: "Connect a GCP project"
sidebar_label: "Connect a GCP project"
description: "One sentence: what the reader will have done when they finish."
---

# Connect a GCP project

One or two sentences: the outcome, who it is for, and roughly how long it takes.

## Before you begin

- Role needed in Offload Security (e.g. **Security Manager**).
- Access needed on the other side (least privilege; link to the permissions page).
- Anything that must exist first.

## Steps

1. **Do the first thing.** Where to click, or the command:
   ```bash
   gcloud ...
   ```
2. **Do the next thing.** ...

## Check that it worked

What the reader should see (status, a count, a screenshot).

## If something goes wrong

- **Symptom** — cause and fix. Link the section troubleshooting page for more.

## Next steps

- [The obvious next task](./next.md)
```

## Admonitions

Each type has one meaning; pick by meaning, not colour.

| Type | Meaning | Example |
| --- | --- | --- |
| `:::tip` | A shortcut or recommended practice the reader can act on | "Start with Critical + one account" |
| `:::note` | Context that helps understanding; nothing to do | "This section vs. the API reference" |
| `:::warning` | Data loss, security impact, irreversible action, or a cost | "The secret is shown once" |

Don't use `:::info`, `:::caution` or `:::danger`. At most one or two per
screen — a page full of boxes stops being read.

## Tables

- Use tables for comparisons, matrices and reference lists. Keep cells short
  (aim for under ~150 characters); move longer explanations to a list or a
  `###` per item below the table.
- Tables scroll sideways on small screens automatically — no HTML needed.
- Use ✓ and — consistently in matrices.

## API endpoints

Write an endpoint as a one-line code block or inline code starting with the
method; the site adds the coloured method badge:

````md
```
GET /api/alerts
```
| Action | Endpoint |
| --- | --- |
| List | `GET /api/alerts` |
````

## Status badges

Front matter, shown under the breadcrumb:

```yaml
status: opt-in      # beta | opt-in | planned | deprecated — only when it is a fact
new_in: 1.5.0       # the release that added the feature this page documents
```

Leave `status` out for normal pages. The 1.4.0 module catalog rates no module
GA, so don't label pages "Available" / "GA".

## Provider-specific steps

Use synced, deep-linkable tabs (`.mdx` pages):

```mdx
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs groupId="cloud" queryString>
<TabItem value="aws" label="AWS"> … </TabItem>
<TabItem value="gcp" label="GCP"> … </TabItem>
<TabItem value="azure" label="Azure"> … </TabItem>
</Tabs>
```

`?cloud=gcp` in the URL opens the GCP tab; the choice carries across pages.

## Screenshots

`static/img/screenshots/<section>/<name>.webp`, captured at 1440×900 (2×),
with descriptive alt text that says what the screen shows. Readers can click
to zoom.

## Before opening a PR

`npm run build` — it must finish without broken-link warnings.
