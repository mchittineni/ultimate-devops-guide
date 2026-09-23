---
title: "How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?"
id: 527
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - dns
  - coredns
  - networking
quiz:
  stem: "Why does querying an external domain like `api.github.com` from inside a standard Kubernetes Pod generate multiple DNS queries to CoreDNS?"
  options:
    - "CoreDNS encrypts requests with four distinct TLS certificates"
    - "The default `ndots:5` setting forces the resolver to test all cluster search domains before querying the root domain"
    - "Kubernetes requires DNS lookups to query all worker nodes sequentially"
    - "CoreDNS does not support IPv4 addresses"
  answer: 2
  explanation: "Because `api.github.com` has only 2 dots (less than `ndots:5`), the resolver appends `.default.svc.cluster.local`, `.svc.cluster.local`, etc., generating several NXDOMAIN queries before querying external upstream DNS."
---

# How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?

**Short answer:** CoreDNS runs as a Deployment behind the `kube-dns` Service; its `kubernetes` plugin watches Services and EndpointSlices through the API and answers `<service>.<namespace>.svc.cluster.local` with the Service's ClusterIP (or the Pod IPs for a headless Service), forwarding everything else upstream. Latency bottlenecks almost always come from three places: the **`ndots:5` search-path expansion** that turns one external lookup into several, **too few CoreDNS replicas** for the query rate, and **conntrack races on UDP** that produce the classic five-second stalls. The standard fixes are fully qualified names or a lower `ndots`, CoreDNS autoscaling, and NodeLocal DNSCache.

## Detail

### How resolution works

The kubelet writes each Pod's `/etc/resolv.conf` (for the default `dnsPolicy: ClusterFirst`):

```text
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

`10.96.0.10` is the `kube-dns` Service's ClusterIP; kube-proxy (or the CNI's eBPF replacement) load-balances it across CoreDNS Pods. CoreDNS's Corefile decides what happens next: the `kubernetes cluster.local` block answers cluster names from its in-memory view of the API, `cache` holds answers for their TTL (30 s by default for cluster records), and `forward . /etc/resolv.conf` sends everything else to the node's upstream resolver.

### The `ndots:5` problem

Any name with fewer than five dots is treated as relative, so the resolver tries every search domain first. For `api.stripe.com` (two dots):

1. `api.stripe.com.default.svc.cluster.local` → NXDOMAIN
2. `api.stripe.com.svc.cluster.local` → NXDOMAIN
3. `api.stripe.com.cluster.local` → NXDOMAIN
4. `api.stripe.com.` → answer

That is four round trips instead of one, and most resolvers (glibc included) send A and AAAA queries in parallel, so it is eight packets for one lookup. Multiplied across every outbound call, this is often the largest share of CoreDNS load in a cluster. The trade-off of lowering `ndots` (say to 2) is that partially qualified cluster names with at least that many dots, such as `checkout.prod.svc`, are then tried as absolute names first, which adds a failed upstream query for them instead.

### Other bottlenecks

- **Capacity.** Two CoreDNS replicas serving a large cluster will queue and drop under bursts. Scale with the `cluster-proportional-autoscaler` (replicas proportional to nodes or cores) or an HPA, and give CoreDNS enough CPU - it is latency-sensitive, so avoid a tight CPU limit.
- **Conntrack races.** Parallel A and AAAA queries from the same socket over UDP can race in the kernel's conntrack NAT insertion; one packet is dropped and the client waits for its five-second retry. Fixes: NodeLocal DNSCache, `options single-request-reopen` (glibc), or TCP for DNS.
- **Upstream latency.** Slow or rate-limited upstream resolvers (for example, per-ENI query limits on cloud VPC resolvers) show up as `forward` plugin latency. Caching and NodeLocal DNSCache reduce the number of queries that reach them.

### Remediation options

| Fix                          | Mechanism                                                                                                                                                                           | Trade-off                                                                                         |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Trailing dot / FQDN          | `api.stripe.com.` is absolute, so no search expansion                                                                                                                               | Must change application config; some HTTP clients and TLS SNI handling dislike the trailing dot   |
| Lower `ndots` per Pod        | `dnsConfig.options: [{name: ndots, value: "2"}]`                                                                                                                                    | Partially qualified cluster names (`checkout.prod.svc`) cost an extra upstream query              |
| NodeLocal DNSCache           | A caching DaemonSet on every node listening on a link-local IP (commonly `169.254.20.10`); Pods query it without NAT, and it talks to CoreDNS over TCP, avoiding the conntrack race | One more component per node to run and upgrade; a failed node cache affects every Pod on the node |
| Autoscale CoreDNS            | More replicas behind `kube-dns`                                                                                                                                                     | Does not reduce the query count, only absorbs it                                                  |
| Raise `cache` TTL / prefetch | Fewer queries reach the API view or upstream                                                                                                                                        | Stale answers for longer after a Service changes                                                  |

## Example

```yaml
# Per-Pod override for a service that makes many external calls
apiVersion: v1
kind: Pod
metadata:
  name: payments-worker
spec:
  dnsConfig:
    options:
      - name: ndots
        value: "2" # api.stripe.com is now tried as absolute first
  containers:
    - name: worker
      image: registry.example.com/payments-worker:3.2.0
```

```bash
# Is CoreDNS the bottleneck? Replicas, restarts, and latency metrics
kubectl -n kube-system get deploy coredns
kubectl -n kube-system get pods -l k8s-app=kube-dns -o wide
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}'

# From a debug Pod: watch the search-path expansion happen
kubectl run -it --rm dnsdebug --image=nicolaka/netshoot -- \
  dig +search +showsearch api.stripe.com

# PromQL: p99 CoreDNS request latency
#   histogram_quantile(0.99, sum by (le) (rate(coredns_dns_request_duration_seconds_bucket[5m])))
```

## Interview tips

- Explain the data path first: Pod `resolv.conf` → `kube-dns` ClusterIP → CoreDNS `kubernetes` plugin (cluster names) or `forward` (everything else).
- Walk through the `ndots:5` expansion for a real external name and count the queries, including A plus AAAA. That is the answer interviewers are listening for.
- Name the five-second timeout and connect it to the UDP conntrack race; NodeLocal DNSCache is the structural fix.
- Offer the fixes with their trade-offs - FQDN, per-Pod `ndots`, NodeLocal DNSCache, CoreDNS autoscaling - rather than one silver bullet.
- Mention that you would measure before tuning: `coredns_dns_request_duration_seconds`, cache hit rate, and `forward` latency.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?]] (`#517`): [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
