---
title: "How do you troubleshoot a Pod stuck in ImagePullBackOff?"
id: 751
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - docker
quiz:
  stem: "A Pod shows `ImagePullBackOff` and its events contain `pull access denied ... repository does not exist or may require authorization`. What is the most likely cause?"
  options:
    - "The node has run out of memory"
    - "The image name or tag is wrong, or the kubelet has no valid credentials for a private registry"
    - "The readiness probe is failing"
    - "The container's entrypoint is not executable"
  answer: 2
  explanation: "Registries return the same 'not found or unauthorized' response for a missing repository and for missing credentials, so check the exact image reference first, then the imagePullSecrets or node IAM role."
---

# How do you troubleshoot a Pod stuck in ImagePullBackOff?

**Short answer:** `ImagePullBackOff` means the kubelet tried to pull the image, failed (`ErrImagePull`), and is now waiting before it tries again, with the delay doubling up to five minutes. The cause is always in the Pod's events, and it is nearly always one of five things: **a wrong image name or tag**, **missing or wrong registry credentials**, **the node cannot reach the registry** (DNS, proxy, firewall, private endpoint), **registry rate limiting** (Docker Hub's anonymous limits are the classic case), or **no image for the node's CPU architecture**. Read the event message, then reproduce the pull from the node with `crictl pull` to separate a Kubernetes configuration problem from a network or registry problem.

## Detail

### What the states mean

- **`ErrImagePull`** - the most recent pull attempt failed.
- **`ImagePullBackOff`** - the kubelet is waiting before the next attempt (back-off doubles to a 300 s cap). Fixing the cause does not take effect until the next retry; deleting the Pod forces an immediate attempt.
- **`ErrImageNeverPull`** - `imagePullPolicy: Never` and the image is not already on the node.
- **`InvalidImageName`** - the reference cannot be parsed (uppercase letters, a stray space, a bad digest).

The Pod stays `Pending` the whole time, because no container has started.

### Map the event message to the cause

| Event message contains                                                | Usual cause                                                       | Fix                                                                                    |
| --------------------------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `manifest unknown`, `not found`                                       | Tag or digest does not exist; image never pushed by CI            | Check the registry; deploy by digest from the pipeline that pushed it                  |
| `pull access denied`, `401 Unauthorized`, `may require authorization` | Private repository and no credentials, or the name is wrong       | Add `imagePullSecrets`, fix the node IAM role, or correct the name                     |
| `403 Forbidden`                                                       | Credentials valid but not allowed on that repository              | Grant pull on the repository (ECR repository policy, Artifact Registry reader role)    |
| `toomanyrequests`                                                     | Registry rate limit (Docker Hub anonymous or free-tier pulls)     | Authenticate, use a pull-through cache or mirror, or copy the image to your registry   |
| `dial tcp ... i/o timeout`, `no such host`, `x509: certificate`       | Network path, DNS, proxy, or a private CA the node does not trust | Fix egress/VPC endpoints/proxy; install the CA in the runtime's trust store            |
| `no matching manifest for linux/arm64`                                | Single-architecture image on a different-architecture node        | Build multi-arch (`docker buildx --platform linux/amd64,linux/arm64`) or pin node arch |

Registries deliberately return the same "not found or unauthorized" answer for a repository that does not exist and for one you cannot see, so always check the exact reference before debugging credentials.

### Credentials, in the order the kubelet uses them

1. **Node-level credentials** - on EKS the node IAM role pulls from ECR through the kubelet's credential provider plugin; GKE and AKS do the same for their registries with the node's identity. A cross-account ECR pull needs a repository policy, not just a node role.
2. **`imagePullSecrets`** on the Pod, or attached to its ServiceAccount so every Pod using it inherits them. The Secret must be type `kubernetes.io/dockerconfigjson`, in the **same namespace** as the Pod, and its registry hostname must match the image's exactly (`ghcr.io` versus `https://ghcr.io/v1/` mismatches are common).
3. Short-lived tokens expire: an ECR token embedded in a static Secret stops working after 12 hours. Use the credential provider, or a controller that refreshes the Secret.

### The cases that look like something else

