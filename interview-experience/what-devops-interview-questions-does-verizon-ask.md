---
title: "What DevOps interview questions does Verizon ask?"
id: 388
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - verizon
  - kubernetes
  - linux-administration
  - docker
  - aws-engineering
  - container-orchestration-advanced
  - devsecops
  - database-management-in-devops
---

# What DevOps interview questions does Verizon ask?

## Questions

**Kubernetes internals**

- **What are the disadvantages of each deployment model in Kubernetes?**
- **In the Kubernetes architecture, which component does not run as a Pod?**
- **What are the Kubernetes quality-of-service classes?**
- **What are requests and limits?**
- **Why can you not place application Pods on the control-plane node by default?**
- **What is the disadvantage of using EBS volumes in EKS?**
- **What are init containers and sidecar containers?**
- **What are liveness and readiness probes?**
- **What is OOM, and how do you resolve an OOM problem?**
- **Is etcd a SQL or a NoSQL database, and why?**

**Cluster operations**

- **How many clusters do you have in your project, and how many Pods per node?**
- **Which Kubernetes version do you use, and have you performed a cluster upgrade?**
- **How do you switch between clusters — what is the command? And what is a context in Kubernetes?**

**Docker**

- **How do you ensure container security while writing a Dockerfile?**
- **In `docker run`, does `-p` stand for port or publish?**

**Linux**

- **Is Linux an operating system or a kernel?**
- **Explain the Linux file hierarchy.**
- **What is the difference between a hard link and a soft link?**
- **What is a cron job?**
- **What are the types of variable in Linux?**
- **What is the difference between `kill` and `kill -9`, and how many signals does Linux have?**
- **How do you check a Linux process without using `ps` or `top`?**

**AWS**

- **What is the difference between Secrets Manager and Parameter Store?**
- **What are the other ways to connect to EC2 without a `.pem` key?**
- **What are the steps to scale an RDS database horizontally and vertically?**
- **What is the difference between RDS Multi-AZ and read replicas?**
- **How do you delete old or untagged images from ECR?**

## Example

```text
Verizon — DevOps Engineer (3 YOE), reported round
28 questions

  Kubernetes internals       10   QoS classes, which component is not a Pod,
                                  why not the control-plane node, EBS in EKS,
                                  init vs sidecar, OOM, is etcd SQL or NoSQL
  Linux                       7   OS vs kernel, file hierarchy, hard vs soft
                                  link, cron, variable types, kill vs kill -9,
                                  process without ps or top
  AWS                         5   Secrets Manager vs Parameter Store, EC2
                                  without a key, RDS scaling, Multi-AZ vs
                                  read replicas, ECR image cleanup
  Cluster operations          3   cluster and Pod counts, version + upgrade,
                                  context switching
  Docker                      2   Dockerfile security, what -p means

A PRECISION ROUND
  At 3 years of experience the questions are unusually exact — QoS classes,
  which component is not a Pod, whether -p means port or publish. These have
  single correct answers, so the round rewards accuracy over breadth.
```

## Interview tips

