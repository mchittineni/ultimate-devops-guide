---
title: "What is Mutual TLS (mTLS) and how does a Service Mesh automate certificate issuance and rotation?"
id: 617
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - service-mesh
  - mtls
  - security
  - certificates
  - istio
quiz:
  stem: "What is the primary operational advantage of delegating mTLS encryption to a Service Mesh sidecar rather than implementing it in application code?"
  options:
    - "Sidecars allow applications to bypass certificate expiration dates"
    - "Developers can write simple HTTP application code while sidecars handle certificate generation, rotation, and encryption transparently without code changes"
    - "Service mesh mTLS requires no CPU compute power"
    - "Sidecars eliminate the need for Kubernetes ServiceAccounts"
  answer: 2
  explanation: "Offloading mTLS to sidecar proxies frees application teams from managing TLS libraries, private keys, and rotation logic across different programming languages."
---

# What is Mutual TLS (mTLS) and how does a Service Mesh automate certificate issuance and rotation?

**Short answer:** In ordinary TLS only the server presents a certificate; in **mutual TLS** the client does too, so each side cryptographically proves its identity and the connection is encrypted. A service mesh automates the painful part: its control plane runs a certificate authority, each workload's proxy (or node-level ztunnel) proves which Kubernetes service account it runs as, receives a short-lived X.509 certificate carrying a **SPIFFE ID**, and renews it automatically well before expiry - in Istio the default workload certificate lifetime is 24 hours. The application keeps speaking plain HTTP to its local proxy. The limits: the mesh only secures hops that go through the mesh, and the root of trust (the CA key) becomes one of your most sensitive assets.

## Detail

**What mTLS proves.** The server's certificate lets the client verify it reached the real `payments` service; the client's certificate lets `payments` verify the caller is `checkout` and not anything else on the network. That verified identity is what authorisation policies (`AuthorizationPolicy` principals, Linkerd `Server`/`AuthorizationPolicy`) are written against - it replaces IP-based trust, which is meaningless when Pod IPs are recycled.

**How issuance works in Istio (sidecar mode)**

1. A Pod starts with a projected Kubernetes service-account token.
2. The `istio-agent` inside the sidecar generates a private key locally (the key never leaves the Pod) and sends a certificate signing request to `istiod`, authenticated by that token.
3. `istiod` validates the token with the Kubernetes API and signs a certificate whose SAN is the SPIFFE ID `spiffe://<trust-domain>/ns/<namespace>/sa/<service-account>`.
4. The agent delivers the certificate and key to Envoy over the **Secret Discovery Service (SDS)**, in memory, and rotates it before it expires - no restart, no file on disk.

In ambient mode ztunnel does the same on behalf of every Pod on its node. Linkerd follows the same pattern with its identity controller (24-hour certificates by default), and SPIRE is the general-purpose SPIFFE implementation many meshes can use instead of a built-in CA.

**Rolling it out.** Use `PERMISSIVE` mode first (accept both plain text and mTLS), confirm from telemetry that all traffic is mTLS, then switch to `STRICT` per namespace; going straight to `STRICT` breaks clients outside the mesh.

**Operational concerns**

- **Root of trust** - replace the self-signed default root with an intermediate CA from your own PKI (for example via cert-manager's istio-csr or a cloud private CA) so the root key is protected and rotation is planned.
- **Trust domains** in multi-cluster meshes must be shared or federated, or cross-cluster calls fail verification.
- **Coverage** - traffic from uninjected Pods, `hostNetwork` workloads, or external callers is not protected by the mesh; the ingress gateway terminates external TLS and re-originates mTLS inside.
- **Short lifetimes replace revocation** - the design relies on certificates expiring quickly rather than on CRLs, so a stalled control plane eventually becomes an outage when certificates expire.

## Example

```yaml
# Require mTLS for every workload in the namespace (after a PERMISSIVE soak)
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: payments }
spec:
  mtls: { mode: STRICT }
---
# Authorise by verified identity, not by IP
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: payments-callers, namespace: payments }
spec:
  selector: { matchLabels: { app: payments } }
  action: ALLOW
  rules:
    - from:
        - source: { principals: ["cluster.local/ns/checkout/sa/checkout"] }
```

```bash
# Inspect the certificate a workload actually holds: SPIFFE ID and validity window
istioctl proxy-config secret deploy/payments -n payments -o json \
  | jq -r '.dynamicActiveSecrets[0].secret.tlsCertificate.certificateChain.inlineBytes' \
  | base64 -d | openssl x509 -noout -subject -ext subjectAltName -dates
```

## Interview tips

- Define mTLS precisely: both sides present certificates, so both identities are verified, not just the server's.
- Walk through issuance - service-account token, locally generated key, CSR to the mesh CA, SPIFFE ID in the SAN, delivery over SDS, automatic rotation.
- Give the default lifetime correctly (24 hours in Istio and Linkerd, rotated automatically before expiry) rather than a vague "hourly".
- Mention the `PERMISSIVE`-to-`STRICT` migration, protecting the root CA, and what the mesh does not cover.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?]] (`#539`): [What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?](../cicd/what-are-slsa-supply-chain-levels-for-software-artifacts-frameworks-and-how-do-they-verify-build-integrity.md)
- [[How does Docker multi-stage building optimize container security and image size?]] (`#513`): [How does Docker multi-stage building optimize container security and image size?](../docker/how-does-docker-multi-stage-building-optimize-container-security-and-image-size.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
