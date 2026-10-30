---
title: "What is the difference between Docker and Podman?"
id: 754
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - docker
  - interview-questions
quiz:
  stem: "What is the main architectural difference between Docker and Podman?"
  options:
    - "Podman cannot run OCI images built by Docker"
    - "Docker routes commands through a long-running daemon, while Podman forks containers directly from the CLI with no central daemon"
    - "Podman only runs on Windows"
    - "Docker does not use namespaces or cgroups"
  answer: 2
  explanation: "Docker's CLI talks to dockerd, which supervises containers. Podman's CLI starts each container itself (via conmon and an OCI runtime), so there is no root daemon to compromise, and rootless operation is the default."
---

# What is the difference between Docker and Podman?

**Short answer:** Both build and run the same OCI images with largely the same CLI, so `alias docker=podman` works for most day-to-day commands. The difference is architecture: **Docker** is client/server - the `docker` CLI sends every request to a long-running daemon (`dockerd`, usually root), which supervises containers through containerd. **Podman** is **daemonless** - the CLI starts each container itself through a small monitor process (`conmon`) and an OCI runtime (`crun` or `runc`), and it runs **rootless by default**, so there is no privileged daemon socket to protect. Podman also has native **pods** (shared network namespace, like Kubernetes) and integrates with **systemd** through Quadlet files. Docker's strengths are ecosystem and polish: Compose, Docker Desktop, BuildKit, and near-universal CI support.

## Detail

### Side by side

|                   | Docker                                               | Podman                                                                                            |
| ----------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Architecture      | CLI → `dockerd` (daemon) → containerd → runc         | CLI → `conmon` → crun/runc; no daemon                                                             |
| Default privilege | Root daemon; rootless mode optional                  | Rootless by default; rootful optional                                                             |
| Attack surface    | Access to `/var/run/docker.sock` = root on the host  | No root daemon socket; per-user API socket only if you enable it                                  |
| Restart on boot   | Daemon restart policies (`--restart unless-stopped`) | systemd units, generated from **Quadlet** `.container` files                                      |
| Pods              | No                                                   | Yes - `podman pod`, and `podman kube play` runs Kubernetes YAML                                   |
| Build engine      | BuildKit                                             | Buildah (same Dockerfile syntax; some BuildKit-only features differ)                              |
| Compose           | `docker compose` (first-party)                       | `podman compose` wraps `docker-compose` or `podman-compose`; Docker API socket works with Compose |
| Desktop app       | Docker Desktop (paid for larger companies)           | Podman Desktop (free, Apache 2.0)                                                                 |
| Default on        | Most CI runners and developer laptops                | RHEL, Fedora, CentOS Stream                                                                       |

### What "daemonless" and "rootless" buy you

- **No single privileged process.** With Docker, anyone who can write to the daemon socket can start a `--privileged` container with `/` mounted - root on the host. With rootless Podman, a container escape lands as the unprivileged user who started it, because container UID 0 is mapped through a **user namespace** to a subordinate UID range (`/etc/subuid`).
- **Containers are ordinary child processes** of the user's session or a systemd unit, so they show up in `systemctl`, `journalctl`, and cgroup accounting naturally, and a daemon crash cannot take every container down at once.

### The costs of rootless (either tool)

- **Low ports**: binding below 1024 needs `net.ipv4.ip_unprivileged_port_start` lowered, or a high port.
- **Networking**: rootless containers use user-mode networking (`pasta` by default in Podman 5, formerly `slirp4netns`), which is slower than a kernel bridge and hides the client source IP in some modes.
- **File ownership**: files written to bind mounts appear on the host under subordinate UIDs; `podman unshare` and `--userns=keep-id` are the tools to manage that.
- **Ecosystem gaps**: tools that hard-code the Docker socket (some CI plugins, Testcontainers setups) need `podman system service` to expose a Docker-compatible API.

Docker's own **rootless mode** closes much of the security gap, but it is opt-in and still a daemon - just one running as your user.

## Example

```bash
# Same images, same verbs
podman run -d --name web -p 8080:80 docker.io/library/nginx:1.29
podman ps
podman unshare cat /proc/self/uid_map     # container UID 0 -> your UID; others -> /etc/subuid range

# Native pods: containers sharing a network namespace, like Kubernetes
podman pod create --name app -p 8080:80
podman run -d --pod app docker.io/library/nginx:1.29
podman kube generate app > app.yaml        # emit Kubernetes YAML from the pod
podman kube play app.yaml                  # or run Kubernetes YAML locally

# Expose a Docker-compatible API for tools that expect a Docker socket
systemctl --user enable --now podman.socket
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock
```

```ini
# ~/.config/containers/systemd/web.container - a Quadlet unit: systemd runs and restarts it
[Unit]
Description=nginx web

[Container]
Image=docker.io/library/nginx:1.29
PublishPort=8080:80

[Service]
Restart=always

[Install]
WantedBy=default.target
```

## Interview tips

- Lead with the architecture: Docker is daemon-based, Podman is daemonless and forks containers directly. Everything else follows from that.
- Tie it to security: the Docker socket is root on the host, while rootless Podman maps container root to an unprivileged UID through user namespaces.
- Be fair to Docker: it also has a rootless mode, and it wins on ecosystem - Compose, BuildKit features, Desktop, and CI defaults.
- Mention Podman's pods, `podman kube play`, and Quadlet/systemd integration as the features with no Docker equivalent.
- Name the rootless trade-offs - ports below 1024, user-mode networking performance, and bind-mount ownership - so the answer does not read as advocacy. See [Docker architecture](./explain-docker-architecture.md) and [why you should avoid running containers as root](./why-should-you-avoid-running-containers-as-the-root-user-and-how-do-you-enforce-non-root-execution.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck in ImagePullBackOff?]] (`#751`): [How do you troubleshoot a Pod stuck in ImagePullBackOff?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-imagepullbackoff.md)
- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
