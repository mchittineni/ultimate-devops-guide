---
title: "What are the 12-Factor App methodology principles and how do they map to Kubernetes deployment patterns?"
id: 602
category: "Cloud Native Architecture"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - cloud-native
  - 12-factor
  - kubernetes
  - architecture
quiz:
  stem: "How does Kubernetes implement the 12-Factor App principle of 'Disposability' (Factor IX: fast startup and graceful shutdown)?"
  options:
    - "By keeping pods running in memory for 30 days after deletion"
    - "By sending a SIGTERM signal to container PID 1 and granting a `terminationGracePeriodSeconds` window to drain connections before issuing SIGKILL"
    - "By compiling source code directly into Linux kernel space"
    - "By requiring all pods to run as singletons"
  answer: 2
  explanation: "Disposability requires apps to stop cleanly on short notice. Kubernetes sends SIGTERM, waits for termination grace period for graceful drain, and issues SIGKILL only if the app fails to stop."
---

# What are the 12-Factor App methodology principles and how do they map to Kubernetes deployment patterns?

**Short answer:** The Twelve-Factor App, written by Heroku engineers in 2011 and open-sourced for community revision in 2024, describes how to build services that are portable and disposable. Kubernetes assumes most of it: config through ConfigMaps and Secrets, stateless Pods scaled by replicas and the HPA, disposability through `SIGTERM` plus a grace period, logs as `stdout` streams collected by a node agent, and admin processes as Jobs. The mapping is not perfect - factor III's "config in environment variables" is weaker for secrets than mounted files or a secrets manager, and stateful workloads legitimately break factor VI with StatefulSets.

## Detail

| Factor                 | Principle                             | Kubernetes pattern                                                                                     |
| ---------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| I. Codebase            | One repo, many deploys                | One image built per commit, promoted through environments (GitOps overlays per environment)            |
| II. Dependencies       | Declare and isolate                   | Everything in the image; no reliance on the node's packages                                            |
| III. Config            | Config in the environment             | ConfigMaps and Secrets as env vars or mounted files; External Secrets / CSI driver for secret managers |
| IV. Backing services   | Attached resources, swappable by URL  | Services, DNS names, and connection strings from config; `ExternalName` or endpoints for external ones |
| V. Build, release, run | Strictly separate stages              | CI builds an immutable image (by digest); a release is image + config; the cluster only runs it        |
| VI. Processes          | Stateless, share-nothing              | Deployments; state in databases, caches, object storage; `emptyDir` is scratch only                    |
| VII. Port binding      | Self-contained, exports a port        | `containerPort` + Service; no app server injected at runtime                                           |
| VIII. Concurrency      | Scale out via processes               | `replicas`, HorizontalPodAutoscaler, KEDA for queue-driven scaling                                     |
| IX. Disposability      | Fast start, graceful stop             | Probes, `SIGTERM` handling, `preStop`, `terminationGracePeriodSeconds`                                 |
| X. Dev/prod parity     | Keep environments alike               | Same image and chart everywhere; kind/k3d or preview namespaces for development                        |
| XI. Logs               | Logs as event streams                 | Write to `stdout`/`stderr`; Fluent Bit or the OpenTelemetry Collector ships them                       |
| XII. Admin processes   | One-off tasks in the same environment | Jobs and CronJobs using the same image, e.g. database migrations                                       |

**Where the mapping needs care**

- **Secrets in env vars** leak into crash dumps, `kubectl describe`, and child processes; mounted files (which can rotate) or a secrets manager are the safer reading of factor III.
- **Disposability** requires the app to stop accepting work on `SIGTERM` while endpoints are removed - a short `preStop` sleep avoids dropping requests during that race.
- **Migrations as admin processes** need ordering (a Job or Helm hook before the new version rolls out) and backward-compatible schema changes.
- **Stateful systems** (databases, brokers) run as StatefulSets with persistent volumes by design; Twelve-Factor describes the stateless services around them.
- The original text predates health endpoints, telemetry, and supply-chain concerns; modern practice adds probes, OpenTelemetry, and signed, scanned images.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders }
spec:
  replicas: 3 # VIII concurrency (HPA can own this)
  selector: { matchLabels: { app: orders } }
  template:
    metadata: { labels: { app: orders } }
    spec:
      terminationGracePeriodSeconds: 30 # IX disposability
      containers:
        - name: orders
          image: ghcr.io/example/orders@sha256:3f1c... # V immutable build by digest
          ports: [{ containerPort: 8080 }] # VII port binding
          envFrom: [{ configMapRef: { name: orders-config } }] # III config
          volumeMounts: [{ name: db-creds, mountPath: /var/run/secrets/db, readOnly: true }]
          lifecycle:
            preStop: { sleep: { seconds: 5 } } # let endpoints update before shutdown
          readinessProbe: { httpGet: { path: /ready, port: 8080 } }
      volumes:
        - name: db-creds
          secret: { secretName: orders-db } # secrets as files, not env vars
---
apiVersion: batch/v1
kind: Job # XII admin process, same image
metadata: { name: orders-migrate-4-2-0 }
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: ghcr.io/example/orders@sha256:3f1c...
          args: ["migrate", "up"]
```

## Interview tips

- Map each factor to a concrete Kubernetes object rather than reciting the list.
- Call out the mismatches - secrets in env vars, stateful workloads, migrations ordering - because that shows judgement.
- Explain disposability precisely: `SIGTERM`, stop accepting new work, drain, exit before the grace period ends, with `preStop` covering the endpoint-update race.
- Mention that the methodology is now community-maintained and that modern additions (health probes, telemetry, supply-chain security) fill its gaps.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
