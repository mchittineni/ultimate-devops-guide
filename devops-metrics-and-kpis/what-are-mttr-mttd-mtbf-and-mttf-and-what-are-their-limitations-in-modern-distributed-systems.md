---
title: "What are MTTR, MTTD, MTBF, and MTTF and what are their limitations in modern distributed systems?"
id: 652
category: "DevOps Metrics and KPIs"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devops-metrics-and-kpis
  - metrics
  - mttr
  - mttd
  - reliability
  - sre
quiz:
  stem: "Why does modern cloud Site Reliability Engineering prioritize reducing MTTR (Mean Time to Recover) over increasing MTBF (Mean Time Between Failures)?"
  options:
    - "Cloud hardware is completely immune to physical failures"
    - "In massive distributed systems, component failures are continuous and inevitable; designing for fast automated recovery (low MTTR) is more effective than attempting to prevent all failures"
    - "MTTR can be calculated without monitoring software"
    - "MTBF can only be measured on Windows machines"
  answer: 2
  explanation: "In large distributed systems, disks fail, nodes reboot, and networks glitch continuously. Designing systems for rapid detection and automated recovery (low MTTR) delivers higher availability than trying to prevent all failures."
---

# What are MTTR, MTTD, MTBF, and MTTF and what are their limitations in modern distributed systems?

**Short answer:** MTTD is Mean Time to Detect; MTTR is Mean Time to Recover/Restore; MTBF is Mean Time Between Failures; MTTF is Mean Time to Failure; in distributed systems, MTBF and MTTF lose most of their meaning because a large fleet is in a continuous state of partial failure, so engineering attention shifts to detecting and recovering quickly (MTTD, MTTR) and to user-facing SLOs.

## Detail

Hardware reliability metrics developed for physical lightbulbs or single servers do not map cleanly to cloud-native microservices:

### Metric Definitions

- **MTTD (Detect)**: Time elapsed from the root-cause trigger of an incident until an alert or human recognizes the issue.
- **MTTR (Recover / Restore)**: Time elapsed from detection (or incident start) until service is mitigated and healthy for customers.
- **MTBF (Between Failures)**: Average operational time between failures of a _repairable_ component or system (roughly MTTF + MTTR).
- **MTTF (To Failure)**: Average time until a _non-repairable_ component fails and is replaced (a disk, a power supply, a lightbulb). Hardware vendors quote it; it describes a population, not when your particular disk will die.

Note that "MTTR" itself is ambiguous - recover, restore, repair, respond, resolve - so always state which start and end events you measure. DORA narrowed its version to _failed deployment recovery time_ (recovery after a bad change) in 2023.

### The Demise of MTBF in Microservices

In a system running 5,000 container pods across 200 nodes, hardware faults, network packet drops, and pod crashes happen every single minute. The system is **always partially broken**.

- Striving for high MTBF (hoping nothing fails) at fleet level is a fool's errand; component MTTF still matters for capacity and spares planning.
- SRE focuses on **minimizing MTTD (fast observability)** and **minimizing MTTR (automated rollbacks, canaries, feature flags)** so that failures are detected and mitigated before users notice.

### Limitations of the Means Themselves

- **Means hide the distribution.** Incident durations are heavily skewed; one 12-hour outage dominates a quarter of 5-minute ones. Report median and p90 and segment by severity.
- **Small samples.** A team with six incidents a quarter cannot tell a real improvement from noise - which is why some SRE practitioners argue against using MTTR as a target at all and prefer SLO attainment, error budget burn, and qualitative incident review.
- **Incidents are not comparable units.** A partial degradation for 1% of users and a full outage both count as "one incident"; customer-impact minutes weight them properly.

## Example

The per-incident intervals behind each acronym, computed from incident timestamps and reported as medians:

```sql
SELECT severity,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY detected_at - started_at)      AS median_ttd,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY acknowledged_at - detected_at) AS median_tta,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY mitigated_at - started_at)     AS median_ttr,
       count(*)                                                                   AS incidents
  FROM incidents
 WHERE started_at >= now() - interval '180 days'
 GROUP BY severity;
```

## Interview tips

- Definitions: MTTD (detection), MTTR (recovery), MTBF (between failures).
- MTBF is outdated in distributed systems because systems are always in partial degradation.
- Focusing engineering effort on shrinking MTTD and MTTR.
- Mitigation (stopping user impact) vs full root-cause resolution.
- Define MTTF (non-repairable) versus MTBF (repairable) - candidates often skip MTTF even though it is in the question.
- Say you report medians and distributions, not means, and that small incident counts make the trend noisy.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?]] (`#536`): [How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?](../cicd/how-do-you-detect-isolate-and-eradicate-flaky-tests-in-a-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
