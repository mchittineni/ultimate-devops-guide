---
title: "What is the Westrum organizational culture model and how does DORA use it?"
id: 785
category: "DevOps Culture and Practices"
difficulty: "Intermediate"
tags:
  - devops
  - devops-culture-and-practices
  - interview-questions
  - culture
  - westrum
  - dora
---

# What is the Westrum organizational culture model and how does DORA use it?

**Short answer:** Sociologist Ron Westrum classified organisations by how information flows through them: **pathological** (power-oriented), **bureaucratic** (rule-oriented), and **generative** (performance-oriented). DORA adopted the model because it can be measured with a short survey, and its research has repeatedly found that generative cultures are associated with better software delivery and organisational performance, and with less burnout.

## Detail

Westrum's insight (from safety-critical domains such as aviation and healthcare, published in 2004) is that how an organisation handles information - especially bad news - predicts how safely and effectively it performs.

| Aspect                | Pathological | Bureaucratic | Generative     |
| --------------------- | ------------ | ------------ | -------------- |
| Cooperation           | Low          | Modest       | High           |
| Messengers (bad news) | Shot         | Neglected    | Trained        |
| Responsibilities      | Shirked      | Narrow       | Shared risks   |
| Bridging across teams | Discouraged  | Tolerated    | Encouraged     |
| Failure leads to      | Scapegoating | Justice      | Inquiry        |
| Novelty leads to      | Crushing     | Problems     | Implementation |

**How DORA measures it.** Respondents rate agreement (on a 7-point scale) with statements such as "information is actively sought", "messengers are not punished when they deliver news of failures", "responsibilities are shared", "cross-functional collaboration is encouraged and rewarded", "failure causes inquiry", and "new ideas are welcomed". The average gives a team-level culture score that DORA correlates with delivery performance, well-being, and organisational outcomes.

**Why it matters for DevOps.** Every technical practice depends on information flowing: a canary is useless if nobody wants to report that it looks wrong, and a post-mortem is theatre if the author fears consequences. Generative culture is the environment in which blameless reviews, psychological safety, and fast feedback loops can actually exist.

**Changing it.** Westrum's own observation is that culture follows practice: change how people work (shared on-call, blameless reviews, cross-team incident channels) and attitudes follow. Leaders shape it most through how they react to the first piece of bad news.

**Limitations.** It is a three-bucket typology of a continuum, the data is self-reported, and teams within one company can sit in different columns. Use the survey for a team's own trend, never as a ranking.

## Example

A short pulse survey using DORA-style Westrum items, scored per team:

```yaml
survey: westrum-culture
scale: 1-7   # strongly disagree .. strongly agree
items:
  - "On my team, information is actively sought."
  - "On my team, messengers are not punished when they deliver bad news."
  - "On my team, responsibilities are shared."
  - "On my team, cross-functional collaboration is encouraged and rewarded."
  - "On my team, failure causes inquiry."
  - "On my team, new ideas are welcomed."
reporting: team averages and trend only; minimum 5 respondents per team
```

## Interview tips

- Name all three types and the key distinguishing behaviour: what happens to the messenger.
- Connect it to DORA explicitly - interviewers use it to test whether you know the culture side of the research, not just the four metrics.
- Link it to blameless post-mortems and psychological safety as the practices that move a team towards generative.
- Acknowledge the limits: survey-based, correlational, and team-level rather than company-wide.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
