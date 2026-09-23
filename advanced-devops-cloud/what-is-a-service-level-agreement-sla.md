---
title: "What is a Service Level Agreement (SLA)?"
id: 148
category: "Advanced DevOps & Cloud"
difficulty: "Beginner"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is a Service Level Agreement (SLA)?

**Short answer:** An SLA is a contractual commitment to a customer about service performance - typically availability - with defined measurement, exclusions, and financial remedies such as service credits when it is missed.

## Detail

**What an SLA contains**

- **The commitment** - for example, 99.9% monthly uptime.
- **How it is measured** - the exact definition of "unavailable", the measurement interval, and whose telemetry counts. This section determines whether the number means anything.
- **Exclusions** - scheduled maintenance windows, customer-caused issues, force majeure, and third-party failures outside the provider's control.
- **Remedies** - service credits, usually a percentage of the monthly fee, scaled by how badly the target was missed.
- **Claim process** - how and within what window the customer must claim; credits are almost never automatic.
- **Support commitments** - response times by ticket severity, which are often more operationally relevant than the uptime figure.

**SLA vs SLO vs SLI**

|     | Audience | Nature        | Consequence         |
| --- | -------- | ------------- | ------------------- |
| SLI | Internal | A measurement | None directly       |
| SLO | Internal | A target      | Error budget policy |
| SLA | External | A contract    | Financial penalty   |

**The critical practice:** set the internal SLO tighter than the external SLA. If you promise customers 99.9%, target 99.95% internally, so the error budget is exhausted - and reliability work triggered - well before you owe anyone money.

**Read the exclusions carefully.** A "99.99%" SLA that excludes maintenance windows, measures monthly, and requires the customer to file a claim within 30 days provides much less protection than the headline suggests. The same applies when _you_ are the customer evaluating a cloud provider.

## Example

```text
Illustrative SLA service-credit schedule (monthly uptime, measured by the provider)

  Monthly uptime            Service credit
  < 99.9%  and >= 99.0%     10% of the monthly fee
  < 99.0%  and >= 95.0%     25%
  < 95.0%                   100%

  Exclusions: scheduled maintenance announced 5+ days ahead, customer-caused
  failures, force majeure. Credits must be claimed within 30 days.

Internal targets that sit behind it
  SLA 99.9%  ->  SLO 99.95% (rolling 28 days)  ->  SLI: good / valid requests at the LB
  99.9% of 30 days = 43 min of allowed downtime; 99.95% = 21.6 min
```

## Interview tips

- "SLO tighter than SLA" is the practical relationship interviewers want stated.
- Note that service credits rarely compensate the actual business loss - SLAs are not insurance.
- The measurement definition and exclusions matter more than the percentage; saying so shows commercial awareness.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
