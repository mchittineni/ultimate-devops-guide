---
title: "What DevOps interview questions does One2N ask?"
id: 359
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - one2n
  - kubernetes
  - scalability-and-high-availability
  - monitoring-and-logging
  - container-orchestration-advanced
  - network-security
  - cicd
  - site-reliability-engineering
---

# What DevOps interview questions does One2N ask?

## Questions

**Something you built end to end**

- **What is something you have implemented end to end in your project?**
- **Explain your HPA implementation in detail.**
- **Why would you deploy RabbitMQ as a StatefulSet rather than a Deployment?**
- **How would you get application-level metrics?**
- **How would an HPA work with a StatefulSet?**

**Design a three-tier architecture**

- **How would you deploy a three-tier architecture, and what is your approach — which set of tools would you pick?**
- **Docker Swarm or Kubernetes?**
- **What kind of database would you use?**
- **How would you manage these microservices?**
- **How would you expose the application?**
- **Is a load balancer required in this setup, and why?**
- **How would the reverse proxy setup work here?**
- **Is nginx required in this setup?**
- **How would you set up DNS here?**
- **How would you manage SSL and TLS?**
- **How would you set up the entire CI/CD for this application?**
- **How would you update the image and deploy it?**
- **Set up alerting for this system.**
- **I want to know how many users are affected. How do you tell me that?**
- **Which metric tells me whether the application is up or down?**

## Example

```text
One2N — DevOps Engineer, reported round
20 questions — but really TWO questions with 18 follow-ups

  BLOCK 1  "Something you built end to end"        5
           -> HPA in detail -> why StatefulSet for RabbitMQ
           -> app-level metrics -> HPA + StatefulSet

  BLOCK 2  "Deploy a 3-tier architecture"          15
           -> tools -> Swarm or K8s -> database -> managing services
           -> exposing it -> is an LB needed -> reverse proxy -> is nginx
           needed -> DNS -> TLS -> CI/CD -> image updates -> alerting
           -> how many users affected -> up/down metric

THE FORMAT IS THE TEST
  This is not a question list, it is a single design conversation that gets
  interrogated for 15 turns. Every answer creates the next question, so a
  shallow choice ("I'd use Kubernetes") gets exposed two follow-ups later.
  Prepare to DEFEND a design, not to recall facts.
```

## Interview tips

- The RabbitMQ-as-StatefulSet question is the sharpest in the round and it has a real answer. A broker needs stable identity and its own durable storage: each node has a persistent message store and a name that cluster peers use to find it, so a StatefulSet gives you ordinal Pod names, per-Pod PersistentVolumeClaims that follow the Pod across restarts, a headless Service for peer discovery, and ordered rolling updates that protect quorum. With a Deployment, replacements get random names and share or lose their volume, so a restarted node cannot rejoin as itself and queues can be lost. Say "stable identity plus per-replica storage plus ordered updates" and you have covered it. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- The "HPA with a StatefulSet" follow-up is a trap worth spotting: it is technically supported, because an HPA can scale any resource with a `scale` subresource — but for a clustered broker or database it is usually wrong. Adding a replica means joining a cluster, rebalancing data, and possibly changing quorum, and scaling _down_ can lose data or break quorum, while the abandoned PVC is retained. Say that autoscaling suits stateless tiers and that stateful systems scale on deliberate, operator-driven decisions — which is precisely why operators exist. That judgement is the answer they want.
- Application-level metrics should be answered with the instrumentation path, not a tool name: expose a `/metrics` endpoint from the application using a Prometheus client library, emit request rate, error rate, and latency histograms with meaningful labels, and let Prometheus discover the Pods and scrape them. Add that a ServiceMonitor or PodMonitor is how you register that with the Operator, and that business metrics — orders placed, messages processed — belong here too. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md).
- "Is a load balancer required, and is nginx required?" are deliberately testing whether you add components reflexively. Answer both honestly: a load balancer is required if you want more than one replica reachable behind one address with health checking, and it is what gives you zero-downtime deploys — but in Kubernetes, the Service already load-balances, so what you need at the edge is one cloud load balancer, not one per service. And nginx is _not_ required as a separate tier: the ingress controller already terminates TLS and does host and path routing, and often _is_ nginx. Say what nginx would add if you did include it — static file serving, response caching, request buffering, or rate limiting — and say that otherwise it is a hop with no purpose. Naming a component you would _remove_ is a strong signal in a design interview.
- On Docker Swarm versus Kubernetes, commit and justify. Swarm is far simpler and adequate for a small fixed deployment; Kubernetes wins on ecosystem, autoscaling, operators, and hiring, and is the default in 2026, at the cost of real operational complexity. Say that for a genuinely small three-tier application on a couple of hosts, Compose or Swarm is a defensible choice and Kubernetes is overkill — showing you can _not_ choose Kubernetes is what distinguishes a designer from a follower. See [what container orchestration is and why you need it](../container-orchestration-advanced/what-is-container-orchestration-and-why-do-you-need-it.md).
- The two closing questions are the best in the round and they are SRE questions in disguise. For "which metric tells me if the application is up or down": not CPU, not Pod count, and not a liveness probe — the answer is the _success rate of real user requests_, the ratio of non-5xx responses to total valid requests, backed by a synthetic probe on the critical path so you still get a signal at zero traffic. Say that a Pod can be `Running` and `Ready` while every request fails. For "how many users are affected": you need per-request labels carrying tenant, user, or region, so you can compute affected sessions or unique identifiers rather than a raw error count — and that is exactly why high-cardinality dimensions matter, and why an error _count_ without a denominator cannot answer the question. See [service level indicators](../site-reliability-engineering/what-are-service-level-indicators-slis.md) and [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md).
- For alerting on this system, alert on symptoms rather than causes: error rate and latency against an SLO with burn-rate windows, plus a small number of cause-based alerts that genuinely need human action such as certificate expiry or a full disk. Say that every page must be actionable and that saturation alerts belong on dashboards, not pagers. See [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- The DNS and TLS pair should be answered as automation: one hostname per environment pointing at the ingress load balancer, external-dns creating records from Ingress annotations, and cert-manager issuing and renewing certificates from Let's Encrypt or ACM with TLS terminated at the ingress. Say that manual certificate renewal is how outages happen, so automatic renewal plus expiry monitoring is the design. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md) and [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- The image-update-and-deploy question wants immutability: tag by Git SHA or digest rather than `latest`, deploy by digest so what runs is what you tested, and change the tag in a Git-tracked manifest that a GitOps controller reconciles — with a rolling update and readiness probes so no traffic reaches a bad replica. Mention `imagePullPolicy` and why `latest` plus `Always` makes rollbacks impossible. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md) and [GitOps](../devops-tools-and-automation/what-is-gitops.md).
- On the database choice, do not name a product before naming the requirement. Ask about the access pattern, consistency needs, and expected scale, then choose — a managed relational database for transactional integrity, adding read replicas and caching before considering sharding. Say that you would use the managed service rather than running the database in the cluster unless there is a specific reason. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- Because the whole round is one escalating conversation, manage it deliberately: state your assumptions and constraints up front (scale, budget, team size, compliance), sketch the design, and then say which parts you would build first and which you would defer. Interviewers here reward "here is what I would not build yet, and why" as much as the design itself.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
