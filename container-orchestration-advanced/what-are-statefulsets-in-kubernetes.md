---
title: "What are StatefulSets in Kubernetes?"
id: 81
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
---

# What are StatefulSets in Kubernetes?

**Short answer:** A StatefulSet manages pods that need stable identity - a predictable name, stable network hostname, and their own persistent storage that survives rescheduling - making it the workload type for databases and other stateful systems.

## Detail

**What it guarantees, and a Deployment does not**

- **Stable, ordinal names.** Pods are `web-0`, `web-1`, `web-2`, not random suffixes. A rescheduled `web-0` is still `web-0`.
- **Stable network identity.** Combined with a headless Service, each pod gets a DNS name: `web-0.web.default.svc.cluster.local`. Cluster members can therefore find each other reliably.
- **Stable storage.** `volumeClaimTemplates` creates one PersistentVolumeClaim per pod, and the same pod always reattaches to the same volume.
- **Ordered operations.** Pods are created 0, 1, 2 and terminated in reverse; each waits for the previous to be Ready. `podManagementPolicy: Parallel` disables this when ordering is unnecessary.
- **Ordered, controlled rollouts** with `partition` for staged canary updates of the set.

**Important caveats.** Deleting a StatefulSet does not delete its PVCs - deliberate, so data is not lost by accident, but it means manual cleanup. Scaling down leaves the volumes behind. And a StatefulSet gives you _identity_, not clustering: replication, leader election, and failover are still the application's job, which is why operators exist for databases.

## Example

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: postgres }
spec:
  serviceName: postgres # must be a headless Service
  replicas: 3
  selector: { matchLabels: { app: postgres } }
  template:
    metadata: { labels: { app: postgres } }
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: postgres
          image: postgres:16
          ports: [{ containerPort: 5432, name: pg }]
          volumeMounts: [{ name: data, mountPath: /var/lib/postgresql/data }]
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: gp3
        resources: { requests: { storage: 100Gi } }
```

## Interview tips

- The headless Service requirement is the detail people forget - mention it unprompted.
- "PVCs are not deleted with the StatefulSet" is a favourite follow-up.
- A strong closing point: for production databases, prefer a managed service or a mature operator over a hand-rolled StatefulSet.

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
