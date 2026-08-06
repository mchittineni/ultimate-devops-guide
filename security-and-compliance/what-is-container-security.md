---
title: "What is Container Security?"
id: 38
category: "Security and Compliance"
difficulty: "Intermediate"
tags:
  - devops
  - security-and-compliance
  - interview-questions
---

# What is Container Security?

**Short answer:** Container security spans the whole lifecycle — securing the image, the build pipeline, the registry, the runtime configuration, and the orchestrator — because a container is only as safe as the weakest of those layers.

## Detail

**Image security.** Start from minimal, trusted bases (distroless, Alpine, or a hardened vendor image), pin by digest rather than a floating tag, and rebuild regularly so patches land. Scan for CVEs on every build and again periodically for deployed images, because new CVEs are discovered against images that have not changed.

**Build security.** Multi-stage builds so no compilers or credentials ship to production. Never bake secrets into layers — they persist in the image history even if deleted later. Generate an SBOM and sign the image (cosign) so provenance is verifiable.

**Runtime configuration.** Run as a non-root user, with a read-only root filesystem, `allowPrivilegeEscalation: false`, all Linux capabilities dropped, and a seccomp profile. Never use `--privileged` or mount the Docker socket into a container — both are effectively host root.

**Orchestrator security.** RBAC with least privilege, separate namespaces per team or environment, NetworkPolicies to restrict pod-to-pod traffic, Pod Security Admission (or an OPA/Kyverno policy) to enforce the above, and admission control that rejects unsigned images.

**Detection.** Runtime tools (Falco, cloud workload protection) alert on unexpected process execution, outbound connections, or filesystem changes inside containers.

## Example

```yaml
securityContext: # pod level
  runAsNonRoot: true
  runAsUser: 10001
  fsGroup: 10001
  seccompProfile: { type: RuntimeDefault }
containers:
  - name: app
    image: ghcr.io/org/app@sha256:9f2a... # pinned by digest
    securityContext: # container level
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities: { drop: ["ALL"] }
    resources:
      limits: { cpu: "1", memory: 512Mi }
```

## Interview tips

- "Containers share the host kernel" is the sentence that frames why isolation is weaker than a VM.
- Mounting `/var/run/docker.sock` is the classic dangerous pattern — name it.
- Mention supply chain: signing, SBOM, and admission policies that verify signatures.

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
