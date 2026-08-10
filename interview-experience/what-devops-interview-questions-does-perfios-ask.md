---
title: "What DevOps interview questions does Perfios ask?"
id: 368
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - perfios
  - network-security
  - aws-engineering
  - cicd
  - kubernetes
  - scripting-and-automation
  - devops-tools-and-automation
---

# What DevOps interview questions does Perfios ask?

## Questions

**The request path, drawn on a whiteboard**

- **What happens when a user hits an application URL — how does the request pass through the network? Draw a diagram and explain it.**
- **Explain the AWS traffic architecture — how does traffic reach a private subnet? Draw it.**

**Architecture and load balancing**

- **What does a three-tier architecture look like, and how does it compare with two-tier?**
- **What are ALB and NLB, and when should you use each?**
- **What is the difference between ClusterIP and NodePort?**

**Delivery and deployment**

- **Do you use one pipeline for three environments or one per environment? Explain — and write a Groovy script for build, test, and deploy stages using any CI/CD tool.**
- **What is the difference between canary and blue-green?**
- **How do you achieve a zero-downtime application upgrade?**
- **When CI builds a package you then need a platform to deploy it onto. How do you build that platform, and if it requires human intervention, how do you eliminate that dependency?**
- **In GitHub, what validations do you run after a commit — and do you validate before or after the commit?**
- **Have you contributed any automation initiatives as a DevOps engineer in your current company?**

**Scripting**

- **Write a shell script that sums the numbers 1 to 100 and prints the result.**
- **Write a shell script that takes an integer N and prints a triangular pattern where each row holds consecutive numbers printed in reverse order, and each row has one more element than the last.**

## Example

```text
Perfios — DevOps Engineer (4.7 YOE), reported round
14 questions

  Delivery and deployment     6   one pipeline vs three, write Groovy,
                                  canary vs blue-green, zero downtime,
                                  build the deploy platform, commit validations
  Request path (whiteboard)   2   URL to response with a diagram,
                                  traffic into a private subnet
  Architecture / LB           3   three-tier vs two-tier, ALB vs NLB,
                                  ClusterIP vs NodePort
  Scripting                   2   sum 1..100, reverse triangular pattern
  Experience                  1   automation you initiated

TWO QUESTIONS SAY "DRAW A DIAGRAM"
  This is a whiteboard round. Practise sketching the request path and the
  public-subnet-load-balancer-to-private-subnet flow, because you will be
  drawing them, not describing them.
```

```bash
# Sum 1..100 — three valid answers, and saying why you'd pick one matters.
sum=0; for i in $(seq 1 100); do sum=$((sum + i)); done; echo "$sum"   # 5050
seq 1 100 | paste -sd+ | bc          # shorter
echo $(( 100 * 101 / 2 ))            # O(1) — Gauss; mention it exists

# The triangular pattern: row r holds r numbers, counted DOWN from the
# highest value in that row.
#!/usr/bin/env bash
n=${1:?usage: $0 N}
counter=1
for (( row=1; row<=n; row++ )); do
  high=$(( counter + row - 1 ))
  for (( v=high; v>=counter; v-- )); do printf '%s ' "$v"; done
  echo
  counter=$(( high + 1 ))
done
# N=4 ->  1
#         3 2
#         6 5 4
#         10 9 8 7
```

## Interview tips

