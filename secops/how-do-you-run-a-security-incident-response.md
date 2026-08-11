---
title: "How do you run a security incident response?"
id: 174
category: "SecOps and Threat Detection"
difficulty: "Intermediate"
tags:
  - devops
  - secops
  - interview-questions
---

# How do you run a security incident response?

**Short answer:** Follow the NIST 800-61 cycle - preparation, detection and analysis, containment, eradication, recovery, and post-incident learning - with an incident commander, a written timeline, and preserved evidence. The differences from an availability incident are that the adversary reacts to your actions, evidence must survive containment, and legal, communications, and regulatory clocks are in scope from the start.

## Detail

**Roles.** An incident commander who decides and does not investigate; a lead investigator; a scribe keeping the timeline; a communications lead handling internal and customer messaging; plus legal/privacy counsel on standby for anything touching personal data. Small organisations combine roles, but the commander must not also be the person running `kubectl`.

**Contain before you eradicate, and preserve while you contain.** Snapshot the disk and capture memory before terminating an instance; export logs to an account the attacker cannot reach; revoke sessions and rotate credentials rather than only disabling one key. Terminating the compromised host first destroys the evidence needed to establish scope - and if you close the initial access path without understanding it, the intruder returns.

**Scoping is the hard part.** From one confirmed compromise, work outward: what else did that identity touch, which credentials were reachable from that host, which other resources share the same trust boundary? Cloud audit logs and identity provider logs carry most of this. Assume any credential present on a compromised host is compromised.

**Regulatory clocks start early.** GDPR requires notifying the supervisory authority within 72 hours of becoming aware of a qualifying personal-data breach; sector rules (financial services, healthcare, critical infrastructure) impose their own, sometimes shorter, windows. Whether the clock has started is a legal determination - engineering's job is to establish facts and timestamps precisely.

**Recovery means rebuilding, not cleaning.** Restore from a known-good image or a backup predating compromise, rotate every credential in the blast radius, and monitor specifically for the attacker's observed behaviour for weeks afterwards. Cleaning a host you do not fully understand leaves persistence behind.

**Learning.** Blameless review, as with any incident, but with security-specific outputs: which detection should have fired, which control would have prevented the initial access, what shortened or lengthened containment, and a small number of tracked, owned actions.

## Example

```text
Timeline discipline - every entry timestamped in UTC, source noted

2026-03-14T02:11Z  DETECT   Alert: IAM user ci-deploy created access key (CloudTrail)
2026-03-14T02:26Z  TRIAGE   Confirmed unexpected; commander appointed; war room opened
2026-03-14T02:34Z  PRESERVE CloudTrail + VPC flow logs exported to forensics account
2026-03-14T02:41Z  CONTAIN  Attacker key deactivated; ci-deploy sessions revoked
2026-03-14T03:15Z  SCOPE    Key had s3:GetObject on 3 buckets; 1 GetObject burst found
2026-03-14T05:02Z  ERADICATE Leaked token rotated at source (exposed in fork PR log)
2026-03-14T06:30Z  RECOVER  New scoped role issued; OIDC federation replaces static key
2026-03-17         LEARN    Review: detection existed, paging threshold was wrong
```

## Interview tips

- Say "preserve evidence before containment" - it is the discipline that separates security response from an outage runbook.
- Mention the 72-hour GDPR notification window and that the legal determination is not engineering's call.
- Expect: "the attacker still has access, do you cut them off now?" - a judgement call between stopping damage and losing visibility, made by the commander with legal input, not unilaterally.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
