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

Pods come and go with new IPs each time. A Service provides the fixed address in front of them. The Endpoints (or EndpointSlice) controller keeps the backend list in sync with the pods matching the selector _and_ passing their readiness probes; kube-proxy programmes the data path.

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

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
