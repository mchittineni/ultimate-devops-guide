---
title: "What is the difference between ENTRYPOINT and CMD in a Dockerfile and how do they interact?"
id: 519
category: "Docker"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - docker
  - dockerfile
  - entrypoint
  - cmd
quiz:
  stem: "Why does using the shell form (`ENTRYPOINT my-app`) instead of exec form (`ENTRYPOINT ["my-app"]`) frequently cause slow container shutdowns?"
  options:
    - "Shell form forces the container to compile the binary on startup"
    - "The application runs as a child of `/bin/sh`, which does not forward `SIGTERM` signals, forcing Docker to wait for timeout and issue `SIGKILL`"
    - "The shell form disables DNS resolution inside the container"
    - "Docker requires an extra license to stop shell-based containers gracefully"
  answer: 2
  explanation: "In shell form, `/bin/sh` is PID 1. Standard shells do not forward signals like SIGTERM to child processes, causing `docker stop` to hang for 10 seconds before forcibly killing the container with SIGKILL."
---

# What is the difference between ENTRYPOINT and CMD in a Dockerfile and how do they interact?

**Short answer:** `ENTRYPOINT` sets the executable the container always runs; `CMD` sets default arguments (or, with no `ENTRYPOINT`, the default command). At start-up Docker concatenates them - `ENTRYPOINT` followed by `CMD` - and arguments given to `docker run` **replace `CMD`** while leaving `ENTRYPOINT` in place; only `--entrypoint` replaces the executable. The interaction only works as expected in **exec form** (JSON arrays): a shell-form `ENTRYPOINT` ignores `CMD` and `docker run` arguments entirely and wraps the process in `/bin/sh -c`, which can stop `SIGTERM` reaching it.

## Detail

**The combination rules.**

| `ENTRYPOINT`               | `CMD`                             | `docker run img`           | `docker run img --port 9090`                   |
| -------------------------- | --------------------------------- | -------------------------- | ---------------------------------------------- |
| none                       | `["/app/server","--port","8080"]` | `/app/server --port 8080`  | `--port 9090` (fails: not a command)           |
| `["/app/server"]`          | none                              | `/app/server`              | `/app/server --port 9090`                      |
| `["/app/server"]`          | `["--port","8080"]`               | `/app/server --port 8080`  | `/app/server --port 9090`                      |
| `/app/server` (shell form) | anything                          | `/bin/sh -c "/app/server"` | `/bin/sh -c "/app/server"` (arguments ignored) |

The third row is the idiomatic pattern: a fixed executable with overridable defaults.

**Exec form versus shell form.**

- **Exec form** (`ENTRYPOINT ["/app/server"]`) runs the binary directly as PID 1, so `docker stop`'s `SIGTERM` reaches it and it can shut down gracefully. There is no shell, so `$VAR` expansion, pipes, and `&&` do not work.
- **Shell form** (`ENTRYPOINT /app/server`) becomes `/bin/sh -c "/app/server"`. If the shell stays as PID 1, it does not forward `SIGTERM` to the child, so Docker waits for the stop timeout (10 seconds by default) and then sends `SIGKILL`. Some shells optimise a single simple command by exec-ing it, which hides the problem - but you cannot rely on that, and shell form still discards `CMD` and run-time arguments.

**Inheritance details.** Only the last `ENTRYPOINT` and last `CMD` in a Dockerfile take effect. Setting `ENTRYPOINT` in a child image resets any `CMD` inherited from the base image, so redeclare `CMD` if you want defaults. A PID 1 process also has to reap zombie children; if yours does not, use `docker run --init` or `tini`.

**Trade-off.** A fixed `ENTRYPOINT` makes the image behave like a single command, which is clean for services and CLIs, but makes ad-hoc debugging (`docker run img sh`) require `--entrypoint`. Images meant to be general-purpose (base images, toolboxes) usually set only `CMD`.

## Example

```dockerfile
# syntax=docker/dockerfile:1
FROM gcr.io/distroless/static-debian12:nonroot
COPY server /app/server
# exec form: the executable is fixed, the flags are defaults
ENTRYPOINT ["/app/server"]
CMD ["--port", "8080", "--env", "production"]
```

```bash
docker run myimage                          # /app/server --port 8080 --env production
docker run myimage --port 9090              # /app/server --port 9090   (CMD replaced)
docker run --entrypoint /busybox/sh myimage # entrypoint replaced (needs an image that has it)
docker inspect -f '{{.Config.Entrypoint}} {{.Config.Cmd}}' myimage
time docker stop <container>                # ~instant with exec form; ~10 s means SIGTERM was lost
```

## Interview tips

- State the rule precisely: the command is `ENTRYPOINT` + `CMD`; `docker run` arguments replace `CMD`; `--entrypoint` replaces `ENTRYPOINT`.
- Recommend exec-form `ENTRYPOINT` plus exec-form `CMD` for defaults, and say why.
- Explain the shell-form problems: `CMD` and run arguments are ignored, and `/bin/sh` as PID 1 may swallow `SIGTERM`, causing a 10-second stop and a `SIGKILL`.
- Mention that a child image's `ENTRYPOINT` resets the inherited `CMD`, and that only the last of each instruction counts.
- For wrapper scripts, end them with `exec "$@"` so the real process becomes PID 1.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Pod in Kubernetes?]] (`#13`): [What is a Pod in Kubernetes?](../kubernetes/what-is-a-pod-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
