---
title: "What are Docker network types (Bridge, Host, Overlay, Macvlan)?"
id: 252
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - docker
  - interview-questions
---

# What are Docker network types (Bridge, Host, Overlay, Macvlan)?

**Short answer:** Docker network drivers control container network isolation and connectivity: **Bridge** (default isolated network on a single host), **Host** (shares host network stack directly), **Overlay** (multi-host network across Swarm/cluster nodes), **Macvlan** (assigns a MAC address so containers appear as physical devices), and **None** (disables networking).

## Detail

Docker uses a pluggable Container Network Model (CNM) to provide network connectivity between containers and external networks:

### 1. Network Driver Breakdown

- **Bridge (Default):**
  - Creates a software bridge (`docker0` or user-defined bridge) on a single Docker host.
  - Containers receive private IP addresses (e.g. `172.17.0.x`) and communicate using NAT (Network Address Translation).
  - _User-defined bridge networks_ provide automatic internal DNS resolution by container name.
- **Host:**
  - Removes network isolation between the container and the Docker host.
  - The container shares the host's IP address and port namespace directly (e.g., container listening on port 80 binds directly to host `:80`). Provides maximum network performance by eliminating NAT overhead.
- **Overlay:**
  - Enables communication between containers running on different physical Docker hosts.
  - Creates a virtual VXLAN overlay network connecting Swarm daemon nodes or multi-host container networks without requiring host-routing rules.
- **Macvlan:**
  - Assigns a unique physical MAC address to a container, making it appear as a physical network device connected directly to the underlying physical network.
  - Ideal for legacy applications expecting direct access to physical subnets.
- **None:**
  - Disables all networking for the container, creating a completely isolated loopback interface.

### 2. Port Mapping & NAT Mechanics (`-p` / `-P`)

When using `bridge` mode, exposed container ports are mapped to host ports via Linux `iptables` rules:
`docker run -d -p 8080:80 nginx` forwards incoming host traffic on TCP `8080` to container TCP `80`.

## Example

Creating and using a custom user-defined bridge network with automatic DNS resolution:

```bash
# 1. Create custom isolated bridge network
docker network create --driver bridge app-net

# 2. Run database container attached to app-net
docker run -d --name postgres-db --network app-net -e POSTGRES_PASSWORD=secret postgres:16

# 3. Run web application container - can reach postgres-db by container name!
docker run -d --name web-app --network app-net -p 8080:80 my-web-app:v1

# 4. Verify network inspection and attached containers
docker network inspect app-net
```

Docker Compose custom overlay network definition for multi-service deployment:

```yaml
# No top-level `version:` key - the Compose Specification dropped it and
# Docker Compose v2 warns that the attribute is obsolete.
services:
  web:
    image: nginx:alpine
    networks:
      - frontend
    ports:
      - "80:80"

  api:
    image: my-api:v1
    networks:
      - frontend
      - backend

  db:
    image: postgres:16
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

## Interview tips

- Always highlight why **user-defined bridge networks** are superior to the default `bridge` network: default `bridge` requires legacy `--link` flags, while custom bridge networks provide automatic container name DNS resolution.
- Explain trade-offs: **Host mode** eliminates NAT overhead for maximum throughput, but introduces port conflict risks on the host and removes network isolation.
- Understand port forwarding mechanics: `docker run -p 8080:80` creates `iptables` DNAT rules intercepting host packets.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Pod in Kubernetes?]] (`#13`): [What is a Pod in Kubernetes?](../kubernetes/what-is-a-pod-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
