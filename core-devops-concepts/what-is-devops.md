---
title: "What is DevOps?"
id: 1
category: "Core DevOps Concepts"
difficulty: "Beginner"
tags:
  - devops
  - core-devops-concepts
  - interview-questions
---

# What is DevOps?

**Short answer:** DevOps is a set of cultural practices, working agreements, and automation that shortens the time between committing a change and running it safely in production, while keeping the system reliable.

## Detail

DevOps emerged as a response to the "wall of confusion" between development teams rewarded for shipping change and operations teams rewarded for stability. Instead of two organisations with opposing incentives, DevOps puts one team behind a shared outcome: working software in the hands of users.

Three things make it real in practice:

- **Culture** - shared ownership of production. The team that builds a service also runs it, carries the pager for it, and feels the cost of its defects.
- **Automation** - the path to production is code: builds, tests, infrastructure provisioning, deployment, and rollback all run without a human typing commands.
- **Measurement and feedback** - telemetry from production flows back into planning. Deployment frequency, lead time, change failure rate, and time to restore are tracked and acted on.

DevOps is not a job title, a tool, or a team you can buy. A "DevOps team" that sits between dev and ops has usually just rebuilt the wall one office further along.

## Example

A concrete before/after for a single change:

|                   | Before                              | With DevOps                       |
| ----------------- | ----------------------------------- | --------------------------------- |
| Path to prod      | Ticket to ops, manual deploy window | Merge to `main` triggers pipeline |
| Frequency         | Monthly release                     | Multiple times per day            |
| Failure response  | Escalation chain, hours             | Automated rollback, minutes       |
| Environment setup | Hand-built, drifts                  | Terraform, reproducible           |

## Interview tips

- Define it without naming a single tool first, then mention tools as implementation detail.
- Anchor the answer in the four DORA metrics - it shows you think in outcomes.
- Have one story ready about a cultural change you made, not just a pipeline you built.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#20`): [What is the difference between Continuous Delivery and Continuous Deployment?](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
