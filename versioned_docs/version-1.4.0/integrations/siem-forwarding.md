---
title: "SIEM Forwarding: Splunk and Syslog / CEF"
sidebar_label: "SIEM Forwarding"
sidebar_position: 4
new_in: 1.4.0
description: "Forward alert-group changes, finding lifecycle changes and optionally the audit trail to a Splunk HTTP Event Collector or any syslog SIEM as CEF — what is sent, how to connect, delivery health on the card, and the audit-trail pull export."
---

# SIEM Forwarding: Splunk and Syslog / CEF

Send the platform's security events to your SIEM: **Splunk** through its HTTP Event Collector (HEC), or any receiver that accepts **ArcSight CEF over RFC 5424 syslog** — rsyslog, syslog-ng, IBM QRadar, ArcSight and similar. Changes are queued and sent every minute, retried with backoff when the receiver is down, and the card shows exactly what was delivered and what was not. Setting up one destination takes about ten minutes.

## What is sent

Each destination chooses its streams and a minimum severity.

| Stream | Default | Events |
| --- | --- | --- |
| **Alerts** (`forward_alerts`) | On | One event when an alert is created, when its status, acknowledgement or assignee changes, and when it is resolved (`alert.created` · `alert.updated` · `alert.resolved`). Not one per repeat occurrence; raw Wazuh alerts are never forwarded |
| **Findings** (`forward_findings`) | On | One event when a finding is new, reopened or resolved by a scan, and for every triage decision or expired decision (`finding.new` · `finding.reopened` · `finding.resolved` · `finding.triage`) |
| **Audit trail** (`forward_audit`) | **Off** | Every entry of the team's hash-chained audit trail (`audit.entry`), as the same CEF line the audit export produces |

`min_severity` (default **high**) applies to alerts and findings; the audit trail is sent in full. Findings with no severity are sent only at minimum severity *info*.

**Splunk** receives JSON events (`source` `offload-security`, sourcetype `offload:security` unless you set one) with an `event_type` field. **Syslog** receives one CEF line per event inside an RFC 5424 message (vendor *Offload Security*, product *Offload Platform*).

:::warning[The audit trail holds personal data]
Audit entries contain user email addresses, source IP addresses and the API paths people called. Turn on **Forward Audit** only for a SIEM that is allowed to hold that data.
:::

## Before you begin

- **Manage Integrations** permission in Offload Security.
- **Splunk:** an HTTP Event Collector input with **SSL enabled**, and its token. **Syslog:** the host and port of a receiver that accepts RFC 5424 syslog over TLS, TCP or UDP.
- The receiver must be reachable from the platform server. Loopback and cloud-metadata addresses are always refused; a receiver on a private network is allowed while `ALLOW_PRIVATE_INTEGRATION_TARGETS` is on (the default).

## Steps