- **`:latest` and `imagePullPolicy`.** A `:latest` tag (or no tag) defaults to `Always`, so every Pod start depends on the registry being up. Pinned tags default to `IfNotPresent`. Deploying by digest avoids both the ambiguity and the "which `latest`?" question.
- **Huge images** can hit the kubelet's pull timeout or fill `imagefs`, causing `DiskPressure`. Smaller images and image pre-pulling or lazy-loading snapshotters (SOCI, stargz) help.
- **Serial pulls.** By default the kubelet pulls one image at a time per node; a single slow pull delays unrelated Pods. `serializeImagePulls: false` with `maxParallelImagePulls` changes that.
- **Private Pods and pre-pulled images.** A kubelet feature introduced as alpha in Kubernetes 1.33 lets it re-check that a Pod is authorised to use an image already on the node (`KubeletEnsureSecretPulledImages`), so a Pod without credentials no longer silently reuses an image another Pod pulled. Expect previously "working" Pods to start failing when this is turned on.

## Example

```bash
# 1. The event message names the cause
kubectl describe pod checkout-7d9f8c-x2k9p -n prod | sed -n '/Events/,$p'
#  Warning  Failed   kubelet  Failed to pull image "ghcr.io/acme/checkout:1.9.0":
#           ... 401 Unauthorized
#  Normal   BackOff  kubelet  Back-off pulling image "ghcr.io/acme/checkout:1.9.0"

# 2. What exactly is the Pod asking for, and with which credentials?
kubectl get pod checkout-7d9f8c-x2k9p -n prod \
  -o jsonpath='{.spec.containers[*].image}{"\n"}{.spec.imagePullSecrets}{"\n"}{.spec.serviceAccountName}{"\n"}'
kubectl get secret ghcr-pull -n prod -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d | jq '.auths | keys'

# 3. Reproduce from the node: separates Kubernetes config from network/registry problems
kubectl debug node/ip-10-0-3-14 -it --profile=sysadmin --image=busybox:1.37 -- chroot /host \
  crictl pull ghcr.io/acme/checkout:1.9.0

# 4. Create a pull secret and attach it to the ServiceAccount so every Pod inherits it
kubectl create secret docker-registry ghcr-pull -n prod \
  --docker-server=ghcr.io --docker-username=ci-bot --docker-password="$GHCR_TOKEN"
kubectl patch serviceaccount default -n prod -p '{"imagePullSecrets":[{"name":"ghcr-pull"}]}'
kubectl delete pod checkout-7d9f8c-x2k9p -n prod   # skip the remaining back-off
```

```yaml
# Explicit, pinned, and credentialed
apiVersion: v1
kind: Pod
metadata: { name: checkout, namespace: prod }
spec:
  imagePullSecrets: [{ name: ghcr-pull }] # same namespace as the Pod
  containers:
    - name: api
      image: ghcr.io/acme/checkout@sha256:9f2c8b1d... # digest: exact and immutable
      imagePullPolicy: IfNotPresent
```

## Interview tips

- Define the state precisely: `ErrImagePull` is a failed attempt, `ImagePullBackOff` is the kubelet waiting before retrying with exponential back-off. The Pod is `Pending` because no container has started.
- Say "read the event message first" and map it: not found means wrong reference, 401/403 means credentials, `toomanyrequests` means rate limiting, timeouts mean the network path, `no matching manifest` means architecture.
- Know where credentials come from - node identity (ECR, Artifact Registry, ACR), `imagePullSecrets` in the same namespace, or a ServiceAccount carrying them - and that static ECR tokens expire after 12 hours.
- Reproduce the pull on the node with `crictl pull`. It is the move that separates a manifest problem from a network one.
- Mention Docker Hub rate limits and pull-through caches; it is a very common real-world cause in clusters that pull public images anonymously.
- Recommend deploying by digest and avoiding `:latest`, which silently makes every Pod start depend on the registry. See [how do you troubleshoot a Pod stuck in Pending or CrashLoopBackOff](./how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md) and [how do you harden a container image](../docker/how-do-you-harden-a-container-image-and-a-dockerfile.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What is Docker?]] (`#6`): [What is Docker?](../docker/what-is-docker.md)
- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
