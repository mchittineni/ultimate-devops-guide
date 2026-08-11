---
title: "How does Docker layer caching work?"
id: 439
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - docker
  - interview-questions
  - cicd
---

# How does Docker layer caching work?

**Short answer:** Each instruction in a Dockerfile produces a **read-only layer** - a filesystem diff - and the image is those layers stacked by a union filesystem with a thin writable layer on top at runtime. On a rebuild, Docker walks the instructions in order and reuses a cached layer only while **both** the instruction and its parent layer are unchanged. The moment one instruction misses, **every instruction after it is rebuilt**, because each layer's identity depends on the layer beneath it. That single rule drives all the practical advice: put the things that rarely change (base image, package installs) early, and the things that change on every commit (your source code) late.

## Detail

### What invalidates a layer

Docker decides differently depending on the instruction:

- **`RUN`** - the cache key is the **command string**, not its effect. `RUN apt-get update && apt-get install -y curl` hits the cache forever, even when the upstream package index has moved on. This is why pinning versions matters and why "the build worked last month" is not evidence the image is current.
- **`COPY` / `ADD`** - the cache key includes a **checksum of the file contents** (plus path and metadata). Change one byte of one copied file and you miss.
- **`FROM`** - a new digest for the base tag invalidates everything.
- **`ARG` / `ENV`** - changing a value used by a later instruction invalidates from that point.

The classic exam question - _layers 1 to 10 are cached, you edit layer 5, what happens to 6 to 10?_ - is answered by the chaining rule: 1 to 4 are reused, 5 is rebuilt, and **6 to 10 are rebuilt even though their instructions did not change**. There is no way to reuse a layer whose parent changed, because the parent's content is part of the child's identity.

### The ordering that follows from it

```text
FROM            <- changes rarely
system packages <- changes rarely
dependency manifest only  (package.json / requirements.txt / go.mod / pom.xml)
install dependencies      <- the expensive step, now cached across code changes
application source        <- changes every commit
build / entrypoint
```

Copying source before installing dependencies is the single most common cause of slow builds: every commit re-downloads the whole dependency tree.

### Layers are additive - deleting does not shrink

`RUN rm -rf /var/lib/apt/lists/*` in a _later_ instruction does not reclaim anything: the files still exist in the earlier layer, and the image carries both. Clean up **in the same `RUN`** that created the files, chained with `&&`. Same reason a secret copied in and deleted later is still extractable with `docker save`.

### Intermediate images and multi-stage builds

Every instruction historically produced an intermediate image; those are cache entries, not part of your final image. In a multi-stage build, only the stages you `COPY --from=` and the final stage contribute to the shipped image - the compiler, build tools, and source tree in earlier stages are simply not there. BuildKit goes further and skips stages nothing depends on, and builds independent stages concurrently.

### Making the cache work in CI, where the daemon is fresh every run

This is the part most candidates miss. A clean CI runner has an empty local cache, so all your careful ordering achieves nothing unless you import cache from somewhere:

- `docker buildx build --cache-from type=registry,ref=repo/app:buildcache --cache-to type=registry,ref=repo/app:buildcache,mode=max` - push and pull the cache through your registry. `mode=max` also exports intermediate stage layers, which is what makes multi-stage builds cache properly.
- **Cache mounts** for package managers: `RUN --mount=type=cache,target=/root/.m2 mvn -o package` keeps the dependency cache outside the layer, so it neither bloats the image nor invalidates on manifest changes.
- In GitHub Actions, `type=gha` is the same idea backed by the Actions cache.
- Pull the previous image before building if you use the legacy builder, or the daemon has nothing to compare against.

### Layer count is not the metric

"Fewer layers" was a real constraint under old storage drivers with a 127-layer limit; today the thing that matters is **total content** and **cache hit rate**. Do not merge unrelated `RUN` steps just to reduce the count - you lose cache granularity. Merge the ones that must be atomic for cleanup.

## Example

```dockerfile
# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src

# 1. POM alone -> dependency layer survives every source change
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline

# 2. source last
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B -o package -DskipTests

# 3. runtime stage carries no Maven, no source, no build cache
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /src/target/app.jar app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

```dockerfile
# Cleanup must be in the SAME RUN, or the files live on in the earlier layer
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl=7.88.1-10+deb12u5 \
 && rm -rf /var/lib/apt/lists/*
```

```bash
# CI: import and export cache so a fresh runner still hits it
docker buildx build \
  --cache-from type=registry,ref=ghcr.io/acme/app:buildcache \
  --cache-to   type=registry,ref=ghcr.io/acme/app:buildcache,mode=max \
  --tag ghcr.io/acme/app:1.9.0 --push .

# Prove where the size and the cache misses actually are
docker history --no-trunc ghcr.io/acme/app:1.9.0
docker buildx build --progress=plain . 2>&1 | grep -E "CACHED|=> \["
```

## Interview tips

- Answer the chaining question crisply: a layer's identity includes its parent, so a miss at step 5 forces 6 onwards to rebuild regardless of their own content. That is the whole mechanism.
- Distinguish the cache keys: `RUN` is keyed on the **command string** (so `apt-get update` can serve stale indexes forever), `COPY` on the **file checksum**. This is the detail that shows you understand rather than remember.
- Say "layers are additive" and give the consequence twice - deleted files still occupy space, and copied-in secrets are still extractable. Cleanup belongs in the same `RUN`.
- Bring up CI cold caches unprompted. "Ordering only helps if the runner can import the cache - `--cache-from`/`--cache-to` against the registry, or cache mounts for the package manager." Very few candidates get here.
- Mention BuildKit cache mounts for `~/.m2`, `~/.npm`, `~/.cache/pip` as the fix for dependency downloads dominating build time.
- Push back gently on "fewer layers is better": the real goals are cache-hit rate and total content, not layer count. See [reducing Docker image size and build time](./how-do-you-reduce-docker-image-size-and-build-time.md), [COPY versus ADD](./what-is-the-difference-between-the-copy-and-add-instructions-in-a-dockerfile.md), and [speeding up a slow CI/CD pipeline](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is inside a Helm chart, and how do you customise one?]] (`#450`): [What is inside a Helm chart, and how do you customise one?](../container-orchestration-advanced/what-is-inside-a-helm-chart-and-how-do-you-customise-one.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
