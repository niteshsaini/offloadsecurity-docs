---
title: "What Offload Reads, Tests and Changes"
sidebar_label: "What Offload Changes"
description: "Every capability that reads, actively tests, simulates or writes to your environment, with the setting that turns it on, the permission it needs and the approval it waits for."
---

# What Offload Reads, Tests and Changes

Most of the platform only **reads**: scans collect configuration, images, code and telemetry with read-only credentials. A smaller set of capabilities does more. Some send test traffic to a target. Some simulate a change. Some write to a system you connected, such as a cloud account, a repository, Jira or Greenbone. This page lists each one separately, with what it touches, whether it is on by default, who can use it and what approval it waits for.

The four categories:

| Category | Meaning |
| --- | --- |
| **Read-only collection** | Reads configuration, metadata, images, code or telemetry. Nothing is created, changed or deleted on the other side. |
| **Active testing** | Sends traffic or requests to a target to see how it responds: web, API and network scans, and live checks of leaked secrets. It can be noticed by the target and can trigger its alerts. |
| **Simulation (dry run)** | Plans and records a change without making it. |
| **Authorized write** | Creates, changes or deletes something in a system you connected, or sends your data to a destination you configured. |

Permissions below are the platform's team permissions; [Roles, Teams & API Keys](./authentication/rbac-team-management.md) lists which roles hold them. **Execute Remediations**, **Manage Integrations**, **Manage Scans** and **Manage Team** are held by **Admin** and **Security Manager**. **Run Scans** is also held by **Security Analyst** and the **Integration** (CI) role.

## Read-only collection

