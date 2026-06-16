---
title: "Evidence Hub"
sidebar_label: "Evidence Hub"
sidebar_position: 4
---

# Evidence Hub

The Evidence Hub is where Offload Security gathers, stores, and exports the audit artifacts that prove your controls are in place. Instead of chasing screenshots and spreadsheets before every audit, the platform continuously collects evidence from your scans and assessments, attaches it to the right controls, and packages it up when an auditor asks.

Every piece of evidence is mapped to a control in the **Secure Controls Framework (SCF)** — a common control set that satisfies many frameworks at once (SOC 2, ISO 27001/27002, NIST CSF 2.0, NIST 800-53, PCI DSS 4.0, HIPAA, GDPR, and more). Collect a control's evidence once, and it counts toward every framework that maps to it.

## What it does

- **Collects evidence automatically.** Results from your cloud (CSPM), vulnerability, container, and Kubernetes scans, plus your completed assessments, are turned into evidence and linked to the controls they support.
- **Pulls verifiable cloud evidence.** For connected AWS, GCP, and Azure accounts, the platform can capture raw read-only API responses (for example, an S3 public-access block or an IAM password policy) so an auditor sees direct proof of configuration, not just a scanner's interpretation.
- **Lets you upload your own artifacts.** Add policies, procedures, certificates, configuration exports, and screenshots by hand and map them to controls.
- **Tracks coverage and gaps.** See, per framework and per control, what evidence exists, where it's missing, and how strong each piece is.
- **Scores and ages evidence.** Each artifact gets a quality score and a validity period, so stale evidence is flagged for refresh before it expires.
- **Protects sensitive data.** Secrets, keys, tokens, and other PII are automatically masked so evidence is safe to share with auditors.
- **Exports an audit-ready package.** Generate a downloadable evidence package per framework, organized control by control.

## Evidence sources

Evidence is labeled by where it came from, so reviewers always know its origin:

| Source | What it captures |
|---|---|
| **CSPM scan** | Cloud misconfiguration findings from posture scans. |
| **Cloud API (AWS / GCP / Azure)** | Raw read-only API responses that directly verify a setting. |
| **Vulnerability scan** | Vulnerability and remediation evidence. |
| **Container scan** | Image and registry scan results. |
| **Kubernetes scan** | Cluster configuration findings. |
| **Assessment** | Answers and attestations from completed [assessments](./interactive-assessments.md). |
| **Manual upload** | Policies, procedures, certificates, configs, and screenshots you add yourself. |

## How evidence is scored and aged

Not all evidence is equally strong, so each artifact carries a **quality score** and a **validity period**. Automated, machine-collected evidence scores highest and is trusted longest within a scan cycle; manual screenshots score lowest because they're point-in-time. When an artifact passes its validity window, it's marked **expired** and surfaced for refresh.

| Evidence type | Validity | Relative strength |
|---|---|---|
| Cloud / CSPM scan result | 90 days | Highest |
| Vulnerability scan result | 90 days | High |
| Assessment answer | 365 days | Medium |
| Policy / procedure document | 365 days | Medium |
| Manual screenshot or log | 365 days | Lowest |

:::note Why validity matters
Auditors expect evidence to be current. The Evidence Hub re-collects automated evidence on each scan, so as long as your scans run on a schedule, your technical evidence stays fresh on its own.
:::

## How to use it

### 1. Open the Evidence Hub

Go to **Compliance → Evidence Hub**. The page shows your frameworks with their coverage, a list of collected evidence, and per-control detail.

### 2. Collect evidence automatically

Select **Collect All** to run a full collection across every connected source — cloud, vulnerabilities, containers, Kubernetes, and assessments. The platform links each result to its controls and refreshes your compliance posture when it finishes. You can re-run this any time; it's also kicked off automatically after scans complete.

:::tip Connect first, then collect
The more you've connected and scanned, the more evidence appears automatically. Before your first collection, [connect your cloud accounts](../cloud-security/connecting-accounts.md) and run a posture scan, and complete any relevant [assessments](./interactive-assessments.md).
:::

### 3. Review a control's evidence

Select any control to open its evidence bundle — every artifact attached to it, with its source, quality score, validity, and review status. This is the view you'll walk an auditor through.

Evidence moves through a simple review workflow:

| Status | Meaning |
|---|---|
| **Auto-collected** | Gathered automatically; awaiting review. |
| **Pending review** | Submitted and waiting on a reviewer. |
| **Approved** | Verified and audit-ready. |
| **Rejected** | Not acceptable; needs to be replaced. |
| **Expired** | Past its validity window; needs a refresh. |

### 4. Upload evidence manually

For artifacts the platform can't collect on its own — signed policies, third-party certificates, board minutes — add them yourself. Choose **Manual Upload**, paste text or attach a file (such as a PDF or image), pick the evidence type, and map it to one or more controls. Manually uploaded evidence is masked and tracked just like automated evidence.

### 5. Check coverage and close gaps

Use the framework view to see which controls have evidence and which don't. Controls show a clear status — implemented, partial, planned, not applicable, or not assessed — so you can prioritize the gaps that block certification.

### 6. Export the audit package

When you're ready for an audit, generate the evidence package for a framework. The package is organized control by control and assembles up to four layers of proof for each:

1. **Policy** — the governing document.
2. **Procedure** — how the control is operated.
3. **Technical proof** — scan results or direct cloud-API evidence.
4. **Attestation** — assessment answers and sign-off.

Hand the package to your auditor as your starting evidence set.

## Sensitive data is masked automatically

Before evidence is stored or exported, the platform redacts sensitive values — passwords, secret keys, API keys, tokens, and identifiers like account IDs embedded in resource names — while keeping the rest of the artifact intact and useful. You get evidence that proves the control without leaking secrets.

:::warning Always review before sharing
Masking is automatic, but you remain the final reviewer. Spot-check exported packages and approve evidence before sending anything to an external auditor.
:::

## Related

- **[Compliance & Risk overview](./index.md)** — how compliance fits together across the platform.
- **[Interactive Assessments](./interactive-assessments.md)** — guided questionnaires that feed attestation evidence.
- **[Autonomous Compliance](./autonomous-compliance.md)** — the common control registry and continuous scoring.
- **[Compliance Dashboard & Reporting](./compliance-dashboard.md)** — framework scores and executive reporting.
- **[Connecting Cloud Accounts](../cloud-security/connecting-accounts.md)** — connect AWS, Azure, or GCP so cloud evidence flows in.
