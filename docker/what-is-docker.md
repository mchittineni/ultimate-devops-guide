---
title: "What is Docker?"
id: 6
category: "Docker"
difficulty: "Beginner"
tags:
  - devops
  - docker
  - interview-questions
---

# What is Docker?

**Short answer:** Docker is a platform for packaging an application together with its dependencies into a portable image, then running that image as an isolated process - a container - on any host with a container runtime.

## Detail

Docker solved "works on my machine" by making the environment part of the artifact. The image contains the application, its runtime, libraries, and filesystem layout; the host contributes only the kernel.

Containers are not lightweight virtual machines. They are ordinary Linux processes constrained by two kernel features:

- **Namespaces** provide isolation - each container gets its own view of process IDs, network interfaces, mounts, hostname, and users.
- **cgroups** provide limits - CPU, memory, and I/O quotas enforced by the kernel.

Because there is no guest operating system, containers start in milliseconds and a host can run hundreds of them.

The core objects: an **image** (immutable, layered template), a **container** (a running instance of an image), a **Dockerfile** (the build recipe), a **registry** (where images are stored and shared), and **volumes** (persistent storage that outlives the container).

## Example

```bash
docker build -t myapp:1.4.0 .
docker run -d --name web -p 8080:80 \
  --memory=512m --cpus=1 \
  -e NODE_ENV=production myapp:1.4.0
docker logs -f web
docker exec -it web sh
```

## Interview tips

- Namespaces + cgroups is the answer that separates people who have read about containers from people who understand them.
- Be clear that containers share the host kernel - that is both the performance win and the security consideration.
- Know the difference between Docker (the tooling) and the OCI standards it now conforms to.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Pod in Kubernetes?]] (`#13`): [What is a Pod in Kubernetes?](../kubernetes/what-is-a-pod-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
