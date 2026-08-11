---
title: "Why does a container fail to start with a permission denied error?"
id: 416
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - docker
  - interview-questions
  - linux-administration
  - devsecops
  - kubernetes
---

# Why does a container fail to start with a permission denied error?

**Short answer:** Almost always one of five things: **the entrypoint is not executable** (`chmod +x`, or a script copied from Windows with CRLF line endings, which fails as `not found` or `permission denied`), **the image runs as a non-root UID that does not own the files or directory it needs**, **a mounted volume is owned by a different UID on the host** so the container user cannot write to it, **a read-only filesystem or a `noexec` mount**, or **a host security module** - SELinux (`:Z` on the bind mount) or AppArmor - denying the access. Read the exact message: `exec /entrypoint.sh: permission denied` is the file's execute bit, whereas `mkdir /data/cache: permission denied` at runtime is volume ownership. They are unrelated problems.

## Detail

### 1. The entrypoint itself cannot be executed

- **Missing execute bit.** `COPY` preserves the source file's mode, so a script committed without `+x` arrives without it. Fix in the repository (`git update-index --chmod=+x entrypoint.sh`) or in the build (`COPY --chmod=0755 entrypoint.sh /`, or a `RUN chmod +x`).
- **CRLF line endings.** A script edited on Windows starts `#!/bin/sh\r`, and the kernel looks for an interpreter literally named `/bin/sh\r`. The error is `not found` or `permission denied` and the file looks perfect. Normalise with `.gitattributes` (`*.sh text eol=lf`) or `dos2unix`.
- **Wrong architecture.** An `amd64` binary on `arm64` (or the reverse on Apple Silicon) gives `exec format error` - adjacent to this family and often confused with it.
- **Shell-form vs exec-form `ENTRYPOINT`.** The exec form (`ENTRYPOINT ["./run.sh"]`) requires the file itself to be executable; `ENTRYPOINT ["sh", "run.sh"]` does not, which is a useful diagnostic: if it works with an explicit interpreter, the problem is the execute bit or the shebang.
- **`noexec`.** A binary on a volume mounted `noexec` cannot run regardless of its mode - common with `/tmp` hardening.

### 2. The container runs as a non-root user without the access it needs

Hardened images (and Kubernetes `runAsNonRoot`) drop to an unprivileged UID. Then:

- Binding to a port below 1024 needs `CAP_NET_BIND_SERVICE` - or better, listen on 8080 and map it.
- Writing to `/app`, `/var/log/app`, or `/data` fails unless the image `chown`s those paths at build time to the runtime UID: `RUN chown -R 10001:10001 /app` before `USER 10001`.
- Anything expecting to write into the image filesystem breaks under `readOnlyRootFilesystem: true` - the fix is an `emptyDir` or `tmpfs` mount for the paths that genuinely need writes (`/tmp`, a cache, a PID file), not disabling the control.
- A `USER` referring to a name that does not exist in `/etc/passwd` produces its own confusing failures - prefer a numeric UID, which is also what Kubernetes' `runAsNonRoot` check requires.

### 3. Volume and bind-mount ownership

This is the most common runtime case. A bind mount keeps the **host's** ownership and the container sees raw numeric UIDs, so a directory owned by host UID 1000 is unwritable by container UID 10001. Options, in order of preference:

- Align the UIDs deliberately - build the image with the UID that owns the data, or `chown` the host directory to it.
- In Kubernetes, set `securityContext.fsGroup`, which makes the kubelet apply group ownership to the volume (with `fsGroupChangePolicy: OnRootMismatch` to avoid a slow recursive chown on large volumes).
- For named Docker volumes, the volume inherits ownership from the image path on first use - so `chown` in the Dockerfile before the volume is populated, and remember an existing volume keeps its old ownership even after you fix the image, which is why "it works on a fresh machine" happens.
- Do **not** reach for `chmod 777` - it fixes the symptom, fails audits, and hides the ownership question you will meet again.

### 4. Host security modules and rootless quirks

- **SELinux** (RHEL, Fedora, CentOS) denies bind-mount access with a plain `Permission denied` and an AVC entry in the audit log. Add `:Z` (private label) or `:z` (shared) to the mount, or set the correct label with `chcon`. `getenforce` and `ausearch -m avc -ts recent` confirm it in seconds.
- **AppArmor** (Ubuntu, Debian) blocks specific syscalls or paths; the denial appears in `dmesg`.
- **Rootless Docker or Podman** maps container UIDs into a subuid range, so files created inside appear as high-numbered host UIDs and host files are frequently unreadable. Understanding this is what makes rootless debugging tractable.
- **`docker.sock` permission denied** is a different problem with the same words: your user is not in the `docker` group, or you are targeting the socket from inside a container without mounting it.

### The Kubernetes translation

