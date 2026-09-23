---
title: "What are Kubernetes Ephemeral Containers and how are they used for zero-downtime debugging?"
id: 523
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - debugging
  - ephemeral-containers
  - distroless
quiz:
  stem: "Why are Ephemeral Containers essential when troubleshooting production workloads running in distroless containers?"
  options:
    - "Distroless images run in read-only RAM disks that cannot receive HTTP traffic"
    - "Distroless images lack shells and diagnostic binaries, preventing conventional `kubectl exec` access"
    - "Kubernetes requires an ephemeral container to capture pod stdout logs"
    - "Ephemeral containers are the only way to restart a failed Pod"
  answer: 2
  explanation: "Because distroless images contain no shell or debug binaries, `kubectl exec` fails. Ephemeral containers bring a full debugging toolchain into the pod's namespaces without restarting it."
---

# What are Kubernetes Ephemeral Containers and how are they used for zero-downtime debugging?

**Short answer:** An ephemeral container is a temporary container added to an **already running** Pod through the Pod's `ephemeralcontainers` subresource, without restarting the Pod or its existing containers. It joins the Pod's network namespace and, with `--target`, the process namespace of a specific container, so you can bring `sh`, `curl`, `tcpdump`, or `strace` to a distroless or scratch image that has none of them. It is GA since Kubernetes 1.25 and is what `kubectl debug` uses. The trade-offs: it cannot be removed once added (it stays in the Pod spec until the Pod is deleted), it has no resource guarantees, and it is a powerful capability that needs its own RBAC and Pod Security controls.

## Detail

**The problem.** Minimal images - distroless, `scratch`, Chainguard-style bases - ship only the application binary. That shrinks the attack surface and CVE count, but `kubectl exec -- sh` fails with `executable file not found`, and rebuilding the image with debug tools, or restarting the Pod, destroys the exact state you wanted to inspect.

**How it works.**

1. `kubectl debug` sends a PATCH to the Pod's `ephemeralcontainers` subresource with a new container spec. The Pod spec's normal `containers` list stays immutable; only this list can grow.
2. The kubelet starts the new container in the existing Pod sandbox, so it shares the Pod's **network namespace** (same IP, same `localhost`, same sockets and routes) and can mount the Pod's volumes.
3. With `--target=<container>`, the runtime places it in that container's **PID namespace**, so `ps` shows the application's processes, `/proc/<pid>/root` exposes the application's filesystem, and `strace` or `gdb` can attach (given the right capabilities). Without `--target`, it only sees its own processes unless the Pod sets `shareProcessNamespace: true`.

**Restrictions by design.**

- No `ports`, probes, `resources`, or `lifecycle` hooks, and it is never restarted. It does not change the Pod's QoS or scheduling.
- It cannot be removed or restarted once added; exiting the shell leaves a terminated entry in `status.ephemeralContainerStatuses`. Add a new one (with a new name) for another session.
- It runs under the Pod's security context and is subject to Pod Security Admission, so a `restricted` namespace will reject a debug container that asks for root or extra capabilities. `kubectl debug --profile` (`general`, `baseline`, `restricted`, `netadmin`, `sysadmin`) sets a matching security context, and `--custom` applies a partial container spec from a file.

**Security trade-off.** Anyone who can update `pods/ephemeralcontainers` can run arbitrary images inside any Pod in scope - effectively `pods/exec` with a toolbox. Grant it as narrowly as `exec`, audit its use, and restrict debug images with admission policy if needed.

**Related `kubectl debug` modes.**

- `--copy-to=<name>` creates a **copy** of the Pod (optionally with a changed image or command) - the right tool for a container that crashes on start, where there is nothing to attach to.
- `kubectl debug node/<name>` runs a Pod on the node with the host filesystem mounted at `/host`, for node-level investigation.

## Example

```bash
# Attach a toolbox to a running distroless Pod, sharing the app container's PID namespace
kubectl debug -it checkout-7d9f8c-x2k9p \
  --image=nicolaka/netshoot --target=app --profile=general -- bash

# Inside the ephemeral container
ps aux                           # the app's processes are visible via --target
ss -tlnp                         # same network namespace: the app's listening sockets
curl -s localhost:8080/healthz   # talk to the app over loopback
ls /proc/1/root/etc              # the app container's filesystem

# See what was added (it persists in the spec until the Pod is deleted)
kubectl get pod checkout-7d9f8c-x2k9p -o jsonpath='{.spec.ephemeralContainers[*].name}{"\n"}'

# Crash on start? Debug a copy with a shell as the entrypoint instead
kubectl debug checkout-7d9f8c-x2k9p -it --copy-to=checkout-debug \
  --container=app --image=busybox:1.37 -- sh
```

```yaml
# RBAC: debugging rights are separate from, and as sensitive as, exec
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: pod-debugger, namespace: shop }
rules:
  - apiGroups: [""]
    resources: ["pods/ephemeralcontainers"]
    verbs: ["update", "patch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list"]
  - apiGroups: [""]
    resources: ["pods/attach"] # for -it; --copy-to additionally needs "create" on pods
    verbs: ["create"]
```

## Interview tips

- Start with the problem: distroless images have no shell, and restarting the Pod destroys the evidence.
- Explain the mechanism: the `ephemeralcontainers` subresource, the shared network namespace, and `--target` for the process namespace.
- Know the restrictions - no ports, probes, or resources; never restarted; cannot be removed until the Pod is deleted.
- Raise the security angle: `pods/ephemeralcontainers` is as powerful as `pods/exec`, and Pod Security Admission applies, which is what `--profile` addresses.
- Distinguish the three `kubectl debug` modes: ephemeral container, `--copy-to` for crash-looping Pods, and `node/<name>` for hosts.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[What are CustomResourceDefinitions and operators in Kubernetes?]] (`#452`): [What are CustomResourceDefinitions and operators in Kubernetes?](../container-orchestration-advanced/what-are-customresourcedefinitions-and-operators-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
