---
title: "What are SOC 2, ISO 27001, and HIPAA compliance frameworks and how is Compliance as Code implemented?"
id: 568
category: "Security and Compliance"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - security
  - compliance
  - soc2
  - policy-as-code
quiz:
  stem: "How does Compliance as Code fundamentally improve an organization's audit readiness compared to traditional annual audits?"
  options:
    - "It exempts companies from hiring accredited third-party auditing firms"
    - "It continuously verifies security and regulatory controls in real-time pipelines rather than relying on point-in-time annual manual checks"
    - "It eliminates all data retention requirements under GDPR"
    - "It automatically encrypts all code repositories"
  answer: 2
  explanation: "Compliance as Code turns static compliance rules into continuous automated tests in CI/CD and runtime, preventing drift and ensuring continuous compliance."
---

# What are SOC 2, ISO 27001, and HIPAA compliance frameworks and how is Compliance as Code implemented?

**Short answer:** SOC 2 is an attestation report against the AICPA Trust Services Criteria, ISO/IEC 27001 is a certifiable standard for an information security management system, and HIPAA is US law governing protected health information. Compliance as Code turns the technical controls they require into policies that run automatically - OPA/Conftest in pipelines, admission control in clusters, AWS Config or Steampipe/Powerpipe against live resources - producing continuous evidence instead of an annual screenshot exercise. Policies and people processes (risk assessments, training, vendor contracts) still need manual evidence.

## Detail

Traditional compliance involved taking screenshots once a year for external auditors, leaving infrastructure vulnerable to drift for the remaining 364 days.

### Framework Summary

- **SOC 2 (Trust Services Criteria)**: Security (always in scope), plus optional Availability, Processing Integrity, Confidentiality, and Privacy. A licensed CPA firm issues the report; **Type I** tests control design at a point in time, **Type II** tests operating effectiveness over an observation period (typically 3-12 months). Common for B2B SaaS.
- **ISO/IEC 27001:2022**: Globally recognized, certifiable Information Security Management System (ISMS) standard. The 2022 revision restructured Annex A into 93 controls in four themes (organisational, people, physical, technological) and added controls such as threat intelligence, cloud services security, and secure coding; the transition period for 2013-based certificates ended in October 2025.
- **HIPAA**: US law regulating Protected Health Information (PHI). The Security Rule sets administrative, physical, and technical safeguards for electronic PHI; covered entities and their business associates (including cloud providers, under a BAA) are in scope. There is no official HIPAA certification - you demonstrate compliance through risk analysis and evidence.

### Implementing Compliance as Code

1. **Policy Enforcement in CI/CD**: Block non-compliant infrastructure code in PRs using OPA/Conftest:

   ```rego
   # Deny unencrypted RDS instances in a Terraform plan (OPA 1.x / Rego v1 syntax)
   package main

   deny contains msg if {
     resource := input.resource_changes[_]
     resource.type == "aws_db_instance"
     not resource.change.after.storage_encrypted
     msg := sprintf("RDS instance %v must set storage_encrypted = true", [resource.address])
   }
   ```

2. **Continuous Runtime Auditing**: Tools like AWS Config conformance packs, GCP Security Command Center, or Steampipe with Powerpipe compliance benchmarks continuously evaluate live resources and alert if an unapproved public IP or unencrypted disk appears.
3. **Evidence Collection**: Store every evaluation result with a timestamp, mapped to control IDs (SOC 2 CC6.1, ISO 27001 Annex A 8.24, HIPAA 164.312(a)(2)(iv)), so a Type II auditor can sample any point in the observation period.

## Example

```bash
# Pipeline gate: evaluate the Terraform plan against the policy above
terraform plan -out=tf.plan && terraform show -json tf.plan > tf.json
conftest test tf.json --policy policy/

# Runtime evidence: run a compliance benchmark against the live AWS account (Powerpipe + Steampipe)
powerpipe benchmark run aws_compliance.benchmark.soc_2 --export=soc2-$(date +%F).json
```

## Interview tips

- Distinguish the three precisely: SOC 2 is an **attestation report** (Type I design, Type II operating effectiveness over a period) against the Trust Services Criteria; ISO 27001 is a **certification** of an ISMS, with Annex A controls selected via a Statement of Applicability; HIPAA is a **law**, with no official certification.
- Say that frameworks overlap heavily, so you map one internal control set to all of them and collect evidence once.
- Compliance as code covers the technical controls - encryption, access, logging, change management - and makes Type II evidence continuous. Risk assessments, policies, training, and vendor management still need owners and manual evidence.
- Use current references: ISO/IEC 27001:2022 (93 Annex A controls), and write policies in Rego v1 syntax now that OPA 1.x is the default in Conftest and Gatekeeper.
- Trade-off: automated checks prove configuration, not intent - an auditor will still sample tickets, approvals, and access reviews, so design processes to leave that trail.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Policy as Code and how do OPA Gatekeeper and Kyverno enforce cluster governance?]] (`#707`): [What is Policy as Code and how do OPA Gatekeeper and Kyverno enforce cluster governance?](../devsecops/what-is-policy-as-code-and-how-do-opa-gatekeeper-and-kyverno-enforce-cluster-governance.md)
- [[What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?]] (`#710`): [What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?](../devsecops/what-are-threat-modeling-frameworks-stride-pasta-and-how-do-they-embed-security-into-early-sprint-design.md)
- [[What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?]] (`#709`): [What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?](../devsecops/what-is-dast-dynamic-application-security-testing-and-how-is-owasp-zap-integrated-into-ci-cd-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
