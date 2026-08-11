---
title: "What are Deployment Strategies?"
id: 90
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
---

# What are Deployment Strategies?

**Short answer:** Deployment strategies control how a new version replaces the old - recreate, rolling, blue/green, canary, A/B, and shadow - trading off downtime, resource cost, rollback speed, and confidence.

## Detail

| Strategy       | How it works                                           | Downtime | Extra cost       | Rollback                     | Best for                                 |
| -------------- | ------------------------------------------------------ | -------- | ---------------- | ---------------------------- | ---------------------------------------- |
| **Recreate**   | Stop all old, start all new                            | Yes      | None             | Redeploy old                 | Dev, or when versions cannot coexist     |
| **Rolling**    | Replace instances incrementally                        | No       | Small            | Roll forward/back gradually  | The sensible default                     |
| **Blue/green** | Two full environments, switch traffic                  | No       | 2× during switch | Instant - switch back        | Fast rollback, big-bang cutover          |
| **Canary**     | Small traffic percentage to new version, then increase | No       | Small            | Instant - shift traffic back | Risky changes, gradual confidence        |
| **A/B**        | Route by user attribute for comparison                 | No       | Small            | Instant                      | Product experiments, not just safety     |
| **Shadow**     | Mirror real traffic to new version, discard responses  | No       | 2× compute       | N/A                          | Validating performance with real traffic |

**Key considerations regardless of strategy**

- **Backward compatibility.** During rolling and canary deploys, two versions run simultaneously - so database schemas and API contracts must support both. The expand/contract pattern (add the new column, deploy code that writes both, backfill, switch reads, remove the old) is how you do this safely.
- **Health checks and readiness gates** determine when traffic reaches new instances.
- **Automated analysis.** Canary is only as good as the metrics that decide to promote or abort - error rate, latency, and business signals compared against the baseline.
- **Deploy is not release.** Feature flags let you deploy code and enable behaviour separately, which is often safer than any traffic-shifting strategy.

## Interview tips

- Backward compatibility during coexistence is the point that separates thorough answers from a memorised table.
- Explain how a canary decides to proceed - automated analysis, not a human staring at a dashboard.
- Blue/green's cost and its database problem (both environments share one database) are worth naming.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[How do you prevent and handle secret leaks in CI/CD pipelines?]] (`#237`): [How do you prevent and handle secret leaks in CI/CD pipelines?](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
