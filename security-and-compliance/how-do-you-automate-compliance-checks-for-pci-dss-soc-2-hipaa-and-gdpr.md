---
title: "How do you automate compliance checks for PCI DSS, SOC 2, HIPAA, and GDPR?"
id: 434
category: "Security and Compliance"
difficulty: "Advanced"
tags:
  - devops
  - security-and-compliance
  - interview-questions
  - devsecops
  - cloud-engineering
  - infrastructure-as-code
---

# How do you automate compliance checks for PCI DSS, SOC 2, HIPAA, and GDPR?

**Short answer:** Translate each framework's requirements into **technical controls**, then enforce each control at the earliest point it can be enforced and **collect the evidence automatically**. Concretely: map requirements to a single internal control set (most controls satisfy several frameworks at once), enforce **preventively** in the pipeline and at admission (IaC scanning, policy as code, admission webhooks, SCPs and Azure Policy) so non-compliant infrastructure cannot be created, monitor **continuously** for drift and for what was created outside the pipeline (Config, Security Hub, Defender for Cloud, Security Command Center), and make the audit trail a by-product of how you work - version control, pull-request approvals, pipeline logs, and immutable audit logs. The framing that wins the interview: **compliance is not a scan you run before an audit; it is a property you enforce continuously, and the auditor's evidence is exported rather than assembled.**

## Detail

### Map once, satisfy many

The four frameworks overlap heavily, so build **one internal control set** and tag each control with the frameworks it serves. Encryption at rest satisfies PCI DSS requirement 3, HIPAA's technical safeguards, SOC 2's CC6, and GDPR Article 32 simultaneously. Where they genuinely differ:

| Framework   | What it actually demands beyond the common baseline                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **PCI DSS** | Scope discipline - segment the cardholder data environment so most systems are out of scope. Strict logging retention, quarterly scanning, and no storage of sensitive authentication data |
| **SOC 2**   | Controls operating **over an observation period** - evidence that the control worked for months, not that it works today                                                                   |
| **HIPAA**   | Business associate agreements, minimum-necessary access, audit controls over PHI access, and a documented risk analysis                                                                    |
| **GDPR**    | Lawful basis, data-subject rights (access, erasure, portability), data-residency and transfer rules, retention limits, and breach notification within 72 hours                             |

Two consequences worth stating: **SOC 2 needs history**, so evidence collection must be continuous rather than assembled the week before the audit; **GDPR is largely about data**, so it is answered with classification, retention, deletion, and residency automation rather than with infrastructure hardening alone.

### Enforce as early as possible

1. **In code review** - IaC scanning (Checkov, tfsec, Trivy) failing the pull request on an unencrypted volume, a public bucket, or an over-broad security group. Cheapest possible place to catch it. See [how do you scan Infrastructure as Code before it is applied](../devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md).
2. **In the pipeline** - dependency and image scanning, secret scanning, SBOM generation, and signed artefacts. Gate on severity and exploitability so the gate stays credible.
3. **At the cloud control plane** - AWS Service Control Policies, Azure Policy with `deny` effects, GCP Organization Policy: these make a violation **impossible**, not merely detected. "You cannot create an unencrypted disk in this organisation" is worth more than a hundred findings.
4. **At the Kubernetes admission layer** - Kyverno or Gatekeeper enforcing non-root, resource limits, allowed registries, and required labels. Run new policies in audit mode first, then enforce. See [how do you enforce Kubernetes admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md).
5. **Continuously, at runtime** - AWS Config rules and conformance packs, Security Hub standards (including the PCI DSS and CIS packs), Azure Defender for Cloud regulatory compliance, GCP Security Command Center, plus CIS benchmark scanning on hosts and images. This is what catches anything created outside the pipeline and anything that drifted.

Preventive controls are what change your posture; detective controls are what prove it and catch what prevention missed. Name both, and say which findings auto-remediate (tag a bucket, close a port, re-encrypt) versus which raise a ticket, because auto-remediation on the wrong control causes outages.

### Evidence is the deliverable, and it should be a by-product

An audit is a request for evidence, so design for export:

- **Change management**: every change is a pull request with a reviewer and a linked ticket, and the pipeline log shows what was applied where and when. That is your SOC 2 change-control evidence, already collected.
- **Access control**: identity from one provider with SSO and MFA, no long-lived credentials, joiner-mover-leaver automation, and periodic access reviews generated from the identity system rather than from a spreadsheet.
- **Audit logs**: CloudTrail / Azure Activity / Cloud Audit Logs to an append-only, retention-locked store in a separate account, plus Kubernetes audit logging. PCI DSS and HIPAA both want a specific retention period - configure it once and prove it with the bucket policy.
- **Control operation over time**: keep the scan and policy-evaluation results, not just the current state. Auditors ask "show me that this was true in March".
- **Data inventory and retention**: tag data stores with classification, automate lifecycle deletion, and keep a record of processing activities - which is the GDPR-specific piece people forget until an audit.

Compliance-as-code frameworks (Chef InSpec, Open Policy Agent bundles, AWS Audit Manager, Vanta/Drata-style tooling) are useful glue, but the substance is the control set and the enforcement points - the tool only collects and formats.

### The parts that are not technical