The same causes appear as `CreateContainerConfigError`, a `CrashLoopBackOff` whose first log line is a permission error, or a Pod rejected by Pod Security Admission. The Pod-level answer is a deliberate `securityContext`: numeric `runAsUser`/`runAsGroup`, `fsGroup` for volumes, `readOnlyRootFilesystem` with writable `emptyDir` mounts where needed, `allowPrivilegeEscalation: false`, and dropped capabilities. See [how do namespaces, cgroups, and capabilities isolate a container](./how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md) and [how do you troubleshoot a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).

## Example

```bash
# Read the message precisely - it tells you which of the five causes it is
docker run --rm checkout:1.9.0
# exec /entrypoint.sh: permission denied        <- execute bit or shebang

# 1. Inspect the file's mode and line endings without starting the app
docker run --rm --entrypoint sh checkout:1.9.0 -c 'ls -l /entrypoint.sh; head -c 20 /entrypoint.sh | od -c | head -2'
# -rw-r--r-- 1 root root 812 /entrypoint.sh          <- no +x
# 0000000   #   !   /   b   i   n   /   s   h  \r  \n <- CRLF: the other classic

# 2. Who am I, and who owns what I need to write?
docker run --rm checkout:1.9.0 id
# uid=10001 gid=10001
docker run --rm -v "$PWD/data:/data" checkout:1.9.0 ls -ld /data
# drwxr-xr-x 2 1000 1000 /data      <- host UID 1000 owns it; container UID 10001 cannot write

# 3. SELinux? Two commands settle it.
getenforce && sudo ausearch -m avc -ts recent | tail -5
docker run --rm -v "$PWD/data:/data:Z" checkout:1.9.0 touch /data/ok   # relabelled

# 4. Confirm a theory by bypassing it (debug only, never the fix)
docker run --rm --user 0 checkout:1.9.0 touch /data/ok   # works as root => ownership
```

```dockerfile
# Build it so this cannot happen: fixed mode, numeric UID, ownership set before USER
FROM python:3.12-slim AS runtime
RUN groupadd -g 10001 app && useradd -u 10001 -g 10001 -m -s /usr/sbin/nologin app
WORKDIR /app
COPY --chmod=0755 entrypoint.sh /entrypoint.sh
COPY --chown=10001:10001 . /app
RUN mkdir -p /app/cache && chown -R 10001:10001 /app/cache
USER 10001
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
```

```yaml
# Kubernetes: the securityContext that makes non-root work with volumes
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001 # numeric - a username here fails the runAsNonRoot check
    fsGroup: 10001 # kubelet applies this group to mounted volumes
    fsGroupChangePolicy: OnRootMismatch # avoids a slow recursive chown on large volumes
  containers:
    - name: api
      securityContext:
        readOnlyRootFilesystem: true
        allowPrivilegeEscalation: false
        capabilities: { drop: ["ALL"] }
      volumeMounts: # the writable paths a read-only root still needs
        - { name: tmp, mountPath: /tmp }
        - { name: cache, mountPath: /app/cache }
  volumes:
    - { name: tmp, emptyDir: {} }
    - { name: cache, emptyDir: {} }
```

## Interview tips

- Start by splitting the failure: `exec ...: permission denied` on startup is the entrypoint's execute bit or shebang, while a permission error in the application log is ownership. Candidates who treat them as one problem debug the wrong layer.
- CRLF line endings are the most satisfying answer to have ready - the file looks perfect, `ls -l` shows the execute bit, and the kernel is looking for `/bin/sh\r`.
- Explain that a bind mount preserves host ownership and the container only sees numeric UIDs. That single fact explains most volume permission problems.
- Name `fsGroup` (and `fsGroupChangePolicy: OnRootMismatch`) for the Kubernetes version. It is the specific answer to "the volume mounts but the app cannot write".
- Say that you would not fix it with `chmod 777` or by running as root, and give the real fix: `chown` at build time to a numeric UID, and writable `emptyDir` mounts under a read-only root filesystem.
- Have SELinux ready with the two-command check (`getenforce`, `ausearch`) and the `:Z` mount flag. It is the answer on any RHEL-family host and few candidates reach for it.
- Mention `--user 0` as a **diagnostic** to confirm the theory, immediately followed by "not the fix" - the distinction is what interviewers are listening for.
- If asked why images run as non-root at all, connect it to container escape risk and Pod Security Admission rather than treating it as a formality. See [how do you reduce Docker image size and build time](./how-do-you-reduce-docker-image-size-and-build-time.md) for the adjacent build-hygiene answer.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between a ConfigMap and a Secret in Kubernetes?]] (`#442`): [What is the difference between a ConfigMap and a Secret in Kubernetes?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)
- [[How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?]] (`#405`): [How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md)
- [[How do you troubleshoot a Kubernetes node that is NotReady?]] (`#449`): [How do you troubleshoot a Kubernetes node that is NotReady?](../kubernetes/how-do-you-troubleshoot-a-kubernetes-node-that-is-notready.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
