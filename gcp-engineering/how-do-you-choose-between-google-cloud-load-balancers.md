---
title: "How do you choose between Google Cloud load balancers?"
id: 757
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - gcp-engineering
  - load-balancing
  - networking
quiz:
  stem: "A game server on Compute Engine needs a UDP load balancer that preserves the client's source IP. Which Google Cloud load balancer fits?"
  options:
    - "Global external Application Load Balancer"
    - "External passthrough Network Load Balancer"
    - "Global external proxy Network Load Balancer"
    - "Regional internal Application Load Balancer"
  answer: 2
  explanation: "Passthrough Network Load Balancers do not terminate connections: packets reach the backend with the original client IP and the backend replies directly, and they support UDP. Application Load Balancers are HTTP(S) only, and proxy Network Load Balancers terminate TCP at a Google proxy, so backends see the proxy's address and UDP is not supported."
---

# How do you choose between Google Cloud load balancers?

**Short answer:** Answer three questions. **Layer**: HTTP(S) traffic goes to an **Application Load Balancer** (L7, Envoy-based proxy - URL maps, TLS termination, Cloud Armor, Cloud CDN, IAP); other TCP/UDP traffic goes to a **Network Load Balancer**, either **proxy** (terminates TCP/SSL at Google's proxies) or **passthrough** (packets go straight to the backend, client IP preserved, UDP supported, backends reply directly). **Exposure**: external (internet-facing) or internal (only inside the VPC). **Scope**: global (one anycast IP, backends in many regions) or regional (data stays in one region; required for some compliance cases). The common answers: a **global external Application Load Balancer** for public web apps and APIs, an **internal Application Load Balancer** for service-to-service HTTP, and an **internal passthrough Network Load Balancer** for TCP services such as databases or as a next hop for firewall appliances.

## Detail

### The family, by decision

| Need                                                | Load balancer                                     | Scope                   |
| --------------------------------------------------- | ------------------------------------------------- | ----------------------- |
| Public HTTP(S), multi-region, CDN/WAF               | Global external Application LB                    | Global, anycast IP      |
| Public HTTP(S), data must stay in one region        | Regional external Application LB                  | Regional                |
| Internal HTTP(S) between services                   | Regional or cross-region internal Application LB  | Regional / cross-region |
| Public TCP or TLS with a proxy (and global anycast) | Global external proxy Network LB                  | Global                  |
| Internal TCP through a proxy                        | Regional / cross-region internal proxy Network LB | Regional / cross-region |
| Public TCP/UDP, client IP preserved, any protocol   | External passthrough Network LB                   | Regional                |
| Internal TCP/UDP, or a next hop for appliances      | Internal passthrough Network LB                   | Regional                |

The older "classic" Application Load Balancer and the earlier TCP/SSL proxy names still appear in existing estates; new designs use the Envoy-based **global external Application Load Balancer**, which has advanced traffic management (weighted splits, header-based routing, retries, mirroring).

### Proxy versus passthrough - the distinction interviewers probe

- **Proxy** load balancers terminate the client connection at a Google front end or Envoy proxy and open a new one to the backend. That is what enables TLS offload, URL routing, Cloud Armor, and anycast across regions - and it means backends see the proxy's address (the client IP arrives in `X-Forwarded-For` for HTTP, or via the PROXY protocol for TCP).
- **Passthrough** load balancers are implemented in the network (Maglev / Andromeda): no termination, the original client IP and port reach the VM, UDP and other IP protocols work, and responses go straight back to the client (direct server return). There is no TLS offload, no WAF, and no URL awareness.

### Pieces you configure, and the gotchas

- **Forwarding rule** (the IP and port) → **target proxy** (for proxy LBs, holding the certificate) → **URL map** (for Application LBs) → **backend service** (balancing mode, health check, Cloud Armor policy, CDN, session affinity) → **backends** (managed instance groups, zonal NEGs for GKE Pods, serverless NEGs for Cloud Run, hybrid or internet NEGs).
- **Health-check firewall rules**: probes come from `35.191.0.0/16` and `130.211.0.0/22`; forgetting to allow them makes every backend unhealthy.
- **Proxy-only subnet**: regional and internal Envoy-based load balancers need a subnet with purpose `REGIONAL_MANAGED_PROXY` in each region; it is the most common "why will this not create?" error.
- **Certificates**: Google-managed certificates through Certificate Manager (DNS authorisation lets you issue before cutover); wildcard and many-domain setups use certificate maps.
- **GKE**: use the **Gateway API** with GKE's gateway classes (`gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, `gke-l7-rilb`) and container-native load balancing (NEGs), so the load balancer targets Pods directly rather than node ports. Attach Cloud Armor and health-check settings through policy resources.
- **Cloud Run**: reached by a load balancer through a serverless NEG - the way to put Cloud Armor, CDN, and a custom domain in front of it - with service ingress restricted to `internal-and-cloud-load-balancing`.

### Why the global load balancer is a differentiator

One anycast IP is announced from Google's edge worldwide; the client connects to the nearest point of presence and the load balancer sends the request to the closest healthy backend region over Google's network. Regional failover therefore does not depend on DNS TTLs - the same comparison as Azure Front Door versus Traffic Manager, or AWS Global Accelerator/CloudFront versus Route 53 failover.

## Example

```bash
# Regional and internal Envoy-based load balancers need a proxy-only subnet per region
gcloud compute networks subnets create proxy-only-euw1 \
  --network=vpc-prod --region=europe-west1 --range=10.129.0.0/23 \
  --purpose=REGIONAL_MANAGED_PROXY --role=ACTIVE

# Health checks come from Google's probe ranges - allow them or every backend is unhealthy
gcloud compute firewall-rules create allow-gclb-health-checks \
  --network=vpc-prod --direction=INGRESS --action=ALLOW --rules=tcp:8080 \
  --source-ranges=35.191.0.0/16,130.211.0.0/22
```

```yaml
# GKE: a global external Application Load Balancer from the Gateway API
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: public-web
  namespace: infra
spec:
  gatewayClassName: gke-l7-global-external-managed
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      allowedRoutes:
        namespaces: { from: All }
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: checkout
  namespace: payments
spec:
  parentRefs:
    - name: public-web
      namespace: infra
  rules:
    - matches:
        - path: { type: PathPrefix, value: /checkout }
      backendRefs:
        - name: checkout # a Service; GKE creates NEGs that target Pods directly
          port: 8080
```

## Interview tips

- Structure the answer on three axes - L7 or L4 (and proxy or passthrough), external or internal, global or regional - then name the one you would pick for the scenario.
- Explain proxy versus passthrough by its consequences: TLS offload, WAF, and URL routing on one side; client IP preservation, UDP, and direct server return on the other.
- Volunteer the operational gotchas: health-check source ranges in the firewall, the proxy-only subnet for regional Envoy load balancers, and Certificate Manager for managed certificates.
- For GKE, say Gateway API with container-native load balancing; for Cloud Run, a serverless NEG behind the load balancer with ingress locked to it.
- Make the cross-cloud comparison: global external Application LB ≈ CloudFront + ALB or Azure Front Door; passthrough Network LB ≈ AWS NLB or Azure Load Balancer. See [how does Google Cloud Armor defend against DDoS and the OWASP Top 10](./how-does-google-cloud-armor-defend-against-ddos-and-owasp-top-10-web-vulnerabilities.md), [what makes a Google Cloud VPC different](./what-makes-a-google-cloud-vpc-different.md), and [what is the difference between a layer 4 and a layer 7 load balancer](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?]] (`#528`): [What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?](../kubernetes/what-is-the-container-network-interface-cni-and-how-do-overlay-and-routed-cni-plugins-differ.md)
- [[What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?]] (`#531`): [What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?](../kubernetes/what-is-the-difference-between-service-types-clusterip-nodeport-loadbalancer-and-externalname.md)
- [[What are Cloud Egress fees and how do you architect networks to minimize them?]] (`#547`): [What are Cloud Egress fees and how do you architect networks to minimize them?](../cloud-platforms/what-are-cloud-egress-fees-and-how-do-you-architect-networks-to-minimize-them.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
