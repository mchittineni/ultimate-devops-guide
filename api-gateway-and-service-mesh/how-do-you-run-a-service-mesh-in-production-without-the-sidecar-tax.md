---
title: "How do you run a service mesh in production without the sidecar tax?"
id: 276
category: "API Gateway and Service Mesh"
difficulty: "Advanced"
tags:
  - devops
  - api-gateway-and-service-mesh
  - interview-questions
---

# How do you run a service mesh in production without the sidecar tax?

**Short answer:** Be honest about what the mesh is for - usually mTLS, retries, and golden signals - then buy only that. In practice: start with an **ambient / sidecar-less** data plane (Istio ambient mode with ztunnel, or Cilium's eBPF mesh) so the per-Pod proxy cost disappears for L4, add L7 proxies only to the namespaces that genuinely need L7 policy, and treat the mesh config as a versioned API with a progressive rollout of its own.

## Detail

**What the sidecar tax actually is.** Each sidecar adds ~50-150 MB of memory and a CPU floor per Pod, two extra network hops per request (typically single-digit milliseconds of p99), a second container to upgrade in lockstep with the control plane, and a set of race conditions - traffic before the proxy is ready, jobs that never exit because the sidecar stays alive, `initContainer` traffic bypassing the mesh. On 5,000 Pods that is thousands of dollars a month and a permanent operational surface. Kubernetes native sidecars (`initContainers` with `restartPolicy: Always`) fixed the startup and Job-completion races; they did not fix the resource cost.

**Ambient / sidecar-less as the default starting point.** Istio's ambient mode splits the data plane: a per-node `ztunnel` DaemonSet does mTLS and L4 authorization for every Pod with zero per-Pod overhead, and an optional per-namespace `waypoint` proxy handles L7 features (HTTP retries, header routing, per-route authorization). You pay for L7 only where you use it. Cilium reaches the same place from below, doing identity and L4 policy in eBPF in the kernel and delegating L7 to a per-node Envoy. Linkerd keeps sidecars but its Rust micro-proxy is small enough that the tax is materially lower than Envoy's.

**Decide what you are buying before you choose a mesh.**

- **mTLS and workload identity everywhere** - the strongest reason, and the cheapest to get: L4 only, ambient handles it.
- **Golden-signal telemetry without touching app code** - real, but check what your existing tracing already gives you; the mesh cannot produce spans your app does not propagate headers for.
- **Traffic shifting for canaries** - needs L7. Usually a handful of namespaces, not the whole fleet.
- **Multi-cluster / multi-tenant policy** - the case where a mesh clearly beats a library.

If the honest answer is "we want retries and timeouts", a gateway plus a resilience library may be the cheaper system. A mesh is a distributed system you now operate.

**Making it survivable in production:**

- **Control-plane blast radius.** `istiod` pushing a bad config reaches every proxy in seconds. Use revision-based canary upgrades (`istio.io/rev` labels), roll one namespace at a time, and keep the previous revision installed until you have soaked the new one.
- **Fail-open vs fail-closed.** If the control plane dies, proxies keep serving their last-known config - so a mesh outage is usually silent until a deploy. Alert on config staleness (`pilot_proxy_convergence_time`), not just on `istiod` pods being up.
- **Ordering and startup.** Native sidecars, plus `holdApplicationUntilProxyStarts` where you cannot use them. Verify Jobs and CronJobs actually terminate.
- **Cost the telemetry, not just the proxies.** Default Envoy metrics are extremely high-cardinality; per-request labels multiplied by every source/destination pair is the line item that surprises teams. Trim with `telemetry` API filters before you scale.
- **Do not run two meshes.** A mesh plus an ingress with its own mTLS plus a cloud load balancer doing TLS termination gives you three places where a certificate can expire.

## Example

```yaml
# Ambient: no sidecars. Label the namespace and every Pod gets mTLS via ztunnel.
apiVersion: v1
kind: Namespace
metadata:
  name: payments
  labels:
    istio.io/dataplane-mode: ambient
---
# L4 authorization, enforced by ztunnel on the node - no per-Pod proxy involved.
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: payments-callers
  namespace: payments
spec:
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/checkout/sa/checkout"]
---
# Opt this namespace into L7 only because it needs retries and header routing.
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: payments-waypoint
  namespace: payments
  annotations:
    istio.io/for: waypoint
spec:
  gatewayClassName: istio-waypoint
  listeners:
    - name: mesh
      port: 15008
      protocol: HBONE
```

```yaml
# Cut telemetry cardinality before it cuts your budget.
apiVersion: telemetry.istio.io/v1
kind: Telemetry
metadata:
  name: trim-labels
  namespace: istio-system
spec:
  metrics:
    - providers: [{ name: prometheus }]
      overrides:
        - match: { metric: ALL_METRICS }
          tagOverrides:
            request_protocol: { operation: REMOVE }
            source_version: { operation: REMOVE }
```

```bash
istioctl proxy-status                  # is every proxy synced with the control plane?
istioctl analyze -A                    # config errors before they reach the data plane
kubectl top pods -n payments           # the sidecar tax, measured rather than assumed
istioctl upgrade --revision canary-1-24  # revisioned control plane, one namespace at a time
```

## Interview tips

- Lead with "what are we buying" - mTLS, telemetry, traffic shifting, or multi-cluster policy. Candidates who install a mesh without naming the requirement get pushed hard.
- Quantify the tax: memory and CPU per Pod, two extra hops, and a second container in every upgrade. Numbers beat adjectives.
- Name ambient mode / eBPF as the current answer to sidecar overhead, and be precise that L4 is free-ish while L7 still needs a proxy somewhere.
- Mention that native Kubernetes sidecars fixed the startup and Job-completion problems - it dates your knowledge correctly.
- Have a control-plane failure story: proxies keep last-known-good config, so the failure surfaces on the next deploy. Alerting on config convergence is the senior detail.
- Be willing to say "we did not need a mesh" for a small estate. Knowing when the answer is a gateway plus a library is a strength, not a gap.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
