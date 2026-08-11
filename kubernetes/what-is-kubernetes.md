---
title: "What is Kubernetes?"
id: 11
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# What is Kubernetes?

**Short answer:** Kubernetes is an open-source container orchestrator that runs containerised workloads across a cluster of machines, continuously reconciling actual state towards the desired state you declare.

## Detail

You do not tell Kubernetes _how_ to run things. You declare what you want - "five replicas of this image, reachable on port 80, with these resource limits" - and a set of controllers works continuously to make reality match. If a node dies, the pods on it are rescheduled. If a pod fails its health check, it is restarted. This reconciliation loop is the central idea.

What it provides out of the box:

- **Scheduling** - placing pods on nodes based on resource requests, affinity rules, taints, and topology spread.
- **Self-healing** - restarting failed containers, replacing pods, and refusing traffic to unready ones.
- **Service discovery and load balancing** - stable virtual IPs and DNS names in front of ephemeral pods.
- **Rollouts and rollbacks** - declarative, incremental deployment with automatic revert on failure.
- **Configuration and secrets** - injected as environment variables or mounted files, separate from images.
- **Autoscaling** - of pods (HPA/VPA) and of nodes (Cluster Autoscaler).
- **Extensibility** - Custom Resource Definitions and operators let you manage anything with the same model.

Originating from Google's internal Borg system, it is now the CNCF's flagship project and the de facto standard across every cloud.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels: { app: web }
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports: [{ containerPort: 80 }]
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits: { cpu: 500m, memory: 256Mi }
          readinessProbe:
            httpGet: { path: /healthz, port: 80 }
```

## Interview tips

- Lead with the reconciliation loop and declarative model - that is the conceptual core.
- Be ready for "when would you _not_ use Kubernetes?" A single small service is better served by a managed platform.
- Know that Kubernetes gives you primitives, not a platform; teams still build the developer experience on top.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
