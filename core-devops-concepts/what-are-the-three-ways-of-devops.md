---
title: "What are the Three Ways of DevOps?"
id: 783
category: "Core DevOps Concepts"
difficulty: "Beginner"
tags:
  - devops
  - core-devops-concepts
  - interview-questions
  - three-ways
  - lean
---

# What are the Three Ways of DevOps?

**Short answer:** The Three Ways, popularised by Gene Kim in _The Phoenix Project_ (2013) and _The DevOps Handbook_ (2016), are the principles every DevOps practice derives from: **flow** (make work move fast from development to production), **feedback** (make problems visible quickly, from production back to development), and **continual learning and experimentation** (build a culture that improves the system and takes safe risks).

## Detail

**The First Way - flow (left to right).** Optimise the whole value stream, not individual silos. The mechanisms are Lean ones: make work visible, limit work in progress, reduce batch size, cut hand-offs, and remove constraints one at a time (theory of constraints). In engineering terms: trunk-based development, CI, deployment automation, environments on demand, and a loosely coupled architecture so teams can release independently. The anti-pattern is local optimisation - a dev team that ships faster into a QA queue that has not changed.

**The Second Way - feedback (right to left).** Create fast, amplified feedback at every stage so problems are found and fixed where they start. Automated tests on every commit, telemetry and alerting on user-visible symptoms, peer review instead of distant approval boards, developers on call for their own services, and "swarming" a problem rather than working around it (the Andon cord idea from the Toyota Production System).

**The Third Way - continual learning and experimentation.** A generative, high-trust culture where failures lead to inquiry rather than blame, where improvement work gets reserved capacity, and where local discoveries become global knowledge (shared post-mortems, shared libraries, paved roads). It also means deliberately injecting stress to build resilience - game days and chaos engineering.

**How they relate to other frameworks.** CALMS describes the same territory as pillars (Culture, Automation, Lean, Measurement, Sharing); DORA's capabilities are the research-backed, measurable version - most DORA capabilities map cleanly onto one of the Three Ways.

**Limitation.** The Three Ways are principles, not a method: they tell you what good looks like, not which change to make first. Pair them with measurement (DORA metrics, value stream mapping) to pick the bottleneck.

## Example

Mapping each Way to concrete practices and the signal that it is working:

```text
Way          Practices                                          Signal it is working
Flow         small PRs, trunk-based dev, CD, WIP limits         lead time and batch size falling
Feedback     CI on every commit, SLO alerts, you-build-it-run-it  defects found pre-merge; fast detection
Learning     blameless reviews, 20% improvement capacity,       actions change systems; near misses
             game days, shared post-mortems                      reported voluntarily
```

## Interview tips

- Name all three in order with their direction: flow left-to-right, feedback right-to-left, learning as the culture that sustains both.
- Give one concrete practice per Way - an answer that stays at the principle level sounds memorised.
- Attribute correctly: Gene Kim, _The Phoenix Project_ and _The DevOps Handbook_ (with Jez Humble, Patrick Debois, John Willis, and Nicole Forsgren on the 2nd edition).
- Follow-up to expect: "which Way does your current team struggle with most?" - have an honest answer and the bottleneck you would attack.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#20`): [What is the difference between Continuous Delivery and Continuous Deployment?](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
