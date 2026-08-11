---
title: "What DevOps interview questions does Nisum Technologies ask?"
id: 356
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - nisum-technologies
  - docker
  - kubernetes
  - infrastructure-as-code
  - cicd
  - devsecops
  - aws-engineering
  - container-orchestration-advanced
---

# What DevOps interview questions does Nisum Technologies ask?

## Questions

**CI/CD and deployment**

- **Explain a CI/CD pipeline.**
- **What deployment strategy do you follow?**
- **Have you upgraded any services?**

**Docker**

- **What is the difference between the `COPY` and `ADD` instructions?**
- **How do you fix security issues in Docker images?**

**Kubernetes**

- **Can you deploy services on the control-plane (master) node?**
- **If your Pod is not running, how do you troubleshoot it?**
- **Have you worked on Helm charts?**

**Terraform**

- **What is the difference between `count` and a tuple in Terraform?**
- **What is the difference between a list and a string in Terraform?**

**AWS**

- **Explain Fargate.**

**Scripting and configuration management**

- **Do you have Python or shell scripting experience? Explain one script you have written.**
- **Do you have Ansible experience?**

**Terminology**

- **What is a scraper?**

## Example

```text
Nisum Technologies — DevOps Engineer, reported round
14 questions

  Docker                      2   COPY vs ADD, fixing image vulnerabilities
  Kubernetes                  3   services on the control plane, Pod not
                                  running, Helm charts
  Terraform                   2   count vs tuple, list vs string
  CI/CD                       3   pipeline, deployment strategy, upgrades
  Scripting / config mgmt     2   Python or shell example, Ansible
  AWS                         1   Fargate
  Terminology                 1   "scraper"

TWO QUESTIONS ARE GARBLED IN THE SOURCE
  "content and tuple" is almost certainly count vs for_each or list vs tuple,
  and "scrapper" is almost certainly the Prometheus scraper. Both are worth
  answering by naming the ambiguity and covering the likely readings — that
  reads as competence, not evasion.
```

## Interview tips

- The "scraper" question is best answered by picking the most likely meaning and saying so. In a DevOps context it is the Prometheus scraper: Prometheus _pulls_ metrics by making periodic HTTP requests to `/metrics` endpoints it finds through service discovery, controlled by `scrape_interval` and `scrape_configs`, with `relabel_configs` shaping the target labels. Say that the pull model is the distinguishing feature and that the Pushgateway is the exception for short-lived batch jobs. Then briefly acknowledge the other reading — a web scraper extracting data from pages — so you have covered both. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md).
- "Can you deploy services on the master node?" needs a two-part answer, and the parts differ. Technically yes: self-managed control-plane nodes carry a `node-role.kubernetes.io/control-plane:NoSchedule` taint, so a workload needs a matching toleration — and the control plane's own components already run there as static Pods. On a managed cluster such as EKS, AKS, or GKE you cannot, because the provider owns and hides those nodes. Then say why you would not in production: a busy workload competing with the API server and etcd for CPU, memory, and disk I/O is how you turn a workload problem into a cluster-wide outage. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- For the garbled Terraform type question, cover the type system properly since that is clearly what is being probed. A `string` is a single scalar value; a `list` is an ordered collection of the _same_ type indexed numerically; a `tuple` is an ordered collection where each position can be a _different_ type; a `set` is unordered with no duplicates; a `map` is key-value pairs of one type; and an `object` allows different types per named attribute. Then, if they meant `count`, give the more useful comparison: `count` produces indexed instances so removing a middle element re-indexes everything above it and destroys resources that did not change, while `for_each` keys instances by a stable string so removals are surgical. Offering both readings and clearly labelling which you are answering is the right move.
- Fixing security issues in Docker images should be a prioritised process, not a tool name. Start with the base image — most reported vulnerabilities come from the distribution packages, so moving to a slim or distroless base often eliminates most findings at once. Then rebuild regularly so patched base layers are picked up, pin and update application dependencies, remove build tools via a multi-stage build so they never reach the runtime image, run as a non-root user with a read-only root filesystem, and scan in CI with Trivy or Grype, gating on severity and whether the vulnerability is actually reachable. Say that a scanner finding in a package your application never invokes is a lower priority than a reachable one — that triage judgement is what separates a real answer. See [prioritising vulnerabilities without blocking delivery](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md) and [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- `COPY` versus `ADD` has a definite recommended answer: use `COPY`. `ADD` additionally auto-extracts local tar archives and can fetch remote URLs, which makes builds non-obvious and can pull in unaudited content — and for a remote file, `curl` plus a checksum verification in a `RUN` step is both clearer and safer. Say that Docker's own guidance is to prefer `COPY`. See [what a Dockerfile is](../docker/what-is-dockerfile.md).
- "Pod is not running" is deliberately open, so answer with a decision tree keyed on the phase rather than a list of commands. `Pending` means the scheduler cannot place it — insufficient CPU or memory, no node matching the selector or affinity, an untolerated taint, or an unbound PVC. `ImagePullBackOff` means the registry, the tag, or the pull secret is wrong. `CrashLoopBackOff` means it starts and exits — read the exit code to separate `OOMKilled` (137) from an application error, and check whether an aggressive liveness probe is killing a healthy-but-slow container. `Running` but not `Ready` means the readiness probe is failing. Say `kubectl describe pod` and reading the events comes first in every branch. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- Fargate should be explained as a _capacity model_ rather than a service: you run containers without provisioning or patching EC2 instances, paying per task for the vCPU and memory you request, and it works behind both ECS and EKS. Then give the trade-offs, because that is what makes it a real answer — no DaemonSets or privileged containers on EKS Fargate, no GPU support, slower task start than a warm node, and a higher unit price that is often still cheaper once you account for idle capacity and the operational cost of managing nodes. See [ECS versus EKS versus Fargate](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md).
- "Have you upgraded any services?" and "have you worked on Helm charts?" are closed capability checks, and a bare yes wastes them. Convert each into a two-sentence claim with a specific detail — which version you upgraded from and to, what broke, how you validated it; or what is in your `values.yaml` and whether you use `helm upgrade --install --atomic`. See [what Helm is](../container-orchestration-advanced/what-is-helm.md).
- On deployment strategy, name the one you actually use and the constraint that decided it. Rolling is the default and needs backward-compatible changes; blue-green gives instant rollback at double the capacity cost; canary limits blast radius but needs the observability to judge it. Say that database schema compatibility is usually what rules options out. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- For the scripting question, have one script ready you can walk through end to end — what problem it solved, how it handles failure, and how it is scheduled. Mention `set -euo pipefail` for Bash or argument parsing and non-zero exit codes for Python; interviewers listen for whether your scripts fail loudly or silently. See [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md) and [when to use Bash and when to use Python](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
