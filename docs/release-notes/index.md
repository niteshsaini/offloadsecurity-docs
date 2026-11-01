---
title: "Release Notes"
sidebar_label: "Release Notes"
description: "Offload Security platform releases — what changed in each version, upgrade steps that need an operator, and how the versioned documentation works."
---

# Release Notes

Each platform release is a version number (`MAJOR.MINOR.PATCH`) and a matching set of container image tags. On-premises installs pin a release with `IMAGE_TAG` in `.env` — see [Deployment & Operations](../on-premises/deployment.md#upgrades).

| Version | Released | Type | Notes |
| --- | --- | --- | --- |
| **1.4.0** (current) | 31 October 2026 | Beta | [1.4.0 release notes](./v1-4-0.md) |

## Versioned documentation

These docs are versioned with the platform. The version selector at the top right shows which release you are reading.

- **The current release** is served at the site root (`docs.offloadsecurity.com/...`). Links to it never change between releases.
- **Earlier releases** stay available under their version number (`docs.offloadsecurity.com/<version>/...`) once a newer release ships, with a banner saying they are no longer the latest.
- 1.4.0 is the first release published with versioned docs. Earlier releases have no separate documentation snapshot.

:::tip[Which version am I running?]
On-premises: the `IMAGE_TAG` value in your `.env`, or `docker compose -f docker-compose.client.yml images`. Read the docs for that version; if you are on an earlier release than the oldest one listed here, upgrade first.
:::

## Version numbers

| Change | Example | Meaning |
| --- | --- | --- |
| Minor | 1.3.0 → 1.4.0 | A release with new features and fixes. Read the release notes' **Upgrade notes** before moving. |
| Patch | 1.4.0 → 1.4.1 | Fixes on top of a shipped release; no new operator steps unless the notes say so. |
| Major | 1.x → 2.0.0 | Breaking API or deployment changes, called out explicitly. |
| Pre-release suffix | 1.5.0-rc.1 | A release candidate — not for production. |