| Capability | What it touches | Off by default? | Who can do it | Approval gate |
| --- | --- | --- | --- | --- |
| [Cloud posture scans](./cloud-security/scan-orchestration.md) (AWS, GCP, Azure) | Cloud provider APIs, with the read-only role you create: AWS `SecurityAudit` + `ReadOnlyAccess`, GCP viewer roles, Azure **Reader** ([permissions](./cloud-security/permissions.md)) | On once an account is connected | Connect: Manage Cloud Accounts. Scan: Run Scans | None |
| [Kubernetes scans](./security-scanning/kubernetes/index.md) | The cluster API, with a **Minimal** or **Extended** read-only `ClusterRole` ([RBAC profiles](./security-scanning/kubernetes/onboarding-clusters.md#rbac-profiles)); neither profile reads Secrets | On once a cluster is onboarded | Run Scans | None |
| [Container registry scans](./security-scanning/containers/registries.md) | Pulls images with pull-only access (`ReadOnlyAccess`, `roles/artifactregistry.reader`, `AcrPull`) | On once a registry is connected | Run Scans | None |
| [Code scans](./security-scanning/code/running-code-scans.md) | Clones repositories with your Git token, or reads an uploaded ZIP | On once a repository is connected | Run Scans | None |
| [Cloud events](./cloud-security/cloud-events.md) and [registry webhooks](./security-scanning/containers/governance.md#registry-webhooks) | Nothing outbound: your cloud or registry pushes events to the platform; a registry push queues a scan | Off until you create the event route or webhook | Set up: Manage Cloud Accounts (cloud events), Manage Container Security (registry webhooks) | None |
| [Wazuh](./integrations/wazuh.md) | Reads the Wazuh API and indexer. Retiring an agent is a platform record only; the [cleanup script](./on-premises/wazuh-agent-fleet.md#remove-agents-from-wazuh) is for your Wazuh administrator to run | Off until connected | Manage Integrations | None. Nothing is deleted in Wazuh by the platform |
| [SonarQube](./integrations/sonarqube.md) | Reads projects and open issues | Off until connected | Manage Integrations | None |

## Active testing

| Capability | What it touches | Off by default? | Who can do it | Approval gate |
| --- | --- | --- | --- | --- |
| [App Scan](./security-scanning/app-scan.md) and [targeted scans](./security-scanning/native-scans.md) (ZAP, Nuclei, OWASP API checks) | Sends crawl and attack payloads to the web app or API you name, optionally signed in as a test user | Runs only when someone starts or schedules it | Run Scans | Authorization attestation in the launcher. Required for every scan only when `SCAN_REQUIRE_AUTHORIZATION=true`; off by default, when scans without one are labelled *authorization not recorded* |
| [State-changing probes](./security-scanning/native-scans.md#opt-in-state-changing-probes) | Sends `X-HTTP-Method-Override: DELETE/PUT/PATCH` requests with the scan's credentials, which can change data in the target | **Off**; a per-scan **Allow state-changing probes** switch | Run Scans | As above, plus the explicit per-scan switch |
| Network and TLS scans (nmap, testssl.sh) | Port scans and TLS handshakes against the hosts you name | Runs only when started or scheduled | Run Scans | Authorization attestation, as above. Private (RFC 1918) targets also need `ALLOW_PRIVATE_SCAN_TARGETS=true` |
| [OpenVAS scans](./on-premises/openvas-scanning.md) | Your Greenbone scanner probes the hosts, with SSH, SMB, SNMP or ESXi logins for credentialed scans | Off until Greenbone is connected | Start: Run Scans. Credentialed scans: Manage Scans | Authorization attestation when the scan starts, as above |
| [Secret live validation](./security-scanning/code/secret-detection.md#live-validation) | Sends each leaked secret found in a code scan to its issuing provider's API (GitHub, Slack, Stripe, AWS STS and about 40 others) to ask whether it is still live. Only the verdict is stored | **On** by default; `SECRET_VALIDATION_ENABLED=false` turns it off | Runs automatically in any code scan | None |
| [AI-SPM prompt-injection tests](./ai-threat-intelligence/ai-spm.md#testing--prompt-injection) | Sends eight OWASP LLM01 probes to the chat endpoint you enter | Dry run unless you give an endpoint; needs `ENABLE_AI_FEATURES` on | Manage Assessments | None beyond entering the endpoint |

## Simulation (dry run)

| Capability | What it touches | Off by default? | Who can do it | Approval gate |
| --- | --- | --- | --- | --- |
| [Auto-Fix Engine](./ai-threat-intelligence/ai-soc-agents.md#auto-fix-engine) and [Compliance Engine remediation](./compliance/autonomous-compliance.md#remediation-playbooks), with `REMEDIATION_LIVE_EXECUTE=false` | Nothing in your cloud. Actions are matched, approved, "executed" and logged as **Simulated** | This is the default mode | Execute Remediations | Each action still needs an approval by someone other than its creator |
| **Process findings** preview | Nothing: counts the actions that would be created before you confirm | Always a preview first | Execute Remediations | Your confirmation |

## Authorized write

| Capability | What it touches | Off by default? | Who can do it | Approval gate |
| --- | --- | --- | --- | --- |
| Cloud remediation, live (Auto-Fix Engine and Compliance Engine playbooks) | Changes cloud resources: blocks public access, enables encryption or logging, removes an open ingress rule. **Rollback** reverts using stored parameters | **Off**: needs `REMEDIATION_LIVE_EXECUTE=true` on the deployment | Execute Remediations | Every action starts *pending* and must be approved by someone other than its creator; an optional multi-level approval chain. See [Live cloud remediation](#live-cloud-remediation) |
| [Fix PR](./security-scanning/code/findings-and-reports.md#fixing) | Pushes a branch and opens a pull request | Runs only when someone clicks it | Execute Remediations, with a token that can open pull requests | Your normal code review; the platform never merges |
| [Fix with agent](./security-scanning/code/agentic-fixes.md) | An agent in a sandbox pushes a branch and opens a pull request | **Off**: `AGENTIC_FIX_ENABLED=true` on the deployment **and** enabled per team | Enable per team: Manage Team. Run: Execute Remediations | Your normal code review; never merges or pushes to a protected branch |
| [Pull request review](./security-scanning/code/pull-request-review.md) | Posts inline and summary comments, GitHub check runs, and GitLab or Bitbucket commit statuses | Off until the GitHub App is installed or the GitLab / Bitbucket hook is created; comments and check run are then on per repository | Manage Integrations | None per review |
| SARIF upload to GitHub Code Scanning | Your CI job uploads SARIF to GitHub; the platform only generates the workflow | **Off**: `upload_to_code_scanning` in the [workflow generator](./cli-and-cicd.md) defaults to false | Whoever adds the workflow to the repository | Your repository's own review |
| [Jira](./integrations/jira.md) | Creates tickets (critical findings automatically, high on request) and transitions them when a finding is resolved | Off until connected | Connect: Manage Integrations | None per ticket |
| [GitHub & GitLab Issues](./integrations/git-issues.md) | Opens one issue per finding or alert group, comments on it and closes it when the finding is resolved | Off until used; auto-create is a separate rule | Vulnerability Management or Manage Alerts permission; rule and shared connection: Manage Integrations | None per issue |
| [OpenVAS task management](./on-premises/openvas-scanning.md#run-scans-from-the-platform) | Creates targets, tasks and login credentials in Greenbone; edits tasks; moves deleted tasks to Greenbone's trashcan | Off until Greenbone is connected | Create and start: Run Scans. Edit, delete, schedule, credentials: Manage Scans | Delete is refused while a task is running |
| [Notifications](./integrations/notifications.md), [webhooks](./integrations/webhooks.md) and [SIEM forwarding](./integrations/siem-forwarding.md) | Sends alert and finding details to Slack, Teams, Google Chat, email, PagerDuty, your webhook receivers, Splunk or syslog | Off until a channel is configured | Manage Integrations | None per message |
| Confluence publish | Creates or updates a compliance summary page in the connected space | Off until Confluence is connected; runs only on request | Manage Integrations | None per page |
| Scheduled reports by email | Emails report files through your SMTP relay | Off until a schedule is created | View Dashboard | None per send |

## Live cloud remediation

Four things must all be true before the platform changes a cloud resource:

1. **The operator turned it on.** `REMEDIATION_LIVE_EXECUTE=true` in the deployment's `.env`. It is a deployment setting, not a team setting, and is `false` by default.
2. **An approved action exists.** Every action is created *pending*, including those from playbooks marked low-risk. Someone with **Execute Remediations** who is not the action's creator approves it, or every level of an approval chain approves it in order.
3. **Someone executes it.** Execution is a separate click (or API call) by a user with **Execute Remediations**. Nothing executes on a schedule.
4. **The credentials can write.** AWS actions run with the account's stored credentials, never the platform host's own identity unless the operator sets `REMEDIATION_ALLOW_DEFAULT_AWS_SESSION=true`. The read-only role you created for scanning cannot make these changes, so the call fails until you grant the specific write permissions the playbook needs. GCP and Azure playbooks run the `gcloud` or `az` command-line tool on the platform host, signed in as whatever identity that tool has there; with none, they fail.

Approvals, denials, executions and rollbacks are audit events, exported in the [remediation audit report](./compliance/audit-reports.md).

:::tip
Run one full cycle with live execution off and read the audit trail before you turn it on. If you never want the platform to change cloud resources, leave `REMEDIATION_LIVE_EXECUTE=false` and keep the scanning role read-only. The two together mean no remediation can reach your cloud.
:::

## Data that leaves the platform

Some capabilities send data to a third party rather than changing anything: AI features (to the LLM provider you configure), secret validation, notification and SIEM destinations, and browser usage analytics. For every destination, the data it receives and how to turn it off, see [What needs outbound access](./on-premises/deployment.md#what-needs-outbound-access).

## Related

- [Required Permissions](./cloud-security/permissions.md): the read-only policies per cloud.
- [Engagement & Evidence](./security-scanning/scan-evidence.md): how authorization for active scans is recorded.
- [Production configuration](./adoption/production-configuration.md): settings to review before go-live.
- [Trust & Security](./trust-and-security.md): how the platform protects your data.
