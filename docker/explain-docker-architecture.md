---
title: "Explain Docker Architecture"
id: 10
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - docker
  - interview-questions
---

# Explain Docker Architecture

**Short answer:** Docker uses a client/server architecture: the CLI talks over a REST API to the Docker daemon, which builds images, manages containers via a runtime stack (containerd → runc), and pulls or pushes images to registries.

## Detail

**Docker client** - `docker` on the command line. It sends API requests over a Unix socket (`/var/run/docker.sock`) or TCP to a daemon, which may be on another host.

**Docker daemon (`dockerd`)** - the long-running server. It handles API requests, builds images with BuildKit, manages networks and volumes, and delegates the actual container lifecycle downwards.

**containerd** - the container runtime that supervises container lifecycle, image pulls, and storage. It is an independent CNCF project, which is why Kubernetes was able to drop the Docker shim and talk to containerd directly.

**runc** - the low-level OCI runtime that actually creates the container: it sets up namespaces and cgroups and execs the process. One short-lived `runc` invocation per container start.

**Registry** - Docker Hub, GHCR, ECR, or a private registry storing images by digest and tag.

**Objects** - images, containers, volumes, networks, and (in Swarm mode) services.

The layered design matters: because `containerd` and `runc` implement OCI standards, images built by Docker run under Podman, CRI-O, or Kubernetes without change.

## Example

```text
docker CLI ──REST/socket──▶ dockerd ──gRPC──▶ containerd ──▶ containerd-shim ──▶ runc ──▶ [namespaces + cgroups] ──▶ your process
                              │
                              └──▶ registry (pull/push), BuildKit (build), libnetwork (networks)
```

## Interview tips

- Being able to name containerd and runc, and say what each does, is the differentiator on this question.
- Explain rootless mode and why exposing the Docker socket to a container is effectively granting root on the host.
- Link it forward: "Kubernetes deprecated dockershim" makes sense only if you know this stack.

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
