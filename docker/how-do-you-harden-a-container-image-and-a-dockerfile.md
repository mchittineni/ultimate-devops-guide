---
title: "How do you harden a container image and a Dockerfile?"
id: 441
category: "Docker"
difficulty: "Advanced"
tags:
  - devops
  - docker
  - interview-questions
  - devsecops
  - security-and-compliance
---

# How do you harden a container image and a Dockerfile?

**Short answer:** Reduce what is in the image, then reduce what the image is allowed to do. Concretely: start from a **minimal, digest-pinned base** (distroless, Alpine, or `-slim`), build in a multi-stage build so no compiler or source ships, run as a **non-root UID with a read-only root filesystem and all capabilities dropped**, keep secrets out of layers entirely (BuildKit secret mounts, never `ENV` or `ARG`), pin dependency versions, and then **scan and sign** the result in CI and enforce the signature at admission. The framing that lands: most container CVEs come from packages the application never uses, so the cheapest security control is having fewer packages, not patching faster.

## Detail

### Shrink the attack surface first

- **Minimal base, pinned by digest.** `FROM gcr.io/distroless/java21-debian12@sha256:...` has no shell, no package manager, and no `curl` - which removes most post-exploitation tooling and most of the CVE count. Pin by digest, not tag, so a rebuild is reproducible; automate digest bumps with Renovate or Dependabot rather than freezing forever.
- **Multi-stage build.** Compilers, build caches, test fixtures, `.git`, and source code stay in the build stage. `COPY --from=build` only the artefact.
- **`.dockerignore` before anything else.** If `.git`, `.env`, `*.pem`, and `node_modules` never enter the build context, they cannot leak into a layer or into a build log.
- **Pin package versions** (`curl=7.88.1-10+deb12u5`, `pip install -r requirements.txt` with hashes, `npm ci` against a lockfile). Unpinned installs make the image non-reproducible and mean you cannot say what you shipped.

### Reduce privilege

| Control                     | How                                                                    | Why it matters                                                                                                        |
| --------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Non-root                    | `RUN adduser -u 10001 -D app` + `USER 10001`                           | Root in the container is root on the host kernel if a namespace escape exists; many CVEs are only exploitable as root |
| Numeric UID                 | `USER 10001`, not `USER app`                                           | Kubernetes `runAsNonRoot` cannot verify a username, only a UID                                                        |
| Read-only root FS           | `--read-only` / `readOnlyRootFilesystem: true` + tmpfs for `/tmp`      | Blocks dropping a payload or modifying binaries at runtime                                                            |
| Drop capabilities           | `--cap-drop=ALL`, add back only what is needed                         | Default Docker keeps ~14 capabilities including `NET_RAW` and `CHOWN`                                                 |
| No privilege escalation     | `--security-opt=no-new-privileges` / `allowPrivilegeEscalation: false` | Neutralises setuid binaries left in the image                                                                         |
| Never `--privileged`        | Use a specific capability or device instead                            | `--privileged` disables nearly every isolation boundary; it is effectively host root                                  |
| Don't mount the socket      | Avoid `-v /var/run/docker.sock:...`                                    | Access to the daemon socket **is** root on the host. Use a rootless builder or Kaniko/BuildKit in CI                  |
| Seccomp / AppArmor          | Keep the default profiles on; tighten per workload                     | The default seccomp profile blocks ~44 syscalls at no cost                                                            |
| No shell in the final stage | Distroless or `scratch`                                                | Removes the easiest interactive foothold                                                                              |

Do not bind a port below 1024 and then justify running as root - listen on 8080 and map it.

### Keep secrets out of the image

Build arguments and environment variables are both visible in `docker history` / `docker inspect`, and any file copied in survives in its layer even after a later `rm`. The correct mechanisms:

- Build time: `RUN --mount=type=secret,id=npmrc ...` (BuildKit) - the secret is mounted for one instruction and never written to a layer.
- Run time: inject from a secret manager or the orchestrator's secret mechanism, and prefer a mounted file over an environment variable, because env vars leak into crash dumps, child processes, and log lines.
- Scan for the ones that slipped through: `trivy image --scanners secret`, `gitleaks` on the repository, and a pre-commit hook.

### Verify continuously, not once

