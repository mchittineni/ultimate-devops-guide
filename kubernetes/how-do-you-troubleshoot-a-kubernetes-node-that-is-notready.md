---
title: "How do you troubleshoot a Kubernetes node that is NotReady?"
id: 449
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - linux-administration
  - incident-management
---

# How do you troubleshoot a Kubernetes node that is NotReady?

**Short answer:** `NotReady` means the **kubelet has stopped posting a healthy status** to the API server - either because the kubelet is down, because it cannot reach the API server, or because it is reporting a condition that makes the node unusable (disk, memory, PID pressure, or no working network plugin). So the diagnosis is a fixed order: first `kubectl describe node` to read the **conditions and their reasons**, which usually names the cause outright; if the reason is generic (`NodeStatusUnknown`, "kubelet stopped posting node status"), get onto the host and check the kubelet and container runtime with `systemctl` and `journalctl`; then check the three resources that push a node out of Ready (disk, memory, PIDs) and the CNI. When one node out of thirty is affected, the cause is local - kubelet, runtime, disk, or that node's network path. When many go `NotReady` together, stop looking at nodes and look at the control plane, the CNI DaemonSet, or a certificate.

## Detail

### What the status actually means

The kubelet updates its `Node` object every few seconds. The node controller marks it `NotReady` if no update arrives within `node-monitor-grace-period` (~40 s), then:

```text
kubelet healthy ──> Ready=True
   │ no status posted for ~40s      -> Ready=Unknown, reason NodeStatusUnknown
   │ kubelet posts an unhealthy condition -> Ready=False with a specific reason
   ▼
node.kubernetes.io/not-ready:NoExecute taint applied
   │
   └─ Pods evicted after tolerationSeconds (default ~300s) and rescheduled elsewhere
```

That timeline answers the frequent follow-up "how long until it recovers or the Pods move?" - roughly 40 seconds to be noticed, about 5 minutes before Pods are evicted, and both are tunable. Pods on the node are **not** killed instantly, which is deliberate: a brief kubelet restart should not cause mass rescheduling.

### The ordered checklist

**1. Read the conditions - they usually contain the answer.**

`kubectl describe node ip-10-0-3-14` and look at `Conditions` and `Events`:

| Condition / reason                                     | Meaning                                                      | Fix                                                                                           |
| ------------------------------------------------------ | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| `DiskPressure=True`                                    | Image/container disk or inodes low                           | Prune images/logs, grow the disk, tighten log rotation, check for a runaway log or core dumps |
| `MemoryPressure=True`                                  | Node memory below the eviction threshold                     | Find the greedy Pod, set/repair memory limits, add capacity                                   |
| `PIDPressure=True`                                     | Process/thread exhaustion                                    | A forking application or a zombie pile-up; raise `pids` limits after fixing the cause         |
| `NetworkUnavailable=True`                              | CNI plugin not initialised                                   | The CNI DaemonSet Pod on that node is failing, or `/etc/cni/net.d` is empty                   |
| `Ready=Unknown`, "kubelet stopped posting node status" | Kubelet dead, host wedged, or it cannot reach the API server | Go to the host                                                                                |
| `KubeletNotReady: container runtime not ready`         | containerd/CRI-O down or its socket missing                  | Restart and inspect the runtime                                                               |

**2. On the host - kubelet and runtime.**

```text
systemctl status kubelet containerd
journalctl -u kubelet --since -20m --no-pager   <- the single most useful command
crictl info ; crictl ps
```

Recurring root causes in kubelet logs: expired **client certificate** (`x509: certificate has expired`, common on long-lived nodes when rotation is off), a bad `--config`/kubeconfig after an upgrade, the API server endpoint unreachable, or the runtime socket gone.

**3. Resources on the host.** `df -h` and `df -ih` (inodes full while bytes look fine is a classic - lots of tiny files, or a container writing millions of log fragments), `free -m`, `dmesg -T | grep -i -E 'oom|blocked|panic'`, `uptime` for load, `iostat` for a disk that has gone read-only. A filesystem flipped to read-only by the kernel after an I/O error presents exactly as a wedged kubelet.

**4. Connectivity.** From the node: can it reach the API server endpoint on 443? Check security groups/NSGs and route tables, especially after any network change, and check for a node that failed to renew its DHCP lease or lost its route. This is the same class of problem as a node that **never joined** the cluster.

**5. Cloud/infrastructure layer.** Is the instance actually healthy? Failed instance status checks, a spot/preemptible reclaim, an autoscaling group replacing it, a kernel panic in the serial console, or a host maintenance event. On managed node groups the pragmatic fix is often to let the node be replaced rather than repaired.

### A node that will not join the cluster

Different symptom, overlapping causes, and asked just as often:

