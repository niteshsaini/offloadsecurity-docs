---
title: "1.4.1-beta.1 Release Notes"
sidebar_label: "1.4.1-beta.1"
slug: "/release-notes/1.4.1-beta.1"
description: "Offload Security 1.4.1-beta.1 (2 November 2026, pre-release): the one-file installer, and fixes for the 1.4.0 known issues — blank .env values, scheduled network and registry scans, Kubernetes token onboarding, per-key API rate limits and drift alert policies."
---

# 1.4.1-beta.1 Release Notes

**Released:** 2 November 2026 · **Type:** Pre-release · **Image tag:** `1.4.1-beta.1` · **Built on:** [1.4.0](./v1-4-0.md)

:::caution[Pre-release]
This beta is for testing, not for production.
:::

The first 1.4.1 pre-release: a one-file installer, and fixes for most of the [1.4.0 known issues](./v1-4-0.md#known-issues) plus the findings of a 1 November end-to-end test.

## Highlights

### One-file installer

A single script installs or upgrades a prebuilt-image deployment: `offload-install-<tag>.sh`, attached to each GitHub release. It writes the deploy files for that tag, generates the secrets and encryption keys on a fresh install, and pulls and starts the stack. See [Deployment & Operations](../on-premises/deployment.md).

### 1.4.0 known issues fixed

| 1.4.0 known issue | Now |
| --- | --- |
| Blank values in `.env` overrode built-in defaults | A blank or whitespace-only value falls back to the default, so a fresh `.env` from the template works as-is. |
| Scheduled Network and Container Registry scans failed with `not_yet_implemented` | Schedules run through the same launch paths as a manual scan. |
| Kubernetes token onboarding needed a kubeconfig | Service Account Token onboarding works end to end, including CA handling and token rotation. |
| Per-key API rate limits weren't enforced | Each key's `rate_limit_per_minute` is enforced, with rate-limit headers on the response. |
| Drift alert policy "Info (all)" acted as High+ and Teams sent nothing | "Info (all)" alerts on every severity, and the Teams channel is delivered. |
| `AGENTIC_FIX_RUNNER=none` in `.env.example` disagreed with the compose default | Both default to `sandbox`. |

The two remaining 1.4.0 known issues, Container Quick Scan and Docker Hub registries, are covered in [1.4.1-beta.3](./v1-4-1-beta-3.md) and the current docs.

### Other changes

- **Scan retention policy changes persist:** overrides are stored, so the workers apply them.
- **Logging:** the default log level is `ERROR`, set by `LOG_LEVEL` in `.env`. Failures and tracebacks stay visible.
- **App Scan:** starting a scan that is already running against the same target with the same settings returns the running scan (HTTP 200) instead of a duplicate.
- **IaC:** Dockerfile variants such as `Dockerfile-prod`, `Containerfile` and `*.tofu` files are assessed.
- **Docker socket proxy:** privileged container creates are refused.
- **Accessibility:** WCAG AA color contrast across every dashboard section, in light and dark.
- Fixes from the 1 November end-to-end test across sign-in, scans, counts and the UI.

## Upgrade notes

- **Logging is quieter:** with the new `ERROR` default, set `LOG_LEVEL=INFO` in `.env` if you rely on informational log lines.
- **API clients that exceed their key's rate limit now get HTTP 429.** Raise the key's limit if a pipeline needs more.

Full engineering record: `CHANGELOG.md` in the platform repository.
