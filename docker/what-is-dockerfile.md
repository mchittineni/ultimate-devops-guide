---
title: "What is Dockerfile?"
id: 8
category: "Docker"
difficulty: "Beginner"
tags:
  - devops
  - docker
  - interview-questions
---

# What is Dockerfile?

**Short answer:** A Dockerfile is the text recipe for building an image - an ordered list of instructions that Docker executes to produce reproducible, layered, versionable images.

## Detail

Common instructions:

- `FROM` - the base image, and the start of a build stage.
- `WORKDIR` - sets the working directory for what follows.
- `COPY` / `ADD` - bring files in; prefer `COPY` unless you need `ADD`'s URL or tar extraction.
- `RUN` - execute a command at build time, creating a new layer.
- `ENV` / `ARG` - runtime environment variables and build-time arguments.
- `EXPOSE` - documents the listening port.
- `USER` - drop from root to an unprivileged user.
- `HEALTHCHECK` - how the runtime decides the container is healthy.
- `ENTRYPOINT` / `CMD` - what runs when the container starts.

Two practices matter most. **Layer ordering:** put the things that change rarely (dependency manifests, `npm ci`) before things that change constantly (application source), so the build cache survives most commits. **Multi-stage builds:** compile in a fat toolchain stage, copy only the artifact into a minimal runtime stage.

## Example

```dockerfile
# ---- build stage ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci                      # cached unless dependencies change
COPY . .
RUN npm run build

# ---- runtime stage ----
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --from=build /app/dist ./dist
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/healthz || exit 1
CMD ["node", "dist/server.js"]
```

## Interview tips

- `ENTRYPOINT` vs `CMD`: entrypoint is the executable, cmd supplies default arguments - and `docker run` overrides cmd.
- Always mention `.dockerignore`; without it you ship `node_modules` and `.git` into the build context.
- Running as non-root and pinning base image tags are the security answers interviewers listen for.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Service in Kubernetes?]] (`#14`): [What is a Service in Kubernetes?](../kubernetes/what-is-a-service-in-kubernetes.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
