---
title: "What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?"
id: 531
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - kubernetes
  - networking
  - services
  - clusterip
quiz:
  stem: "How does an `ExternalName` Kubernetes Service direct traffic to an external database endpoint?"
  options:
    - "kube-proxy translates the database TCP packets through a stateful NAT proxy"
    - "CoreDNS returns a DNS CNAME record pointing to the external hostname, with no packet proxying"
    - "The cloud provider automatically provisions an external Network Load Balancer"
    - "Worker nodes establish a persistent IPSec tunnel to the database host"
  answer: 2
  explanation: "ExternalName services have no selector or endpoints; CoreDNS simply returns a CNAME record redirecting client DNS resolution directly to the external hostname."
---

# What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?

**Short answer:** `ClusterIP` (the default) gives a Service a virtual IP reachable only inside the cluster. `NodePort` additionally opens the same port (30000-32767 by default) on every node and forwards it to the Service. `LoadBalancer` additionally asks a cloud or load-balancer controller to provision an external load balancer in front. `ExternalName` is different in kind: it has no IP, no endpoints, and no proxying - cluster DNS just returns a CNAME to an external hostname. The first three are layered on each other; `ExternalName` is a DNS alias.

## Detail

**The layering.**

```text
ClusterIP     virtual IP, kube-proxy/eBPF DNAT to ready Pod IPs
  └─ NodePort     + <any node IP>:<nodePort> forwards to the ClusterIP backends
       └─ LoadBalancer + cloud LB whose targets are the node ports (or Pod IPs directly)
ExternalName  DNS CNAME only - nothing is programmed on the nodes
```

| Type           | Reachable from                          | Mechanism                                                                                | Typical use                                                     | Limitation                                                                                                             |
| -------------- | --------------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `ClusterIP`    | Inside the cluster                      | Virtual IP; kube-proxy (iptables or nftables) or an eBPF dataplane load-balances to Pods | Service-to-service traffic; the backend of Ingress and Gateway  | Not reachable externally; balances connections, not requests                                                           |
| `NodePort`     | Anything that can reach a node IP       | Port opened on every node, forwarded to backends                                         | Bare metal, behind an external LB, quick tests                  | Odd port range, every node exposed, clients must track node IPs                                                        |
| `LoadBalancer` | Internet or VPC, via the provisioned LB | Cloud controller (or MetalLB, AWS Load Balancer Controller) creates and syncs an LB      | Non-HTTP protocols, or a single public entry point              | One billed LB per Service; L4 only - no host or path routing                                                           |
| `ExternalName` | Inside the cluster                      | CoreDNS returns a CNAME for `spec.externalName`                                          | Stable in-cluster name for RDS, a SaaS endpoint, or a migration | No ports or proxying; HTTP `Host` headers and TLS SNI still carry the in-cluster name unless the client overrides them |

**Details interviewers probe.**

- **`externalTrafficPolicy: Local`** on NodePort and LoadBalancer Services preserves the client source IP and avoids a second hop, at the cost of uneven load and health checks that fail on nodes without a local Pod. The default `Cluster` spreads evenly but SNATs the client IP.
- **Direct-to-Pod load balancing.** Many cloud controllers can target Pod IPs rather than node ports (for example, the AWS Load Balancer Controller's IP target mode), and `allocateLoadBalancerNodePorts: false` skips node-port allocation entirely. `loadBalancerClass` selects which controller implements the Service.
- **Headless** (`clusterIP: None`) is not a type but a ClusterIP variant: DNS returns the Pod IPs directly, which StatefulSets and client-side load balancing rely on.
- **`spec.externalIPs`** - manually attaching IPs to a Service - is deprecated since Kubernetes 1.36 because of CVE-2020-8554 and is planned for removal; use `LoadBalancer` with MetalLB or a cloud controller instead.
- **For HTTP**, one Gateway API Gateway (or Ingress controller) behind one `LoadBalancer` usually replaces many per-Service load balancers.

## Example

```yaml
apiVersion: v1
kind: Service
metadata: { name: checkout } # ClusterIP: internal only
spec:
  selector: { app: checkout }
  ports: [{ port: 80, targetPort: 8080 }]
---
apiVersion: v1
kind: Service
metadata:
  name: mqtt-broker # LoadBalancer: non-HTTP traffic from outside
spec:
  type: LoadBalancer
  externalTrafficPolicy: Local # keep the client IP
  selector: { app: mqtt }
  ports: [{ port: 8883, targetPort: 8883, protocol: TCP }]
---
apiVersion: v1
kind: Service
metadata: { name: orders-db } # ExternalName: DNS alias, no proxying
spec:
  type: ExternalName
  externalName: orders.cluster-abc123.eu-west-1.rds.amazonaws.com
```

```bash
kubectl get svc -o wide                              # TYPE, CLUSTER-IP, EXTERNAL-IP, PORT(S)
kubectl run -it --rm dns --image=nicolaka/netshoot -- dig +short orders-db.default.svc.cluster.local
# orders.cluster-abc123.eu-west-1.rds.amazonaws.com.   <- a CNAME, then the RDS address
```

## Interview tips

- State the layering: `LoadBalancer` includes `NodePort` includes `ClusterIP`, and `ExternalName` is a DNS alias outside that chain.
- Know the default NodePort range (30000-32767) and why NodePort alone is rarely the production answer.
- Bring up `externalTrafficPolicy: Local` versus `Cluster` - client IP preservation versus even balancing - as the most common follow-up.
- Explain the cost argument for Gateway API or Ingress in front of many HTTP Services instead of one load balancer each.
- For `ExternalName`, mention the `Host`/SNI pitfall and that it does no health checking or failover.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?]] (`#517`): [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
