---
title: "What DevOps interview questions does SAP ask?"
id: 376
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - sap
  - kubernetes
  - devops-tools-and-automation
  - devsecops
  - version-control
  - cloud-cost-optimization
  - container-orchestration-advanced
---

# What DevOps interview questions does SAP ask?

## Questions

**Deployment strategies and verification**

- **Can you run a blue-green deployment inside a single namespace? If so, how do you manage the two versions?**
- **Once a blue-green deployment is complete, how do you confirm it succeeded?**
- **You deployed with a canary. When do you delete the old Pods, and which KPIs do you check before doing so?**
- **Which deployment strategy is better on cost?**

**Kubernetes failure and scheduling**

- **A new deployment went out and suddenly all Pods — new and old — crashed. What is the reason?** The interviewer's own answer was that the new deployment exhausted the resource limits, so `limits` must be set in the manifest.
- **You are trying to schedule a new Pod and it is not deploying properly. What checks do you run?**
- **How does autoscaling work, end to end — what happens in the back end, from the worker nodes to the control plane, and what is the communication path?**

**Argo CD and delivery**

- **You want a deployment to reach only specific workloads or regions, and the update must not go to other parts. There is an option in Argo CD for this — what is it?**
- **Why would you use Argo CD over Jenkins?**

**Images and patching**

- **How do you keep your base image free of vulnerabilities?**
- **How do you apply patches regularly?**

**Git**

- **What are Git submodules for?**

## Example

```text
SAP — DevOps Engineer (8 YOE), reported round
12 questions

  Deployment strategies       4   blue-green in one namespace, verifying
                                  success, canary KPIs before deleting old
                                  Pods, which strategy costs less
  K8s failure / scheduling    3   all Pods crashed after a deploy, Pod will
                                  not schedule, autoscaling end to end
  Argo CD and delivery        2   restrict a rollout to specific
                                  workloads/regions, Argo CD over Jenkins
  Images and patching         2   vulnerability-free base image, regular patching
  Git                         1   submodules

THE ROUND IS BUILT AROUND ONE THEME
  Six of twelve questions are about releasing safely — how you cut over, how
  you prove it worked, and when it is safe to delete the old version. Prepare
  the verification story, not just the strategy names.
```

## Interview tips

