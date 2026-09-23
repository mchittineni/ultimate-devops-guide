---
title: "What is Docker Compose?"
id: 9
category: "Docker"
difficulty: "Beginner"
tags:
  - devops
  - docker
  - interview-questions
---

# What is Docker Compose?

**Short answer:** Docker Compose defines and runs multi-container applications from a single YAML file, so an entire local stack - app, database, cache, queue - starts with `docker compose up`.

## Detail

Compose is primarily a development and testing tool. It creates a dedicated network so services reach each other by service name, manages named volumes for persistence, wires up environment variables, and expresses startup ordering with dependency conditions.

Useful capabilities:

- **Service discovery by name** - the app connects to `db:5432`, no IP addresses anywhere.
- **`depends_on` with `condition: service_healthy`** - start the app only once the database passes its health check.
- **Profiles** - optional services (say, a seed job or an observability stack) enabled per invocation.
- **Override files** - `compose.override.yaml` layers local-only settings such as bind mounts and debug ports.

Two modernisation points trip people up. The standalone Python `docker-compose` (v1) reached end of life in 2023; today's Compose is the Go-based `docker compose` CLI plugin implementing the open **Compose Specification**. And the top-level `version:` key is obsolete - Compose ignores it and prints a warning - so current files start directly with `services:`. Newer features such as `docker compose watch` (sync or rebuild on file changes) and `include:` (compose files from other projects) build on that spec.

For production orchestration, Kubernetes or a managed container service is the normal choice; Compose does not provide scheduling, self-healing across hosts, or rolling updates. The trade-off is deliberate: Compose is simple precisely because it manages one host, and it is still a reasonable way to run a small, single-server deployment if you accept that the host is a single point of failure.

## Example

```yaml
services:
  api:
    build: .
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgres://app:secret@db:5432/app
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10

volumes:
  pgdata:
```

```bash
docker compose up -d --build
docker compose logs -f api
docker compose down -v      # -v also removes named volumes
```

## Interview tips

- Say explicitly where Compose stops and Kubernetes starts - it shows you know the tool's scope.
- `depends_on` alone only waits for _start_, not readiness; the health-check condition is the correct answer.
- Compose files are excellent for reproducible integration tests in CI.
- If you see `version: "3.8"` or `docker-compose` in a file or script, say it is legacy: the key is obsolete and v1 is end-of-life.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Pod in Kubernetes?]] (`#13`): [What is a Pod in Kubernetes?](../kubernetes/what-is-a-pod-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
