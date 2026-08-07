---
title: "What is the difference between Continuous Delivery and Continuous Deployment?"
id: 20
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
---

# What is the difference between Continuous Delivery and Continuous Deployment?

**Short answer:** Both keep every change production-ready through an automated pipeline. Continuous delivery stops at a manual approval before production; continuous deployment releases automatically with no human gate.

## Detail

|                        | Continuous Delivery                   | Continuous Deployment                |
| ---------------------- | ------------------------------------- | ------------------------------------ |
| Path to production     | Automated up to a manual approval     | Fully automated                      |
| Who decides to release | A human (product, release manager)    | The pipeline's test results          |
| Typical cadence        | On demand - daily, weekly, per sprint | Every merged commit                  |
| Test requirement       | Strong                                | Comprehensive and trusted absolutely |
| Risk control           | Human judgement plus automation       | Canary, feature flags, auto-rollback |
| Common fit             | Regulated, on-prem, mobile releases   | SaaS web services                    |

The shared foundation is identical: trunk-based development, an immutable artifact promoted through environments, automated tests at every stage, and infrastructure as code. The delta is one approval step.

Choosing continuous delivery is often a _business_ decision - coordinating a release with marketing, satisfying a change-advisory process, or shipping software customers must install. Choosing continuous deployment is a _technical maturity_ decision: it requires progressive rollout, automated verification, and observability good enough to detect a bad release without a human watching.

A useful middle ground many teams adopt: continuous deployment to staging automatically, continuous delivery to production, with the approval becoming a formality that is eventually removed.

## Interview tips

- The crispest phrasing: "delivery means every change _could_ go to production; deployment means every change _does_."
- Note that both require deployment to be decoupled from release, via feature flags.
- Say which you would pick for a given context, and why - the judgement is what is being assessed.

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
