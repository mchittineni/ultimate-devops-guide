---
title: "What is a Service Mesh Control Plane?"
id: 156
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is a Service Mesh Control Plane?

**Short answer:** The control plane is the management layer of a service mesh - it discovers services, translates high-level policy into proxy configuration, distributes it to the data-plane proxies, and issues the certificates that make mutual TLS work.

## Detail

**Responsibilities**

- **Service discovery** - watch the platform (typically the Kubernetes API) for services, endpoints, and their health.
- **Configuration distribution** - translate declarative CRDs (VirtualService, DestinationRule, AuthorizationPolicy) into Envoy configuration and push it to every proxy over xDS, incrementally and continuously.
- **Certificate authority** - issue short-lived workload identity certificates (SPIFFE SVIDs), rotate them automatically, and validate them. This is what makes zero-configuration mTLS possible.
- **Policy management** - authorisation rules, rate limits, and traffic policy resolved centrally and enforced at the edge by the proxies.
- **Telemetry configuration** - tell proxies what metrics, logs, and traces to emit and where to send them.

**Control plane vs data plane.** The data plane (Envoy proxies) carries every request; the control plane carries no user traffic. That separation is what allows the control plane to be temporarily unavailable without breaking the mesh - proxies continue operating on their last known configuration, though new workloads cannot be configured and certificates will eventually expire. This "fail static" behaviour is an important design property to be able to explain.

**Implementations:** Istio's `istiod` (consolidated from the earlier Pilot, Citadel, and Galley), Linkerd's destination and identity controllers, and Consul's servers.

**Operating it:** run it highly available across zones, monitor proxy configuration convergence and certificate issuance, size it for the number of proxies and services (memory grows with the size of the configuration each proxy receives - the `Sidecar` resource limits this), and upgrade it carefully, since it is a critical dependency for every new pod.

## Interview tips

- "Control plane configures, data plane carries traffic" is the essential distinction.
- Fail-static behaviour during control-plane downtime is the detail that demonstrates operational depth.
- Certificate issuance and rotation is the control plane's most valuable function - do not reduce it to routing.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
