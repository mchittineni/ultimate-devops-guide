---
title: "How do you explain your DevOps project in an interview?"
id: 271
category: "Interview Experience"
difficulty: "Beginner"
tags:
  - devops
  - interview-experience
  - interview-questions
---

# How do you explain your DevOps project in an interview?

**Short answer:** Give a 90-second structured walkthrough - business context, architecture, your specific contribution, and one measurable outcome - then stop and let them drill. Prepare it as a **request path** (a user clicks, and here is every hop to the database and back) because that is the shape most follow-ups take. Above all, be ready to justify every choice: the most common follow-up in real interviews is not "what did you use" but "**why did you choose that?**"

## Detail

**Why this question dominates.** Almost every DevOps interview opens with "explain your current project." It is asked because it is unfakeable: your architecture description sets the agenda for the next forty minutes, and every technical question is then anchored to something you claimed to have built. Answer it vaguely and the interviewer picks the topics; answer it well and you steer them onto ground you know.

**The 90-second structure:**

1. **Context (15s).** What the system does and its scale. "A payments API for a retail platform - about 4,000 requests per second at peak, 60 engineers across 8 teams."
2. **Architecture (30s).** The stack in the order a request travels, not as a tool list. Route 53 → CloudFront → ALB → EKS ingress → 30 microservices → RDS Postgres and ElastiCache.
3. **Your contribution (30s).** Specifically what _you_ owned. "I owned the delivery platform: the Terraform modules for EKS and networking, the Argo CD setup, and the golden-path pipeline every team uses."
4. **Outcome (15s).** One number. "Deploys went from twice a week to about 40 a day, and lead time from commit to production dropped from three days to under an hour."

Then stop talking. Silence invites the drill-down, and the drill-down is where you score.

**Be ready to defend every choice.** Analysis of real interview write-ups shows the follow-ups cluster on justification: _why EKS over ECS? why Argo CD over deploying from Jenkins? why did you put the web tier in a public subnet? why StatefulSet when a Deployment with a PVC would work? why RDS Proxy?_ Prepare a two-sentence rationale for each significant decision - the trade-off you accepted, and what would make you choose differently. "That was decided before I joined" is acceptable exactly once, and only if you follow it with what you would do now.

**Prepare the request path in detail.** A very common deep-dive is: _"walk me through every component a request touches from the browser to the backend pod - including firewalls, NACLs, security groups, and route tables."_ Be able to name, in order: DNS, CDN, WAF, internet gateway, NACL, security group, load balancer, ingress controller, Service, EndpointSlice, Pod - and where TLS terminates. If you can sketch it, sketch it; interviewers consistently note when a candidate draws the diagram.

**Numbers make it real.** Node counts, request rates, cluster sizes, deploy frequency, incident counts, monthly cloud spend, the size of your team. Vague scale ("quite large") reads as second-hand. You do not need exact figures - "roughly 40 nodes, about $80k a month" is fine and far better than nothing.

**Own your actual scope honestly.** If you worked on one component of a large platform, say so and describe that component deeply. Claiming to have architected everything invites questions you cannot answer, and the collapse is worse than the modest version would have been. "I owned X, and I worked alongside the team that owned Y" is a strong, credible framing.

**Have a failure story ready.** "Tell me about something that went wrong" is close to universal at senior level. Use a real incident: what broke, how you detected it, what you did, what the root cause was, and - the part most candidates omit - what you changed so it could not recur. Blameless framing, specific timeline, no hero narrative.

**Rehearse it out loud.** This is the one answer worth practising verbatim until it is fluent, because it is the only one you are guaranteed to be asked.

## Example

```text
STRUCTURE — 90 seconds, then stop

  Context      "Payments platform for a retail company. ~4k rps peak,
                60 engineers, 8 product teams, EU + US regions."

  Architecture "Request path: Route 53 → CloudFront → WAF → ALB →
                NGINX ingress on EKS → ~30 services → RDS Postgres
                (Multi-AZ) + ElastiCache. Async work on SQS.
                Everything in Terraform, deployed by Argo CD from Git."

  My scope     "I owned the delivery platform, not the product services:
                the Terraform modules for VPC and EKS, the Argo CD
                app-of-apps setup, and the reusable pipeline template
                the product teams consume. I ran the on-call rotation
                for the platform itself."

  Outcome      "Deploy frequency went from ~2/week to ~40/day.
                Lead time from commit to prod: 3 days → under 1 hour.
                Change failure rate stayed flat at about 5%."


ANTICIPATED FOLLOW-UPS — prepare two sentences each

  Why EKS and not ECS?            → team already ran K8s on-prem; needed
                                    portability and the operator ecosystem.
  Why Argo CD and not kubectl
    from the pipeline?            → cluster state reconciled from Git, drift
                                    detected, no cluster credentials in CI.
  Why RDS and not Aurora?         → cost at our volume; would reconsider above ~10k rps.
  How do you roll back?           → Argo CD sync to the previous Git SHA;
                                    DB migrations are expand/contract so they
                                    are backward compatible.
  What went wrong once?           → [specific incident, detection, fix, prevention]
```

## Interview tips

- Rehearse the 90 seconds until it is fluent, then deliberately stop and let them pick the thread.
- Order the architecture along the request path, not as a tool list. "We use Docker, Kubernetes, Jenkins, Terraform" tells the interviewer nothing about how it fits together.
- Have a justification ready for every technology named. "Why X over Y" is the single most common follow-up in real interviews.
- Bring numbers. Scale, frequency, cost, team size - specificity is what separates a real project from a tutorial.
- Be precise about your own scope. Overclaiming collapses under two questions; owning one area deeply is more impressive than owning everything vaguely.
- Prepare the full browser-to-Pod request path including NACLs, security groups, and route tables - it is asked verbatim.
- Ask if you may sketch the architecture. It buys thinking time and interviewers remember candidates who draw.
- Keep one failure story and one improvement story loaded. They cover most of the behavioural round too.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
