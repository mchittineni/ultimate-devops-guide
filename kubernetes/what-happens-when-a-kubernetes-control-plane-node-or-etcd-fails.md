---
title: "What happens when a Kubernetes control-plane node or etcd fails?"
id: 448
category: "Kubernetes"
difficulty: "Advanced"
tags:
  - devops
  - kubernetes
  - interview-questions
  - scalability-and-high-availability
  - incident-management
---

# What happens when a Kubernetes control-plane node or etcd fails?

**Short answer:** Running workloads keep running. The control plane is the _reconciliation_ layer, not the data path: kubelets keep their Pods alive from their local state, kube-proxy's rules stay programmed, and traffic keeps flowing through Services and load balancers. What you lose is **change** - no new scheduling, no rollouts, no scaling, no `kubectl`, no Service/endpoint updates, and no self-healing, so a Pod or node that fails during the outage is _not_ replaced. With three control-plane nodes, losing one is a non-event: the API servers are stateless and behind a load balancer, the controller-manager and scheduler re-elect a leader in seconds, and etcd still has 2 of 3 for quorum. Losing **two of three** is the real failure - etcd loses quorum and goes **read-only**, so the whole control plane stops accepting writes even though the API may still answer reads.

## Detail

### What breaks, and what does not

| Still works                                        | Stops working                                                                   |
| -------------------------------------------------- | ------------------------------------------------------------------------------- |
| Running Pods and their traffic                     | Creating, deleting, or updating any object                                      |
| kube-proxy / eBPF rules already programmed         | Endpoint and EndpointSlice updates (so a Pod that dies keeps receiving traffic) |
| CoreDNS answering from its existing config         | New Service/DNS records                                                         |
| An Ingress/LB routing to existing Pods             | Rollouts, scale, HPA, cluster autoscaler                                        |
| Kubelet restarting a crashed container on its node | Rescheduling Pods from a failed node                                            |
| Node-local storage mounts                          | New volume attach/detach                                                        |
| Metrics and logs from node agents                  | `kubectl` of any kind, the dashboard, CI deployments                            |

The key operational sentence: **a control-plane outage converts your cluster from self-healing into static**. That is survivable for a while, and it is exactly why an incident here is urgent but not usually customer-visible in the first minutes.

### Quorum arithmetic - the bit people get wrong

etcd uses Raft, so it needs a **majority** (`n/2 + 1`) to commit a write:

| etcd members | Quorum | Failures tolerated               |
| ------------ | ------ | -------------------------------- |
| 1            | 1      | 0                                |
| 3            | 2      | **1**                            |
| 5            | 3      | **2**                            |
| 4            | 3      | 1 (no better than 3, and slower) |

Hence odd numbers only, and hence three control-plane nodes across three availability zones. When quorum is lost, etcd serves reads from its local state but refuses writes; the API server surfaces this as timeouts and `etcdserver: request timed out` on every mutation. Recovery is either restoring the failed members (preferred - the surviving member catches them up) or, in the worst case, a **snapshot restore** onto a new single-member cluster followed by re-adding peers.

Two more etcd realities worth naming:

- **etcd is disk-latency-sensitive.** Raft commits an fsync per write; if disk write latency (`etcd_disk_wal_fsync_duration_seconds`) exceeds ~10 ms at p99, you get leader-election churn and a control plane that feels broken while nothing has "failed". Give etcd dedicated fast SSD, never a network filesystem, and watch `etcd_server_leader_changes_seen_total`.
- **When etcd latency spikes above a few hundred milliseconds**, the scheduler slows (it cannot bind Pods), controllers fall behind on their watches, and the API server starts shedding load and returning 429/504 - so the whole cluster feels slow even though no component has crashed. That is the "why does the cluster feel slow?" answer.

### One control-plane node versus three

- **Single control-plane node down**: Pods keep running, `kubectl` is dead, nothing reconciles. Recoverable by restarting the node - and if etcd's data directory survives, no data is lost. This is why a single-node control plane is a lab topology, not production.
- **Three nodes, one down**: no user-visible impact. API server load is redistributed by the LB; the scheduler and controller-manager run active-passive with a leader lease, so a new leader takes over within a lease period. Do not start a cluster upgrade in this state.
- **Managed clusters (EKS/GKE/AKS)**: the provider runs and heals the control plane across zones, and etcd is their problem - which is a legitimate answer to "how do you make the control plane HA?" You still own worker capacity, the API server's request budget (watch out for a chatty controller exhausting it), and private-endpoint reachability.

### Making it survivable

