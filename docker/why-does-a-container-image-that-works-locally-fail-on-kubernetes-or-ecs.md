---
title: "Why does a container image that works locally fail on Kubernetes or ECS?"
id: 793
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - docker
  - troubleshooting
  - multi-arch
  - kubernetes
quiz:
  stem: "An image built on an Apple Silicon laptop runs locally but every Pod on the cluster's x86 nodes exits immediately with `exec format error`. What is the cause?"
  options:
    - "The image was built for arm64 only and the nodes run amd64"
    - "The container is running out of memory"
    - "The security group blocks the container port"
    - "The Deployment is missing a readiness probe"
  answer: 1
  explanation: "exec format error means the kernel cannot execute the binary's architecture. Build multi-platform images in CI with docker buildx --platform linux/amd64,linux/arm64, or match the node architecture."
---

# Why does a container image that works locally fail on Kubernetes or ECS?

**Short answer:** Usually because "the same image" is not actually the same, or because the image is the same but the **environment around it** differs. The repeat causes are: a **different image** (rebuilt per environment, or a mutable tag such as `latest` that now points elsewhere), a **CPU architecture mismatch** (arm64 laptop build on amd64 nodes gives `exec format error`), **missing configuration** (environment variables, secrets, config files, endpoints), **identity and network** (IAM role, security groups, DNS, the app listening on `127.0.0.1`), and **runtime constraints** the laptop did not apply (memory limits, non-root user, read-only filesystem, probes). Build once in CI, deploy by digest, and diff the runtime settings rather than guessing.

## Detail

**1. Is it really the same image?** Laptops often have a locally built image that was never pushed, or a cached `latest`. Clusters pull whatever the tag points to at that moment. Build once in CI, push, and deploy the **digest** (`image@sha256:...`) through every environment so dev, staging, and prod run identical bytes. Compare `docker inspect --format '{{index .RepoDigests 0}}'` locally with the `imageID` in `kubectl get pod -o jsonpath='{.status.containerStatuses[0].imageID}'`.

**2. CPU architecture.** Apple Silicon builds `linux/arm64` by default. On amd64 nodes the container exits at once with `exec format error`, or the pull fails with `no matching manifest for linux/amd64`. Build multi-platform images with `docker buildx build --platform linux/amd64,linux/arm64`, or deliberately match nodes (Graviton on AWS is arm64).

**3. Configuration that existed only locally.** A `.env` file, a credentials file under `~/.aws`, or a local config file baked in by accident. In the cluster those must come from ConfigMaps, Secrets, or ECS task definition `environment` and `secrets`. A startup check that fails fast with a clear message on a missing variable saves hours.

**4. Identity and permissions.** Locally the app uses the developer's cloud credentials. In the cluster it needs its own role: EKS Pod Identity or IRSA for Pods, a **task role** for ECS (the **execution role** is only for pulling the image and reading secrets at launch, which people often confuse). Missing permissions show up as `AccessDenied` in the application logs.

**5. Networking.**

- The app binds to `127.0.0.1`. That works when the developer runs it directly on the laptop, but inside a container it is unreachable from port mappings, probes, and Services. Bind to `0.0.0.0`.
- `containerPort`, the Service `targetPort`, the ECS port mapping, and the port the app actually listens on must agree.
- Security groups or NetworkPolicies block traffic that a laptop never filtered, and the app may call `localhost:5432` for a database that only existed in local Compose.

**6. Runtime constraints.**

- **Memory limits.** Local Docker usually has no per-container limit; the cluster does, so the process is `OOMKilled` (exit code 137).
- **Security context.** `runAsNonRoot`, `readOnlyRootFilesystem`, and dropped capabilities break images that write to `/app` or bind to port 80 as root. Pod Security Admission or Fargate restrictions make this more likely.
- **Probes.** A liveness probe that fires before a slow start finishes restarts the container in a loop; use a startup probe or a longer ECS health check grace period.
- **Command overrides.** A Pod's `command` and `args` replace the image's `ENTRYPOINT` and `CMD`, so a manifest can run something different from `docker run`.

**Debugging order.** Read the status and events, then the logs of the previous attempt, then compare the settings.

## Example

```bash
# Kubernetes: what happened, and what did the crashed container print?
kubectl describe pod api-6b7c9 | sed -n '/State:/,/Ready:/p;/Events:/,$p'
kubectl logs api-6b7c9 --previous

# Which image and architecture is actually running?
kubectl get pod api-6b7c9 -o jsonpath='{.status.containerStatuses[0].imageID}{"\n"}'
docker buildx imagetools inspect registry.example.com/api:1.8.0   # lists platforms in the manifest

# ECS: why did the task stop?
aws ecs describe-tasks --cluster prod --tasks <task-arn> \
  --query 'tasks[0].{reason:stoppedReason,containers:containers[].[name,exitCode,reason]}'

# Reproduce locally with cluster-like constraints
docker run --rm --platform linux/amd64 --memory 512m --read-only --user 10001 \
  --env-file prod-like.env registry.example.com/api@sha256:<digest>
```

```bash
# Build once, for both architectures, in CI
docker buildx build --platform linux/amd64,linux/arm64 \
  -t registry.example.com/api:1.8.0 --push .
```

## Interview tips

- A common partial answer covers only ports, security groups, and image tags. Those are real, but add architecture, missing configuration, IAM identity, and memory or security-context constraints to show breadth.
- Lead with "build once, promote the same digest" because it eliminates a whole class of differences before any debugging starts.
- Know what `exec format error` (architecture) and exit code 137 (`OOMKilled`) mean on sight.
- For ECS, separate the task role from the task execution role; interviewers like that distinction.
- Show a method: events, previous logs, then a diff of env, ports, limits, and identity, then reproduce locally with the same digest and similar limits.

**Telling it as a STAR story** (an adaptable example)

- **Situation:** Developers kept reporting that images worked on their laptops but crashed on EKS, and each case took hours on calls.
- **Task:** Remove the common causes systematically instead of fixing them one by one.
- **Action:** I grouped recent failures by cause. Several were `exec format error` from arm64 laptop builds pushed directly to the registry, so I restricted pushes to CI and built multi-platform images with `docker buildx`, deploying by digest. Others were `OOMKilled` because local Docker had no memory limit; I right-sized requests and limits from metrics. The rest were missing variables and IAM permissions, so I added a Compose setup that loads the same keys as the Helm chart and a startup check that names any missing variable.
- **Result:** "Works locally, fails in the cluster" tickets dropped sharply over the next couple of months, and the remaining ones were diagnosed from events and logs in minutes.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Kubernetes Finalizers and how do you resolve a namespace stuck in the Terminating state?]] (`#529`): [What are Kubernetes Finalizers and how do you resolve a namespace stuck in the Terminating state?](../kubernetes/what-are-kubernetes-finalizers-and-how-do-you-resolve-a-namespace-stuck-in-the-terminating-state.md)
- [[How do you troubleshoot a Pod that fails because a Secret or ConfigMap cannot be mounted or referenced?]] (`#788`): [How do you troubleshoot a Pod that fails because a Secret or ConfigMap cannot be mounted or referenced?](../kubernetes/how-do-you-troubleshoot-a-pod-that-fails-because-a-secret-or-configmap-cannot-be-mounted-or-referenced.md)
- [[How do you troubleshoot a Pod stuck in ImagePullBackOff?]] (`#751`): [How do you troubleshoot a Pod stuck in ImagePullBackOff?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-imagepullbackoff.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