- Token or certificate: expired `kubeadm` join token, clock skew making TLS fail, missing CA hash.
- Networking: the node cannot reach the API server (SG/NSG/firewall, wrong private endpoint), or DNS cannot resolve the endpoint.
- IAM/identity: on EKS, the node's role is not mapped (historically the `aws-auth` ConfigMap, now access entries), so the kubelet authenticates but is not authorised - the node simply never appears.
- Version skew: kubelet newer than the control plane, or outside the supported skew.
- Bootstrap failure: user-data/cloud-init errored - read `/var/log/cloud-init-output.log`.
- Capacity: no IP addresses left in the subnet for the ENI, or the CNI cannot allocate.

### One node versus many

- **One node**: local. Kubelet, runtime, disk, that node's network, or the instance itself. Cordon it, drain it, fix or replace it.
- **Several at once**: look up the stack. Control-plane or etcd trouble (kubelets cannot post status), the CNI DaemonSet rolled a bad version, a cluster-wide certificate expiry, a change to the API server's load balancer or security group, or a bad AMI/node-image rollout. Do not repair nodes one by one while the cause is central.

### Making it safe while you work

Cordon first so nothing new lands on it, then drain respecting PodDisruptionBudgets; if Pods will not evict, check the PDB rather than reaching for `--force`. For hosts where the kubelet is unreachable, `kubectl debug node/<name> -it --image=busybox` gives you a privileged Pod with the host filesystem mounted - the way to investigate a node you cannot SSH into. And when the answer is "replace it", terminate the instance and let the node group rebuild rather than nursing a broken host.

## Example

```bash
# 1. triage: how many, and what do the conditions say?
kubectl get nodes -o wide | grep -v ' Ready'
kubectl describe node ip-10-0-3-14 | sed -n '/Conditions/,/Addresses/p'
kubectl get events --field-selector involvedObject.name=ip-10-0-3-14 --sort-by=.lastTimestamp

# 2. no SSH? get a shell with the host mounted at /host
kubectl debug node/ip-10-0-3-14 -it --image=busybox
chroot /host
systemctl status kubelet containerd
journalctl -u kubelet --since -20m --no-pager | tail -50

# 3. the three resources that flip a node out of Ready
df -h /var/lib/containerd /var/log ; df -ih          # inodes, not just bytes
free -m ; cat /proc/pressure/memory
dmesg -T | grep -iE 'oom-kill|read-only|I/O error|panic'

# 4. reclaim disk on a DiskPressure node
crictl images | wc -l ; crictl rmi --prune
journalctl --vacuum-size=200M

# 5. make it safe, then fix or replace
kubectl cordon ip-10-0-3-14
kubectl drain ip-10-0-3-14 --ignore-daemonsets --delete-emptydir-data
kubectl uncordon ip-10-0-3-14        # only after it is genuinely Ready again
```

```bash
# Which Pods were on it, and did they actually move?
kubectl get pods -A -o wide --field-selector spec.nodeName=ip-10-0-3-14
kubectl get pods -A --field-selector status.phase=Pending   # nowhere to reschedule?

# A node that never joined: check identity and bootstrap, not the kubelet's mood
aws eks list-access-entries --cluster-name prod         # or: kubectl -n kube-system get cm aws-auth -o yaml
kubectl get csr | grep -i pending                       # kubelet serving certs awaiting approval
```

## Interview tips

- Define `NotReady` precisely - the kubelet has stopped posting healthy status - and then say the three families of cause: kubelet/runtime down, node cannot reach the API server, or a resource pressure condition. Structure beats a list of commands.
- Give the timeline: ~40 s to be marked NotReady, ~5 min before Pods are evicted, then rescheduled. That earns credit because it explains observed behaviour rather than reciting defaults.
- Say "read the conditions first" and name what each one implies. `DiskPressure`, `MemoryPressure`, `PIDPressure`, `NetworkUnavailable` are the interview's expected vocabulary.
- Volunteer the one-node-versus-many split. Escalating to the control plane, CNI DaemonSet, or a certificate when many nodes fail together is exactly the judgement being tested by "29 of 30 nodes are Ready".
- Name the two commands that actually solve it in practice: `journalctl -u kubelet` and `kubectl describe node`. Add `kubectl debug node/...` for hosts you cannot SSH into - that detail signals real operational experience.
- Mention inodes (`df -ih`) separately from disk space, and expired kubelet certificates. Both are common and both look mysterious.
- For a node that will not join, pivot to bootstrap causes: token/cert, connectivity to the API endpoint, IAM mapping, version skew, subnet IP exhaustion, cloud-init logs. See [node pressure and Pod evictions](./how-do-you-handle-node-pressure-and-pod-evictions-in-kubernetes.md), [what happens when a control-plane node or etcd fails](./what-happens-when-a-kubernetes-control-plane-node-or-etcd-fails.md), [troubleshooting SSH failures, high CPU, and disk space on Linux](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md), and [what is a PodDisruptionBudget](./what-is-a-poddisruptionbudget-and-when-do-you-need-one.md).

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
