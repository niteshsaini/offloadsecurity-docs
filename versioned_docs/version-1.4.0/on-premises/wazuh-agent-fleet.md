---
title: "Wazuh Agent Health & Cloud Links"
sidebar_label: "Agent Health & Cloud Links"
sidebar_position: 4.2
new_in: 1.4.0
description: "Keep the Wazuh fleet honest — find disconnected, silent, outdated and unmatched agents, retire stale agents and hand Wazuh a cleanup script, see which cloud VMs have no agent, and link agents to their cloud VMs one at a time or in bulk."
---

# Wazuh Agent Health & Cloud Links

A fleet view is only as good as its roster. This page covers the three jobs that keep it accurate: finding agents with a problem, retiring agents of hosts that no longer exist, and making sure every agent is tied to the right cloud VM. All of it is under **Infra Command Center → Endpoint Security**.

Viewing and **Export CSV** need the **View Integrations** permission. Retire, restore, the cleanup script and link changes need **Manage Integrations** (the permission used to connect Wazuh).

## Check agent health

**Endpoint Security → Overview** counts total, active, disconnected and never-connected agents (click a tile for the filtered Agents list) and shows 30-day trends. Below them, **Agent health** has one tile per gap:

| Tile | Meaning |
| --- | --- |
| Disconnected | Wazuh marked the agent disconnected |
| Stopped reporting | Wazuh still lists it active but its keep-alive is late — choose the threshold (15 minutes to 30 days; 30 minutes by default) |
| Never connected | Enrolled but never reported |
| Outdated agent | Older than the manager |
| Not seen in SCA · No vulnerability data | The agent reports, but not configuration checks or vulnerability state |
| No cloud match | No cloud VM is linked to the agent |
| Retired | Agents you retired (below); excluded from the other tiles and counted here |

Narrow any tile with the **last seen** filter — more than 7, 30 or 90 days ago, or a number of days you type (up to 3650). **Export CSV** downloads every agent matching the current tile and filters, not just the page on screen. Click an agent to open its [Endpoint 360](./endpoint-security.md#endpoint-360).

The page states which sync its data comes from and how many agents it covers. Ages are measured at that sync, not now; a tile reads — when the answer is unknown, never 0; and "roster partial: N of M agents read" means the last sync could not read every agent.

## Retire stale agents

Retire agents of hosts that no longer exist so they stop inflating health counts and coverage.

1. **Pick the stale agents.** In Agent health, choose a tile (for example *Disconnected* or *No cloud match*) and a last-seen filter (for example more than 90 days).
2. **Retire.** Tick agents and click **Retire selected**, or **Retire all N matching**. Enter a reason (at least 3 characters) and confirm. If the list changed in the meantime (a different count or a newer sync), nothing is retired and the page says why.
3. **Check the result.** The **Retired** tile lists each retired agent with who retired it, when, why, and how many of its findings were closed. Endpoint 360 shows a *Retired* badge.

What retirement does:

- The agent leaves the health counts and the Coverage lists, and no longer counts as covering a cloud VM.
- Its open Wazuh vulnerability findings are closed with the reason *agent retired*, in the background within a few minutes. Findings you marked false positive or accepted risk are not touched.
- **A retirement is not a fix**: these closures are left out of mean time to remediate and "resolved" counts, and an SLA breach stays recorded.
- Agents still reporting (active with a recent keep-alive) are skipped, with the reason shown. At most 10,000 agents per retire or restore.

**Restore** (from the Retired tile, with a reason) puts each finding back in the state it had, including its assignee — unless you triaged it yourself after the retirement, in which case your decision stands. An agent that sends a new keep-alive after retirement returns on its own, flagged **Reconnected after retirement**, and its findings reopen.

## Remove agents from Wazuh

Retiring changes nothing in Wazuh. To remove the agents there, click **Cleanup script** for the selected (or all matching) agents and give the script to your Wazuh administrator:

1. Set the Wazuh API user and password (or a Wazuh API token) in the environment on a machine that can reach the Wazuh API.
2. Run the script without options: a dry run lists what would be removed.
3. Run it with `--delete` and type the confirmation it asks for. It prints how many agents Wazuh removed and how many failed.

The script sends at most 100 agents per request, removes an agent only if its status is still the one it had when the script was generated, skips agents seen more recently than its older-than setting, and never includes agents pending enrollment. Use a token if the password contains a double quote or backslash; the summary needs `python3`. Each download is recorded with who generated it and for which agents.

:::warning[Removal in Wazuh is permanent]
A host removed from Wazuh must be re-enrolled to report again. Run the dry run first and check the list.
:::

## See which cloud VMs have no agent

**Endpoint Security → Coverage** lists cloud VMs from the asset inventory that have no Wazuh agent, by provider, account and region, and the agents that match no cloud VM. A VM counts as covered when it is linked to a connected agent; retired agents never cover a VM. Coverage is blank, not 0%, until links have been computed, and the page discloses stale links and VMs discovered since the last link run.

## Link agents to cloud VMs

The sync links agents to VMs automatically and never guesses between several candidates (see [Wazuh Integration](./wazuh-integration.md#agent--cloud-vm-link)). Fix the rest one at a time in an agent's **Endpoint 360 → Cloud VM link** panel (confirm, change, mark *not a cloud VM*, or *Revert to automatic*), or in bulk under **Coverage → Fix cloud links in bulk**:

| Tool | Use it for |
| --- | --- |
| **Ambiguous matches** | Agents with several possible VMs. The strongest candidate is pre-selected; change it if needed, tick rows (kept across pages), enter a reason, then **Confirm selected** — or **Not a cloud VM** for on-premises hosts |
| **CSV import** | A UTF-8 file with columns `agent` (id or name) and `vm` (instance id, asset id or VM name), plus optional `account` to tell same-named VMs apart. **Preview** shows each row's outcome and changes nothing; **Apply** (with a reason) links the rows marked *Will link* |
| **Rules** | A hostname pattern (`*` and `?`), an optional IP range such as `10.20.0.0/16`, and either "Only consider VMs in account" or "Mark not a cloud VM". A saved rule does nothing until you **Preview** and then **Apply** it; re-apply after new VMs are discovered. **Revert** undoes only that rule's decisions |

Every change is recorded in the agent's link history with who, when, the reason and the tool used, and the affected endpoint vulnerabilities are re-scored (a large change is finished over the next syncs, and the page says how many remain).

Safeguards and limits:

- A rule never overrides a manual decision (*Manual decision kept*), and never links an agent by IP or hostname alone to a VM another agent is, or would be, linked to (*Still ambiguous*).
- Bulk confirm accepts only a VM the matcher proposed; link any other VM from Endpoint 360 or by CSV.
- Retired agents are skipped by every bulk tool and counted.
- At most 1,000 agents per bulk action; 1,000 rows and 256 KB per CSV file; 100 saved rules per team; 5,000 agents changed by one rule apply. Larger requests are refused with the limit, never cut short.

## Related

- [Wazuh Integration](./wazuh-integration.md) — what syncs and how links are matched.
- [Endpoint Security](./endpoint-security.md) — Endpoint 360, Fix first, alert triage, logins, file integrity.
- [Asset Inventory](../cloud-security/asset-inventory.md) — the VM side of the link.
