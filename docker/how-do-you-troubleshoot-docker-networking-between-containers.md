---
title: "How do you troubleshoot Docker networking between containers?"
id: 415
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - docker
  - interview-questions
  - network-security
  - linux-administration
---

# How do you troubleshoot Docker networking between containers?

**Short answer:** Check the three things that cause almost every case, in order: **are both containers on the same user-defined network** (`docker network inspect` - containers on the default bridge get no DNS-based service discovery, only IP), **are you using the container or service name rather than `localhost`** (each container has its own network namespace, so `localhost` is itself), and **is the target process listening on `0.0.0.0` rather than `127.0.0.1`** inside its container. After that: the port you connect to must be the **container's** port, not the host-published one; `-p` is only for host-to-container traffic and is irrelevant between containers on the same network.

## Detail

### The mental model that prevents most of these bugs

Each container has its own network namespace, its own loopback, and its own IP on each network it joins. Consequences worth stating:

- `localhost` inside a container means that container. An application configured with `DB_HOST=localhost` will never reach a database in another container.
- Containers on the **same user-defined network** reach each other by **container name or network alias**, resolved by Docker's embedded DNS at `127.0.0.11`. On the **default** `bridge` network there is no such DNS - which is why "it works in Compose but not with plain `docker run`" is such a common report: Compose creates a user-defined network for you.
- Between containers you use the **container port** (`db:5432`), not the published host port. `-p 15432:5432` maps the host to the container; another container on the same network still connects to `5432`.
- Publishing to `127.0.0.1:8080:80` binds to the host loopback only - which is correct for security but means nothing outside the host can reach it, including other hosts and, on some setups, other VMs.

### The diagnostic sequence

1. **Same network?** `docker network inspect <net>` lists the attached containers with their IPs, and `docker inspect -f '{{json .NetworkSettings.Networks}}' <ctr>` shows what a container is joined to. Two containers on different networks cannot reach each other, no matter how correct the application configuration is.
2. **Does the name resolve?** From inside the client container: `getent hosts db` or `nslookup db`. Resolution failing means wrong network, wrong name, or the container is stopped - Docker's DNS only has records for running containers, and a restarted container may have a new IP, which is exactly why you must use names and never cache IPs.
3. **Is anything listening, and on which address?** In the target container: `ss -lntp` (or `netstat -lntp`). `127.0.0.1:8080` means the process bound to loopback and is unreachable from outside; it must bind `0.0.0.0`. This is the second-most-common cause after the network mismatch.
4. **Test the path in layers.** From the client container: `nc -zv db 5432` (TCP reachability), then the application-level call. A **timeout** points to a firewall, a policy, or a wrong network; **connection refused** means the packet arrived and nothing was listening on that port.
5. **Check startup ordering.** `depends_on` in Compose waits for the container to _start_, not for the service to be _ready_. A client that connects once at boot and exits will "randomly" fail; use a healthcheck with `condition: service_healthy`, or make the client retry.
6. **Check the host layer if it is host-to-container.** Published port occupied by another process, the daemon's iptables rules flushed by a firewall tool (`firewalld`/`ufw` reload commonly breaks Docker's `DOCKER` chain - the fix is restarting the daemon so it re-creates them), `net.ipv4.ip_forward` disabled, or SELinux/AppArmor blocking. On Docker Desktop, `host.docker.internal` is the way back to the host; `--network host` behaves differently on macOS and Windows than on Linux.
7. **Overlay-specific issues** for Swarm or multi-host: the control plane needs TCP/UDP 7946 and UDP 4789 (VXLAN) open between nodes, and MTU mismatches produce the signature symptom of small requests working while large payloads hang.

### Use the right tools inside a minimal container

Production images have no `ping`, `dig`, or `ss`, and installing them into a running container is a bad habit. Attach a debug container to the same network namespace instead:

```bash
docker run --rm -it --network container:<target> nicolaka/netshoot bash
```

That gives you a full toolbox _inside the target's namespace_, so what you observe is exactly what the application sees.

### The design that avoids the whole class

Define an explicit user-defined network per application stack, refer to services by name, keep all inter-service ports unpublished (publish only the edge), add healthchecks so ordering is expressed rather than assumed, and put database credentials and hostnames in environment variables that name the service (`DB_HOST=db`), never `localhost`. See [what are Docker network types](./what-are-docker-network-types-bridge-host-overlay-macvlan.md) and [what is Docker Compose](./what-is-docker-compose.md).

## Example

```bash
# 1. Are they even on the same network?
docker network inspect app-net --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'
docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' api db
# api: app-net    db: bridge     <- there is the bug: different networks

# 2. Debug from inside the client's namespace, with real tools
docker run --rm -it --network container:api nicolaka/netshoot bash
  getent hosts db            # DNS via Docker's resolver at 127.0.0.11
  nc -zv db 5432             # timeout = blocked/wrong network; refused = nothing listening
  curl -sv http://api:8080/healthz

# 3. What is the target actually listening on?
docker exec db ss -lntp
# LISTEN 0 128 127.0.0.1:5432   <- bound to loopback: unreachable from other containers

# 4. Fix the network membership without recreating anything
docker network connect app-net db
```

```yaml
# Compose: one explicit network, names not localhost, readiness not just start order
services:
  api:
    image: checkout:1.9.0
    environment:
      DB_HOST: db # the SERVICE NAME - never localhost
      DB_PORT: "5432" # the CONTAINER port - not a published host port
    depends_on:
      db:
        condition: service_healthy # depends_on alone only waits for "started"
    networks: [app-net]
    ports: ["127.0.0.1:8080:8080"] # only the edge is published, host-loopback only

  db:
    image: postgres:16.4
    command: ["postgres", "-c", "listen_addresses=*"] # bind 0.0.0.0, not 127.0.0.1
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
    networks: [app-net] # no published ports: reachable only inside the network

networks:
  app-net: # user-defined -> embedded DNS, so names resolve
    driver: bridge
```

## Interview tips

- Lead with the network-namespace consequence: `localhost` is the container itself. It explains a large share of real failures in one sentence.
- The user-defined-versus-default bridge distinction is the key technical point - DNS-based service discovery only exists on user-defined networks. Mentioning that Compose creates one for you explains the "works in Compose, not in `docker run`" report.
- Say that between containers you use the container port, and that `-p` is host-to-container only. Candidates who publish ports to make two containers talk have revealed a wrong mental model.
- `ss -lntp` showing a bind to `127.0.0.1` is the second cause to name, and it is the one that survives every YAML fix.
- Distinguish timeout from connection refused as diagnostic information, not just as error text.
- Mention `--network container:<target>` with netshoot. It shows you debug inside the right namespace instead of installing tools into production images.
- Have one host-layer cause ready - a firewall reload flushing Docker's iptables chains is the classic - and the overlay MTU symptom if the interviewer moves to multi-host.
- Close on `depends_on` not meaning ready, and healthchecks plus client-side retries as the correct fix.

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
