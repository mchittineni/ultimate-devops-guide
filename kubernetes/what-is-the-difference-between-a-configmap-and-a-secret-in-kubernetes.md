---
title: "What is the difference between a ConfigMap and a Secret in Kubernetes?"
id: 442
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - devsecops
---

# What is the difference between a ConfigMap and a Secret in Kubernetes?

**Short answer:** Both are namespaced key-value objects that decouple configuration from the image, and both are consumed the same way - as environment variables or as mounted files. The difference is **intent and handling**, not strength: a `Secret` stores its values base64-encoded (encoding, not encryption), is kept out of some log and describe output, can be encrypted at rest in etcd if you configure `EncryptionConfiguration`, has typed variants (`kubernetes.io/tls`, `dockerconfigjson`, service-account tokens), and is what RBAC and admission policy treat as sensitive. The honest interview answer is that **a Secret is not secure by default** - base64 is trivially reversible, and anyone with `get secrets` in the namespace or read access to etcd can read it - which is why production setups pair Secrets with encryption at rest, tight RBAC, and an external secret manager.

## Detail

### What is actually different

|                             | ConfigMap                                                          | Secret                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| Stored as                   | Plain UTF-8 (`data`) or binary (`binaryData`)                      | Base64 in `data`, plain in `stringData` on write                                                                                       |
| Encrypted at rest           | No                                                                 | **Only** if `EncryptionConfiguration` is enabled on the API server (or a KMS provider)                                                 |
| Shown by `kubectl describe` | Values printed                                                     | Values redacted (byte counts only)                                                                                                     |
| Typed                       | No                                                                 | Yes - `Opaque`, `kubernetes.io/tls`, `kubernetes.io/dockerconfigjson`, `kubernetes.io/service-account-token`, `basic-auth`, `ssh-auth` |
| Kubelet handling            | Cached like any object                                             | Stored in tmpfs on the node when mounted, so it does not hit node disk                                                                 |
| Size limit                  | ~1 MiB (etcd value limit)                                          | ~1 MiB                                                                                                                                 |
| Right for                   | Feature flags, log level, `nginx.conf`, JVM options, endpoint URLs | Passwords, API keys, TLS private keys, registry credentials                                                                            |

Both are namespace-scoped, so a Pod cannot reference one in another namespace - a frequent "why can't my Pod see it?" cause.

### Environment variable or mounted file - and why the answer is usually file

|                   | Env var (`envFrom` / `valueFrom`)                                                           | Volume mount                                                                                                                        |
| ----------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Updates on change | **Never** - fixed at Pod start, needs a restart                                             | Yes - kubelet refreshes the file (roughly on its sync period, ~1 min; instant for `subPath`… **no**, `subPath` mounts never update) |
| Leak surface      | Visible in `/proc/<pid>/environ`, child processes, crash dumps, and many logging frameworks | Readable only at the mounted path                                                                                                   |
| Suits             | Small scalars, 12-factor apps                                                               | Certificates, config files, anything multi-line                                                                                     |

For secrets, prefer files. For config, either is fine, but if you want configuration reload without a restart you need the volume form **and** an application that watches the file.

### Making a config change actually take effect

This is the question behind the question. A ConfigMap edit does not restart anything. Three approaches:

