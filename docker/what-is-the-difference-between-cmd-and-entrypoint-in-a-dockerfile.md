---
title: "What is the difference between CMD and ENTRYPOINT in a Dockerfile?"
id: 437
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - docker
  - interview-questions
---

# What is the difference between CMD and ENTRYPOINT in a Dockerfile?

**Short answer:** `ENTRYPOINT` declares **what the container is** - the executable that always runs. `CMD` declares **the default arguments** to that executable, and anything you append to `docker run` replaces them. If you set only `CMD`, the whole command is replaceable; if you set only `ENTRYPOINT`, arguments you pass are appended rather than replacing anything. The idiomatic production pattern is `ENTRYPOINT` in exec form naming the binary, plus `CMD` in exec form holding the default flags - so `docker run image` works out of the box and `docker run image --other-flag` still does something sensible.

## Detail

### The override rules, which is what interviewers actually test

| Dockerfile                                     | `docker run img`  | `docker run img --port 9090`                    |
| ---------------------------------------------- | ----------------- | ----------------------------------------------- |
| `CMD ["app","--port","8080"]`                  | `app --port 8080` | `--port 9090` (tries to execute `--port`, dies) |
| `ENTRYPOINT ["app"]`                           | `app`             | `app --port 9090`                               |
| `ENTRYPOINT ["app"]` + `CMD ["--port","8080"]` | `app --port 8080` | `app --port 9090`                               |

The third row is the one to write. It gives a working default and a clean override surface. `ENTRYPOINT` can still be replaced, but only with the explicit `docker run --entrypoint` flag - which is exactly the point: overriding the identity of the container should be deliberate.

### Exec form versus shell form

- **Exec form** - `ENTRYPOINT ["nginx", "-g", "daemon off;"]`. Runs the binary directly as **PID 1**. Signals from `docker stop` (SIGTERM) reach the process, so it shuts down gracefully.
- **Shell form** - `ENTRYPOINT nginx -g "daemon off;"`. Docker wraps it as `/bin/sh -c "..."`. The shell becomes PID 1 and **does not forward SIGTERM** to its child, so `docker stop` waits the full grace period and then SIGKILLs your application mid-request. This is the single most common real bug arising from this pair of instructions.

Two consequences of exec form worth knowing: there is no shell, so `$VARIABLE` is not expanded and `&&`, pipes, and globs do not work. If you need them, call the shell explicitly (`ENTRYPOINT ["sh","-c","exec app --flag $PORT"]`, keeping `exec` so the app still becomes PID 1), or better, do the work in an entrypoint script.

### Only the last one wins

If a Dockerfile contains several `CMD` or `ENTRYPOINT` lines, the build **does not error** - Docker silently uses the last of each. This is a favourite trick question. The same applies across a multi-stage build and across inheritance: a base image's `CMD` is inherited, and declaring your own `ENTRYPOINT` in a child image **resets the inherited `CMD` to null**, so you must redeclare `CMD` if you still want defaults.

### The entrypoint-script pattern

Real images usually need a little setup before the process starts - render a config template, wait for a dependency, apply migrations, drop privileges. Put that in a script, and end it with `exec "$@"` so the script is replaced by the real process and PID 1 semantics are preserved. Then `CMD` holds the default command that `"$@"` expands to.

### `init` and zombie reaping

PID 1 is also expected to reap orphaned child processes. If your application spawns children and does not reap them, you accumulate zombies. Use `docker run --init` (or `tini` in the image) rather than writing your own reaper.

## Example

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# exec form: gunicorn is PID 1 and receives SIGTERM from `docker stop`
ENTRYPOINT ["/app/entrypoint.sh"]
# default arguments - overridable on the command line
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:app"]
```

```bash
#!/bin/sh
# entrypoint.sh - setup, then hand PID 1 to the real process
set -e

envsubst < /app/config.tmpl > /app/config.yaml   # render config from env vars
until nc -z "$DB_HOST" 5432; do sleep 1; done    # wait for the database

exec "$@"     # <- the crucial line: replaces the shell, so signals reach the app
```

```bash
# Behaviour you should be able to predict on the spot
docker run img                      # entrypoint.sh -> gunicorn --bind 0.0.0.0:8080 ...
docker run img gunicorn --workers 8 # entrypoint.sh -> gunicorn --workers 8   (CMD replaced)
docker run img /bin/sh              # entrypoint.sh -> /bin/sh                (debug shell)
docker run --entrypoint /bin/sh img # skips entrypoint.sh entirely            (deliberate)

# Inspect what an image will actually run
docker inspect -f 'ENTRYPOINT={{.Config.Entrypoint}} CMD={{.Config.Cmd}}' img
```

## Interview tips

- Lead with the sentence that answers it: `ENTRYPOINT` is what runs, `CMD` is the default arguments, and `docker run` arguments replace `CMD` but only append to `ENTRYPOINT`.
- Then volunteer the exec-versus-shell-form point about signals. Saying "shell form makes `/bin/sh` PID 1, so `docker stop` never reaches your application and you get a hard kill after the grace period" is what separates a memorised answer from an operational one.
- If asked whether multiple `CMD` lines break the build, say no - the last one silently wins. Same for `ENTRYPOINT`.
- Mention that declaring `ENTRYPOINT` in a child image resets the base image's `CMD`. This trips people up when extending official images.
- Have the `exec "$@"` entrypoint-script pattern ready; it is the answer to "how do you run setup before your app starts without breaking signal handling?"
- The classic follow-up is the port mismatch: "the image `EXPOSE`s 8080 but the app listens on 9090". `EXPOSE` is documentation only - what matters is `-p`/`--publish` mapping and what the process actually binds. See [what is Dockerfile](./what-is-dockerfile.md) and [reducing Docker image size and build time](./how-do-you-reduce-docker-image-size-and-build-time.md).

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