- Both diagram questions are the core of this round, so rehearse drawing them. The URL-to-response path: browser cache, then OS resolver and `/etc/hosts`, then the recursive resolver walking root, TLD, and authoritative nameservers; then the TCP handshake, then the TLS handshake with certificate validation; then the request arrives at CloudFront or a load balancer, is routed to a target, hits the application, which queries the database and returns; then the response renders. Say where you would observe each hop. There is a full walkthrough at [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).
- The private-subnet traffic diagram is the AWS-specific companion: an internet gateway attached to the VPC, an internet-facing load balancer in _public_ subnets across two availability zones, targets in _private_ subnets with a security group that only accepts traffic from the load balancer's security group, and a NAT gateway in a public subnet giving those private instances outbound-only access for patching. Draw the two route tables — the public one sending `0.0.0.0/0` to the internet gateway, the private one sending it to the NAT gateway — because the route tables are what actually make a subnet public or private. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- The "build the platform, then remove the human" question is the most interesting in the round and it is really asking about GitOps. Say that the platform is provisioned as code — Terraform for the cluster and its add-ons, so it is reproducible rather than hand-built — and then the human step disappears because the pipeline stops deploying at all: it publishes an immutable artefact and updates a tag in a Git-tracked manifest, and an in-cluster controller such as Argo CD reconciles the cluster to match. Name what remains deliberately manual — a production approval — and say that an approval is a _control_, not a dependency, which is the distinction the interviewer is probing. See [GitOps](../devops-tools-and-automation/what-is-gitops.md) and [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- "One pipeline for three environments, or one each?" has a preferred answer: one pipeline definition, parameterised per environment, so the build happens once and the _same artefact_ is promoted through dev, QA, and production with only configuration differing. Say why three separate pipelines is worse — they drift, and rebuilding per environment means you never tested what you shipped. Then mention the mechanism: stage-level approvals and environment-scoped credentials in one pipeline.
- The commit-validation question wants both sides of the boundary, and the good answer names both. _Before_ the commit: pre-commit hooks running formatters, linters, and secret scanning locally, so obvious problems never enter history. _After_ the commit: the pull-request pipeline — build, unit tests, static analysis, dependency and image scanning — plus branch protection requiring those checks and a review before merge. Say that local hooks are a convenience that can be bypassed, so the _enforcing_ gate must be server-side. See [using Git hooks for automated linting, testing, and commit validation](../version-control/how-do-you-use-git-hooks-for-automated-linting-testing-and-commit-validation.md).
- On the triangular-pattern script, talk through the invariant before you write: row `r` contains `r` values, and the numbers continue from where the previous row stopped, printed in descending order. Keeping a running counter and computing the row's highest value is what makes it clean. Say the complexity and handle `N=0` or a non-integer argument — validating the input is a cheap way to look production-minded. See [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).
- For the sum, give the loop answer since that is what is being tested, then mention the closed-form `n(n+1)/2` as an aside. It costs one sentence and signals you think about complexity rather than just syntax.
- ClusterIP versus NodePort should come with when you would actually use each: ClusterIP is the default and internal-only, reached by DNS from inside the cluster; NodePort opens the same port on every node in the 30000-32767 range, which is useful for development or as a target for an external load balancer, but it is a poor production front door because you must track node IPs and the port range is unfriendly. Say that LoadBalancer builds on NodePort, and that an Ingress behind one load balancer is what you would use for many services. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md).
- Canary versus blue-green needs the trade-off, not just the mechanic: blue-green runs two full environments and switches all traffic at once, giving instant rollback at double the capacity cost; canary shifts a small percentage first, limiting blast radius but requiring the observability to judge whether the canary is healthy. Say that database schema compatibility is usually what decides between them, and name automated canary analysis with Argo Rollouts or Flagger. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- Zero downtime is a set of properties rather than one strategy, so list them: readiness probes gating traffic so no request reaches an unready replica, `maxUnavailable: 0` with surge, connection draining and `preStop` hooks so in-flight requests finish, backward-compatible database migrations using expand-and-contract, and idempotent retryable requests. Saying "backward-compatible schema changes" is the detail most candidates miss, and during a rolling update both versions run simultaneously — which is why it matters.
- ALB versus NLB deserves a reason rather than a table: ALB for HTTP and HTTPS with path and host routing, header inspection, and WAF integration; NLB for raw TCP or UDP, extreme throughput, static IPs, or TLS passthrough. Say which you have used and why. See [layer 4 versus layer 7 load balancers](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md).
- The automation-initiative question is your chance to sound like an owner rather than an operator. Bring one initiative you started — not one you were assigned — with the problem, what you built, and the measured outcome. See [turning ad-hoc scripts into maintainable automation](../scripting-and-automation/how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