- "Which component does not run as a Pod?" has one answer: the **kubelet**. Everything else on a `kubeadm`-built cluster — API server, etcd, scheduler, controller manager, kube-proxy — runs as a Pod (static Pods for the control plane), but the kubelet is a `systemd` service on the host, because something outside the Pod abstraction has to start Pods in the first place. Add that the container runtime (`containerd`) is also a host service for the same reason. That bootstrap argument is what makes the answer convincing rather than memorised. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- The QoS question expects the three classes by name and the rule that assigns them: **Guaranteed** when every container has requests equal to limits for both CPU and memory; **Burstable** when requests are set but lower than limits, or only one resource is specified; **BestEffort** when neither requests nor limits are set. Then give the consequence, which is the point of the question: under node memory pressure the kubelet evicts BestEffort first, then Burstable exceeding its requests, and Guaranteed last — so QoS is how you decide which workloads survive a squeeze. Say that a critical database Pod should be Guaranteed for exactly that reason. This links directly to the requests-and-limits question: requests drive scheduling, limits cap runtime usage, and together they determine the QoS class.
- The control-plane-node question is about a taint, not a rule: control-plane nodes carry a `node-role.kubernetes.io/control-plane:NoSchedule` taint, so a Pod needs a matching toleration to land there. Then say why the taint exists — an application competing with the API server and etcd for CPU, memory, and disk I/O turns a workload problem into a cluster-wide outage — and that on managed services such as EKS you cannot do it at all because the provider owns those nodes. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- "Is etcd SQL or NoSQL?" is **NoSQL** — specifically a distributed key-value store, not relational: no tables, no schema, no joins, no SQL. Then add the properties that actually matter, because that is where the answer earns marks: it is strongly consistent via the raft consensus protocol rather than eventually consistent, every write requires a quorum fsync (which is why etcd needs low-latency disks), and it exposes a watch API — which is precisely what Kubernetes controllers rely on to react to changes instead of polling.
- The EBS-in-EKS disadvantage question has a specific answer: an EBS volume is **zonal and single-attach**, supporting only `ReadWriteOnce`, so it binds the Pod to one availability zone and effectively to one node. The practical failure is a Pod being rescheduled to a node in a different zone and getting stuck `Pending` because the volume cannot follow it — which also means a StatefulSet replica cannot be moved across zones. Say the mitigations: `volumeBindingMode: WaitForFirstConsumer` so the volume is created where the Pod is scheduled, and EFS when you genuinely need `ReadWriteMany` across nodes. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- The `-p` question is a small precision test with a slightly annoying answer: `-p` is the short form of `--publish`, so it means **publish** — mapping a container port to a host port. Say that `-P` (capital) publishes _all_ exposed ports to random host ports, and that `EXPOSE` in a Dockerfile is documentation only and publishes nothing. That trio shows you know the mechanism rather than the flag.
- OOM should be answered as two different failures. In a container, exceeding the memory **limit** gets the process killed by the kernel's OOM killer, the container reports exit code 137, and `kubectl describe pod` shows `OOMKilled` — the fix is to right-size the limit from observed usage, or fix the leak. At node level, memory pressure triggers kubelet **eviction**, which is where QoS class decides who dies. The resolution path: read the exit code to confirm it was OOM, check actual working-set usage against the limit, raise the limit only if the usage is legitimate, and set requests so the scheduler stops overcommitting the node. Say that raising the limit without understanding the growth just delays the failure.
- Init versus sidecar containers is a lifecycle distinction: init containers run to completion, in order, **before** any application container starts — used to wait for a dependency, run a migration, or fetch config — and if one fails the Pod restarts per its `restartPolicy`. A sidecar runs **alongside** the application for its whole life, sharing the Pod's network and volumes — a log shipper, a proxy, a secret refresher. Add the modern detail: Kubernetes now supports native sidecars as init containers with `restartPolicy: Always`, which fixes the old problem of sidecars not being ready before the main container or not shutting down cleanly. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md).
- The Linux "OS or kernel" question is a definitional check: **Linux is a kernel**; a distribution such as Ubuntu or RHEL is the operating system, bundling the kernel with GNU userland tools, a libc, an init system, and a package manager. Saying that cleanly, then noting that this is why containers share the host _kernel_ while carrying their own userland, connects it to the Docker half of the round.
- `kill` versus `kill -9` needs the signal semantics: plain `kill` sends `SIGTERM` (15), which the process can catch to flush buffers and shut down cleanly; `kill -9` sends `SIGKILL`, which cannot be caught, blocked, or ignored, so the process dies immediately with no cleanup — risking corrupt state. Add the fact that completes the answer: a process stuck in uninterruptible sleep (state `D`, usually blocked on I/O) will not die from either, because it is not scheduled to handle signals. Linux has **64** signals (1-31 standard, 32-64 real-time); `kill -l` lists them. Say you always try `SIGTERM` first — reaching for `-9` reflexively is how you corrupt a database.
- "Check a process without `ps` or `top`" is asking whether you know where that information comes from: `/proc`. So read `/proc/<pid>/status`, `cmdline`, `limits`, and `fd/`, or list `/proc/[0-9]*` to enumerate processes. Other valid answers: `pgrep` and `pidof`, `systemctl status <unit>` for a managed service, `ls /proc | grep '^[0-9]'`, and `htop` or `pidstat` if those count. Naming `/proc` first is the answer they want, because it shows you understand that `ps` is just a formatter over it. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).
- Linux variable types has a specific expected answer: **shell (local)** variables visible only to the current shell, **environment** variables exported to child processes, and **shell/special** variables set by the shell itself (`$?`, `$$`, `$#`, `$@`, `PATH`, `HOME`). Say `export` is what promotes a local to an environment variable, and that this is why a variable set in a script is invisible to the parent shell unless sourced.
- Secrets Manager versus Parameter Store deserves the decision criteria rather than a feature list: Parameter Store is free for standard parameters, holds configuration and `SecureString` secrets, and has no built-in rotation; Secrets Manager charges per secret per month but adds native rotation with Lambda, cross-region replication, and tight integration with RDS credential management. So: configuration and cheap secrets in Parameter Store, anything that must rotate — especially database credentials — in Secrets Manager. Say that both encrypt with KMS and that the KMS key policy is a common cause of a puzzling `AccessDenied`. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- Multi-AZ versus read replicas is a purpose distinction, not a size one: a Multi-AZ standby is a **synchronous** copy you cannot read from, existing purely for automatic failover — so it buys availability and costs you nothing in RPO; a read replica is **asynchronous**, readable, can live in another region, and can be promoted — so it buys read throughput and cross-region disaster recovery, with replication lag as your RPO. Then answer the scaling question with that framing: vertical scaling means changing the instance class (an online operation with a brief failover, and irreversible in the sense that you must change it back deliberately); horizontal scaling means adding read replicas for reads, and for writes it means Aurora, sharding, or a caching layer — because you cannot horizontally scale a single writer. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- EC2 without a `.pem` key should name four routes, best first: **Session Manager** (no inbound port, no key, full audit log), EC2 Instance Connect, the serial console for a broken instance, and — if you must restore key access — attaching the root volume to another instance to append a public key, or adding one via `user_data` on next boot. Say Session Manager is the production answer and that key management is the problem it removes. See [troubleshooting SSH failures](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- ECR cleanup is a **lifecycle policy** on the repository: rules that expire untagged images after N days and keep only the most recent N images matching a tag prefix, evaluated by priority. Say you would combine that with tag immutability and scan-on-push, and that untagged images accumulate silently from every rebuild — which is why the untagged rule is the one that actually reclaims storage.
- Dockerfile security should be a checklist you can rattle off: a minimal or distroless base pinned by digest, multi-stage build so no compilers or credentials reach the runtime image, a non-root `USER`, a read-only root filesystem with `tmpfs` for scratch space, dropped capabilities, no secrets in `ARG` or `ENV` (use BuildKit `--mount=type=secret`), a `.dockerignore` excluding `.git` and `.env`, dependencies pinned, `COPY` rather than `ADD`, a `HEALTHCHECK`, and scanning plus signing in CI. Say that most reported vulnerabilities come from the base image, so choosing a smaller base is the single highest-leverage change. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md) and [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md).
- Context switching is `kubectl config use-context <name>`, with `get-contexts` to list and `--namespace` or `set-context --current --namespace=` to change the default namespace. Define a context properly: a named tuple of cluster, user, and namespace in `kubeconfig` — so switching context switches which cluster you are talking to _and_ as whom, which is exactly why a mis-set context is how people apply to the wrong cluster. Mention `kubectx` and `kubens`, and that a distinct prompt colour per environment is a cheap safeguard.
- The three cluster-operations questions — how many clusters, which version, have you upgraded — are calibration checks. Have exact numbers and a real upgrade story ready; vagueness here undercuts every technical answer that follows.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