1. **Roll on change** - annotate the Pod template with a hash of the config (`checksum/config: {{ sha256sum ... }}` in Helm, or Kustomize's `configMapGenerator` with a name suffix). The template changes, so the Deployment performs a normal rolling update. This is the standard and the one to name first.
2. **Immutable ConfigMaps/Secrets** (`immutable: true`) - blocks edits entirely, forces a new object name, and reduces API server watch load at scale. Good discipline for anything versioned.
3. **In-app reload** - watch the mounted file (or accept a SIGHUP). Only worth it for things like nginx or a log level you want to flip live.

### Making Secrets genuinely secret

- **Encryption at rest**: `EncryptionConfiguration` on the API server with `aescbc`/`secretbox` or, better, a **KMS provider** (AWS KMS, Azure Key Vault, GCP KMS) so the key is not on the control-plane host. Without this, etcd holds your secrets in plaintext - on managed clusters check whether the provider has enabled it (EKS supports KMS envelope encryption; GKE and AKS have equivalents).
- **RBAC**: `get`/`list` on secrets in a namespace is equivalent to reading every credential in it. Never grant it broadly; audit for wildcards. Also disable `automountServiceAccountToken` where the workload does not call the API.
- **External secret managers**: keep the source of truth in Vault, AWS Secrets Manager, or Azure Key Vault and project it in - via the **External Secrets Operator** (syncs into a Secret), the **Secrets Store CSI driver** (mounts directly, optionally without creating a Secret object), or a Vault agent sidecar. This is what gives you rotation, audit trails, and per-request policy.
- **Never commit a Secret manifest to Git.** With GitOps use SOPS or Sealed Secrets so the repository holds ciphertext only.
- Do not use a ConfigMap "temporarily" for a credential. It gets forgotten and it shows up in `kubectl describe`, in support bundles, and in log scrapes.

## Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata: { name: api-config-7f4c2b }   # name suffix = new object on change
immutable: true
data:
  LOG_LEVEL: "info"
  application.yaml: |
    server:
      port: 8080
    features:
      newCheckout: true
---
apiVersion: v1
kind: Secret
metadata: { name: api-secrets }
type: Opaque
stringData: # stringData: you write plaintext, the API server base64s it
  DB_PASSWORD: "changeme"
  api-key: "sk_live_placeholder"
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  template:
    metadata:
      annotations:
        checksum/config: "7f4c2b9e" # changes with the config -> triggers a rollout
    spec:
      automountServiceAccountToken: false
      containers:
        - name: api
          image: registry.example.com/api:1.9.0
          envFrom:
            - configMapRef: { name: api-config-7f4c2b } # scalars as env vars
          volumeMounts:
            - { name: cfg, mountPath: /etc/app, readOnly: true }
            - { name: sec, mountPath: /etc/secrets, readOnly: true } # secrets as files
      volumes:
        - name: cfg
          configMap:
            name: api-config-7f4c2b
            items: [{ key: application.yaml, path: application.yaml }]
        - name: sec
          secret: { secretName: api-secrets, defaultMode: 0400 }
```

```bash
# Prove that "Secret" is encoding, not encryption
kubectl create secret generic demo --from-literal=pw='changeme'
kubectl get secret demo -o jsonpath='{.data.pw}' | base64 -d   # -> changeme

# Who can read every credential in this namespace?
kubectl auth can-i get secrets --namespace prod --as system:serviceaccount:prod:ci
kubectl get rolebindings,clusterrolebindings -A -o json \
  | jq -r '.items[] | select(.roleRef.name|test("admin|edit")) | .metadata.name'

# Is encryption at rest actually on? (self-managed control plane)
grep -n "resources:" -A6 /etc/kubernetes/enc/enc.yaml
```

```yaml
# The production pattern: source of truth outside the cluster
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: api-secrets }
spec:
  refreshInterval: 1h # rotation happens upstream; this pulls it through
  secretStoreRef: { name: aws-secrets-manager, kind: ClusterSecretStore }
  target: { name: api-secrets, creationPolicy: Owner }
  data:
    - secretKey: DB_PASSWORD
      remoteRef: { key: prod/api/db, property: password }
```

## Interview tips

- State the real difference in one line - same mechanism, different intent and handling - then immediately say **base64 is encoding, not encryption**. Volunteering that is the single highest-signal thing in this answer.
- Follow with what makes a Secret actually safe: encryption at rest with a KMS provider, narrow RBAC on `get secrets`, and an external secret manager for rotation and audit.
- Know the update semantics cold: env vars are frozen at Pod start, mounted files refresh (except `subPath` mounts, which never do). This is the answer to "I rotated the secret in Key Vault, why is the Pod still using the old one?"
- Name the rollout trigger - a config checksum annotation, or Kustomize/Helm name suffixing - because "how do you make the change take effect?" always follows.
- Mention `immutable: true` as both a safety and a scale control; it reduces API server watch traffic in large clusters.
- If GitOps comes up, say Secrets never go into Git in plaintext - SOPS, Sealed Secrets, or the External Secrets Operator. See [how do you manage Kubernetes secrets in a GitOps workflow](../devsecops/how-do-you-manage-kubernetes-secrets-in-a-gitops-workflow.md), [how do you manage secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md), [how do you rotate secrets without downtime](../devsecops/how-do-you-rotate-secrets-without-downtime.md), and [how does RBAC work in Kubernetes](./how-does-rbac-work-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you harden a container image and a Dockerfile?]] (`#441`): [How do you harden a container image and a Dockerfile?](../docker/how-do-you-harden-a-container-image-and-a-dockerfile.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
