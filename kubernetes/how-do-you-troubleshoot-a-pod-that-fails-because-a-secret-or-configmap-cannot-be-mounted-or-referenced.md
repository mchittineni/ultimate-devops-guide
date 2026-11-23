---
title: "How do you troubleshoot a Pod that fails because a Secret or ConfigMap cannot be mounted or referenced?"
id: 788
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - secrets
  - configmap
  - troubleshooting
quiz:
  stem: "A Pod is stuck in `CreateContainerConfigError` and its events say `secret \"db-creds\" not found`. Where is the Secret most likely referenced?"
  options:
    - "In a `secretKeyRef` or `secretRef` used to build environment variables"
    - "In an `imagePullSecrets` entry"
    - "In a `secret` volume mounted into the container"
    - "In the ServiceAccount's token projection"
  answer: 1
  explanation: "Environment variables are resolved when the kubelet builds the container config, so a missing Secret or key there gives CreateContainerConfigError. A missing Secret in a volume leaves the Pod in ContainerCreating with a FailedMount event instead."
---

# How do you troubleshoot a Pod that fails because a Secret or ConfigMap cannot be mounted or referenced?

**Short answer:** Start with `kubectl describe pod` and read the **status and events**, because the way the Pod fails tells you how the object is referenced. A missing Secret or ConfigMap used as a **volume** leaves the Pod in `ContainerCreating` with a `FailedMount` event; one used for **environment variables** gives `CreateContainerConfigError`. From there the cause is almost always one of a short list: the object does not exist yet, it is in a **different namespace**, the **name or key** is misspelled, an external secret controller has not synced it, or the mount works but the application cannot **read** the file. The kubelet keeps retrying, so once the object is fixed the Pod usually recovers without being recreated.

## Detail

**Read the symptom first.** The two consumption paths fail at different stages:

| How it is referenced                               | Pod status                   | Event message                                                                                     |
| -------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------- |
| `volumes[].secret` / `volumes[].configMap`         | `ContainerCreating`          | `FailedMount ... MountVolume.SetUp failed for volume "creds" : secret "db-creds" not found`       |
| `env[].valueFrom.secretKeyRef` / `configMapKeyRef` | `CreateContainerConfigError` | `Error: secret "db-creds" not found` or `couldn't find key password in Secret prod/db-creds`      |
| `envFrom[].secretRef` / `configMapRef`             | `CreateContainerConfigError` | `Error: secret "db-creds" not found`                                                              |
| Secrets Store CSI driver volume                    | `ContainerCreating`          | `FailedMount ... rpc error` with the provider's message (often an IAM or Key Vault access denial) |

**The usual causes, in the order to check them.**

- **It does not exist (yet).** Run `kubectl get secret <name> -n <ns>`. A Secret defined in the same manifest or Helm chart as the Deployment is fine because the kubelet retries, but a Secret created by a separate pipeline step, a later Argo CD sync wave, or an operator may simply not be there yet.
- **Wrong namespace.** Secrets and ConfigMaps are namespaced and a Pod can only reference objects in its own namespace. There is no cross-namespace reference syntax; copy the object or use a controller that replicates it.
- **Wrong name or key.** The object exists but the `key` in `secretKeyRef` or in a volume's `items` list does not. Compare against `kubectl get secret <name> -o jsonpath='{.data}'`, which lists the keys without decoding values.
- **External secret not synced.** With the External Secrets Operator, the Kubernetes Secret only appears after the `ExternalSecret` reconciles. `kubectl get externalsecret` shows a `SecretSyncedError` status when the store credentials, IAM role, or remote key path is wrong, so the real fix is upstream.
- **CSI driver cannot fetch.** With the Secrets Store CSI driver there is no Secret object to check; the mount itself calls the cloud provider, so the workload identity (EKS Pod Identity, IRSA, Azure Workload Identity) needs read access to that secret.
- **Mounted but unreadable.** The Pod runs, but the app logs "permission denied". Secret volumes default to mode `0644`; a restrictive `defaultMode` such as `0400` combined with `runAsUser` that differs from the file owner breaks reads. Set `fsGroup` or adjust the mode.
- **Mounted over something important.** Mounting a ConfigMap at `/etc/nginx` hides every other file the image shipped in that directory. Use `subPath` for a single file, accepting that `subPath` mounts never receive updates.

