---
title: "What is the difference between SRE, DevOps, and Platform Engineering?"
id: 232
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - site-reliability-engineering
  - interview-questions
---

# What is the difference between SRE, DevOps, and Platform Engineering?

**Short answer:** DevOps is a set of cultural and practice principles for shortening the path from commit to production. SRE is a specific implementation of those principles with reliability as the measured objective — SLOs, error budgets, toil limits. Platform engineering is the discipline of building the internal product that makes those practices self-service for other teams. They are complementary, not competing.

## Detail

|               | DevOps                               | SRE                                        | Platform Engineering                            |
| ------------- | ------------------------------------ | ------------------------------------------ | ----------------------------------------------- |
| Nature        | philosophy / practices               | prescriptive engineering discipline        | product discipline                              |
| Objective     | flow, feedback, shared ownership     | reliability targets met at acceptable cost | developer self-service and consistency          |
| Key artefacts | CI/CD, automation, blameless culture | SLOs, error budgets, PRRs, toil budget     | golden paths, IDP, catalogue, guardrails        |
| Measures      | DORA metrics                         | error budget attainment, toil %, MTTR      | adoption, DORA outcomes, developer satisfaction |
| Users         | the delivering team itself           | service owners and their users             | other engineering teams                         |

**"SRE implements DevOps" is the accepted framing** (and Google's own). DevOps says reduce silos, automate, measure, accept failure as normal; SRE gives concrete mechanisms: an SLO to define acceptable failure, an error budget to arbitrate between speed and stability, a cap on toil (often 50%) to protect engineering time, and blameless post-mortems as a required practice.

**Platform engineering emerged from a practical failure of "you build it, you run it".** Asking every team to own Kubernetes, IaC, observability, secrets, and compliance produces duplicated effort and wildly variable quality. Platform teams provide those capabilities as a product so stream-aligned teams keep ownership of their services without each solving infrastructure from first principles.

**They coexist in real organisations.** A common shape: stream-aligned teams own their services and their on-call; a platform team provides the paved road; an SRE function (embedded, consulting, or owning shared critical infrastructure) sets reliability standards, runs production readiness reviews, and partners on the hardest services. Titles vary far more than the underlying division of work.

**Where the roles genuinely differ in day-to-day work:** an SRE spends time on SLOs, incident response, capacity, and eliminating toil for specific services; a platform engineer spends time on internal APIs, templates, upgrade migrations, and developer experience; a DevOps engineer — as the title is commonly used — usually builds and runs CI/CD and infrastructure automation for a team or product.

**Say plainly what the anti-patterns are:** a "DevOps team" that is the old operations team renamed and still receives tickets; an SRE team with no authority to enforce an error budget policy, which makes SLOs decorative; a platform team that builds what it finds interesting rather than what teams need. Naming these is often what the interviewer is really probing.

## Interview tips

- Lead with "SRE is a concrete implementation of DevOps principles; platform engineering productises them" — it is the cleanest formulation.
- Give one artefact per discipline (error budget, golden path, CI/CD pipeline) to make the distinction tangible.
- Expect: "which are you?" — answer with the work you actually do rather than the title, and name the anti-pattern you would fix first.

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