1. **Three (or five) control-plane nodes across distinct AZs**, behind a load balancer with a health check on `/readyz`.
2. **Back up etcd on a schedule**, store snapshots off-cluster, and **practise the restore**. An untested etcd backup is a rumour. `etcdctl snapshot save`, plus certificate material and any static manifests, is the complete recovery set.
3. **Monitor the control plane itself**: `apiserver_request_duration_seconds`, `apiserver_current_inflight_requests`, `etcd_disk_wal_fsync_duration_seconds`, `etcd_server_has_leader`, leader-change counters, and certificate expiry. Expired control-plane certificates are a self-inflicted outage that looks identical to a node failure.
4. **Protect the API server** with Priority and Fairness (APF) so one runaway client cannot starve kubelets, and keep `--max-requests-inflight` sane.
5. **Design workloads not to need the control plane** during an incident: readiness-gated Services, no in-cluster dependency on the API for the request path, PDBs and spread so a single node loss is absorbed.
6. **Know your worker-side failure story too**: if a _worker_ node dies, the node controller marks it `NotReady` after `node-monitor-grace-period` (~40 s), then Pods get evicted after `tolerationSeconds` (~5 min by default) and rescheduled - which is why a Pod can take five minutes to come back after a node failure, and why that number is a tunable.

## Example

```bash
# Health of the control plane and etcd quorum
kubectl get nodes -l node-role.kubernetes.io/control-plane
kubectl get --raw='/readyz?verbose' | tail -20
kubectl -n kube-system get lease | grep -E 'scheduler|controller-manager'  # who holds it

# etcd membership and leader (from a control-plane node)
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint status --write-out=table
# expect: one IS LEADER=true, all with the same RAFT TERM, low DB SIZE growth
```

```bash
# Backup - and the restore you must actually rehearse
etcdctl snapshot save /backup/etcd-$(date +%F-%H%M).db   # + copy /etc/kubernetes/pki
etcdutl snapshot status /backup/etcd-2026-08-10-0200.db --write-out=table

# Disaster restore onto a rebuilt member (control plane stopped first)
etcdutl snapshot restore /backup/etcd-2026-08-10-0200.db \
  --name cp-1 --initial-cluster cp-1=https://10.0.1.10:2380 \
  --initial-advertise-peer-urls https://10.0.1.10:2380 \
  --data-dir /var/lib/etcd-restored
# then point the etcd static Pod at the new data dir, start it, re-add peers
```

```text
Alerts that catch this before users do

  etcd_server_has_leader == 0                       for 1m   -> quorum at risk
  increase(etcd_server_leader_changes_seen_total[15m]) > 3    -> disk or network sick
  histogram_quantile(0.99,
    rate(etcd_disk_wal_fsync_duration_seconds_bucket[5m])) > 0.01   -> slow disk
  apiserver_current_inflight_requests near the limit           -> a client is abusing the API
  control-plane certificate expiry < 30d                       -> scheduled outage otherwise
```

## Interview tips

- Lead with the headline: existing workloads and traffic are unaffected, because the control plane is the reconciliation layer, not the data path. Then list what you lose - scheduling, rollouts, scaling, self-healing, `kubectl`.
- Immediately add the sharp edge: **the cluster stops self-healing**, so a Pod or node failing during the outage is not replaced. That is the risk that makes it an incident.
- Do the quorum arithmetic out loud. Three nodes tolerate one failure, five tolerate two, four are worse than three. Losing two of three makes etcd read-only.
- Mention that etcd is fsync-bound and that slow disks cause leader churn - "the cluster feels slow, nothing has crashed" is a real scenario and few candidates can explain it.
- If asked whether you can write to etcd directly: technically yes with `etcdctl`, and you should never do it - it bypasses validation, admission, and the resource version machinery, and it is how people corrupt a cluster.
- Have the worker-node counterpart ready: `NotReady` after ~40 s, eviction and rescheduling after the ~5 minute toleration, which explains recovery time.
- Close on preparation, not theory: three control-plane nodes across AZs, scheduled etcd snapshots stored off-cluster, a **rehearsed** restore, and certificate-expiry monitoring. See [how do you back up and restore a Kubernetes cluster](../container-orchestration-advanced/how-do-you-back-up-and-restore-a-kubernetes-cluster.md), [the main components of Kubernetes architecture](./what-are-the-main-components-of-kubernetes-architecture.md), [troubleshooting a node that is NotReady](./how-do-you-troubleshoot-a-kubernetes-node-that-is-notready.md), and [executing a disaster recovery failover](../backup-and-disaster-recovery/how-do-you-execute-a-disaster-recovery-failover-with-minimal-rto-and-rpo.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [[How do you run an application across multiple Kubernetes clusters?]] (`#414`): [How do you run an application across multiple Kubernetes clusters?](../container-orchestration-advanced/how-do-you-run-an-application-across-multiple-kubernetes-clusters.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