**Optional references.** Setting `optional: true` on a reference lets the Pod start when the object or key is missing. It is right for genuinely optional config, and wrong for a database password, because the failure then moves into the application.

**Size and immutability.** Both object types are limited to about 1 MiB, and an object marked `immutable: true` cannot be edited, so "I updated it and nothing changed" with an immutable object means a new object name is needed.

## Example

```bash
# 1. What state is the Pod in, and what do the events say?
kubectl get pod api-7d9f -n prod
kubectl describe pod api-7d9f -n prod | sed -n '/Events:/,$p'

# 2. Does the object exist in the Pod's namespace, and which keys does it have?
kubectl get secret db-creds -n prod -o jsonpath='{.data}' | jq 'keys'
kubectl get configmap api-config -n prod -o yaml

# 3. What exactly does the Pod reference?
kubectl get pod api-7d9f -n prod -o yaml | grep -nE -A3 'secretKeyRef|secretRef|configMapRef|secretName|configMap:'

# 4. If an operator owns the Secret, check its sync status
kubectl get externalsecret -n prod
kubectl describe externalsecret db-creds -n prod
```

```yaml
# A reference that will only start once the key exists
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-creds
        key: password # must match a key in .data exactly
volumes:
  - name: tls
    secret:
      secretName: api-tls
      defaultMode: 0440
```

## Interview tips

- The common incomplete answer is "run `kubectl describe pod` and check the Secret exists." Go further: say what the status tells you (`ContainerCreating` with `FailedMount` versus `CreateContainerConfigError`) and list namespace, key name, and controller sync as the next checks.
- Mention that the kubelet retries, so fixing the object normally fixes the Pod. Deleting the Pod forces an immediate retry if you do not want to wait.
- Expect the follow-up "the Secret exists and the Pod is running, but the app still can't read it" and answer with file permissions, `fsGroup`, and mounts that shadow a directory.
- Know that a Pod cannot reference a Secret in another namespace, and that ordering problems are about separate pipelines or sync waves, not the order of documents inside one manifest.
- If secrets come from Vault, AWS Secrets Manager, or Key Vault, say the failure often sits in the workload identity's permissions rather than in Kubernetes.

**Telling it as a STAR story** (an adaptable example)

- **Situation:** After a release, new Pods for a payments API sat in `CreateContainerConfigError` while the old ReplicaSet kept serving traffic.
- **Task:** Find out why the new Pods could not start and fix it without rolling back the release.
- **Action:** The events showed `couldn't find key db_password in Secret payments/db-creds`. Listing the Secret's keys showed `DB_PASSWORD`: the chart had renamed the key, but the `ExternalSecret` still mapped the old name. I corrected the `secretKey` in the `ExternalSecret`, confirmed it reported `SecretSynced`, and the kubelet started the Pods on its next retry. I then added a CI check that renders the chart and compares every `secretKeyRef` against the keys declared in the `ExternalSecret`.
- **Result:** The rollout finished within minutes of the fix with no downtime, and the same mismatch has not reached a cluster since.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container image that works locally fail on Kubernetes or ECS?]] (`#793`): [Why does a container image that works locally fail on Kubernetes or ECS?](../docker/why-does-a-container-image-that-works-locally-fail-on-kubernetes-or-ecs.md)
- [[What are Kubernetes Admission Webhook failure policies and how do you prevent self-locking outage loops?]] (`#628`): [What are Kubernetes Admission Webhook failure policies and how do you prevent self-locking outage loops?](../container-orchestration-advanced/what-are-kubernetes-admission-webhook-failure-policies-and-how-do-you-prevent-self-locking-outage-loops.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
