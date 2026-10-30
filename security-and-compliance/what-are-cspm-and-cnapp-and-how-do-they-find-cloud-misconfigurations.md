---
title: "What are CSPM and CNAPP, and how do they find cloud misconfigurations?"
id: 766
category: "Security and Compliance"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - security-and-compliance
  - cspm
  - cnapp
  - cloud-security
quiz:
  stem: "A CSPM reports 4,000 findings. Which prioritisation approach best reflects how modern CNAPP tools rank risk?"
  options:
    - "Fix findings alphabetically by resource name"
    - "Rank by attack path: combine misconfiguration, exposure to the internet, exploitable vulnerabilities, and privileged identities on the same resource, and fix the combinations that lead to sensitive data first"
    - "Fix only findings older than one year"
    - "Disable all rules that produce more than ten findings"
  answer: 2
  explanation: "Individual findings are rarely the risk; toxic combinations are. A public VM with a critical CVE and an admin role that can read customer data is an attack path, while the same CVE on an isolated, unprivileged host is backlog."
---

# What are CSPM and CNAPP, and how do they find cloud misconfigurations?

**Short answer:** **CSPM** (Cloud Security Posture Management) continuously reads your cloud accounts' configuration through the provider APIs and compares it with rules - CIS Benchmarks, PCI DSS, your own policies - to flag misconfigurations such as public buckets, open security groups, unencrypted volumes, disabled logging, and over-privileged identities. **CNAPP** (Cloud-Native Application Protection Platform) is the consolidated category that bundles CSPM with workload protection (CWPP), identity entitlement analysis (CIEM), Kubernetes posture (KSPM), IaC and image scanning, and increasingly data and AI posture, then correlates them into **attack paths**. Native options are AWS Security Hub and Config, Microsoft Defender for Cloud, and Google Security Command Center; commercial CNAPPs include Wiz, Prisma Cloud, Orca, and Sysdig. The value is not the finding count - it is prioritising the few combinations that actually lead to your data.

## Detail

### How CSPM works

Most CSPM is **agentless**: a read-only cross-account role (or Azure/GCP equivalent) lets the tool enumerate resources and their configuration on a schedule and on change events (CloudTrail, Activity Log). Rules evaluate the resulting resource graph - "S3 bucket with public ACL", "security group allowing 0.0.0.0/0 on 22", "root account without MFA", "CloudTrail disabled in a region". Agentless **snapshot scanning** extends this to workloads: the tool snapshots disks and inspects them for vulnerable packages and secrets without installing anything on the instance.

### The CNAPP components

| Component        | Question it answers                                                      |
| ---------------- | ------------------------------------------------------------------------ |
| CSPM             | Is the cloud configuration safe and compliant?                           |
| KSPM             | Are clusters and workloads configured safely (RBAC, PSA)?                |
| CIEM             | Which identities can do what, and which permissions are unused?          |
| CWPP             | Are VMs, containers, and functions vulnerable or compromised at runtime? |
| IaC / image scan | Will the next deployment introduce a misconfiguration or CVE?            |
| DSPM             | Where is sensitive data, and who can reach it?                           |

### Attack paths are the differentiator

A single finding rarely matters on its own. What matters is a **toxic combination**: an internet-exposed VM, running a package with a known exploited CVE, whose instance role can read the customer-data bucket. Graph-based tools join network exposure, vulnerabilities, identity permissions, and data classification to rank that path above thousands of isolated findings. This is the same idea as prioritising vulnerabilities by KEV, EPSS, and reachability rather than CVSS alone.

### Where it fits with shift-left

CSPM is **detective**: it sees what is deployed, including console changes and drift that never went through a pipeline. IaC scanning and admission control are **preventive**. A mature setup runs the same policy intent in both places and closes the loop: a recurring CSPM finding becomes an IaC rule, an SCP or Azure Policy deny, or a fix to the platform module, so it cannot recur. Tracing a finding back to the Terraform file and the owning team (via tags) is what makes it actionable.

### Limitations to name

- **Noise**: default rule packs produce thousands of findings; without ownership tags and prioritisation, teams ignore them.
- **Detection, not prevention**: CSPM tells you after the bucket is public. Pair it with guardrails that make the violation impossible.
- **Auto-remediation risk**: automatically closing a port or blocking a bucket can cause an outage; restrict it to unambiguous cases and keep an audit trail.
- **Coverage gaps**: application logic, business data flows, and SaaS outside the cloud provider APIs are invisible to it (SSPM covers some SaaS).
- **Access**: the scanning role is a high-value target itself; keep it read-only, monitored, and separate from remediation permissions.

## Example

```bash
# Native CSPM on AWS: enable a Security Hub standard (add the CIS benchmark the same way), then list failing controls
aws securityhub batch-enable-standards --standards-subscription-requests \
  'StandardsArn=arn:aws:securityhub:eu-west-1::standards/aws-foundational-security-best-practices/v/1.0.0'

aws securityhub get-findings --max-items 20 --filters '{
  "ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}],
  "SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],
  "RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}' \
  --query 'Findings[].[Compliance.SecurityControlId,Resources[0].Id,Title]' --output table

# Open-source equivalent: Prowler, with output you can archive as audit evidence
prowler aws --compliance cis_4.0_aws --output-formats json-ocsf html
```

```text
One attack path, ranked above 4,000 single findings

internet --> ALB (public) --> i-0abc (CVE-2026-XXXX, in CISA KEV, reachable)
                                 |
                                 +-- instance role: s3:GetObject on arn:aws:s3:::customer-exports/*
                                                         |
                                                         +-- bucket tagged data_classification=restricted

Fix order: patch or isolate i-0abc -> scope the role -> then the long tail of findings
```

## Interview tips

- Define the layers: CSPM reads cloud configuration via APIs; CNAPP combines it with workload, identity, Kubernetes, IaC, and data posture into one risk graph.
- Lead with **attack paths and toxic combinations** rather than finding counts - prioritising exposure plus exploitable vulnerability plus privileged identity plus sensitive data is the modern answer.
- Position it as **detective** and pair it with **preventive** controls (IaC scanning, admission policy, SCPs/Azure Policy); every recurring finding should become a guardrail.
- Mention agentless snapshot scanning and its trade-off against runtime agents: broad coverage and easy rollout versus no real-time detection.
- Be careful with auto-remediation and say which findings you would fix automatically and which you would route to an owner.
- Name native and open-source options (Security Hub, Defender for Cloud, Security Command Center, Prowler, Steampipe/Powerpipe) so the answer is not tied to one vendor. See [how do you automate compliance checks](./how-do-you-automate-compliance-checks-for-pci-dss-soc-2-hipaa-and-gdpr.md) and [what is the principle of least privilege](./what-is-the-principle-of-least-privilege-and-how-is-it-practically-enforced-in-cloud-iam.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you manage TLS certificates in production?]] (`#491`): [How do you manage TLS certificates in production?](../network-security/how-do-you-manage-tls-certificates-in-production.md)
- [[How Do You Design and Execute Threat Modeling for Cloud-Native Infrastructure?]] (`#713`): [How Do You Design and Execute Threat Modeling for Cloud-Native Infrastructure?](../secops/how-do-you-design-and-execute-threat-modeling-for-cloud-native-infrastructure.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
