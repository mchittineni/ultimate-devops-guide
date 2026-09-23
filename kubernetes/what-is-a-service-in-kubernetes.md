---
title: "What is a Service in Kubernetes?"
id: 14
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# What is a Service in Kubernetes?

**Short answer:** A Service is a stable network endpoint - a virtual IP and DNS name - that load-balances traffic to a dynamic set of pods selected by labels, insulating clients from pod churn.

## Detail

Pods come and go with new IPs each time. A Service provides the fixed address in front of them. The EndpointSlice controller keeps the backend list in sync with the pods matching the selector _and_ passing their readiness probes (the older `Endpoints` API is deprecated since Kubernetes 1.33 but still populated for compatibility); kube-proxy, or an eBPF replacement such as Cilium, watches those slices and programmes the data path on every node. The trade-off of this design is that a ClusterIP is a layer-4 construct: it balances connections, not requests, so long-lived HTTP/2 or gRPC connections can pin to one backend - which is where client-side balancing through a headless Service, or a mesh, comes in.

**Types:**

- **ClusterIP** (default) - a virtual IP reachable only inside the cluster. The building block for internal service-to-service traffic.
- **NodePort** - allocates a port (30000–32767) on every node that forwards to the Service. Mostly a primitive for other layers.
- **LoadBalancer** - asks the cloud provider for an external load balancer pointing at the Service. The usual way to expose something publicly on a managed cluster.
- **ExternalName** - a CNAME to an external DNS name; no proxying at all.
- **Headless** (`clusterIP: None`) - no virtual IP; DNS returns pod IPs directly, which StatefulSets and client-side load balancing rely on.

For HTTP, an **Ingress** or **Gateway API** resource typically sits in front, providing host/path routing and TLS termination across many Services from a single load balancer. Know which way this is going: Ingress is feature-frozen, and **Gateway API is its successor** - role-oriented (cluster operators own the `Gateway`, app teams own the `HTTPRoute`), with header matching, traffic splitting, and cross-namespace routing expressed in the API instead of in controller-specific annotations. New clusters should start on Gateway API.

## Example

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: ClusterIP
  selector: { app: web } # matches pod labels
  ports:
    - port: 80 # the Service port
      targetPort: 8080 # the container port
```

In-cluster DNS: `web.default.svc.cluster.local`, usually just `web` from the same namespace.

## Interview tips

- The label selector plus readiness probe is what makes traffic routing safe - say both.
- Know why one LoadBalancer per service gets expensive, and how Ingress solves it - then say that Gateway API is the successor and Ingress is frozen.
- Headless Services plus StatefulSets is a common follow-up for databases.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
