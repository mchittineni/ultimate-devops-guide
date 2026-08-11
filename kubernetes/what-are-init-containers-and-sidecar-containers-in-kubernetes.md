---
title: "What are init containers and sidecar containers in Kubernetes?"
id: 445
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - cloud-native-architecture
---

# What are init containers and sidecar containers in Kubernetes?

**Short answer:** Both are extra containers in the same Pod, sharing its network namespace and volumes, but they differ in **lifecycle**. An **init container** runs to completion **before** any application container starts; several run strictly in order, and if one fails the Pod restarts it (per `restartPolicy`) and the application never starts. That makes init containers the right place for one-off preconditions: wait for a dependency, run a schema migration, fetch a secret or a config file, fix volume permissions. A **sidecar** runs _alongside_ the application for the Pod's whole life - log shipper, metrics exporter, service-mesh proxy, secret-refresher. Since Kubernetes 1.29 a sidecar is expressed properly as **an init container with `restartPolicy: Always`**, which fixes the two long-standing problems: the sidecar starts before the app and shuts down after it, and it no longer blocks Jobs from ever completing.

## Detail

### Init containers: ordering as a feature

- They run **sequentially**, each to successful completion, in the order listed. Application containers start only after the last one exits 0.
- They see the same volumes and the same Pod IP, so they can prepare state the app will consume.
- They can hold **different, more privileged** credentials or tooling than the app - the classic pattern is an init container with `curl`, `git`, or `chown` so the runtime image can stay distroless and non-root.
- A failing init container puts the Pod in `Init:Error` / `Init:CrashLoopBackOff`, and `kubectl logs <pod> -c <init-name>` is where the answer is. `kubectl describe` shows `Init Containers: 0/2 complete`.
- Their resource requests are considered separately: the Pod's effective request is `max(largest single init request, sum of app requests)`. A greedy init container can therefore make a Pod unschedulable.

Canonical uses: wait for a database or a migration to be ready, run `flyway`/`alembic` migrations exactly once per rollout, render a config template from a ConfigMap plus environment, `chown` an `emptyDir` or PVC so a non-root app can write to it, and download a model or dataset into a shared volume.

The nuance about ordering dependencies: an init container is the answer to "how do you make container A start before container B **in the same Pod**". If A and B are separate _workloads_, the answer is not an init container - it is readiness probes plus retry logic in the client, because Kubernetes deliberately does not sequence Deployments.

### Sidecars: the old way and the current way

Historically a sidecar was just another entry in `containers[]`, which caused two well-known problems:

1. **No ordering guarantee.** The app could start and issue requests before the mesh proxy or the Vault agent was ready, so the first requests failed. Teams worked around it with sleeps and readiness gates.
2. **Jobs never finished.** A `Job` completes when all its containers exit; a log shipper that never exits keeps the Job running forever. This is the standard "my CronJob never completes" cause.

The **native sidecar** (`initContainers` entry with `restartPolicy: Always`, stable from 1.29) fixes both: it starts before the app containers, keeps running, restarts independently if it dies, is **ignored** when deciding whether a Job has completed, and is terminated only after the application containers have stopped - so log lines and traces from shutdown still get shipped.

### What they share, and why that is the point

Containers in a Pod share the **network namespace** (same IP, so `localhost` works between them and ports must not collide), **IPC**, and any declared **volumes**. They do **not** share a filesystem otherwise, or a process namespace unless you set `shareProcessNamespace: true` (handy for debugging, and required for some `nsenter`-style tooling). That shared surface is exactly what makes the pattern work: the sidecar reads the app's log directory from a shared `emptyDir`, or intercepts its traffic on `localhost`.

### When not to use a sidecar

Sidecars multiply. One per Pod means CPU, memory, and startup latency per replica, plus an upgrade fan-out across every workload - the "sidecar tax". Node-level alternatives are often better:

- **Log collection**: a `DaemonSet` (Fluent Bit, Vector) reading the node's container log directory usually beats a per-Pod shipper. Use a sidecar only when the app writes to a file inside the container rather than stdout.
- **Metrics**: prefer the app exposing `/metrics` directly over an exporter sidecar, unless the software cannot be changed.
- **Service mesh**: ambient/sidecar-less modes (Istio ambient, Cilium) exist precisely to remove this cost at scale.

