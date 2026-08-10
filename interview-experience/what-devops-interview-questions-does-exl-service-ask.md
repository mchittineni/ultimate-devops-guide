---
title: "What DevOps interview questions does EXL Service ask?"
id: 328
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - exl-service
  - kubernetes
  - infrastructure-as-code
  - cicd
  - devops-tools-and-automation
  - devsecops
  - monitoring-and-logging
  - backup-and-disaster-recovery
  - network-security
---

# What DevOps interview questions does EXL Service ask?

## Questions

**Architecture and scale**

- **You are onboarding a new customer with more than five million users. As a solution architect, how would you design the complete application architecture?**
- **Explain the complete request flow when a user visits an address served through your ingress, all the way until the request reaches the application Pod.**
- **Which EC2 instance types have you used, and why did you pick them?**
- **Give a real-world use case for AWS Lambda.**

**CI/CD, GitOps, and deployment strategy**

- **Explain your complete CI/CD pipeline from code commit through to production deployment.**
- **Explain your Git branching strategy, and how code from different branches reaches different environments.**
- **If Git is already the source of truth, why do you need Argo CD at all? Why not deploy straight from the pipeline with Helm or `kubectl`?**
- **Explain rolling update, blue-green, and canary deployment strategies.**
- **For a mission-critical production application, which deployment strategy would you choose, and why?**
- **You are implementing a canary release where only 10% of users get the new version. How do you implement that through your CI/CD pipeline?**
- **During that canary, how do you verify the 10% is healthy, and which metrics do you check before going to 100%?**
- **What is the difference between `git merge` and `git rebase`?**

**Kubernetes networking**

- **You need to expose an application internally without using a LoadBalancer or NodePort Service. How?**
- **Pods in different namespaces can currently talk to each other. How do you block that, and where exactly do you apply the NetworkPolicy?**

**Terraform**

- **Do you run Terraform locally or through a pipeline? Explain the complete workflow.**
- **Two engineers are working on the same Terraform code. How do you prevent conflicts and handle state locking and drift?**
- **Draw and explain your Terraform repository structure — how do dev, QA, and prod consume a shared module such as the VPC module?**

**Networking constraint**

- **Two VPCs must communicate but their CIDR ranges overlap, and Transit Gateway is not permitted. What would you recommend instead?**

**Disaster recovery**

- **Have you worked on disaster recovery? Explain your DR strategy including RTO, RPO, failover, and how traffic is redirected.**

**Secrets and incident response**

- **Where do you store CI/CD secrets such as pipeline credentials?**
- **Where do you store application configuration and secrets — ConfigMaps, Kubernetes Secrets, HashiCorp Vault?**
- **A developer accidentally commits AWS credentials to Git. What is your complete incident response process?**

**Monitoring and cost**

- **Which metrics do you monitor with Prometheus?**
- **Which dashboards and alerts have you configured in Grafana?**
- **Which monitoring agents are installed in your environment?**
- **How do you use monitoring and observability data to drive infrastructure cost optimisation?**

**Data platform**

- **Have you worked on Databricks pipelines? Describe that experience.**
- **What do you know about Apache Hadoop and its ecosystem?**

## Example

```text
EXL Service — DevOps Engineer (5 YOE), reported round
28 questions

  CI/CD / GitOps / deploy     8   full pipeline, branching->environments,
                                  why Argo CD, three strategies, canary at 10%
                                  + verification metrics, merge vs rebase
  Terraform                   3   local vs pipeline, two-engineer conflict,
                                  repo structure with shared modules
  Monitoring / cost           4   Prometheus metrics, Grafana dashboards,
                                  agents, cost from observability
  Architecture / scale        4   5M-user design, ingress request path,
                                  instance choice, Lambda use case
  Secrets / incident          3   pipeline secrets, app secrets, leaked
                                  AWS credentials response
  K8s networking              2   internal exposure without LB/NodePort,
                                  cross-namespace NetworkPolicy
  DR                          1   RTO/RPO/failover/traffic redirect
  Overlapping-CIDR VPCs       1   no Transit Gateway allowed
  Data platform               2   Databricks, Hadoop ecosystem

THE TWO STANDOUT QUESTIONS
  "Why Argo CD if Git is already the source of truth" and "overlapping CIDRs
  without Transit Gateway" are both designed to catch people who have only
  read about the tool. Both have specific, learnable answers.
```

## Interview tips

