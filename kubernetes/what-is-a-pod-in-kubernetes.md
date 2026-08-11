---
title: "What is a Pod in Kubernetes?"
id: 13
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# What is a Pod in Kubernetes?

**Short answer:** A Pod is the smallest deployable unit in Kubernetes - one or more containers that share a network namespace, IP address, and storage volumes, and are always scheduled together on the same node.

## Detail

Containers in a pod share a network namespace, so they reach each other on `localhost` and share one IP address and port space. They can share volumes, which makes tightly-coupled helper patterns possible.

Pods are **ephemeral and disposable**. They are never repaired in place - a failed pod is replaced by a new one with a new IP. That is why you never point a client at a pod IP; you point it at a Service.

Multi-container patterns:

- **Sidecar** - a companion container adding capability: a log shipper, a service-mesh proxy, a config reloader.
- **Init containers** - run to completion before app containers start; used for migrations, waiting on dependencies, or fetching secrets.
- **Ambassador / adapter** - proxying outbound connections, or reshaping the app's metrics output.

Pods define resource `requests` (used for scheduling) and `limits` (enforced at runtime), plus probes: `startupProbe`, `readinessProbe` (should this pod receive traffic?), and `livenessProbe` (should this container be restarted?).

## Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  initContainers:
    - name: migrate
      image: myapp:1.4.0
      command: ["./migrate", "up"]
  containers:
    - name: app
      image: myapp:1.4.0
      ports: [{ containerPort: 8080 }]
      volumeMounts: [{ name: logs, mountPath: /var/log/app }]
    - name: log-shipper # sidecar, same volume
      image: fluent-bit:3.1
      volumeMounts: [{ name: logs, mountPath: /var/log/app, readOnly: true }]
  volumes:
    - name: logs
      emptyDir: {}
```

## Interview tips

- "Why not one container per pod always?" - because sidecars need the shared network and filesystem.
- Be precise on readiness vs liveness; confusing them causes real outages (a failing liveness probe restart-loops a healthy-but-slow app).
- In practice you rarely create bare Pods - Deployments, StatefulSets, and Jobs create them for you.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
