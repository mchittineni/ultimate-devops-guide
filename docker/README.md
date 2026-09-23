---
title: "Docker"
category: "Docker"
tags:
  - devops
  - docker
  - index
---

# Docker

Container fundamentals - images versus containers, Dockerfile authoring, Compose, and the client/daemon architecture underneath `docker run`.

**22 questions** · 🟢 Beginner: 9 · 🟡 Intermediate: 10 · 🔴 Advanced: 3

## Questions

| #   | Question                                                                                                                                                                                                       | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 6   | [What is Docker?](./what-is-docker.md)                                                                                                                                                                         | 🟢 Beginner     |
| 7   | [What is the difference between Docker Image and Docker Container?](./what-is-the-difference-between-docker-image-and-docker-container.md)                                                                     | 🟢 Beginner     |
| 8   | [What is Dockerfile?](./what-is-dockerfile.md)                                                                                                                                                                 | 🟢 Beginner     |
| 9   | [What is Docker Compose?](./what-is-docker-compose.md)                                                                                                                                                         | 🟢 Beginner     |
| 10  | [Explain Docker Architecture](./explain-docker-architecture.md)                                                                                                                                                | 🟡 Intermediate |
| 252 | [What are Docker network types (Bridge, Host, Overlay, Macvlan)?](./what-are-docker-network-types-bridge-host-overlay-macvlan.md)                                                                              | 🟡 Intermediate |
| 260 | [How do you reduce Docker image size and build time?](./how-do-you-reduce-docker-image-size-and-build-time.md)                                                                                                 | 🟡 Intermediate |
| 291 | [How do namespaces, cgroups, and capabilities isolate a container?](./how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md)                                                                       | 🔴 Advanced     |
| 415 | [How do you troubleshoot Docker networking between containers?](./how-do-you-troubleshoot-docker-networking-between-containers.md)                                                                             | 🟡 Intermediate |
| 416 | [Why does a container fail to start with a permission denied error?](./why-does-a-container-fail-to-start-with-a-permission-denied-error.md)                                                                   | 🟡 Intermediate |
| 437 | [What is the difference between CMD and ENTRYPOINT in a Dockerfile?](./what-is-the-difference-between-cmd-and-entrypoint-in-a-dockerfile.md)                                                                   | 🟡 Intermediate |
| 438 | [What is the difference between the COPY and ADD instructions in a Dockerfile?](./what-is-the-difference-between-the-copy-and-add-instructions-in-a-dockerfile.md)                                             | 🟢 Beginner     |
| 439 | [How does Docker layer caching work?](./how-does-docker-layer-caching-work.md)                                                                                                                                 | 🟡 Intermediate |
| 440 | [What is the difference between a bind mount and a volume in Docker?](./what-is-the-difference-between-a-bind-mount-and-a-volume-in-docker.md)                                                                 | 🟢 Beginner     |
| 441 | [How do you harden a container image and a Dockerfile?](./how-do-you-harden-a-container-image-and-a-dockerfile.md)                                                                                             | 🔴 Advanced     |
| 513 | [How does Docker multi-stage building optimize container security and image size?](./how-does-docker-multi-stage-building-optimize-container-security-and-image-size.md)                                       | 🟢 Beginner     |
| 514 | [What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?](./what-are-linux-cgroups-v2-and-how-do-they-improve-container-resource-isolation-over-cgroups-v1.md)         | 🔴 Advanced     |
| 515 | [How does Docker BuildKit work and what caching and build features does it unlock?](./how-does-docker-buildkit-work-and-what-caching-and-build-features-does-it-unlock.md)                                     | 🟡 Intermediate |
| 516 | [What happens under the hood when a container experiences an Out Of Memory (OOM) kill?](./what-happens-under-the-hood-when-a-container-experiences-an-out-of-memory-oom-kill.md)                               | 🟡 Intermediate |
| 517 | [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](./how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)           | 🟡 Intermediate |
| 518 | [Why should you avoid running containers as the root user and how do you enforce non-root execution?](./why-should-you-avoid-running-containers-as-the-root-user-and-how-do-you-enforce-non-root-execution.md) | 🟢 Beginner     |
| 519 | [What is the difference between ENTRYPOINT and CMD in a Dockerfile and how do they interact?](./what-is-the-difference-between-entrypoint-and-cmd-in-a-dockerfile-and-how-do-they-interact.md)                 | 🟢 Beginner     |

## What interviewers probe here

- Image layers, the build cache, and how to keep images small.
- Why a container is not a virtual machine.
- Multi-stage builds and running as a non-root user.

---

[⬅ Back to all topics](../README.md)
