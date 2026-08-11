---
title: "What is a SIEM and how do you make one useful?"
id: 170
category: "SecOps and Threat Detection"
difficulty: "Intermediate"
tags:
  - devops
  - secops
  - interview-questions
---

# What is a SIEM and how do you make one useful?

**Short answer:** A SIEM centralises security-relevant logs, normalises them to a common schema, correlates events across sources, and raises detections. It becomes useful only when three things are true: the right sources are onboarded, fields are normalised so a rule works across them, and detections are version-controlled and tuned rather than accumulated.

## Detail

**Normalisation is the whole game.** An AWS CloudTrail event, an Entra ID sign-in, and an SSH log all describe "an identity did something from an IP", but they name those fields differently. Mapping onto a schema - the Elastic Common Schema, or OCSF - means one rule for "impossible travel" instead of one per source. Skip this and every detection becomes source-specific and unmaintainable.

**Source priority when you have limited ingest budget:**

1. Identity provider (sign-ins, MFA failures, consent grants)
2. Cloud control plane (CloudTrail, Azure Activity, GCP Audit Logs)
3. Endpoint/EDR telemetry
4. Kubernetes API audit logs, and container runtime events
5. Network flow logs and DNS
6. Application logs for business-critical flows (payments, admin actions)

**Cost drives architecture.** SIEM pricing is broadly per GB ingested or per compute unit, so teams route high-volume, low-signal data (flow logs, CDN logs) to cheap object storage with a query engine over it, and keep hot, correlated data in the SIEM. That tiering must be deliberate - analysts need to know what is searchable in seconds versus minutes.

**Detection-as-code.** Rules live in Git, written in a portable format (Sigma) or the platform's own language, reviewed like code, and tested against recorded attack telemetry before merge. Each rule carries metadata: ATT&CK technique, severity, owner, false-positive notes, and a linked response playbook. A rule with no playbook produces an alert no one knows how to handle.

**Retention has two drivers:** the compliance minimum (often 12 months) and the investigation window - since intrusions are frequently discovered months later, searchable history shorter than 90 days routinely makes scoping impossible.

## Example

```yaml
# A portable Sigma rule: cloud audit log shows public exposure of a bucket
title: S3 bucket ACL made public
id: 4f2c8b1e-2c1a-4d55-9f2e-2b8a1d3c9f01
status: stable
logsource:
  product: aws
  service: cloudtrail
detection:
  selection:
    eventSource: s3.amazonaws.com
    eventName:
      - PutBucketAcl
      - PutBucketPolicy
    requestParameters|contains: "AllUsers"
  condition: selection
falsepositives:
  - Static website buckets in the public-web account
level: high
tags:
  - attack.exfiltration
  - attack.t1530
```

## Interview tips

- Lead with normalisation and source prioritisation; "it aggregates logs" is a dictionary answer.
- Detection-as-code with ATT&CK tagging and a linked playbook is the practice-level detail interviewers reward.
- Expect a cost question: explain hot/cold tiering and which sources you would route where.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
