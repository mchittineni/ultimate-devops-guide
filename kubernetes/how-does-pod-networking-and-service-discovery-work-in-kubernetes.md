---
title: "How does Pod networking and service discovery work in Kubernetes?"
id: 447
category: "Kubernetes"
difficulty: "Advanced"
tags:
  - devops
  - kubernetes
  - interview-questions
  - network-security
  - cloud-native-architecture
---

# How does Pod networking and service discovery work in Kubernetes?

**Short answer:** Kubernetes mandates a flat network model: **every Pod gets its own IP, and any Pod can reach any other Pod's IP directly, without NAT, across nodes**. A **CNI plugin** implements that - it allocates the IP, wires the Pod's veth pair into the node, and makes cross-node routing work (native VPC routing, or an overlay such as VXLAN/Geneve, or eBPF). Because Pod IPs are ephemeral, discovery goes through a **Service**: a stable virtual IP and a DNS name, backed by an EndpointSlice that the endpoints controller keeps in sync with the Pods matching the Service's selector. **CoreDNS** resolves `service.namespace.svc.cluster.local`, and **kube-proxy** (iptables or IPVS mode) or an eBPF dataplane programs each node so that traffic to the ClusterIP is load-balanced to a healthy Pod IP. So: two Pods on the same node talk over the node's bridge; two Pods on different nodes talk over the CNI's routing; and neither needs to know the other's IP because DNS plus Service abstraction hides it.

## Detail

### The four rules of the Kubernetes network model

1. Every Pod has a unique, routable IP within the cluster.
2. Pods can communicate with all other Pods without NAT.
3. Nodes can communicate with all Pods without NAT.
4. The IP a Pod sees for itself is the IP others see for it.

Containers **within** a Pod share the network namespace: they reach each other on `localhost` and must not both bind the same port. That is why a sidecar can intercept the app's traffic.

### What the CNI actually does

On Pod creation, the kubelet calls the CNI plugin, which: allocates an address from the node's Pod CIDR (or from the VPC, depending on plugin), creates a veth pair with one end in the Pod's namespace as `eth0` and the other on the node, and installs routes so packets leave and arrive correctly.

| Approach                                                  | Examples                           | Trade-off                                                                                                                                                                                                                 |
| --------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Native VPC routing** - Pod IPs come from the VPC subnet | AWS VPC CNI, Azure CNI, GKE native | No encapsulation overhead, Pods reachable from outside the cluster, security groups apply. **Consumes real subnet IPs**, so IP exhaustion is a genuine capacity constraint, and there are per-instance-type ENI/IP limits |
| **Overlay** - Pod IPs are cluster-internal, encapsulated  | Calico with VXLAN/IPIP, Flannel    | Independent of VPC address space, works anywhere. Encapsulation costs a little throughput and complicates packet capture                                                                                                  |
| **eBPF dataplane**                                        | Cilium, Calico eBPF                | Replaces kube-proxy's iptables with eBPF maps, better performance at scale, richer policy and observability. Newer kernel requirements                                                                                    |

This is the substance behind "Calico versus the VPC CNI": choose the VPC CNI when you want VPC-native addressing and security groups per Pod and have IP space to spare; choose Calico/Cilium when you need address-space independence, richer NetworkPolicy (including L7 or egress FQDN rules), or better performance at very high Service counts. Note the VPC CNI does not implement NetworkPolicy on its own - you add Calico or Cilium (or the newer VPC CNI network-policy agent) for that.

### From a name to a Pod: the full path

```text
app code: GET http://payments:8080/charge
   │
   ├─ DNS: /etc/resolv.conf points at the CoreDNS ClusterIP, with
   │        search prod.svc.cluster.local svc.cluster.local cluster.local
   │        -> "payments" expands to payments.prod.svc.cluster.local
   │        -> CoreDNS answers with the Service's ClusterIP  (10.96.42.7)
   │
   ├─ kube-proxy has programmed this node so that packets to 10.96.42.7:8080
   │        DNAT to one of the ready backend Pod IPs (10.244.3.19:8080)
   │        - iptables mode: a chain of probabilistic rules per Service
   │        - IPVS mode: a real load-balancer table, O(1) at scale
   │        - Cilium: an eBPF map, no iptables at all
   │
   ├─ CNI routes 10.244.3.19 to the node hosting it (VPC route or VXLAN tunnel)
   └─ veth into the Pod's netns -> the container's listening socket
```

Endpoint membership comes from the **readiness probe**: a Pod that is not Ready is removed from the EndpointSlice and stops receiving traffic. That is why "the Service has no endpoints" is almost always a selector mismatch or a failing readiness probe rather than a networking fault.

### DNS specifics interviewers probe

- **Names**: `svc.namespace.svc.cluster.local` for Services; cross-namespace access is just the longer name. Because of the `search` list, `payments` works within a namespace and `payments.prod` works across.
- **Headless Services** (`clusterIP: None`) return the **Pod IPs** directly instead of a virtual IP - the mechanism behind StatefulSet identity, where `mysql-0.mysql.prod.svc.cluster.local` resolves to one specific Pod. This is how a replicated database finds its peers.
- **`ExternalName`** Services return a CNAME to an outside hostname - the clean way to give an RDS endpoint a stable in-cluster name.
- **`dnsPolicy`** and `dnsConfig` control resolver behaviour; `ndots: 5` (the default) means unqualified external lookups try several search-domain permutations first, which is a classic latency and CoreDNS-load problem. Fully-qualifying hot external names (`api.example.com.`) or tuning `ndots` fixes it.
- **NodeLocal DNSCache** puts a per-node DNS cache in front of CoreDNS, which removes a large class of intermittent resolution timeouts under load.

