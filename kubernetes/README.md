---
title: "Kubernetes"
category: "Kubernetes"
tags:
  - devops
  - kubernetes
  - index
---

# Kubernetes

The control plane, the workload objects you touch daily, and the networking abstractions that make Pods reachable.

**39 questions** · 🟢 Beginner: 5 · 🟡 Intermediate: 26 · 🔴 Advanced: 8

## Questions

| #   | Question                                                                                                                                                                                                         | Difficulty      |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 11  | [What is Kubernetes?](./what-is-kubernetes.md)                                                                                                                                                                   | 🟢 Beginner     |
| 12  | [What are the main components of Kubernetes architecture?](./what-are-the-main-components-of-kubernetes-architecture.md)                                                                                         | 🟡 Intermediate |
| 13  | [What is a Pod in Kubernetes?](./what-is-a-pod-in-kubernetes.md)                                                                                                                                                 | 🟢 Beginner     |
| 14  | [What is a Service in Kubernetes?](./what-is-a-service-in-kubernetes.md)                                                                                                                                         | 🟢 Beginner     |
| 15  | [Explain the difference between Docker Swarm and Kubernetes](./explain-the-difference-between-docker-swarm-and-kubernetes.md)                                                                                    | 🟡 Intermediate |
| 234 | [How do you troubleshoot a Pod stuck in Pending or CrashLoopBackOff?](./how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)                                                                   | 🟡 Intermediate |
| 255 | [How do liveness, readiness, and startup probes differ?](./how-do-liveness-readiness-and-startup-probes-differ.md)                                                                                               | 🟡 Intermediate |
| 256 | [How do you control which node a Pod runs on?](./how-do-you-control-which-node-a-pod-runs-on.md)                                                                                                                 | 🟡 Intermediate |
| 257 | [How does RBAC work in Kubernetes?](./how-does-rbac-work-in-kubernetes.md)                                                                                                                                       | 🟡 Intermediate |
| 258 | [How do you autoscale workloads and nodes in Kubernetes?](./how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md)                                                                                           | 🔴 Advanced     |
| 259 | [How do you expose an application running in Kubernetes to the outside world?](./how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md)                                                 | 🟡 Intermediate |
| 403 | [How do you troubleshoot a Kubernetes Service that has no endpoints?](./how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md)                                                                   | 🟡 Intermediate |
| 404 | [How do you debug DNS resolution failures inside a Kubernetes cluster?](./how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md)                                                               | 🟡 Intermediate |
| 405 | [How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?](./how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md)                                | 🔴 Advanced     |
| 406 | [How do you debug a Kubernetes Ingress that is not routing traffic?](./how-do-you-debug-a-kubernetes-ingress-that-is-not-routing-traffic.md)                                                                     | 🟡 Intermediate |
| 407 | [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](./how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)                                                         | 🟡 Intermediate |
| 408 | [How do you troubleshoot a Kubernetes Job or CronJob that never completes?](./how-do-you-troubleshoot-a-kubernetes-job-or-cronjob-that-never-completes.md)                                                       | 🟡 Intermediate |
| 409 | [How do you handle node pressure and Pod evictions in Kubernetes?](./how-do-you-handle-node-pressure-and-pod-evictions-in-kubernetes.md)                                                                         | 🔴 Advanced     |
| 410 | [How do you perform and roll back a rolling update in Kubernetes?](./how-do-you-perform-and-roll-back-a-rolling-update-in-kubernetes.md)                                                                         | 🟡 Intermediate |
| 442 | [What is the difference between a ConfigMap and a Secret in Kubernetes?](./what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)                                                             | 🟡 Intermediate |
| 443 | [How does persistent storage work in Kubernetes?](./how-does-persistent-storage-work-in-kubernetes.md)                                                                                                           | 🟡 Intermediate |
| 444 | [How do requests, limits, and QoS classes work in Kubernetes?](./how-do-requests-limits-and-qos-classes-work-in-kubernetes.md)                                                                                   | 🟡 Intermediate |
| 445 | [What are init containers and sidecar containers in Kubernetes?](./what-are-init-containers-and-sidecar-containers-in-kubernetes.md)                                                                             | 🟡 Intermediate |
| 446 | [What is a PodDisruptionBudget and when do you need one?](./what-is-a-poddisruptionbudget-and-when-do-you-need-one.md)                                                                                           | 🔴 Advanced     |
| 447 | [How does Pod networking and service discovery work in Kubernetes?](./how-does-pod-networking-and-service-discovery-work-in-kubernetes.md)                                                                       | 🔴 Advanced     |
| 448 | [What happens when a Kubernetes control-plane node or etcd fails?](./what-happens-when-a-kubernetes-control-plane-node-or-etcd-fails.md)                                                                         | 🔴 Advanced     |
| 449 | [How do you troubleshoot a Kubernetes node that is NotReady?](./how-do-you-troubleshoot-a-kubernetes-node-that-is-notready.md)                                                                                   | 🟡 Intermediate |
| 520 | [How does the Kubernetes Gateway API evolve beyond standard Ingress resources?](./how-does-the-kubernetes-gateway-api-evolve-beyond-standard-ingress-resources.md)                                               | 🟡 Intermediate |
| 521 | [What is the difference between Kubernetes Horizontal Pod Autoscaler and Vertical Pod Autoscaler?](./what-is-the-difference-between-kubernetes-horizontal-pod-autoscaler-and-vertical-pod-autoscaler.md)         | 🟡 Intermediate |
| 522 | [How does Kubernetes In-Place Pod Resource Resizing work and what problem does it solve?](./how-does-kubernetes-in-place-pod-resource-resizing-work-and-what-problem-does-it-solve.md)                           | 🔴 Advanced     |
| 523 | [What are Kubernetes Ephemeral Containers and how are they used for zero-downtime debugging?](./what-are-kubernetes-ephemeral-containers-and-how-are-they-used-for-zero-downtime-debugging.md)                   | 🟡 Intermediate |
| 524 | [What is the difference between Mutating and Validating Admission Webhooks in Kubernetes?](./what-is-the-difference-between-mutating-and-validating-admission-webhooks-in-kubernetes.md)                         | 🟡 Intermediate |
| 525 | [How does Kubernetes Leader Election work for HA control planes and custom controllers?](./how-does-kubernetes-leader-election-work-for-ha-control-planes-and-custom-controllers.md)                             | 🔴 Advanced     |
| 526 | [What is Kubernetes Topology Spread Constraints and how does it differ from Pod Anti-Affinity?](./what-is-kubernetes-topology-spread-constraints-and-how-does-it-differ-from-pod-anti-affinity.md)               | 🟡 Intermediate |
| 527 | [How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?](./how-does-coredns-resolve-services-in-kubernetes-and-how-do-you-troubleshoot-dns-latency-bottlenecks.md) | 🟡 Intermediate |
| 528 | [What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?](./what-is-the-container-network-interface-cni-and-how-do-overlay-and-routed-cni-plugins-differ.md)             | 🟡 Intermediate |
| 529 | [What are Kubernetes Finalizers and how do you resolve a namespace stuck in the Terminating state?](./what-are-kubernetes-finalizers-and-how-do-you-resolve-a-namespace-stuck-in-the-terminating-state.md)       | 🟡 Intermediate |
| 530 | [How do Pod Disruption Budgets (PDB) protect application availability during cluster maintenance?](./how-do-pod-disruption-budgets-pdb-protect-application-availability-during-cluster-maintenance.md)           | 🟢 Beginner     |
| 531 | [What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?](./what-is-the-difference-between-service-types-clusterip-nodeport-loadbalancer-and-externalname.md)          | 🟢 Beginner     |

## What interviewers probe here

- What each control-plane component does when you run `kubectl apply`.
- Service types and when each is appropriate.
- Why Pods are ephemeral and what that implies for state.

---

[⬅ Back to all topics](../README.md)
