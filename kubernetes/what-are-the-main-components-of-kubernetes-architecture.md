---
title: "What are the main components of Kubernetes architecture?"
id: 12
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# What are the main components of Kubernetes architecture?

**Short answer:** A control plane (API server, etcd, scheduler, controller manager, cloud controller manager) makes decisions about the cluster, and node components (kubelet, kube-proxy, container runtime) execute them on each worker machine.

## Detail

**Control plane**

- **kube-apiserver** - the only component that talks to etcd, and the front door for everything else. It authenticates, authorises, validates, runs admission control, and persists objects. All communication flows through it.
- **etcd** - the distributed key-value store holding all cluster state. It is the single source of truth, and the thing you back up.
- **kube-scheduler** - watches for pods with no assigned node and picks one, filtering on resource requests, taints/tolerations, and affinity, then scoring the survivors.
- **kube-controller-manager** - runs the reconciliation loops (deployment, replicaset, node, endpoint, service account controllers) that drive actual state towards desired state.
- **cloud-controller-manager** - cloud-specific control loops for load balancers, nodes, and routes.

**Node components**

- **kubelet** - the agent on each node. It takes pod specs from the API server, tells the runtime to start containers, runs probes, and reports status.
- **kube-proxy** - programmes iptables or IPVS rules so Service virtual IPs route to healthy pod endpoints.
- **container runtime** - containerd or CRI-O, which actually runs the containers via the CRI.

**Add-ons** - CoreDNS for cluster DNS, a CNI plugin for pod networking, and metrics-server for autoscaling inputs.

## Example

What happens on `kubectl apply -f deployment.yaml`:

```text
kubectl → apiserver (authn/authz/admission) → etcd
deployment controller → creates ReplicaSet → ReplicaSet controller → creates Pods (nodeName empty)
scheduler → binds Pod to a Node
kubelet on that node → CRI → containerd → runc → container running
kubelet → reports status → apiserver → etcd
```

## Interview tips

- Walking through that `kubectl apply` trace is the strongest way to answer this question.
- Emphasise that only the API server touches etcd - it explains the security and backup story.
- Mention control-plane HA: three or five etcd members for quorum.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
