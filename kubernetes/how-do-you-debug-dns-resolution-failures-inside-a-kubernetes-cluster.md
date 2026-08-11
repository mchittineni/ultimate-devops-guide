---
title: "How do you debug DNS resolution failures inside a Kubernetes cluster?"
id: 404
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - network-security
  - monitoring-and-logging
---

# How do you debug DNS resolution failures inside a Kubernetes cluster?

**Short answer:** Decide first _which_ resolution is failing - a cluster-internal name, or an external one - because the causes are different. Then work down: **the Pod's `/etc/resolv.conf`** (is it pointing at the cluster DNS service, and what is the `ndots` and search path?), **the `kube-dns` Service and its endpoints**, **CoreDNS Pod health and logs**, **the CoreDNS Corefile** (the `forward` block decides all external lookups), and finally **NetworkPolicy or firewall rules blocking UDP/TCP 53**. Internal names failing points at CoreDNS or its Service; external names failing points at the upstream forwarder or egress path.

## Detail

### How cluster DNS actually resolves

Every Pod gets a `/etc/resolv.conf` written by the kubelet, pointing at the cluster DNS ClusterIP (the `kube-dns` Service, served by CoreDNS), with a search path and `options ndots:5`. That `ndots:5` is the source of most surprising behaviour: any name with fewer than five dots is first tried with each search-domain suffix appended. So `api.example.com` (two dots) is looked up as `api.example.com.default.svc.cluster.local`, then `.svc.cluster.local`, then `.cluster.local`, and only then as the absolute name - up to five queries, each of which must fail before the right one is tried. That is why external DNS "works but is slow" inside clusters, and why a fully-qualified name with a trailing dot (`api.example.com.`) is the quick fix for a latency-sensitive lookup.

### The debugging sequence

1. **Reproduce from inside a Pod in the affected namespace.** Use a Pod with tools (`nicolaka/netshoot`) rather than the application container, which usually lacks `dig`. Test three things separately: a cluster Service name, a fully-qualified external name, and a direct query to the DNS ClusterIP.
2. **Read `/etc/resolv.conf` in the Pod.** Wrong nameserver means a `dnsPolicy` problem: `hostNetwork: true` Pods need `dnsPolicy: ClusterFirstWithHostNet` or they inherit the node's resolver and lose cluster DNS entirely. `dnsPolicy: Default` (inherit the node's) and `None` (use `dnsConfig`) are the other cases worth knowing.
3. **Is CoreDNS reachable?** Check the `kube-dns` Service has endpoints and the CoreDNS Pods are `Ready`. Then query the ClusterIP directly with `dig @<clusterIP>` - if the direct query works but the Service name does not, the problem is the Pod's resolver configuration, not DNS itself.
4. **Read the CoreDNS logs.** Enable the `log` plugin if it is off; `errors` is on by default. `SERVFAIL`/`REFUSED` from the upstream, `i/o timeout` to the forwarder, or a plugin configuration error appear here. `kubectl logs -n kube-system -l k8s-app=kube-dns`.
5. **Read the Corefile.** `kubectl -n kube-system get configmap coredns -o yaml`. The two lines that matter: the `kubernetes cluster.local` block (which serves internal names) and the `forward . /etc/resolv.conf` or `forward . 10.0.0.2` block (which decides external resolution). A common misconfiguration is forwarding to a resolver the nodes cannot reach, or a `forward` loop that CoreDNS detects and crash-loops on.
6. **Check capacity and throttling.** CoreDNS with too few replicas, no `autoscaler`, or a low memory limit under a query storm produces intermittent timeouts - the symptom that looks like a flaky application. Look at CoreDNS request rate, cache hit rate, and `SERVFAIL` count; scale replicas or enable **NodeLocal DNSCache** for high-QPS clusters, which also removes the conntrack UDP race that causes classic 5-second DNS delays.
7. **Check NetworkPolicy and node firewalls.** A default-deny egress policy in the namespace blocks DNS unless you explicitly allow UDP **and** TCP port 53 to the `kube-system` namespace. This is the single most common self-inflicted DNS outage. For external names, also check the node's security group, NAT egress, and any upstream resolver ACL.

### The distinction that ends the investigation quickly

- **Internal names fail, external work** → CoreDNS's Kubernetes plugin, RBAC on the CoreDNS service account, or a stale API connection. Check CoreDNS logs and whether it can watch the API.
- **External names fail, internal work** → the `forward` block, the upstream resolver, egress network path, or NAT.
- **Both fail, from every namespace** → CoreDNS is down, unscheduled, or the `kube-dns` Service has no endpoints.
- **Both fail from one namespace only** → NetworkPolicy in that namespace.
- **Intermittent** → capacity, conntrack races, or a single unhealthy CoreDNS replica still receiving traffic.

## Example

```bash
# Reproduce with tools, in the affected namespace
kubectl run -it --rm netshoot -n prod --image=nicolaka/netshoot -- bash

cat /etc/resolv.conf
# nameserver 10.96.0.10
# search prod.svc.cluster.local svc.cluster.local cluster.local
# options ndots:5

dig +short checkout.prod.svc.cluster.local      # internal name
dig +short api.example.com.                     # external, fully qualified (trailing dot)
dig @10.96.0.10 +short checkout.prod.svc        # bypass the Pod's resolver config
dig +time=2 +tries=1 slow.example.com           # is it failing, or just slow?

# Is the DNS service itself healthy?
kubectl -n kube-system get pods -l k8s-app=kube-dns -o wide
kubectl get endpointslices -n kube-system -l kubernetes.io/service-name=kube-dns
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=50
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}'
```

```yaml
# The policy line people forget: default-deny egress silently kills DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: prod }
spec:
  podSelector: {} # every Pod in the namespace
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
      ports:
        - { protocol: UDP, port: 53 }
        - { protocol: TCP, port: 53 } # TCP too - large responses fall back to it
```

## Interview tips

- Split internal versus external resolution in your first sentence. It halves the search space and is the structure interviewers are listening for.
- Explain `ndots:5` and the search path. Being able to say why `api.example.com` generates several failed lookups before succeeding is a strong signal, and the trailing-dot fix is memorable.
- Mention `hostNetwork` needing `ClusterFirstWithHostNet`. It is a real production trap and few candidates know it.
- Name the default-deny egress policy blocking UDP _and_ TCP 53 as the most common self-inflicted DNS outage.
- For intermittent failures, bring up CoreDNS replica capacity, cache hit rate, and NodeLocal DNSCache - and the conntrack race behind the classic 5-second delay.
- Show the isolation move: `dig @<clusterIP>` bypasses the Pod's resolver, so a working direct query proves the problem is `resolv.conf`, not CoreDNS.
- Close on the observability you would add: alert on CoreDNS `SERVFAIL` rate and p99 latency, because DNS failures usually surface as unexplained application timeouts. See [how do you write effective PromQL queries and Alertmanager rules](../monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run a multi-tenant Kubernetes cluster?]] (`#453`): [How do you run a multi-tenant Kubernetes cluster?](../container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md)
- [[How does Prometheus collect metrics, and what components sit around it?]] (`#500`): [How does Prometheus collect metrics, and what components sit around it?](../monitoring-and-logging/how-does-prometheus-collect-metrics-and-what-components-sit-around-it.md)
- [[How do the ELK and EFK stacks fit together?]] (`#501`): [How do the ELK and EFK stacks fit together?](../monitoring-and-logging/how-do-the-elk-and-efk-stacks-fit-together.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
