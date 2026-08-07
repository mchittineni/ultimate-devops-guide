---
title: "What is the difference between an SLA, an SLO, an SLI, and an OLA?"
id: 184
category: "SLA Management"
difficulty: "Beginner"
tags:
  - devops
  - sla-management
  - interview-questions
---

# What is the difference between an SLA, an SLO, an SLI, and an OLA?

**Short answer:** An SLI is the measurement, an SLO is the internal target for that measurement, an SLA is the external contract with a consequence attached, and an OLA is the internal agreement between teams that makes the SLA achievable. The SLO is always stricter than the SLA, so you have room to react before money is at stake.

## Detail

| Term | Audience             | Contains                                            | Consequence of breach               |
| ---- | -------------------- | --------------------------------------------------- | ----------------------------------- |
| SLI  | engineering          | a metric definition and vantage point               | none - it is just a number          |
| SLO  | engineering, product | target + window + error budget                      | error budget policy actions         |
| SLA  | customer, legal      | promise + measurement method + credits + exclusions | service credits, termination rights |
| OLA  | internal teams       | what a supporting team owes                         | escalation, internal remediation    |

**The buffer between SLO and SLA is deliberate.** If you promise 99.9% contractually, target 99.95% internally. The gap is your warning zone: exhausting the internal budget triggers engineering action long before you owe a customer anything. Setting them equal means the first sign of trouble is a credit claim.

**An SLA is a legal artefact.** It specifies not just the number but how it is measured (whose clock, which vantage point, what sampling interval), what is excluded (announced maintenance, force majeure, customer misconfiguration, beta features), how a claim is filed, and the deadline for filing it. Engineering's obligation is to be able to produce the evidence the contract demands.

**OLAs are what make SLAs real.** A 99.95% customer promise depends on the platform team's cluster availability, the data team's pipeline freshness, and the vendor's uptime. Each supporting commitment should be written down; otherwise the customer-facing team has made a promise nobody upstream has agreed to.

**Not everything needs an SLA.** Internal services usually have SLOs only. Adding contractual language internally creates adversarial behaviour without improving reliability - the useful internal artefacts are the SLO and the error budget policy.

## Example

```text
Checkout service, layered

SLI  successful (non-5xx) requests / total requests, measured at the edge, 1-min samples
SLO  99.95% over a rolling 30 days   → budget 21.6 min   (internal target)
SLA  99.9% per calendar month        → budget 43.2 min   (customer contract)
     credits: 10% below 99.9%, 25% below 99.5%, 100% below 99.0%
     exclusions: announced maintenance (max 4 h/month, 7 days' notice)
OLA  platform team: 99.99% Kubernetes API and node capacity
     payments vendor: 99.95% authorisation API (their SLA, our dependency)
```

## Interview tips

- Lead with "SLA has a consequence, SLO does not" - that is the distinction being tested.
- Volunteer the SLO-stricter-than-SLA buffer; few candidates mention it and it demonstrates real practice.
- Expect: "should internal services have SLAs?" - no, SLOs plus an error budget policy; explain why contracts internally backfire.

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
