---
title: "Upgrade Impact"
sidebar_label: "Upgrade Impact"
sidebar_position: 4.5
new_in: 1.4.0
description: "Rank dependency upgrades by how many vulnerabilities each one resolves across your repositories, with what remains and why, copyable commands and a compatibility hint."
---

# Upgrade Impact

Dependency findings are usually the longest list and the cheapest to fix — but forty CVEs on one package are one upgrade, not forty tasks. **Upgrade Impact** turns the open dependency findings into a ranked list of upgrades: *"Upgrading `<package>` from `<current>` to `<recommended>` resolves N vulnerabilities (x Critical, y High, z Medium, w Low)"*, with what that upgrade does **not** fix and why.

**Where:** Code Command Center → **Upgrade Impact**.

The same engine and view serve Linux patch management for endpoints, so "upgrading X resolves N" is the same number everywhere it appears.

## Read the list

Each row is one **upgrade opportunity**: one package on one release line (the same package on 3.x and 4.x is two rows).

| Tile | Counts |
| --- | --- |
| **Upgrade opportunities** | Rows in the list. |
| **CVEs resolvable** | Package × CVE pairs a recommended upgrade resolves. |
| **Critical / High resolvable** | The same, at critical and high severity. |
| **KEV resolvable** | Resolvable CVEs on the CISA KEV list. |
| **CVEs remaining** | Package × CVE pairs no recommended upgrade resolves. |

Filter by package name, ecosystem or **Resolves a KEV CVE**, and sort by impact score, most KEV, most Critical, most CVEs resolved, most assets, or name.

## Open an upgrade

Select a row to open the package drawer:

- the headline, and the **current**, **recommended** and **alternative** versions;
- every CVE with its status and fixed versions, and the repositories carrying the package;
- copyable upgrade **commands**;
- a **compatibility** hint.

The drawer also opens from the [SBOM & Licences](./sbom-and-licenses.md) package table (the "⬆ version" cell or the "resolves N" line) and from **Top fixes** on the Findings tab. A link with `?tab=upgrades&upgrade=<id>` opens one upgrade directly.

## How the numbers are made

| Topic | Rule |
| --- | --- |
| **Recommended version** | The smallest fixed version on your installed release line that resolves the most CVEs. A newer major version that resolves more is shown separately as the **alternative**, marked as a major upgrade. |
| **Fixed versions** | Taken from the scanners' findings. No version is invented; an unknown is shown as "—" with the reason, never as 0. |
| **Version comparison** | Ecosystem-aware (PEP 440, semver, Maven, NuGet, Composer, RubyGems and others). |
| **Remaining CVEs** | Listed with the reason: no fix known, fixed only above the recommended version, fix data pending, versions not comparable, advisory says not affected, or scanner and advisory disagree. |
| **Commands** | The ecosystem's default package manager (for example `npm install`, `pip install`), labelled *ecosystem default*. Adapt them if the repository uses another manager. |
| **Compatibility** | For semver ecosystems (npm, Cargo, Composer, NuGet, Go) a major-version change — or a minor change on 0.x — is flagged. PyPI major changes are flagged with a note that PyPI gives no compatibility guarantee. Other ecosystems show *Compatibility unknown*. |

## What is counted

- Only **open** dependency findings on **default branches**. Findings under an approved risk exception are excluded, and the page says how many.
- The tiles count each package × CVE once. The drawer's numbers cover every repository with that package, even when it is opened from one repository.
- Known vulnerabilities in the recommended version itself are not checked for code packages; the drawer shows *— (not checked)*.

The list is recomputed in the background. Right after a scan it can show *Computing upgrade impact…* for a short while; **Recompute now** queues a fresh computation. The drawer is always computed fresh.

## From upgrade to pull request

- **Copy** the commands and open the change yourself, or use the SBOM **Fix Plan** for a pull-request body.
- With agentic fixes enabled, **Upgrade with agent** on a *Group by fix* row in Findings runs one upgrade and opens one pull request that closes that group's CVEs — see [Fix with Agent](./agentic-fixes.md).

## Related

- [SBOM & Licences](./sbom-and-licenses.md) — the package inventory behind the list.
- [Findings & Reports](./findings-and-reports.md) — *Top fixes* and *Group by fix*.
- `GET /api/vulnerabilities/upgrade-impact?domain=code` and `GET /api/vulnerabilities/upgrade-impact/{id}` — the same data over the API ([Scanning API](../api.md#code)).
