---
title: "What DevOps interview questions does EY ask?"
id: 329
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - ey
  - kubernetes
  - cicd
  - docker
  - version-control
  - api-gateway-and-service-mesh
  - monitoring-and-logging
  - container-orchestration-advanced
---

# What DevOps interview questions does EY ask?

## Questions

### Round set 1 — short screening

- **Introduce yourself and explain your current project.**
- **Questions on Kubernetes Deployments, Services, and configuration objects.**
- **How do you integrate Grafana with Prometheus?**
- **Questions on Terraform.**
- **What is a service mesh?**
- **What is a PodDisruptionBudget?**
- **What is `git squash`?**
- **What is `git rebase`?**
- **What is the purpose of Docker?**

### Round set 2 — full technical round

**Kubernetes**

- **Explain the Kubernetes architecture and how it works.**
- **What is a Deployment in Kubernetes?**
- **What is a Service in Kubernetes?**
- **How does Pod-to-Pod communication work?**
- **What is a PodDisruptionBudget?**
- **What does `CrashLoopBackOff` mean, and what causes it?**
- **What is a PersistentVolume?**
- **What is a ConfigMap?**
- **What is a service mesh and how does it work?**
- **What command or syntax do you use to deploy an application with Helm charts?**

**CI/CD and build tooling**

- **Have you used Jenkins as your CI/CD tool, or others such as GitLab?**
- **What is the difference between a declarative and a scripted pipeline?**
- **How do you manage concurrent builds in Jenkins without performance degrading?**
- **Which build tool do you use for Java applications?**
- **What happens internally during a Maven build — how does it resolve and fetch dependencies from the repository?**
- **Have you used an artefact repository such as Nexus or Artifactory, and where do your dependencies live?**
- **Which source-code management tool have you used?**
- **Have you integrated security tooling into your pipelines?**

**Deployment strategies**

- **What are rolling and canary deployment strategies?**
- **What is a hash-based deployment?**

**Git, Docker, and scope of work**

- **What is `git rebase`?**
- **What is the purpose of Docker?**
- **Have you deployed both applications and infrastructure, and which tech stack have you mainly worked on?**
- **Explain your current project.**

**Observability**

- **Which observability tools have you used, and which metrics do you monitor?**

## Example

```text
EY — DevOps Engineer, two reported rounds (~34 questions)

  SET 1  Short screening              9    K8s objects, Grafana+Prometheus,
                                           Terraform, service mesh, PDB,
                                           squash, rebase, Docker purpose

  SET 2  Full technical               25   K8s (10), CI/CD + build (8),
                                           deployment strategies (2),
                                           Git/Docker/scope (4), observability (1)

WHAT REPEATS ACROSS BOTH ROUNDS
  PodDisruptionBudget, service mesh, git rebase, Docker's purpose, and
  "explain your current project" are all asked twice. Those five are the
  guaranteed questions.

UNUSUAL FOR A DEVOPS ROUND
  Real depth on the Java build chain — Maven dependency resolution and
  Nexus/Artifactory. Consulting delivery work means Java, so revise it.
```

## Interview tips

- Five questions repeat across the two rounds, so treat them as certainties and make each answer excellent rather than adequate: PodDisruptionBudget, service mesh, `git rebase`, Docker's purpose, and your current project.
- The Maven internals question is the one most DevOps candidates fumble. Walk it properly: Maven reads `pom.xml`, resolves the dependency tree including transitive dependencies, checks the local `~/.m2/repository` cache first, then goes to the configured remote repository or a Nexus/Artifactory proxy, downloads the JAR plus its POM and checksum, and runs the lifecycle phases — validate, compile, test, package, install, deploy. Add that nearest-wins resolution and `dependencyManagement` control version conflicts, and that a proxy repository exists so builds are reproducible and do not depend on Maven Central being reachable.
- "Hash-based deployment" is not standard terminology, so define what it most likely means rather than bluffing: deploying artefacts identified by an immutable content hash or Git SHA rather than a mutable tag like `latest`, so every deployment is uniquely and verifiably identified and rollback means pointing at a previous hash. Say that this is the practice behind immutable image tags and digest-pinned deployments. If they mean consistent hashing for traffic distribution, say that too — offering both readings and asking which they mean is stronger than guessing.
- A service mesh answer should reach the sidecar or ambient dataplane and the control plane, then name what it buys you: mutual TLS between services, retries and timeouts and circuit breaking without application changes, fine-grained traffic splitting for canaries, and per-hop telemetry. Then say the cost — extra latency, resource overhead per Pod, and real operational complexity — because interviewers listen for whether you would actually recommend one. See [what Istio is](../container-orchestration-advanced/what-is-istio.md).
- For PodDisruptionBudget, define it as a constraint on _voluntary_ disruptions only: `minAvailable` or `maxUnavailable` stops a drain or upgrade from taking too many replicas down at once, but it does nothing when a node dies unexpectedly. Add the failure mode — a PDB set to `minAvailable: 100%` will block node drains forever.
- Grafana with Prometheus is a short answer, so make it precise: add Prometheus as a data source with its URL, then build panels with PromQL queries, and note that Grafana only queries — Prometheus does the scraping and storage, and Alertmanager handles routing. Mention provisioning dashboards as code rather than clicking them together. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md), [what Grafana is](../monitoring-and-logging/what-is-grafana.md), and [writing effective PromQL and Alertmanager rules](../monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md).
- Pod-to-Pod communication should state the model before the mechanism: every Pod gets its own routable IP and can reach every other Pod without NAT, which the CNI plugin implements — then Services provide a stable virtual IP and DNS name on top, because Pod IPs change. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md) and [what a Service is](../kubernetes/what-is-a-service-in-kubernetes.md).
- Concurrent Jenkins builds is a capacity question: executors per agent, distributed agents rather than building on the controller, `throttle` or lockable resources for jobs that contend on a shared dependency, ephemeral agents on Kubernetes so capacity scales with demand, and workspace cleanup so disk does not fill. Say that building on the controller is the anti-pattern. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- Declarative versus scripted needs one clear distinction plus a recommendation: declarative is a structured, validated `pipeline {}` block that is easier to read and supports `post` conditions and restart-from-stage; scripted is full Groovy with arbitrary control flow. Default to declarative and drop into a `script` block for the rare case that needs it.
- `git squash` is not actually a command — it is `git rebase -i` with `squash`/`fixup`, or `git merge --squash`. Saying that correctly, then explaining that it collapses several commits into one to keep history readable, is a small precision win. Pair it with rebase rewriting commits onto a new base and the golden rule about not rebasing shared branches. See [git merge, rebase, and cherry-pick](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md).
- `CrashLoopBackOff` is asked in most rounds in this collection. Give the mechanism — the container exits, the kubelet restarts it with exponential backoff up to five minutes — then the causes split by exit code, and the commands: `logs --previous`, `describe`, and checking probes. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- On Docker's purpose, do not define containers. Answer with the problem it solves: consistent, isolated, reproducible runtime packaging so the same artefact runs identically from a laptop to production, with far less overhead than a VM because it shares the host kernel. See [what Docker is](../docker/what-is-docker.md) and [image versus container](../docker/what-is-the-difference-between-docker-image-and-docker-container.md).
- Helm deployment commands: `helm install <release> <chart> -f values-prod.yaml`, or `helm upgrade --install` for idempotency, with `--atomic` and `--timeout` so a failed release rolls back automatically. Naming `--atomic` signals production use. See [what Helm is](../container-orchestration-advanced/what-is-helm.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
