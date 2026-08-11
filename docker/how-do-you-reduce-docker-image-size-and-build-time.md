---
title: "How do you reduce Docker image size and build time?"
id: 260
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - docker
  - interview-questions
---

# How do you reduce Docker image size and build time?

**Short answer:** Size comes from multi-stage builds that ship only the artifact, a minimal base image (slim, Alpine, or distroless), and not creating layers you then have to delete. Speed comes from understanding the layer cache: order your Dockerfile so the parts that change least come first, copy dependency manifests before source code, and use BuildKit cache mounts for package managers.

## Detail

**Multi-stage builds are the single biggest win.** Compile in a stage that has the toolchain, then `COPY --from` only the resulting binary or bundle into a clean runtime stage. A Go image drops from ~800 MB to ~15 MB; a Node image from ~1.1 GB to ~180 MB. Compilers, headers, test fixtures, and build-time credentials never reach the published image - which is a security win as much as a size one.

**Deleting a file in a later layer does not shrink the image.** Layers are additive and immutable; a `RUN rm secret.key` adds a whiteout entry while the original bytes stay in the earlier layer, still readable via `docker save`. This is why the cleanup must happen _in the same `RUN`_ that created the files, and why secrets must never be `COPY`ed at all - use BuildKit `--mount=type=secret`.

**Base image choice, in rough order of size:**

| Base                | Notes                                                              |
| ------------------- | ------------------------------------------------------------------ |
| `debian` / `ubuntu` | Largest; full package manager and shell                            |
| `-slim` variants    | Same distro, docs and extras stripped - the safe default           |
| `alpine`            | Tiny, but musl libc breaks some native modules and can slow Python |
| `distroless`        | Runtime and app only - no shell, no package manager                |
| `scratch`           | Nothing at all; viable for static Go/Rust binaries                 |

Distroless and scratch also shrink the attack surface: no shell means no shell for an attacker either. The trade-off is debugging - use `kubectl debug` ephemeral containers or a `:debug` tag variant.

**How the build cache actually works** - the layer-caching question interviewers love. Each instruction produces a layer keyed on the instruction plus, for `COPY`/`ADD`, a checksum of the copied content. On rebuild Docker walks the layers in order and reuses them until one key differs. **Once a layer is invalidated, every layer after it is rebuilt**, cached or not. So if layers 1-10 are cached and you edit the file used by layer 5, layers 1-4 are reused and 5-10 all rebuild - not because their own inputs changed, but because their parent did.

That single rule dictates Dockerfile ordering: **least-volatile first**. Copy `package.json`/`requirements.txt`/`go.mod` and install dependencies _before_ copying application source. Source changes on every commit; dependencies change weekly, so the expensive install stays cached.

**A `.dockerignore` is not optional.** Without one, `COPY . .` sends `.git`, `node_modules`, build output, and local `.env` files into the build context - slowing every build, busting the cache on irrelevant changes, and potentially baking secrets into the image.

**BuildKit features worth naming:** `--mount=type=cache` keeps a package manager's cache across builds without putting it in a layer; `--mount=type=secret` exposes a credential to one `RUN` without persisting it; and in CI, `--cache-from`/`--cache-to` with a registry restores the cache on ephemeral runners that start with nothing.

**Other reliable reductions:** chain related `RUN` commands with `&&` and clean up in the same layer (`rm -rf /var/lib/apt/lists/*`); use `--no-install-recommends`; install production dependencies only (`npm ci --omit=dev`); and pin the base image by digest so builds are reproducible.

## Example

```dockerfile
# syntax=docker/dockerfile:1
# ---------- build stage ----------
FROM node:22-slim AS build
WORKDIR /app

# Dependency manifests first: this layer survives every source-only commit.
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Source changes constantly, so it comes last.
COPY . .
RUN npm run build && npm prune --omit=dev

# ---------- runtime stage ----------
FROM gcr.io/distroless/nodejs22-debian12 AS runtime
WORKDIR /app
ENV NODE_ENV=production

# Only the artifact and production dependencies cross the boundary.
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

USER nonroot
EXPOSE 8080
CMD ["dist/server.js"]
```

```bash
# Where the bytes went, layer by layer
docker history ghcr.io/acme/api:1.4.0 --no-trunc --format '{{.Size}}\t{{.CreatedBy}}'

# Deep analysis, including wasted space from delete-in-a-later-layer
dive ghcr.io/acme/api:1.4.0

# CI: restore and persist the cache on ephemeral runners
docker buildx build \
  --cache-from type=registry,ref=ghcr.io/acme/api:buildcache \
  --cache-to   type=registry,ref=ghcr.io/acme/api:buildcache,mode=max \
  -t ghcr.io/acme/api:$GIT_SHA --push .
```

## Interview tips

- Lead with multi-stage builds and be ready with a concrete before/after number - it makes the answer credible.
- The layer-cache question is near-guaranteed: **invalidating one layer rebuilds every layer after it.** State the rule, then give the consequence - manifests before source.
- "Does `RUN rm` reduce image size?" - no. Explain whiteout layers and that the data is still recoverable, which is why secrets must never enter a layer.
- Know when Alpine is the wrong choice: musl libc, native modules, and slower Python builds. Recommending `-slim` or distroless instead shows judgement rather than habit.
- If asked about build _time_ specifically, separate the two levers: cache ordering (avoid rebuilding) and cache transport (`--cache-from` in CI, where every runner starts cold).
- Mention `.dockerignore` unprompted. Interviewers notice when candidates forget the build context.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Service in Kubernetes?]] (`#14`): [What is a Service in Kubernetes?](../kubernetes/what-is-a-service-in-kubernetes.md)
- [[How does RBAC work in Kubernetes?]] (`#257`): [How does RBAC work in Kubernetes?](../kubernetes/how-does-rbac-work-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