- The Argo CD question is the best one in the round. Git being the source of truth for _code_ is not the same as continuous reconciliation of _cluster state_. A pipeline that runs `kubectl apply` pushes once and then stops caring — if someone edits a Deployment by hand, nothing corrects it. Argo CD pulls continuously, detects drift, shows sync status, self-heals, gives one-click rollback to any Git revision, and removes the need to hand cluster credentials to CI. Say the phrase "push versus pull" and "drift detection". See [GitOps](../devops-tools-and-automation/what-is-gitops.md) and [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- Overlapping CIDRs with Transit Gateway ruled out has a real answer: PrivateLink. Expose the specific service behind an NLB and consume it through an interface endpoint in the other VPC, which works precisely because it never routes between the overlapping ranges. Secondary answers are a private NAT gateway to translate addresses, or re-addressing one VPC using a secondary CIDR block. Say that peering is impossible with overlapping ranges — that is the fact being tested. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- Exposing internally without a LoadBalancer or NodePort means ClusterIP — the default — reached by DNS from inside the cluster, with an Ingress or gateway if you need HTTP routing from outside, or `port-forward` for ad-hoc access. A headless Service is the answer if they want direct Pod addressing. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md).
- The NetworkPolicy "where" is the important half: policies are namespaced and apply to the _destination_ Pods, so you create them in the namespace you are protecting, selecting those Pods and allowing only specific namespaces via `namespaceSelector`. Add that a default-deny ingress policy per namespace is the baseline, and that policies do nothing unless your CNI enforces them. See [network segmentation](../network-security/what-is-network-segmentation.md).
- For the canary verification question, name concrete signals rather than "monitor it": error rate and HTTP 5xx ratio for the canary versus baseline, latency percentiles, saturation, and business metrics such as checkout completion — compared side by side, with automated analysis via Argo Rollouts or Flagger and an automatic abort on regression. The comparison against baseline is the detail that matters. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- For the mission-critical choice, commit to an answer: blue-green when you need instant, complete rollback and can afford double capacity; canary when you want to limit blast radius and have the observability to judge it. Say which you would pick and name the constraint that decides it — database schema compatibility is usually the deciding factor.
- The leaked-credentials question wants a sequence, and the order is what is graded: revoke or deactivate the key immediately, rotate the credential, review CloudTrail for use during the exposure window, contain anything that was accessed, only then clean history with `git filter-repo` or BFG and force-push, and finally add prevention — pre-commit secret scanning, push protection, and short-lived credentials so there is no long-lived key to leak. Emphasise that rewriting history first is the classic mistake, because the key stays valid while you tidy up. See [preventing and handling secret leaks in CI/CD](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).
- Distinguish the two secrets questions rather than answering them the same way: pipeline credentials belong in the CI system's own secret store or, better, are replaced by OIDC federation so no static key exists; application secrets belong in Vault or a cloud secret manager, surfaced through the External Secrets Operator or CSI driver — and Kubernetes Secrets are only base64-encoded, so say that plainly and mention encryption at rest for etcd. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- Two engineers on one Terraform codebase is a state-locking question: a remote backend with locking, short-lived branches with plan output posted on the pull request, apply only from CI so nobody applies locally, and scheduled `plan -refresh-only` to catch drift. Mention that locking prevents concurrent applies but does not prevent conflicting _intentions_, which is what review is for. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- For DR, give real numbers and a named tier. Define RPO as tolerable data loss and RTO as tolerable time to recover, then pick a pattern — backup and restore, pilot light, warm standby, or active-active — and say how traffic moves, which is Route 53 health checks with failover records or a global load balancer. Add that the untested DR plan is the one that fails. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md) and [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- The five-million-user design should be answered in tiers with a bottleneck named at each: CDN and edge caching, stateless application tier behind a load balancer with autoscaling, a cache layer, read replicas and eventually sharding or partitioning for the database, asynchronous queues for slow work, and multi-AZ throughout. Say what you would measure to find the real bottleneck rather than pre-optimising. See [scalability in DevOps](../scalability-and-high-availability/what-is-scalability-in-devops.md) and [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).
- The full ingress request path is a set piece worth rehearsing end to end: DNS resolution, the external load balancer, the ingress controller Pod, TLS termination, host and path rule matching, the Service, EndpointSlice selection, kube-proxy or the CNI dataplane, and finally the container port. There is a related walkthrough at [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).
- Be honest about Databricks and Hadoop if they are outside your experience — this is an analytics-services company probing for adjacency, and a confident "no, but here is the closest thing I have run" is better than an invented answer.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
