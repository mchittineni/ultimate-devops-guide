---
title: "What DevOps interview questions does Netcracker ask?"
id: 353
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - netcracker
  - kubernetes
  - linux-administration
  - network-security
  - monitoring-and-logging
  - container-orchestration-advanced
---

# What DevOps interview questions does Netcracker ask?

## Questions

**Linux and host performance**

- **What is the difference between a mount and a directory in Linux?**
- **How do you restart the HTTP service on a VM?**
- **What is disk I/O and how do you measure it?**
- **What is CPU throttling?**

**Kubernetes scheduling and RBAC**

- **What is a custom resource in Kubernetes?**
- **For a junior team member, which roles would you grant in Kubernetes?**
- **What is the difference between a Role and a RoleBinding?**
- **Which command — or what would you put in a `rolebinding.yaml` — gives read-only view access to the cluster?**
- **If I want my application deployed specifically on worker node 2, what do I do?**
- **What is the difference between `nodeSelector` and node affinity on one side, and taints and tolerations on the other?**

**Cluster operations**

- **How do you upgrade worker nodes in Kubernetes?**
- **While updating a worker node you try to drain the Pods, but some Pods are not removed from the node. What do you do?**
- **How do you monitor the cluster with Prometheus?**

**Ingress**

- **What is an Ingress?**
- **An application is configured with an Ingress but the web page will not load. What steps do you check?**

**Storage**

- **What are storage classes in Kubernetes, and what is their purpose?**
- **What is NFS?**

**Pod networking**

- **Two Pods are on the same worker node — can they communicate?**
- **Two Pods are on different worker nodes — can they communicate?**
- **How do you restrict communication between them?**
- **What must be present in a NetworkPolicy YAML file?**

## Example

```text
Netcracker — DevOps Engineer (7 YOE), reported round
21 questions

  K8s scheduling / RBAC       6   custom resources, junior-member roles,
                                  Role vs RoleBinding, view access,
                                  pin to node2, selector/affinity vs taints
  Pod networking              4   same node, different nodes, restrict,
                                  NetworkPolicy required fields
  Linux / host performance    4   mount vs directory, restart httpd,
                                  disk I/O, CPU throttling
  Cluster operations          3   worker node upgrade, drain that won't
                                  complete, Prometheus monitoring
  Ingress                     2   what it is, page won't load
  Storage                     2   storage classes and their purpose, NFS

THE INTERVIEWER'S TECHNIQUE
  The four Pod-networking questions build a staircase: can they talk on one
  node -> across nodes -> now stop them -> now write the YAML. Answer the
  first two with the flat-network model and the last two land easily.
```

## Interview tips

