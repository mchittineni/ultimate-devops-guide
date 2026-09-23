---
title: "How does Docker BuildKit work and what caching and build features does it unlock?"
id: 515
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - docker
  - buildkit
  - cache
  - performance
quiz:
  stem: "What is the primary security advantage of using BuildKit secret mounts (`--mount=type=secret`) over build arguments (`ARG`)?"
  options:
    - "BuildKit compiles secrets into machine code before sending to the daemon"
    - "Secret mounts provide credentials only during command execution without persisting them in image layers or history"
    - "BuildKit transmits secrets directly over unencrypted DNS records"
    - "ARG variables are accessible only by the root user in the running container"
  answer: 2
  explanation: "Values passed via ARG are permanently inspectable via `docker history`. BuildKit secret mounts mount temporary in-memory files that disappear once the instruction finishes."
---

# How does Docker BuildKit work and what caching and build features does it unlock?

**Short answer:** BuildKit is the build engine behind `docker build` (the default since Docker Engine 23.0, where `docker build` is an alias for `docker buildx build`). A **frontend** - normally the Dockerfile frontend selected by `# syntax=docker/dockerfile:1` - converts the Dockerfile into **LLB**, a content-addressed graph of build steps. BuildKit then solves that graph: it runs independent steps and stages in parallel, skips stages the target does not need, and caches each step by the hash of its inputs. On top of that it adds `RUN --mount` (cache, secret, SSH, and bind mounts), exportable cache backends for CI, multi-platform builds, and SBOM and provenance attestations. The trade-off is a few more concepts - builders, drivers, exporters - and some features that depend on which builder driver you use.

## Detail

**How a build runs.**

1. The client sends the build context (filtered by `.dockerignore`) and the Dockerfile to a **builder**.
2. The frontend parses the Dockerfile into LLB. Because the syntax line pulls the frontend as an image, new Dockerfile features (heredocs, `COPY --link`, `--exclude`) arrive without upgrading the daemon.
3. The solver walks the graph from the requested target backwards. Stages that the target does not depend on are never built; independent branches run concurrently.
4. Each vertex is cached by a digest of its definition and inputs, so a changed input invalidates only that vertex and what depends on it.
5. An **exporter** writes the result: into the local image store, to a registry (`--push`), to an OCI tarball, or to a local directory.

**Features it unlocks.**

| Feature                              | What it does                                                                                           | Example use                                            |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------ |
| `RUN --mount=type=cache`             | Persistent directory reused across builds, never stored in a layer                                     | `~/.cache/pip`, `~/.npm`, `/root/.m2`, Go module cache |
| `RUN --mount=type=secret`            | Mounts a secret file or env var for one instruction only                                               | Private registry tokens, `.npmrc`                      |
| `RUN --mount=type=ssh`               | Forwards the client's SSH agent into one instruction                                                   | `git clone` of private repositories                    |
| `RUN --mount=type=bind`              | Binds files from the context or another stage without copying them into a layer                        | Build from source without a `COPY` layer               |
| `--cache-to` / `--cache-from`        | Export and import cache to a registry, the GitHub Actions cache (`type=gha`), S3, or local disk        | Warm caches on ephemeral CI runners                    |
| `--platform linux/amd64,linux/arm64` | Multi-architecture images via QEMU emulation or native nodes, pushed as one manifest list              | One tag for Graviton and x86 nodes                     |
| `--sbom`, `--provenance`             | Attach SBOM and SLSA provenance attestations to the image                                              | Supply-chain evidence for admission policies           |
| `COPY --link`                        | Makes a copied layer independent of the layers below it, so it can be reused after a base-image change | Faster rebuilds after base bumps                       |

**Builders and drivers.** `docker buildx` can target the Docker daemon's built-in BuildKit (`docker` driver), a BuildKit container (`docker-container`), a Kubernetes deployment (`kubernetes`), or a remote BuildKit. Some exporters and cache backends historically required a non-default driver; with the containerd image store (the default for fresh installs since Docker Engine 29) the built-in driver supports more of them. Rootless BuildKit is the usual way to build in Kubernetes CI without mounting the Docker socket.

**Trade-offs and limits.** Cache mounts are local to a builder and are not exported with `--cache-to`, so on ephemeral runners they only help if the builder persists. `mode=max` cache exports every intermediate layer and can grow large. Multi-platform builds through QEMU emulation are slow for compile-heavy work. And secrets are only safe if you use the secret mount - anything passed through `ARG` or `ENV` is still visible in image metadata.

## Example

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim AS deps
WORKDIR /app
COPY requirements.txt .
# cache mount: pip's download cache survives across builds but is never in a layer
# secret mount: the private index URL (with its token) exists only for this instruction
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=secret,id=pip_index_url,env=PIP_INDEX_URL \
    pip install --prefix=/install -r requirements.txt

# skipped entirely unless you build with --target test
FROM python:3.13-slim AS test
COPY --from=deps /install /usr/local
COPY . /app
RUN python -m pytest /app/tests

FROM python:3.13-slim AS runtime
COPY --from=deps /install /usr/local
COPY --link src/ /app/src/
USER 10001
CMD ["python", "-m", "app"]
```

```bash
# CI: remote cache, multi-arch, attestations, secret from the environment
docker buildx create --use --name ci --driver docker-container
PIP_INDEX_URL="https://__token__:${TOKEN}@pypi.example.com/simple" docker buildx build \
  --secret id=pip_index_url,env=PIP_INDEX_URL \
  --cache-from type=registry,ref=ghcr.io/acme/app:buildcache \
  --cache-to type=registry,ref=ghcr.io/acme/app:buildcache,mode=max \
  --platform linux/amd64,linux/arm64 \
  --sbom=true --provenance=mode=max \
  -t ghcr.io/acme/app:1.9.0 --push .

docker buildx du          # how much space the builder's cache is using
```

## Interview tips

- Explain the architecture: frontend → LLB graph → solver with content-addressed cache → exporter. That is what "BuildKit" actually means.
- Name the parallelism and stage-skipping behaviour, and show you know `--target` builds only what that stage needs.
- Go through the `--mount` types, especially cache and secret, and why a secret passed as `ARG` leaks.
- Explain remote cache (`--cache-to`/`--cache-from`, `mode=max`) for cold CI runners, and that cache mounts do not travel with it.
- Mention multi-platform builds and SBOM/provenance attestations - they connect BuildKit to supply-chain security.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Service in Kubernetes?]] (`#14`): [What is a Service in Kubernetes?](../kubernetes/what-is-a-service-in-kubernetes.md)
- [[How does RBAC work in Kubernetes?]] (`#257`): [How does RBAC work in Kubernetes?](../kubernetes/how-does-rbac-work-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
