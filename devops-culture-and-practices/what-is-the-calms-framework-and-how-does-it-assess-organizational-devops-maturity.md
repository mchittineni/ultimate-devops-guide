---
title: "What is the CALMS framework and how does it assess organizational DevOps maturity?"
id: 681
category: "DevOps Culture and Practices"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - devops-culture-and-practices
  - culture
  - calms
  - devops-maturity
  - leadership
quiz:
  stem: "What does the 'L' in the CALMS DevOps framework represent?"
  options:
    - "Logging"
    - "Lean (minimizing work-in-progress, small batches, and eliminating waste)"
    - "Licensing"
    - "Linux"
  answer: 2
  explanation: "The 'L' stands for Lean, derived from Lean manufacturing principles focusing on small batch sizes, minimizing WIP, and eliminating process waste."
---

# What is the CALMS framework and how does it assess organizational DevOps maturity?

**Short answer:** CALMS is a holistic lens covering Culture, Automation, Lean, Measurement, and Sharing - John Willis and Damon Edwards coined CAMS in 2010 and Jez Humble added Lean - asserting that DevOps success requires transforming organization and culture, not just adopting CI/CD tools.

## Detail

Many companies buy Kubernetes and GitLab, declare themselves 'DevOps', and fail because silos, fear, and bureaucracy remain unchanged.

### The Five Pillars of CALMS

1. **Culture**: Blameless communication, psychological safety, shared responsibility between Dev and Ops, embracing failure as a learning opportunity.
2. **Automation**: Replacing repetitive manual toil with automated pipelines (CI/CD, IaC, automated testing, chatops).
3. **Lean**: Applying lean manufacturing principles—minimizing work-in-progress (WIP), shrinking batch sizes, eliminating waste, and shortening feedback loops.
4. **Measurement**: Telemetry-driven decisions using DORA metrics, SLOs, user experience metrics, and business KPIs.
5. **Sharing**: Transparent cross-team collaboration, inner-sourcing, sharing post-mortems globally, and eliminating siloed knowledge hoarding.

### Using CALMS as a Maturity Assessment

CALMS is not a formal, scored maturity model - there is no official questionnaire. Teams use it as a structured self-assessment: rate each pillar with evidence (for example "Measurement: we track DORA metrics per service" rather than "we value data"), find the weakest pillar, and pick one improvement. The limitation is that self-ratings drift towards optimism and compliance theatre, so anchor each score to observable outcomes such as DORA metrics or survey results, and compare trends rather than scores between teams.

## Example

A lightweight CALMS self-assessment, where every score needs evidence:

```yaml
team: payments
assessed: 2026-09
pillars:
  culture:     { score: 3, evidence: "blameless reviews published; on-call shared with devs" }
  automation:  { score: 4, evidence: "CI/CD to prod, IaC for all envs; DB migrations still manual" }
  lean:        { score: 2, evidence: "WIP unlimited; median PR open 2.5 days" }
  measurement: { score: 3, evidence: "DORA metrics per service; no SLOs for batch jobs" }
  sharing:     { score: 2, evidence: "runbooks exist but not linked from alerts" }
next_improvement: "Lean - WIP limit of 3 per engineer, PR review SLA of 1 working day"
```

## Interview tips

- DevOps is a cultural transformation, not a software tool or job title.
- Correct attribution: CAMS from John Willis and Damon Edwards, with Jez Humble adding Lean.
- Using it as an evidence-based self-assessment rather than a scored certification.
- Listing the five CALMS pillars: Culture, Automation, Lean, Measurement, Sharing.
- Lean principles: reducing WIP and batch sizes.
- Sharing knowledge transparently across organizational silos.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
