---
title: "What is the difference between a bind mount and a volume in Docker?"
id: 440
category: "Docker"
difficulty: "Beginner"
tags:
  - devops
  - docker
  - interview-questions
---

# What is the difference between a bind mount and a volume in Docker?

**Short answer:** A **bind mount** maps a specific path on the host into the container - you choose the path, the host owns it, and the container sees whatever is there. A **volume** is storage that **Docker creates and manages** in its own area (`/var/lib/docker/volumes/...` by default) or through a volume driver, referenced by name rather than by host path. Bind mounts are for development (live-reloading your source) and for deliberately reaching host resources; named volumes are what you use for persistent application data in production, because they are portable across hosts through drivers, backed up as a unit, and do not depend on the host's directory layout or permissions.

## Detail

### The comparison

|                                             | Bind mount                                                        | Named volume                                                  |
| ------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------- |
| Declared as                                 | `-v /host/path:/in/container` or `--mount type=bind,...`          | `-v myvol:/in/container` or `--mount type=volume,...`         |
| Who owns the path                           | You / the host filesystem                                         | Docker (or a volume driver)                                   |
| Exists before the container?                | Must exist (or Docker creates an empty dir)                       | Created on first use if absent                                |
| Pre-populated from the image?               | **No** - mounting over a directory hides the image's contents     | **Yes** - an empty new volume is seeded from the image path   |
| Portable across hosts                       | No - the path is host-specific                                    | Yes, with a driver (NFS, cloud block storage, CSI)            |
| Managed by `docker volume ls/inspect/prune` | No                                                                | Yes                                                           |
| Typical use                                 | Local development, mounting a config file, `/var/run/docker.sock` | Databases, uploads, any state that must outlive the container |

There is a third type, **tmpfs** (`--mount type=tmpfs`), which lives only in host memory and never touches disk - the right choice for scratch space and for secrets you do not want written down.

### The two behaviours that cause real bugs

**Mounting hides what was there.** A bind mount over `/app/node_modules` replaces whatever the image built into that path with the host's contents - which on a Mac or Windows host may be the wrong architecture, or empty. The standard fix is to bind-mount the source directory and then declare an **anonymous volume for the dependency directory** so the image's version wins.

**Named volumes seed once, then never again.** The first time an empty named volume is attached, Docker copies the image's contents at that path into it. On every later start the volume's existing contents are used and the image's are ignored. So updating a config file baked into the image has no visible effect if a volume already covers that path - and the "fix" people reach for (delete the volume) also deletes the data. Know this before you debug it at 2 a.m.

### Permissions, which is where most of the pain lives

A bind mount carries the host's numeric UID/GID straight through. If the container runs as UID 1000 and the host directory is owned by root, you get `permission denied`. Options, in order of preference: run the container as the owning UID (`--user "$(id -u):$(id -g)"`), fix ownership on the host, or use a named volume - Docker initialises a new volume with the ownership of the image path, which sidesteps the mismatch entirely. On SELinux hosts you additionally need the `:z` or `:Z` suffix on bind mounts.

### `-v` versus `--mount`

`-v` is terse and overloads its meaning by the shape of the argument - a leading `/` means bind mount, a bare word means volume, and a typo silently creates a stray volume instead of failing. `--mount` is explicit key-value (`type=`, `source=`, `target=`, `readonly`) and errors if the source is missing. Prefer `--mount` in anything scripted; it is also the only way to pass driver options and tmpfs settings.

### Where this maps onto Kubernetes

Interviewers frequently pivot here. `hostPath` is the bind mount (same host-coupling problems, plus it breaks scheduling assumptions and is a security concern), `emptyDir` is roughly the anonymous volume or tmpfs, and a **PersistentVolumeClaim** is the named volume with a driver - the CSI plugin doing what the Docker volume driver did. Say that mapping out loud; it shows you understand storage rather than two flags.

## Example

```bash
# Named volume: managed, portable, survives `docker rm`
docker volume create pgdata
docker run -d --name db \
  --mount type=volume,source=pgdata,target=/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=changeme postgres:16

# Bind mount: live source reload in development, with the image's deps preserved
docker run --rm -it \
  --mount type=bind,source="$PWD"/src,target=/app/src \
  -v /app/node_modules \
  -p 3000:3000 myapp:dev

# Read-only bind mount for config, tmpfs for scratch - both are good habits
docker run -d \
  --mount type=bind,source=/etc/myapp/config.yaml,target=/etc/app/config.yaml,readonly \
  --mount type=tmpfs,target=/tmp,tmpfs-size=64m \
  myapp:1.9.0
```

```yaml
# docker-compose.yml - the same distinction, declaratively
services:
  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data # named volume: state
  api:
    build: .
    volumes:
      - ./src:/app/src # bind mount: code
      - /app/node_modules # anonymous volume: keep the image's deps
      - ./config.yaml:/etc/app/config.yaml:ro
volumes:
  pgdata: # declared, so Docker manages it
```

```bash
# Operating volumes: inspect, back up, and reclaim
docker volume inspect pgdata --format '{{.Mountpoint}} {{.Driver}}'
docker run --rm -v pgdata:/data -v "$PWD":/backup alpine \
  tar czf /backup/pgdata-$(date +%F).tgz -C /data .
docker volume ls -f dangling=true      # anonymous volumes nobody owns
docker volume prune                    # DESTRUCTIVE: deletes unused volumes
```

## Interview tips

- Open with ownership: a bind mount is a host path **you** choose, a volume is storage **Docker** manages by name. Then give the use cases - bind mounts for development and host resources, named volumes for production state.
- Volunteer the seeding asymmetry: an empty named volume is pre-populated from the image, a bind mount hides the image's contents. That difference explains a whole class of "my config change did nothing" bugs.
- Have the permissions answer ready - bind mounts pass host UIDs straight through, which is the usual cause of `permission denied` on startup. See [why does a container fail to start with a permission denied error](./why-does-a-container-fail-to-start-with-a-permission-denied-error.md).
- Mention `tmpfs` as the third type. It is the correct answer to "where do you put a secret or scratch data you do not want on disk?"
- Recommend `--mount` over `-v` and say why: `-v` infers the type from the string shape and silently creates a stray volume on a typo.
- Close by mapping to Kubernetes - `hostPath` ≈ bind mount, `emptyDir` ≈ anonymous volume, PVC ≈ named volume with a driver. See [how does persistent storage work in Kubernetes](../kubernetes/how-does-persistent-storage-work-in-kubernetes.md) and [Docker architecture](./explain-docker-architecture.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Service in Kubernetes?]] (`#14`): [What is a Service in Kubernetes?](../kubernetes/what-is-a-service-in-kubernetes.md)
- [[How does RBAC work in Kubernetes?]] (`#257`): [How does RBAC work in Kubernetes?](../kubernetes/how-does-rbac-work-in-kubernetes.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