1. **Scan on build and on a schedule.** Trivy, Grype, or the registry's own scanner. Scheduled rescans matter because a CVE published tomorrow affects an image built today. Gate on severity **plus exploitability** (`--ignore-unfixed`, EPSS/KEV context) or the gate gets bypassed within a fortnight.
2. **Lint the Dockerfile.** Hadolint catches unpinned versions, `latest` tags, missing `USER`, and `ADD <url>` cheaply in CI.
3. **Generate an SBOM** (`syft`, `docker buildx --sbom=true`) and store it with the image, so answering "are we affected by this CVE?" is a query, not an investigation.
4. **Sign and enforce.** `cosign sign --key ...` (or keyless with OIDC) at publish, then a Kyverno or Gatekeeper policy that rejects unsigned images and images from unapproved registries. Signing without admission enforcement changes nothing.
5. **Runtime detection.** Falco or a managed equivalent for behaviour the image scan cannot see: a shell spawning in a container that should not have one, unexpected outbound connections, writes to `/etc`.

### Rebuild rather than patch in place

The answer to "a CVE is in a running container" is not `apt-get upgrade` inside it - that mutates the writable layer and vanishes on restart. Bump the base digest, rebuild, rescan, redeploy through the normal pipeline. If patching genuinely cannot happen quickly (a vulnerable transitive dependency with no fix), compensate: network policy to remove reachability, a WAF rule, disabling the feature, and a documented risk acceptance with a date.

## Example

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
# static binary, no debug symbols, no cgo -> runs on distroless/static
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/api ./cmd/api

# private registry credentials that must never reach a layer
FROM node:20-alpine AS assets
WORKDIR /a
COPY package*.json ./
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci --omit=dev

FROM gcr.io/distroless/static-debian12:nonroot@sha256:d71f4d239b1f0a4b5b1a4c8bd3b6bd0a7a0e4dcf3f6b2f1e0c9d8a7b6c5d4e3f
USER 65532:65532
COPY --from=build /out/api /api
EXPOSE 8080
ENTRYPOINT ["/api"]
```

```yaml
# The other half of hardening lives in the runtime spec, not the image
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  template:
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        seccompProfile: { type: RuntimeDefault }
      containers:
        - name: api
          image: registry.example.com/api@sha256:9f2c8b1d... # digest, not tag
          securityContext:
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false
            capabilities: { drop: ["ALL"] }
          volumeMounts: [{ name: tmp, mountPath: /tmp }]
          resources: { limits: { memory: 256Mi, cpu: "500m" } }
      volumes: [{ name: tmp, emptyDir: { medium: Memory, sizeLimit: 64Mi } }]
```

```bash
# CI gate: lint, scan, SBOM, sign - in that order
hadolint Dockerfile
docker buildx build --secret id=npmrc,src=$HOME/.npmrc --sbom=true \
  -t registry.example.com/api:1.9.0 --push .

trivy image --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 registry.example.com/api:1.9.0

cosign sign --yes registry.example.com/api:1.9.0          # keyless OIDC in CI
cosign verify --certificate-identity-regexp '.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  registry.example.com/api:1.9.0

# Prove nothing sensitive is in the layers
docker history --no-trunc registry.example.com/api:1.9.0
```

## Interview tips

- Lead with the reframe - "most CVEs in a container are in packages the app never calls, so the first control is a smaller image, not a faster patch cycle." Then give distroless plus multi-stage as the mechanism.
- Split your answer into **image-time** and **runtime** controls, and say explicitly that a hardened image with a `privileged` pod spec is not hardened. That distinction is what senior interviewers are listening for.
- Use a numeric UID in `USER` and explain why: `runAsNonRoot` cannot resolve a username to a UID, so `USER app` can still fail admission.
- Be precise about secrets: `ARG` and `ENV` are visible in `docker history`, deleted files persist in their layer, and the fix is BuildKit `--mount=type=secret` at build and a mounted file at run.
- Mention that mounting `/var/run/docker.sock` is equivalent to giving root on the host - it is the most common self-inflicted CI vulnerability. Offer rootless BuildKit or Kaniko instead.
- Say that signing only matters with admission enforcement, and name Kyverno or Gatekeeper. See [how do you sign and verify container images](../devsecops/how-do-you-sign-and-verify-container-images.md), [Kubernetes admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md), [prioritising vulnerabilities without blocking delivery](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md), and [namespaces, cgroups, and capabilities](./how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- If asked how to fix a CVE in a running container, refuse the in-place upgrade and describe rebuild-rescan-redeploy plus compensating controls when the fix is genuinely far off.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[What is the difference between a ConfigMap and a Secret in Kubernetes?]] (`#442`): [What is the difference between a ConfigMap and a Secret in Kubernetes?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)
- [[What does a DevSecOps pipeline look like end to end?]] (`#161`): [What does a DevSecOps pipeline look like end to end?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
