---
title: "What are the 12-Factor App principles?"
id: 70
category: "Cloud Native Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
---

# What are the 12-Factor App principles?

**Short answer:** The Twelve-Factor App is a methodology for building services that are portable, disposable, and suited to continuous deployment on cloud platforms — covering config, dependencies, processes, state, logs, and parity between environments.

## Detail

1. **Codebase** — one codebase tracked in version control, many deploys.
2. **Dependencies** — declared explicitly and isolated; never rely on system-wide packages.
3. **Config** — stored in the environment, not in code. Anything that varies between deploys is config.
4. **Backing services** — databases, queues, and caches are attached resources, swappable by changing a URL.
5. **Build, release, run** — strictly separated stages; a release is an immutable build plus config, with a unique ID.
6. **Processes** — stateless and share-nothing; persist state in a backing service.
7. **Port binding** — the app is self-contained and exports HTTP by binding a port, rather than being injected into a runtime container.
8. **Concurrency** — scale out by running more processes, not by threading a single big one.
9. **Disposability** — fast startup and graceful shutdown on `SIGTERM`; robust against sudden death.
10. **Dev/prod parity** — keep development, staging, and production as similar as possible in time, personnel, and tooling.
11. **Logs** — treat logs as event streams written to stdout; the platform handles routing and storage.
12. **Admin processes** — run migrations and one-off tasks as one-off processes in an identical environment.

**Why it still matters:** these principles are precisely what a container orchestrator assumes. A Twelve-Factor app runs on Kubernetes, Cloud Run, or Heroku with no modification; one that writes session state to local disk and logs to a file will not scale or survive rescheduling.

Common additions for modern services: expose health endpoints, emit telemetry (metrics and traces), and treat API contracts as versioned artifacts.

## Interview tips

- The three most commonly violated in practice are config in code, stateful processes, and logging to files — call those out.
- Connect each factor to a Kubernetes behaviour (disposability ↔ pod eviction, logs ↔ `kubectl logs`) to show applied understanding.
- Note that factor 10 (dev/prod parity) is what containers and IaC finally made achievable.

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