- The Pod-networking staircase has one underlying answer, so state the model once and reuse it: the Kubernetes network model requires that every Pod can reach every other Pod without NAT, regardless of node. So yes on the same node — usually via the node's bridge — and yes across nodes, via the CNI's overlay or native routing. Then the third question follows naturally: because the default is _allow all_, restricting traffic requires a NetworkPolicy, and until you create one nothing is blocked. Saying "the default is open, policies are opt-in" is what the sequence is testing. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md).
- For the NetworkPolicy YAML question, name the required fields precisely: `podSelector` to choose which Pods the policy applies to (an empty selector means all Pods in the namespace), `policyTypes` declaring `Ingress`, `Egress`, or both, and then `ingress`/`egress` rule blocks with `from`/`to` peers — `podSelector`, `namespaceSelector`, or `ipBlock` — plus optional `ports`. Add the two facts that show experience: policies are namespaced and apply to the _destination_ Pods, and they do nothing at all unless your CNI enforces them. See [network segmentation](../network-security/what-is-network-segmentation.md).
- The drain-that-will-not-complete question is the best operational scenario here, and there is a canonical list of causes. A PodDisruptionBudget that would be violated blocks eviction indefinitely — that is the most common. Bare Pods not owned by a controller will not be evicted without `--force`. Pods with local storage need `--delete-emptydir-data`. DaemonSet Pods are skipped and need `--ignore-daemonsets`. A long `terminationGracePeriodSeconds` or a stuck `preStop` hook makes it look hung. And there may simply be nowhere else to schedule the Pods, so eviction succeeds but the replacements stay `Pending`. Say you would `kubectl get pdb` and read the drain output first rather than reaching for `--force`. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- Deploying to a specific node has three mechanisms and the good answer distinguishes them by intent. `nodeSelector` and node affinity are _workload_ attracting itself to nodes with certain labels — affinity adds soft preferences and expressive operators. Taints and tolerations are the _node_ repelling workloads unless they explicitly tolerate it. So a `nodeName` or `nodeSelector` pins the Pod to node 2; a taint on node 2 reserves it for a class of workload. Say that pinning to a single named node is fragile because it removes the scheduler's ability to reschedule if that node dies, and that labelling a group of nodes is the production pattern. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- Role versus RoleBinding is the same shape as ClusterRole versus ClusterRoleBinding: the Role is a namespaced set of permissions on resources and verbs, and the RoleBinding grants that Role to subjects — users, groups, or service accounts. The detail worth adding is that a RoleBinding can reference a _ClusterRole_, which grants those permissions scoped to just that namespace, and that is exactly how you answer the two follow-ups. For view access, name the built-in `view` ClusterRole and bind it — cluster-wide with a ClusterRoleBinding, or namespace-scoped with a RoleBinding — and mention `kubectl create clusterrolebinding dev-view --clusterrole=view --user=alice` as the imperative form. For the junior team member, say `view` in the namespaces they work in, plus `edit` in a development namespace if they need to deploy, never `cluster-admin`, and `kubectl auth can-i --as` to verify what you granted. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- The Ingress-not-loading question deserves an ordered path, since it appears in many rounds: DNS resolves to the load balancer, the ingress controller Pods are running and its Service has an external address, the Ingress object has an `ADDRESS` assigned, `ingressClassName` matches the controller, host and path rules match the request, the backend Service has non-empty `Endpoints`, the Service `targetPort` matches the container port, and the TLS secret exists in the same namespace as the Ingress. Empty Endpoints and a mismatched ingress class are the two most common causes — say so. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- Mount versus directory is a genuinely good Linux question. A directory is a node in one filesystem's tree; a mount point is a directory where a _different_ filesystem has been grafted on, so its contents come from another device and its inode numbers and free space belong to that device. Add the practical consequences: `df -h` shows mounts not directories, `du` on a mount point measures the mounted filesystem, files hidden under a mount point still exist but are inaccessible while mounted, and a hard link cannot cross a mount boundary. See [Linux filesystem hierarchy](../linux-administration/what-is-linux-file-system-hierarchy.md).
- CPU throttling should be answered in the container context because that is where it bites: when a container exceeds its CPU _limit_, the kernel's CFS quota stops it running until the next scheduling period, which shows up as latency spikes rather than high CPU. Name the signal — `container_cpu_cfs_throttled_seconds_total` in Prometheus — and the counter-intuitive fix: lowering or removing an over-tight CPU limit can _improve_ latency, while memory limits must stay because exceeding those means `OOMKilled` instead. That contrast between CPU (throttled) and memory (killed) is the strongest point you can make here. See [how namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- For disk I/O, name the tools and the metrics that matter: `iostat -x` for utilisation, await, and queue depth, `iotop` for per-process attribution, and `pidstat -d`. Say that IOPS, throughput, and latency are three different limits and that a cloud volume has a provisioned ceiling on each, so "the disk is slow" usually means you hit the IOPS or burst-credit limit rather than that the hardware is failing. See [debugging a Linux performance problem from first principles](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md).
- Restarting HTTP is `systemctl restart httpd` or `nginx`, but the answer that earns marks adds the distinction between `restart` and `reload` — reload re-reads configuration without dropping connections — and says you would run `nginx -t` or `apachectl configtest` _before_ reloading so a syntax error does not take the service down. See [managing services in Linux](../linux-administration/how-do-you-manage-services-in-linux.md).
- Storage classes should be answered with purpose, not definition: a StorageClass names a provisioner and its parameters — volume type, IOPS, encryption, filesystem, reclaim policy, and whether expansion is allowed — so a PVC can request a _tier_ of storage rather than a specific volume, which is what makes dynamic provisioning and self-service possible. Say one class is marked default, and mention `volumeBindingMode: WaitForFirstConsumer` as the setting that stops a volume being created in the wrong availability zone. Then tie NFS in: a shared network filesystem that supports `ReadWriteMany`, which block storage generally does not, so it is what you reach for when several Pods must write the same volume.
- Custom resources should be framed as extending the API: a CustomResourceDefinition registers a new kind so `kubectl get <yourkind>` works and the object is stored in etcd like any built-in, and a controller or operator then watches it and reconciles reality to match. Say that the CRD alone does nothing without a controller — that is the point people miss.
- Prometheus monitoring of a cluster should name the components rather than just the product: kube-state-metrics for object state, node-exporter for host metrics, cAdvisor via the kubelet for container metrics, service discovery to find targets, Alertmanager for routing, and Thanos or Mimir if you need long retention. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