Say clearly that not all of it can be automated: risk assessments, vendor and business-associate agreements, incident-response and business-continuity plans with evidence they were **tested**, security training records, and a data-protection impact assessment for GDPR. Automation gets you the technical evidence continuously and cheaply; the policy and process evidence still needs owners and dates. A candidate who claims 100% automation is signalling inexperience.

### Scope reduction is the strongest control

The cheapest way to pass PCI DSS is to have less in scope: tokenise card data so your systems never store a primary account number, keep the cardholder data environment in a separate account or VPC with tightly controlled connectivity, and use a hosted payment page. The same logic applies to HIPAA (fewer systems touching PHI) and GDPR (collect less, keep it shorter). Mentioning scope reduction before controls is what distinguishes an engineer who has been through an audit from one who has read the standard. See [what is compliance as code](./what-is-compliance-as-code.md) and [what is policy as code](../advanced-devops-cloud/what-is-policy-as-code.md).

## Example

```text
One control, many frameworks - the mapping that stops duplicated work

  Control: all data stores encrypted at rest with customer-managed keys
    PCI DSS 3.5/3.6   HIPAA 164.312(a)(2)(iv)   SOC 2 CC6.1   GDPR Art.32
    prevent:  SCP denies creation of unencrypted RDS/EBS/S3      <- impossible, not audited
    prevent:  Checkov CKV_AWS_* fails the pull request
    detect:   AWS Config rule + Security Hub PCI pack, daily
    evidence: Config compliance history exported monthly to the evidence bucket

  Control: no direct human write access to production
    SOC 2 CC6.3 / CC8.1   PCI DSS 7   HIPAA 164.308(a)(4)
    prevent:  no standing IAM users; SSO + short-lived roles; GitOps only
    detect:   CloudTrail alert on any console write in prod account
    evidence: PR approvals + pipeline logs + quarterly access review export
```

```yaml
# Prevention at admission: audit first, then enforce (Kyverno)
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: pci-baseline
  annotations:
    policies.kyverno.io/description: "PCI DSS 2.2 / SOC 2 CC6.1 baseline for CDE namespaces"
spec:
  validationFailureAction: Audit # switch to Enforce after reviewing the audit report
  background: true
  rules:
    - name: images-from-approved-registry-only
      match:
        any:
          - resources: { kinds: [Pod], namespaces: ["cde-*"] }
      validate:
        message: "Images must come from the signed internal registry"
        pattern:
          spec:
            containers:
              - image: "registry.example.com/*"
    - name: require-non-root-and-limits
      match: { any: [{ resources: { kinds: [Pod], namespaces: ["cde-*"] } }] }
      validate:
        message: "Containers must run as non-root with resource limits set"
        pattern:
          spec:
            containers:
              - securityContext: { runAsNonRoot: true }
                resources: { limits: { memory: "?*", cpu: "?*" } }
```

```bash
# Detection and evidence, on a schedule - the artefacts an auditor asks for
aws configservice describe-compliance-by-config-rule \
  --query 'ComplianceByConfigRules[?Compliance.ComplianceType==`NON_COMPLIANT`].ConfigRuleName'

aws securityhub get-findings --filters '{
  "ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}],
  "RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}' \
  --query 'Findings[].[Compliance.SecurityControlId,Severity.Label,Resources[0].Id]' --output table

# Host and image baselines as testable code (InSpec / CIS)
inspec exec https://github.com/dev-sec/linux-baseline --reporter json:evidence/linux-$(date +%F).json
trivy image --scanners vuln,secret,misconfig --compliance docker-cis-1.6.0 registry.example.com/app:1.9.0

# Evidence retention that is itself a control
aws s3api put-object-lock-configuration --bucket acme-audit-evidence \
  --object-lock-configuration '{"ObjectLockEnabled":"Enabled",
    "Rule":{"DefaultRetention":{"Mode":"COMPLIANCE","Years":1}}}'
```

## Interview tips

- Open with the reframe: compliance is a continuously enforced property, and evidence is exported rather than assembled. That sentence answers the question behind the question.
- Map controls to frameworks rather than treating each framework as a project - and give an example (encryption at rest satisfying four at once). It shows you have done this rather than read a checklist.
- Distinguish **preventive** from **detective** clearly, and say that an SCP or Azure Policy denial is worth more than a dashboard of findings because it makes the violation impossible.
- Name the difference that matters per framework: SOC 2 needs the control to have operated over a period, so evidence collection must be continuous; GDPR is mostly about data - classification, retention, deletion, residency.
- Bring up scope reduction first for PCI DSS (tokenisation, a separate cardholder data environment, a hosted payment page). Auditors and interviewers both respect it, and it is what actually saves the money.
- Be careful about auto-remediation: say which controls you would auto-fix and which you would only ticket, because remediating the wrong thing automatically causes outages.
- Mention audit-mode-then-enforce for new policies. Rolling out an enforcing policy across a live estate without an audit pass is a self-inflicted outage.
- Be explicit that risk assessments, vendor agreements, tested incident-response plans, and training records are not automatable. Claiming full automation reads as inexperience. See [what are security best practices in DevOps](./what-are-security-best-practices-in-devops.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you manage TLS certificates in production?]] (`#491`): [How do you manage TLS certificates in production?](../network-security/how-do-you-manage-tls-certificates-in-production.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[What does a DevSecOps pipeline look like end to end?]] (`#161`): [What does a DevSecOps pipeline look like end to end?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
