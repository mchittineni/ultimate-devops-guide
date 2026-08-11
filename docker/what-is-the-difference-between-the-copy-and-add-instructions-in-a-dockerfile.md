---
title: "What is the difference between the COPY and ADD instructions in a Dockerfile?"
id: 438
category: "Docker"
difficulty: "Beginner"
tags:
  - devops
  - docker
  - interview-questions
---

# What is the difference between the COPY and ADD instructions in a Dockerfile?

**Short answer:** Both copy files from the build context into the image, but `ADD` does two extra things: it **auto-extracts local tar archives** and it can **fetch a remote URL**. Those extra behaviours are exactly why the official guidance is to use `COPY` by default - it does one predictable thing. Use `ADD` only when you deliberately want tar extraction (the classic case is `ADD rootfs.tar.xz /` when building a base image). Never use `ADD <url>` to download something: it cannot verify a checksum on older syntax, it bloats the layer with the archive, and `curl`/`wget` in a `RUN` step gives you verification and cleanup in the same layer.

## Detail

### The behavioural difference, precisely

| Behaviour                                                     | `COPY`          | `ADD`                                     |
| ------------------------------------------------------------- | --------------- | ----------------------------------------- |
| Copy files and directories from build context                 | Yes             | Yes                                       |
| Auto-extract a local `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz` | No              | **Yes** - into the destination directory  |
| Auto-extract a `.zip` or a plain `.gz`                        | No              | No (only tar formats)                     |
| Fetch a remote URL                                            | No              | Yes - and the result is **not** extracted |
| Copy from a previous build stage or image                     | Yes (`--from=`) | Yes, but nobody does                      |
| Predictable for a reviewer reading the file                   | Yes             | Depends on the file extension             |

The trap is the tar behaviour being **implicit**. `ADD app.tar.gz /opt/` leaves you with the _contents_ at `/opt/`, while `COPY app.tar.gz /opt/` leaves you with the _archive_ at `/opt/app.tar.gz`. If a build suddenly changes behaviour because someone renamed an artefact, this is why.

### Why `ADD <url>` is the wrong tool

```dockerfile
ADD https://example.com/tool.tar.gz /tmp/    # downloads, does NOT extract
```

Problems: the download lands in its own layer and stays in the image even if you delete it later; you cannot pipe it through a checksum or signature check in the same instruction on classic syntax; and cache invalidation is driven by remote metadata rather than content. The `RUN` equivalent verifies and cleans up in one layer:

```dockerfile
RUN curl -fsSL https://example.com/tool.tar.gz -o /tmp/t.tgz \
 && echo "9f2c8b1d...  /tmp/t.tgz" | sha256sum -c - \
 && tar -xzf /tmp/t.tgz -C /usr/local && rm /tmp/t.tgz
```

Modern BuildKit does add `ADD --checksum=sha256:...` for remote URLs, which closes the verification gap - worth mentioning as the nuance, while noting the layer-hygiene argument still stands.

### Flags both instructions share

- `--chown=user:group` (and `--chmod=` on BuildKit) - set ownership at copy time instead of a separate `RUN chown`, which would duplicate the whole directory into a new layer.
- `--from=<stage|image>` - copy out of a build stage or another image. This is the backbone of multi-stage builds: `COPY --from=build /out/app /usr/local/bin/app`.

### The things that actually cause build bugs here

- **A trailing slash on the destination matters.** `COPY file /dest` treats `/dest` as a file if it does not exist; `COPY file /dest/` treats it as a directory. Always use a trailing slash for directories.
- **You cannot copy from outside the build context** (no `COPY ../secrets .`). That is a security boundary, not a bug.
- **Copying too much destroys the cache.** `COPY . .` invalidates every later layer on any file change. Copy the dependency manifest first, install, then copy the source - and keep a `.dockerignore` so `.git/`, `node_modules/`, and local `.env` files never enter the context at all.
- **Secrets copied in are permanently in the image**, even if a later layer deletes them. Use BuildKit `--mount=type=secret` instead.

## Example

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine AS build
WORKDIR /src

# 1. dependency manifests first: this layer is cached until they change
COPY package.json package-lock.json ./
RUN npm ci

# 2. then the source - a code change only invalidates from here down
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
# 3. COPY --from: only the built assets reach the final image
COPY --from=build --chown=nginx:nginx /src/dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

```dockerfile
# The one legitimate ADD: building a base image from a rootfs tarball
FROM scratch
ADD alpine-minirootfs-3.20.0-x86_64.tar.gz /     # auto-extraction is the point here
CMD ["/bin/sh"]
```

```text
# .dockerignore - do this before arguing about COPY vs ADD
.git
node_modules
**/*.env
Dockerfile
.dockerignore
```

## Interview tips

- One sentence first: `ADD` is `COPY` plus local tar extraction plus remote URL fetching, and because those are implicit, `COPY` is the default you should reach for.
- Give the concrete difference: `ADD app.tar.gz /opt/` extracts, `COPY app.tar.gz /opt/` does not. Interviewers are listening for that specific example.
- State the one good use of `ADD` - unpacking a rootfs tarball when building a base image - so it does not sound like you are just reciting a lint rule.
- If they push on remote URLs, explain the layer-bloat and checksum arguments, then mention BuildKit's `ADD --checksum=` as the modern nuance. That combination reads as current knowledge.
- Volunteer `--chown` and `--from=` - both come up as follow-ups, and `--from` leads naturally into multi-stage builds.
- Expect the pivot to caching: "which lines invalidate the cache?" Answer with manifests-first ordering and `.dockerignore`. See [how does Docker layer caching work](./how-does-docker-layer-caching-work.md) and [reducing Docker image size and build time](./how-do-you-reduce-docker-image-size-and-build-time.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Explain the difference between Docker Swarm and Kubernetes]] (`#15`): [Explain the difference between Docker Swarm and Kubernetes](../kubernetes/explain-the-difference-between-docker-swarm-and-kubernetes.md)
- [[What is the difference between a ConfigMap and a Secret in Kubernetes?]] (`#442`): [What is the difference between a ConfigMap and a Secret in Kubernetes?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)
- [[How does persistent storage work in Kubernetes?]] (`#443`): [How does persistent storage work in Kubernetes?](../kubernetes/how-does-persistent-storage-work-in-kubernetes.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
