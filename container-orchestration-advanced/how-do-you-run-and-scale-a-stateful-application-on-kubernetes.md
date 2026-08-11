---
title: "How do you run and scale a stateful application on Kubernetes?"
id: 413
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
  - kubernetes
  - database-management-in-devops
  - scalability-and-high-availability
---

# How do you run and scale a stateful application on Kubernetes?

**Short answer:** Use a **StatefulSet** for stable identity (`app-0`, `app-1`) and per-Pod storage from `volumeClaimTemplates`, plus a **headless Service** for per-Pod DNS so members can find each other. But the platform only gives you identity, storage, and ordering - **the application still has to do the hard part**: replication, leader election, and quorum. So the real answer is that you scale a stateful system by whatever its own clustering model allows, spread replicas across zones with anti-affinity and topology spread, protect them with a PodDisruptionBudget, and for databases prefer a **purpose-built operator** over hand-written manifests. And say the honest part: `kubectl scale` adds a Pod with an empty volume - it does not add a working replica.

## Detail

### What a StatefulSet gives you, precisely

- **Stable network identity** - `checkout-0.checkout-headless.prod.svc.cluster.local` survives rescheduling, which is what clustering protocols need for peer discovery.
- **Stable per-Pod storage** - each ordinal gets its own PVC from `volumeClaimTemplates`, and `checkout-0` is reattached to _its_ volume when it restarts. Note the deliberate safety behaviour: those PVCs are **not deleted** when you scale down or delete the StatefulSet unless you set `persistentVolumeClaimRetentionPolicy`.
- **Ordered, one-at-a-time operations** - Pods are created 0→N and terminated N→0, and a rolling update goes in reverse ordinal order, waiting for each Pod to be `Ready`. `podManagementPolicy: Parallel` opts out for systems that do not need ordering.
- **`partition` in `updateStrategy`** - a built-in canary: set `partition: 3` and only ordinals ≥ 3 update, so you can validate the new version on one member before the rest.

### What it does not give you

Nothing about data. Kubernetes will not replicate your data, elect a leader, resolve split-brain, or make a fresh Pod join a cluster. This is the point most candidates miss and every interviewer probes: scaling a stateful application means **triggering the application's own join and rebalance procedure** - a new PostgreSQL replica must be seeded with a base backup and start streaming, a Kafka broker must have partitions reassigned to it, a Cassandra node must bootstrap and stream ranges, an Elasticsearch node must receive shard allocations. Scale-in is worse: removing a member usually requires draining or decommissioning it first, or you lose quorum or data. Hence: **use an operator** (CloudNativePG or Zalando for PostgreSQL, Strimzi for Kafka, ECK for Elasticsearch, Vitess for MySQL) which encodes those procedures as controllers. Writing them yourself in `initContainers` and lifecycle hooks is a project, not a manifest.

### Storage decisions that determine your architecture

- **`ReadWriteOnce` block storage** (EBS, Azure Disk, GCE PD) is the right default for databases: fast, single-writer, and **zonal** - which means a Pod can only be rescheduled into the availability zone its volume lives in. Plan for that, or the loss of one zone leaves Pods `Pending` rather than moving.
- **`ReadWriteMany`** (EFS, Azure Files, NFS) lets many Pods share a filesystem - appropriate for shared assets or legacy applications that expect a shared directory, and a poor fit for databases because of latency and locking semantics.
- **Local NVMe** gives the best performance and no mobility at all: the data dies with the node, so it only works when the application replicates (Cassandra, Kafka with replication factor > 1) and you accept a full re-stream on node loss.
- Set `reclaimPolicy: Retain` for real data, `allowVolumeExpansion: true` so you can grow, and use `VolumeSnapshot` before risky operations. See [how do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md).

### Availability under failure and maintenance

- **Spread across failure domains**: `topologySpreadConstraints` on `topology.kubernetes.io/zone` plus `podAntiAffinity` on hostname, so no two replicas share a node and no zone holds a majority of a three-member quorum.
- **A PodDisruptionBudget** (`maxUnavailable: 1`) so drains, node upgrades, and autoscaler scale-down cannot take two members at once - the difference between a rolling maintenance and a lost quorum.
- **Probes that reflect data readiness, not process liveness.** A replica still catching up must not be `Ready`, or clients will read stale data; and a liveness probe that restarts a slow-recovering database makes an incident permanent. Long `startupProbe`, conservative `livenessProbe`.
- **Graceful shutdown**: `terminationGracePeriodSeconds` long enough for a checkpoint or a clean leader handover, and a `preStop` hook that steps down leadership rather than being killed while holding it.
- **Node loss is where stateful hurts.** A `NotReady` node holding an RWO volume blocks reattachment until the volume is detached - which is why `Multi-Attach error` shows up in exactly this scenario, and why a genuinely resilient design replicates at the application layer instead of relying on volume mobility.