1. **Open the card.** Integrations → **Splunk** (or **Syslog / CEF**, both under *SIEM & SOAR*) → **Connect**.
2. **Enter the destination.**
   - *Splunk:* `hec_url` — `https://splunk.example.com:8088` is enough; the event endpoint is added. `hec_token`. `index` is optional (blank = the token's default index); `sourcetype` defaults to `offload:security`. HEC URLs must be `https://`.
   - *Syslog / CEF:* `syslog_host` and `syslog_port`; `transport` — `tls` (default; encrypted, the receiver's certificate is checked), `tcp` or `udp` (both clear text); `tcp_framing` — `octet-counting` (default) or `newline` (RFC 6587); `syslog_facility` — `local0` (default) to `local7`.
3. **Choose what to send.** `forward_alerts`, `forward_findings`, `forward_audit` and `min_severity`, as in the table above.
4. **TLS.** Keep `verify_ssl` on. If the receiver's certificate is signed by a private CA, paste that CA certificate (PEM) into `ca_cert`.
5. **Test.** The connection test sends one real event of type `connection.test` and says what was verified.
6. **Complete the setup.** Forwarding starts from this moment; earlier alerts, findings and audit entries are not sent.

## Check that it worked

- Search the SIEM for the `connection.test` event — for syslog this is the only proof, because syslog has no acknowledgement (*delivered* means the TCP / TLS connection accepted the data, or for UDP that the datagram was sent).
- The card shows the streams being sent, when the last batch was delivered, how many events are queued and how long the oldest has waited, and — after a failure — the error and the next retry time.
- **Splunk with indexer acknowledgement** enabled on the HEC input: a batch counts as delivered when Splunk accepts it, and later runs ask Splunk whether it was indexed. The card shows how many events were confirmed indexed, how many are waiting, and how many were accepted but never confirmed (not within 10 minutes, or on a data channel a new HEC URL replaced). Unconfirmed events are not resent — check them in Splunk.

## Delivery behavior

| Behavior | Detail |
| --- | --- |
| Cadence | Queued changes are sent every minute, in batches (Splunk: up to 100 events or 800 KB per request) |
| Retries | After a failure the destination waits 30 seconds, doubling up to 1 hour. **Reconfigure** with a passing test retries straight away |
| Delivery guarantee | At least once: after a restart a batch can arrive twice. Every event has a stable `event_id` — de-duplicate on it |
| Queue | Up to **10,000** events per destination. Near that limit, alert and audit collection pauses and resumes where it stopped (nothing lost). Finding changes cannot wait: when the queue is full the **oldest** finding events are dropped, and the card says how many, when, why and which time range |
| Rejected data | Events the receiver rejects as invalid are dropped after 3 attempts (only those events; the rest of their batch is resent) and counted on the card |
| Long text | Titles over 500 characters and descriptions over 2,000 are shortened and marked (`title_truncated: true`; CEF `flexString1=true`). Over UDP, a message larger than one datagram is shortened and marked `[truncated]` |

:::tip[Prefer TLS or TCP]
Many UDP syslog receivers silently cut messages longer than about 2 to 8 KB, which the platform cannot see. Use TLS or TCP when events carry long descriptions.
:::

## Limits

- Findings changed outside the findings lake — for example by Jira status sync or Wazuh agent retirement — are not forwarded yet.
- When two people in a team set up the same tool, only the newest configuration forwards; the older card says *Not forwarding: a newer configuration … is the one used*. Remove the older card.
- There is no dedicated QRadar or Microsoft Sentinel card. QRadar and ArcSight accept CEF over syslog; for Sentinel, use a syslog / CEF collector or [webhooks](./webhooks.md).

## Pull the audit trail instead

A SIEM can also **pull** the hash-chained audit trail on a schedule, independent of the forwarding above:

```
GET /api/audit-trail/export/siem?after_seq=0&limit=500&format=jsonl
```

- `format=jsonl` (one JSON object per line, each with `seq`, `prev_hash` and `hash` so the receiver can check continuity) or `format=cef`.
- Paging is by cursor: pass the `X-Audit-Next-After-Seq` response header as `after_seq` on the next call; `X-Audit-Has-More: true` means another page is ready. `limit` is 1–5,000 (default 500).
- Call it signed in as a team admin, or with a team admin's API key that holds the `admin:audit` scope. There is no screen for it.
- Entries written before the hash chain existed are not in this export; use `GET /api/audit-trail/export` (CSV) for those.

## If something goes wrong

- **"Splunk HEC answered HTTP 403 … check the HEC token"** — the token is wrong or its input is disabled. Copy the token again from Splunk (*Settings → Data inputs → HTTP Event Collector*) and **Reconfigure**.
- **"HEC URL must start with https://"** — enable SSL on the HEC input and use its https URL; the token travels in every request.
- **"Splunk HEC answered HTTP 400 (code 7) … the token may not write to that index"** — leave `index` blank or add the index to the token's allowed indexes. Events stay queued meanwhile.
- **"TLS certificate of … was not trusted"** — paste the CA that signed the receiver's certificate into `ca_cert`, or use the receiver's exact host name.
- **"Host … is not allowed"** — loopback and cloud-metadata are always refused; for a private receiver on a deployment that set `ALLOW_PRIVATE_INTEGRATION_TARGETS=false`, ask the administrator.
- **"Collection of … is paused while the queue is nearly full"** — the receiver is down or not keeping up. Nothing is lost; collection resumes once the queue drains.
- **Red "event(s) were not forwarded" box** — finding events dropped from a full queue, events the receiver rejected, or the queue of an older configuration that a newer one replaced. Fix the receiver; new events flow again by themselves.

See also [Troubleshooting & FAQ](./troubleshooting.md).

## Next steps

- [Webhooks](./webhooks.md) — signed `alert.*` and other platform events to your own HTTPS endpoint.
- [Notifications](./notifications.md) — human-facing channels.
