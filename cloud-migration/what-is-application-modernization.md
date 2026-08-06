---
title: "What is Application Modernization?"
id: 139
category: "Cloud Migration"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-migration
  - interview-questions
---

# What is Application Modernization?

**Short answer:** Application modernisation is updating legacy applications to take advantage of cloud-native capabilities — containerisation, managed services, microservices, serverless — to improve scalability, delivery speed, and maintainability.

## Detail

**Approaches, from least to most invasive**

- **Containerise** — package the existing application in a container for portability and consistent deployment, with little or no code change.
- **Replatform data and middleware** — move to managed databases, queues, and caches, removing operational burden without changing application logic.
- **Refactor internals** — remove local-disk state, externalise configuration and sessions, add health endpoints and structured logging (essentially adopting Twelve-Factor).
- **Re-architect** — decompose into services around domain boundaries, or move event-driven workloads to serverless.
- **Rewrite / replace** — when the existing codebase costs more to modernise than to replace.

**The strangler fig pattern** is the standard incremental technique: place a facade in front of the legacy application, implement new functionality as new services behind it, route traffic capability by capability, and retire pieces of the legacy system as they are replaced. It avoids the big-bang rewrite, which has a famously poor success record.

**Sequencing that works.** Modernise the delivery pipeline first — even a legacy monolith benefits enormously from automated build, test, and deploy. Then externalise state and configuration. Then extract the highest-value or highest-churn capability. Measure at each stage.

**Choosing what to modernise:** high change frequency plus high business value justifies investment. A stable system nobody touches, however old, may be best left alone — modernising it returns nothing.

## Interview tips

- The strangler fig pattern is the answer to "how do you modernise without a risky rewrite?"
- "Automate the pipeline first" is practical, underrated advice that shows delivery experience.
- Show restraint: not everything should be modernised, and saying so demonstrates judgement.

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