### And the question you should ask back

For a managed-database-shaped workload, the strongest answer includes _whether it should be in the cluster at all_. RDS, Cloud SQL, or a managed Kafka removes replication, failover, backup verification, and version upgrades from your on-call rota. Run data in Kubernetes when you need portability, when the operator ecosystem is genuinely good for that system, or when scale makes managed pricing untenable - and be able to say which of those applies. See [how do you run a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md) and [what does a DevOps engineer need to know about databases](../database-management-in-devops/what-does-a-devops-engineer-need-to-know-about-databases.md).

## Example

```yaml
apiVersion: v1
kind: Service # headless: per-Pod DNS for peer discovery, no load balancing
metadata: { name: pg-headless, namespace: data }
spec:
  clusterIP: None
  selector: { app: pg }
  ports: [{ name: pg, port: 5432 }]
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: pg, namespace: data }
spec:
  serviceName: pg-headless # required: gives pg-0.pg-headless... names
  replicas: 3
  podManagementPolicy: OrderedReady
  updateStrategy:
    type: RollingUpdate
    rollingUpdate: { partition: 2 } # canary: only pg-2 updates until you lower this
  persistentVolumeClaimRetentionPolicy:
    whenDeleted: Retain # never let a delete take the data with it
    whenScaled: Retain
  template:
    spec:
      terminationGracePeriodSeconds: 120 # time to checkpoint and hand over leadership
      affinity:
        podAntiAffinity: # never two members on one node
          requiredDuringSchedulingIgnoredDuringExecution:
            - topologyKey: kubernetes.io/hostname
              labelSelector: { matchLabels: { app: pg } }
      topologySpreadConstraints: # and never a quorum majority in one zone
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: pg } }
      containers:
        - name: pg
          image: postgres:16.4
          readinessProbe: # "ready" must mean caught up, not just listening
            exec: { command: ["pg_isready", "-U", "postgres"] }
            periodSeconds: 5
          startupProbe: # slow recovery must not be mistaken for failure
            exec: { command: ["pg_isready", "-U", "postgres"] }
            failureThreshold: 60
            periodSeconds: 10
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: gp3-retain
        resources: { requests: { storage: 200Gi } }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: pg, namespace: data }
spec:
  maxUnavailable: 1 # one member at a time, or you lose quorum during maintenance
  selector: { matchLabels: { app: pg } }
```

```bash
# Scaling out is an application operation, not just a Kubernetes one
kubectl scale statefulset pg -n data --replicas=4     # creates pg-3 + an EMPTY volume
# ...the new member still has to be seeded and join replication. With an operator:
kubectl patch cluster pg -n data --type=merge -p '{"spec":{"instances":4}}'
# the operator base-backups from the primary, starts streaming, and waits for sync

# Scale-in safely: decommission at the application layer FIRST
kubectl exec -n data pg-3 -- pg_ctl stop -m fast       # or nodetool decommission, etc.
kubectl scale statefulset pg -n data --replicas=3
kubectl get pvc -n data                               # PVCs remain by design - clean up deliberately
```

## Interview tips

- Give the split in your first breath: Kubernetes provides identity, storage, and ordering; the application provides replication, leader election, and quorum. Everything else follows from that.
- Say plainly that `kubectl scale` on a StatefulSet creates a Pod with an empty volume, not a working replica. It is the single most revealing sentence in this answer.
- Name the headless Service and _why_ it exists (per-Pod DNS for peer discovery), plus `volumeClaimTemplates` for per-ordinal storage.
- Mention that PVCs survive scale-down and deletion by default, and that `persistentVolumeClaimRetentionPolicy` is how you change it. Interviewers like this because it is both a safety feature and a cost surprise.
- Bring up zonal volumes limiting rescheduling, and local NVMe as the trade of performance for mobility. It shows you have thought about failure, not just steady state.
- Recommend an operator by name for the system in question, and be able to say what it automates: seeding, failover, backups, version upgrades.
- The `partition` field in `updateStrategy` is the detail that marks StatefulSet experience - a built-in canary for stateful rollouts.
- Finish with the architectural question: should this be managed instead? A candidate who can justify running data in Kubernetes _and_ knows when not to is the one who gets hired. See [what are StatefulSets in Kubernetes](./what-are-statefulsets-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
