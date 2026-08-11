---
title: "What is a cloud landing zone?"
id: 215
category: "Cloud Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-engineering
  - interview-questions
---

# What is a cloud landing zone?

**Short answer:** A landing zone is the pre-built, governed foundation that workloads land in: account or project structure, identity and access, network topology, logging and security baselines, guardrail policies, and cost controls - all provisioned as code. Its purpose is that the tenth team to arrive gets the same compliant starting point as the first, without asking anyone.

## Detail

**The components, provider-independent:**

| Area          | What the landing zone provides                                              |
| ------------- | --------------------------------------------------------------------------- |
| Tenancy       | account/subscription/project structure with an OU or folder hierarchy       |
| Identity      | SSO federation, group-based roles, break-glass accounts, no long-lived keys |
| Network       | hub-and-spoke or shared network, address plan, egress and inspection        |
| Guardrails    | SCPs / Azure Policy / org policy constraints, applied by default            |
| Observability | centralised, tamper-resistant audit logs and metrics                        |
| Security      | posture management, threat detection, KMS key hierarchy                     |
| Cost          | tagging/labelling standard, budgets, anomaly alerts, showback               |
| Provisioning  | an automated request path that creates and baselines a new environment      |

**Vendor accelerators exist and are usually worth starting from:** AWS Control Tower with Account Factory, Azure Landing Zones from the Cloud Adoption Framework, and Google's Cloud Foundation Toolkit. They encode a decade of others' mistakes; the work is adapting them to your compliance and network realities, not rebuilding them.

**The vending machine is the part teams undervalue.** A landing zone that requires a ticket and a human to create an account has not solved the problem. The valuable artefact is a self-service pipeline: request an environment, get an account/project with identity, network, logging, budgets, policies, and a catalogue entry attached, in minutes and fully audited.

**Guardrails must be preventive, not just detective.** Detective controls tell you afterwards that someone created a public database; preventive controls (deny policies at the organisation level) stop it. A good landing zone uses both - preventive for the small set of rules you are certain about, detective for the long tail.

**Day two is where landing zones fail.** Policies drift, accounts are created outside the factory, exceptions accumulate, and the accelerator's own version falls behind. Treat the landing zone as a product with a version, a changelog, a rollout process for policy changes (audit first, then enforce), and periodic reconciliation that finds unbaselined accounts.

**Do not gold-plate it.** For a small team, a landing zone can be three accounts, SSO, a logging account, and five guardrails. The full enterprise pattern costs months of platform time and is only justified when you have many teams, real compliance obligations, or both. Right-sizing this is a strong signal in interviews.

## Example

```text
Minimum viable landing zone - deliberately small, still governed

Tenancy      management + security/log-archive + shared-services + per-workload envs
Identity     IdP SSO -> groups -> roles; break-glass account with MFA in a safe
Guardrails   deny leaving org · deny disabling audit logs · approved regions only
             · deny public object storage · deny long-lived access keys
Logging      org-wide audit trail -> log-archive account, write-once, no workload access
Network      one hub with egress inspection; /16 per environment from a planned range
Cost         mandatory owner + cost-centre tags (enforced) · budget alert per account
Provisioning Terraform pipeline: create -> baseline -> register in catalogue

Expand only when a real requirement appears. Every guardrail must have an owner.
```

## Interview tips

- Define it as "the governed foundation, provisioned as code, that every workload lands in" and then list the areas.
- The self-service vending machine and preventive-versus-detective distinction are the strongest points to make.
- Expect: "how big should it be?" - right-size it; describing the enterprise version for a five-person team is the trap.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Engineering](./README.md) · [All topics](../README.md)