### Reaching a Pod without a Service

You can, and interviewers ask: a Pod IP is directly routable inside the cluster, so `curl 10.244.3.19:8080` from another Pod works. You just should not depend on it, because the IP changes on every restart. The legitimate no-Service patterns are a headless Service (stable per-Pod DNS) or a StatefulSet's ordinal names.

### Why two healthy Pods sometimes cannot talk

Run through this list rather than guessing:

1. **NetworkPolicy** - the moment any policy selects a Pod, that direction becomes default-deny. Two Pods in the same ReplicaSet failing to talk is very often a policy with no intra-app ingress rule, or an egress policy that omits DNS (UDP/TCP 53) so name resolution fails before any connection is attempted.
2. **Namespace** - different namespaces need the qualified name; and cross-namespace policy needs `namespaceSelector`.
3. **Readiness** - not Ready means not in the EndpointSlice.
4. **Wrong port** - `targetPort` versus `containerPort`, or a `named` port that does not exist. Omitting `targetPort` makes it default to `port`, which silently works only when they happen to match.
5. **CNI or node-level** - a broken node route, MTU mismatch on an overlay (fragmentation shows up as large responses hanging while small ones work), or IP exhaustion leaving Pods without addresses.
6. **Security groups / host firewall** - with VPC-native CNIs, the VPC's rules apply to Pod traffic too.

## Example

```bash
# Prove the model from inside the cluster
kubectl run netshoot --rm -it --image=nicolaka/netshoot -- bash

# 1. resolution
cat /etc/resolv.conf                    # nameserver = CoreDNS ClusterIP, ndots:5
nslookup payments                        # short name -> via search domains
nslookup payments.prod.svc.cluster.local
nslookup mysql-0.mysql.data.svc.cluster.local   # headless -> one Pod IP

# 2. the Service's actual backends (this is what kube-proxy programmes)
kubectl get endpointslice -l kubernetes.io/service-name=payments -o wide
kubectl get pods -l app=payments -o wide         # do the IPs match? are they Ready?

# 3. direct Pod-to-Pod, bypassing the Service - proves the flat network
curl -s -m 2 http://10.244.3.19:8080/healthz

# 4. is a NetworkPolicy in the way?
kubectl get networkpolicy -n prod
kubectl describe networkpolicy default-deny -n prod
```

```yaml
# Headless Service: per-Pod DNS for a StatefulSet's peers
apiVersion: v1
kind: Service
metadata: { name: mysql, namespace: data }
spec:
  clusterIP: None # <- headless: DNS returns Pod IPs, no virtual IP, no proxying
  selector: { app: mysql }
  ports: [{ port: 3306, name: mysql }]
---
# ExternalName: give a managed database a stable in-cluster name
apiVersion: v1
kind: Service
metadata: { name: orders-db, namespace: prod }
spec:
  type: ExternalName
  externalName: orders.cluster-abc123.eu-west-1.rds.amazonaws.com
```

```yaml
# Allow intra-app traffic AND DNS - the egress rule people forget
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: payments-allow, namespace: prod }
spec:
  podSelector: { matchLabels: { app: payments } }
  policyTypes: [Ingress, Egress]
  ingress:
    - from: [{ podSelector: { matchLabels: { app: api } } }]
      ports: [{ port: 8080, protocol: TCP }]
  egress:
    - to: [{ namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } } }]
      ports: [{ port: 53, protocol: UDP }, { port: 53, protocol: TCP }] # DNS or nothing works
```

## Interview tips

- Open with the four network-model rules, especially "every Pod has its own IP and no NAT between Pods". Everything else is an implementation of that contract.
- Separate the three layers cleanly: **CNI** gives Pods IPs and routing, **CoreDNS** turns names into ClusterIPs, **kube-proxy or eBPF** turns a ClusterIP into a real Pod IP. Candidates who blur these get exposed by the follow-ups.
- Answer "can two Pods on the same node talk?" and "on different nodes?" the same way - yes, by design - then say what makes it work in each case (node bridge; VPC route or overlay tunnel).
- Volunteer the readiness link: endpoints are populated from Ready Pods, so a failing readiness probe silently removes a backend. That connects networking to a huge share of real incidents.
- Know headless Services and what they are for - StatefulSet peer discovery, and the answer to "how do you reach one specific Pod?"
- For the Calico-versus-VPC-CNI question, answer in trade-offs: VPC-native addressing and security groups versus IP exhaustion and per-instance limits, against overlay independence and richer policy.
- Have the "two Pods cannot communicate, no errors anywhere" checklist ready, and lead with NetworkPolicy plus the missing DNS egress rule - it is the most common cause and the one people miss. See [how do Kubernetes NetworkPolicies work](./how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md), [debugging DNS resolution failures inside a cluster](./how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md), [a Service that has no endpoints](./how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md), and [exposing an application to the outside world](./how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run a multi-tenant Kubernetes cluster?]] (`#453`): [How do you run a multi-tenant Kubernetes cluster?](../container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md)
- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
