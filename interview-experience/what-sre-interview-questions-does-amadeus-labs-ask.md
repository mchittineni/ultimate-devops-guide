---
title: "What SRE interview questions does Amadeus Labs ask?"
id: 313
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - amadeus-labs
  - kubernetes
  - site-reliability-engineering
  - linux-administration
  - devsecops
  - scalability-and-high-availability
---

# What SRE interview questions does Amadeus Labs ask?

## Questions

**Kubernetes failure scenarios**

- **Pod-level autoscaling is not happening. How do you approach diagnosing it?**
- **An application configured with an HPA was scaling correctly and has suddenly stopped. What is your approach?**
- **An Ingress is configured but end users cannot reach the application. How do you find and fix the break?**

**Kubernetes mechanics**

- **Explain how Kubernetes handles service discovery — how one Pod finds and reaches another.**
- **You have five application teams sharing a cluster. How do you guarantee no single team consumes more than its allotted amount of storage?**
- **Can a Pod be scheduled with a `securityContext` that sets `runAsNonRoot: true` and `runAsUser: 0` at the same time? Explain what happens.**

**Automation experience**

- **What kinds of automation have you built on or around Kubernetes?**
- **Describe a specific piece of automation you delivered that measurably saved time on your project.**

**Linux**

- **What is a leap second, and what problems does one cause on a Linux system?**

## Example

```text
Amadeus Labs — SRE (5 YOE), reported round
9 questions

  K8s failure scenarios       3   HPA not scaling, HPA stopped working,
                                  Ingress unreachable
  K8s mechanics               3   service discovery, per-team storage quota,
                                  contradictory securityContext
  Automation experience       2   what you automated, what saved time
  Linux                       1   leap second

WHERE TO SPEND PREP TIME
  ~67% Kubernetes. Two of three scenarios are the same shape — "it worked,
  now it doesn't" — so rehearse one ordered diagnostic path and reuse it.
```

```yaml
# The trick question. runAsUser: 0 IS root, so this fails the
# runAsNonRoot: true assertion.
securityContext:
  runAsNonRoot: true
  runAsUser: 0 # <- contradiction
```

## Interview tips

- The `securityContext` question has a precise answer: the Pod is admitted and scheduled, but the kubelet refuses to start the container and it fails with a `CreateContainerConfigError` stating that the container has `runAsNonRoot` set and would run as root — UID 0. The distinction between "scheduled" and "started" is what is being tested, so say both halves. See [how namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- For the HPA questions, give an ordered path rather than guesses: `kubectl describe hpa` to read the conditions, then check whether metrics-server is healthy and returning data, whether the Deployment's containers declare CPU or memory `requests` (without requests, utilisation-based scaling cannot compute a target), whether the maximum replica count is already reached, and whether the cluster simply has no room to schedule new Pods. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- "It worked and then stopped" points at change rather than misconfiguration. Say that explicitly and ask what changed — a metrics-server upgrade, a removed `requests` block, a new quota, an exhausted node pool. Interviewers reward candidates who ask that question.
- Debug Ingress from the outside in: DNS resolves to the load balancer, the ingress controller Pods are running, the Ingress object has an address assigned, the `ingressClassName` matches the controller, the backend Service has non-empty `Endpoints`, the Service `targetPort` matches the container port, and TLS secrets exist in the right namespace. Empty Endpoints is the single most common cause — say so. See [exposing an application to the outside world](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md) and [what a Service is](../kubernetes/what-is-a-service-in-kubernetes.md).
- The five-teams storage question wants `ResourceQuota` scoped per namespace, specifically `requests.storage` and `persistentvolumeclaims` counts, optionally per StorageClass, with `LimitRange` for defaults. Mention that quotas apply to requests at admission time, so a team cannot exceed them by editing a running PVC. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md).
- Service discovery should cover both halves: DNS through CoreDNS resolving `service.namespace.svc.cluster.local`, and the Service-to-Endpoints mapping that kube-proxy programs into iptables or IPVS rules. Add headless Services for StatefulSet Pod-level addressing. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md) and [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- Leap seconds matter because a repeated or skipped second breaks monotonic-time assumptions: timers fire twice, distributed leases and certificate validity get confused, and some kernels have historically hung. The expected mitigation is NTP leap smearing rather than a step adjustment. Being aware of the failure mode is enough at this level.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you do capacity planning?]] (`#230`): [How do you do capacity planning?](../site-reliability-engineering/how-do-you-do-capacity-planning.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What are Service Level Objectives (SLOs)?]] (`#97`): [What are Service Level Objectives (SLOs)?](../site-reliability-engineering/what-are-service-level-objectives-slos.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