An **ephemeral container** (`kubectl debug`) is the right tool for temporary troubleshooting - not adding a permanent sidecar with a shell.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  template:
    spec:
      initContainers:
        # 1. classic init: block until the database answers, then migrate
        - name: wait-for-db
          image: busybox:1.36
          command:
            ["sh", "-c", 'until nc -z db 5432; do echo waiting; sleep 2; done']
        - name: migrate
          image: registry.example.com/api-migrations:1.9.0
          args: ["migrate", "up"]
          envFrom: [{ secretRef: { name: api-secrets } }]
        # 2. native sidecar: starts before the app, stops after it, restarts on its own
        - name: log-shipper
          image: fluent/fluent-bit:3.1
          restartPolicy: Always # <- this is what makes it a sidecar
          volumeMounts: [{ name: logs, mountPath: /var/log/app }]
          resources: { requests: { cpu: 20m, memory: 64Mi }, limits: { memory: 128Mi } }
      containers:
        - name: api
          image: registry.example.com/api:1.9.0
          volumeMounts: [{ name: logs, mountPath: /var/log/app }] # shared volume
          readinessProbe: { httpGet: { path: /healthz, port: 8080 } }
      volumes: [{ name: logs, emptyDir: {} }]
```

```yaml
# The Job that used to hang forever - now completes, because the sidecar is ignored
apiVersion: batch/v1
kind: Job
metadata: { name: nightly-report }
spec:
  template:
    spec:
      restartPolicy: OnFailure
      initContainers:
        - name: metrics-pusher
          image: prom/pushgateway-sidecar:latest
          restartPolicy: Always # sidecar: does not keep the Job "running"
      containers:
        - name: report
          image: registry.example.com/reporting:1.4.0
```

```bash
# Debugging init containers - the logs are per-container
kubectl get pod api-7f4c2b                       # STATUS: Init:1/2 or Init:CrashLoopBackOff
kubectl logs api-7f4c2b -c migrate               # the actual failure
kubectl logs api-7f4c2b -c wait-for-db --previous
kubectl describe pod api-7f4c2b | grep -A12 "Init Containers"

# Temporary troubleshooting without editing the Pod spec
kubectl debug -it api-7f4c2b --image=nicolaka/netshoot --target=api
```

## Interview tips

- Frame it as lifecycle: init containers run **to completion before** the app, sequentially; sidecars run **for the life of** the Pod. Say they share the Pod's network namespace and volumes, which is what makes both patterns possible.
- Give two or three concrete init-container uses - wait for a dependency, run migrations, `chown` a volume so a non-root container can write. Concrete beats definitional here.
- Volunteer the native sidecar change (`initContainers` + `restartPolicy: Always`, 1.29+) and the two problems it solves: startup ordering versus the mesh proxy, and Jobs that never complete. Very few candidates mention this, and it is current.
- If asked how to make one container start before another in the same Pod, say init container. If the two things are separate Deployments, say Kubernetes does not order workloads - use readiness probes and client retries - because that is the trap in the question.
- Mention the resource-request rule (`max(init) vs sum(app)`) if sizing comes up; it explains a Pod that will not schedule for no obvious reason.
- Push back thoughtfully on sidecar sprawl: a DaemonSet log collector or direct `/metrics` exposure is usually cheaper than a sidecar per Pod, and name the "sidecar tax". See [what is a sidecar pattern](../advanced-devops-cloud/what-is-a-sidecar-pattern.md), [running a service mesh in production without the sidecar tax](../api-gateway-and-service-mesh/how-do-you-run-a-service-mesh-in-production-without-the-sidecar-tax.md), [troubleshooting a Job or CronJob that never completes](./how-do-you-troubleshoot-a-kubernetes-job-or-cronjob-that-never-completes.md), and [what are DaemonSets in Kubernetes](../container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [[What are CustomResourceDefinitions and operators in Kubernetes?]] (`#452`): [What are CustomResourceDefinitions and operators in Kubernetes?](../container-orchestration-advanced/what-are-customresourcedefinitions-and-operators-in-kubernetes.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