- The "all Pods crashed after a new deployment" question has a specific mechanism worth explaining properly, because the interviewer's own answer is only half of it. Without `resources.limits`, a container can consume all available memory on its node; the kernel's OOM killer then reaps processes on that node, taking down _other_ Pods that were behaving — which is exactly why old Pods died alongside new ones. Add the second half: without `requests`, the scheduler has no idea what the Pod needs, so it overcommits the node in the first place. So the fix is both — requests so scheduling is accurate, and limits so one workload cannot starve its neighbours — plus a `ResourceQuota` and `LimitRange` at namespace level so a manifest without them cannot be admitted. Mentioning that the blast radius crossed Pod boundaries is what makes this answer stand out. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- Blue-green in one namespace is a yes, and the mechanism is label selectors. Run two Deployments — `app=web,version=blue` and `app=web,version=green` — and point a single Service's selector at one version; the cutover is a one-line patch to the Service selector, and rollback is patching it back. Say what you have to manage: unique Deployment and ConfigMap names, double the resource consumption while both are live, and a shared database that must be compatible with both versions. Then say when you would use separate namespaces instead — when you want hard isolation of quotas, secrets, and network policy between the two. Naming the Service-selector switch is the answer. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- The canary-KPI question is the best in the round and it wants named signals, not "monitor it". Compare canary against baseline rather than against absolute thresholds: error rate and 5xx ratio, latency at p95 and p99, saturation (CPU, memory, connection pool), Pod restart count, and at least one business metric such as checkout or login success. Then the discipline: bake for long enough to cover a full traffic cycle, ensure the canary has statistically meaningful traffic, and only delete the old Pods once the canary has served 100% for a soak period — because deleting them earlier removes your instant rollback. Name Argo Rollouts or Flagger for automated analysis with an auto-abort. Saying "the old Pods _are_ the rollback plan" is the line that lands.
- For verifying a completed blue-green, give layers rather than "check the pods are running": readiness probes passing and the Service's `Endpoints` populated with the new version; synthetic checks against the real user journey through the public endpoint; error rate and latency compared against the pre-cutover baseline; a canary or smoke test suite; and confirmation that no traffic is still reaching the old version — checked at the load balancer or ingress, not just in the cluster. Add that you keep the old version warm for a defined window before tearing it down.
- The Argo CD "specific workloads or regions" question is asking for a feature by name. The direct answer is **ApplicationSet** — with a cluster generator or a matrix generator plus selectors and labels, so a single definition targets only the clusters or regions you choose. Alongside it, name sync windows to constrain _when_ a rollout may happen, per-Application sync policies so some environments are manual, and `syncOptions` with selective sync for targeting specific resources. If they mean progressive rollout across clusters, ApplicationSet progressive syncs are the mechanism. See [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- "Argo CD over Jenkins" is not a tool preference question — they solve different problems, and saying so is the answer. Jenkins is a CI engine that pushes changes outward and stops caring once `kubectl apply` returns; Argo CD is a controller inside the cluster that continuously reconciles live state against Git, so it detects drift, self-heals, shows sync status per resource, gives one-click rollback to any Git revision, and removes the need to hand cluster credentials to CI. Say "push versus pull, and continuous reconciliation versus one-shot apply", then add that the usual architecture keeps Jenkins for CI and gives Argo CD the CD half. See [GitOps](../devops-tools-and-automation/what-is-gitops.md).
- The cost question deserves a real comparison rather than a single winner. Blue-green costs roughly double capacity for the duration of the cutover, so it is the most expensive but gives the fastest, cleanest rollback. Canary costs only the small extra slice for the canary replicas, making it much cheaper at scale, but it needs the observability investment to be safe. Rolling update is effectively free, needing only surge capacity, but rollback means another rollout rather than a switch. Say that on a large fleet blue-green is often financially impossible, which is precisely why canary and rolling dominate — and that the real cost of a cheap strategy is a slower rollback.
- The autoscaling end-to-end question wants the control path, so trace it: the kubelet and cAdvisor expose usage, metrics-server aggregates it and serves the metrics API, the HPA controller in the controller manager polls that API on its sync interval, computes the desired replica count from current utilisation against the target, and updates the Deployment's `scale` subresource; the Deployment controller adjusts the ReplicaSet, the scheduler places the new Pods, and if none fit, the Cluster Autoscaler or Karpenter sees unschedulable Pods and provisions nodes, whose kubelets then register with the API server. Emphasise that everything goes _through_ the API server — no component talks directly to another — and mention the stabilisation window that prevents thrashing.
- The Pod-will-not-schedule question should be answered as a decision tree keyed on the phase: `Pending` means the scheduler cannot place it — insufficient CPU or memory against _requests_, no node matching the selector or affinity, an untolerated taint, an unbound PVC (often because the volume is in the wrong availability zone), or an exhausted `ResourceQuota`. `ImagePullBackOff` means registry, tag, or pull-secret. `CrashLoopBackOff` means it starts and exits. Say `kubectl describe pod` and read the events first in every branch. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- The base-image and patching questions are one answer, and the key idea is that you do not patch running containers — you rebuild. Say: pin base images by digest rather than a floating tag so builds are reproducible, rebuild on a schedule _and_ on upstream advisories so patched layers are picked up, use minimal or distroless bases so there is little to patch, scan in CI with Trivy or Grype and gate on severity plus reachability, maintain a small set of approved golden base images that application teams inherit, sign images and enforce provenance with admission control, and generate an SBOM so you can answer "are we affected" without rebuilding everything. For hosts, the equivalent is immutable infrastructure — bake a new AMI and roll the nodes rather than patching in place. See [prioritising vulnerabilities without blocking delivery](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md) and [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md).
- Git submodules should come with the caveat, because the honest answer is more useful than the definition. A submodule embeds another repository at a pinned commit inside your tree, which is how you vendor a shared library or share IaC modules while keeping histories separate. But say the operational cost: clones need `--recurse-submodules`, contributors routinely forget to update the pointer, CI must initialise them, and a detached-HEAD submodule is a common source of confusion — which is why many teams prefer a package registry, a Terraform module registry, or a monorepo instead. Naming that trade-off is what an eight-year candidate is expected to do. See [what Git is](../version-control/what-is-git.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
