---
title: "How do you manage Kubernetes secrets in a GitOps workflow?"
id: 504
category: "DevSecOps"
difficulty: "Advanced"
tags:
  - devops
  - devsecops
  - interview-questions
  - kubernetes
  - devops-tools-and-automation
---

# How do you manage Kubernetes secrets in a GitOps workflow?

**Short answer:** GitOps says the desired state lives in Git, but a plaintext `Secret` manifest in Git is a credential leak - so you store either **ciphertext** or a **reference**. Three patterns, and the choice is the answer. **Encrypted in Git**: SOPS (with age or a cloud KMS key) or Sealed Secrets, so the repository holds ciphertext that only the cluster can decrypt - Git stays the single source of truth, at the cost of manual rotation and unreadable diffs. **Referenced from a secret manager** (the usual production answer): the **External Secrets Operator** syncs values from Vault, AWS Secrets Manager, or Azure Key Vault into Kubernetes `Secret`s, or the **Secrets Store CSI driver** mounts them straight into Pods - Git holds only a pointer, rotation happens upstream, and you get an audit trail. **Eliminate the secret entirely**: workload identity federation (IRSA, EKS Pod Identity, Entra Workload ID, GCP Workload Identity) so the Pod gets a short-lived token instead of a stored credential, and Vault dynamic secrets so a database password exists for an hour. The framing that lands: the best answer to "how do you store this secret in Git?" is often **"we do not have one to store"**.

## Detail

### The three patterns compared

|                                      | Encrypted in Git (SOPS / Sealed Secrets)      | Referenced (ESO / CSI driver)         | Eliminated (workload identity, dynamic secrets) |
| ------------------------------------ | --------------------------------------------- | ------------------------------------- | ----------------------------------------------- |
| What Git holds                       | Ciphertext                                    | A pointer (`remoteRef`)               | Nothing secret at all                           |
| Single source of truth               | **Yes** - fully declarative                   | Split: Git for shape, vault for value | Git for identity only                           |
| Rotation                             | Manual: re-encrypt, commit, sync              | **Upstream, no commit**               | Automatic by design                             |
| Audit "who read this?"               | No                                            | **Yes**, in the secret manager        | Yes                                             |
| Works air-gapped / disaster recovery | Yes - clone the repo and go                   | Needs the vault to be up              | Needs the identity provider                     |
| Extra infrastructure                 | Almost none                                   | An operator + a vault                 | Cluster/identity configuration                  |
| Diff readability in review           | Poor (ciphertext blobs)                       | Good                                  | Good                                            |
| Best for                             | Small teams, bootstrap secrets, edge clusters | Most production estates               | Cloud API access, databases                     |

Most mature setups use **all three**: workload identity for cloud API access (no secret exists), ESO for third-party credentials that must be a `Secret`, and SOPS for the handful of bootstrap secrets needed before the operator itself is running - the chicken-and-egg problem of "ESO needs credentials to reach Vault". Being able to describe that layering, and naming the bootstrap problem, is what a senior answer sounds like.

### SOPS versus Sealed Secrets

**SOPS** encrypts the _values_ of a YAML file, leaving keys and structure readable, using age or a KMS key (AWS KMS, GCP KMS, Azure Key Vault, or PGP). Flux has native decryption support; Argo CD uses a plugin or `ksops`. Because keys stay in plaintext, a reviewer can see _which_ secrets changed even without decrypting - a genuine advantage. Multiple recipients mean per-environment keys: developers hold the dev key, only the cluster and the release pipeline hold the production key.

**Sealed Secrets** (Bitnami) works differently: a controller in the cluster generates a keypair, you encrypt with `kubeseal` using the public key, and the resulting `SealedSecret` custom resource can only be decrypted by that controller. It is simple and needs no external KMS, but the private key is cluster-scoped state that you **must back up** - lose it and every sealed secret in the repository is unrecoverable. It also ties ciphertext to one cluster by default (scoped by namespace and name), which is a security feature and a multi-cluster inconvenience.

Both share the same weaknesses: **rotation means re-encrypt and commit**, ciphertext diffs are unreadable, and nothing gives you an access audit trail.

### External Secrets Operator, the common production answer

ESO introduces a `SecretStore`/`ClusterSecretStore` (where the values live and how to authenticate) and an `ExternalSecret` (which keys to pull and what `Secret` to create). Git holds only the pointer. Points worth making:

- **Authenticate the operator with workload identity**, not a static token - IRSA on EKS, a managed identity on AKS, Workload Identity on GKE, or Vault's Kubernetes auth method exchanging the service-account token. If ESO itself holds a long-lived credential, you have moved the problem rather than solved it.
- **`refreshInterval`** pulls rotated values automatically. But remember the Kubernetes semantics: an updated `Secret` does **not** restart anything, and env vars are fixed at container start. Pair it with Reloader/Stakater or a rollout trigger, or mount as a file and have the application re-read it.
- **`PushSecret`** covers the reverse direction when something generates a credential in-cluster.
- **Templating** lets you assemble a connection string or a `dockerconfigjson` from several vault keys.

The **Secrets Store CSI driver** is the alternative: it mounts secrets directly into the Pod's filesystem with no `Secret` object at all (unless you opt into `secretObjects` syncing), which means nothing sensitive is in etcd. That is the stronger posture; the trade-off is that anything needing a real `Secret` - image pull secrets, webhook TLS, `envFrom` - still needs the sync.

### Making the underlying Secret worth trusting

Whichever pattern you choose, a Kubernetes `Secret` is **base64, not encryption**, so:

- **Encryption at rest** on etcd with a **KMS provider**, so the key is not on the control-plane host. On managed clusters, verify the provider has it enabled (EKS supports KMS envelope encryption; AKS and GKE have equivalents).
- **RBAC**: `get`/`list` on secrets in a namespace is equivalent to reading every credential in it. Audit for wildcards, and disable `automountServiceAccountToken` where the workload does not call the API.
- **Mount as files, not env vars** - env vars leak into crash dumps, child processes, and log lines, and they never refresh.
- **Admission policy** (Kyverno/Gatekeeper) rejecting any `Secret` with a literal value in a GitOps-managed path, which is how you enforce the rule rather than document it.

### The GitOps-specific failure modes

- **Drift and self-heal fighting you**: Argo CD sees the ESO-created `Secret` as an object it does not manage, or as out of sync. Mark it with `argocd.argoproj.io/compare-options: IgnoreExtraneous` or exclude the resource, otherwise the sync loop deletes or recreates it.
- **Ordering**: the operator, its `SecretStore`, and its identity must exist before any workload that needs a secret. Use sync waves (Argo CD) or `dependsOn` (Flux), or the first deploy of a new cluster fails confusingly.
- **Bootstrap**: the credential ESO uses to reach the vault cannot itself come from ESO. Solve it with workload identity (no credential at all) or one SOPS-encrypted bootstrap secret.
- **Disaster recovery**: "rebuild the cluster from Git" only works if the secret source is reachable. Document and test the recovery path, including restoring the Sealed Secrets private key if you use it.
- **A developer commits a plaintext secret anyway**: pre-commit hooks (`gitleaks`, `git-secrets`), push protection on the platform, and a CI check that fails on a `kind: Secret` with `data`/`stringData` outside an allowlist. And when it happens, treat the credential as compromised - **rotate first**, then clean history; deleting the line does not remove it from history, forks, or clones.

### Dynamic secrets, the strongest version

Vault (and cloud equivalents) can **generate** a database credential on request with a short lease and revoke it on expiry. The application asks for a credential, gets one valid for an hour, and there is nothing long-lived to store, leak, or rotate - rotation becomes the normal operating mode rather than an event. Combine with the Vault Agent Injector or the CSI driver and Git holds only the role name. If an interviewer asks how you would design this from scratch, this is the answer to build towards.

## Example

```yaml
# Pattern 2 (usual production): Git holds a POINTER, not a value.
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata: { name: aws-secrets }
spec:
  provider:
    aws:
      service: SecretsManager
      region: eu-west-1
      auth:
        jwt: # IRSA: the operator has no static credential
          serviceAccountRef: { name: external-secrets, namespace: external-secrets }
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: payments-secrets
  namespace: prod
  annotations:
    argocd.argoproj.io/sync-wave: "-1" # created before the workload that needs it
spec:
  refreshInterval: 1h # rotation happens upstream; no commit, no PR
  secretStoreRef: { name: aws-secrets, kind: ClusterSecretStore }
  target:
    name: payments-secrets
    creationPolicy: Owner
    template: # assemble a connection string from several vault keys
      data:
        DATABASE_URL: "postgresql://{{ .user }}:{{ .password }}@orders.prod:5432/orders"
  data:
    - { secretKey: user, remoteRef: { key: prod/payments/db, property: username } }
    - { secretKey: password, remoteRef: { key: prod/payments/db, property: password } }
```

```yaml
# Argo CD: stop the sync loop fighting an operator-managed Secret
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: payments }
spec:
  syncPolicy:
    automated: { prune: true, selfHeal: true }
  ignoreDifferences:
    - group: ""
      kind: Secret
      name: payments-secrets
      jsonPointers: ["/data"] # ESO owns the values; Argo must not revert them
```

```bash
# Pattern 1: SOPS with a KMS key - ciphertext in Git, keys still readable in review
cat > secret.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata: { name: bootstrap, namespace: external-secrets }
stringData:
  vault-role-id: "changeme"
EOF
sops --encrypt --kms arn:aws:kms:eu-west-1:111122223333:key/abc-123 \
  --encrypted-regex '^(data|stringData)$' secret.yaml > secret.enc.yaml
git add secret.enc.yaml   # keys visible, values encrypted -> reviewable diffs

# Flux decrypts natively
flux create kustomization apps --source=GitRepository/infra --path ./apps \
  --decryption-provider=sops --decryption-secret=sops-age

# Sealed Secrets: encrypt with the controller's public key
kubectl create secret generic api-key -n prod --dry-run=client \
  --from-literal=key='changeme' -o yaml \
  | kubeseal --controller-namespace kube-system -o yaml > sealed-api-key.yaml
# BACK UP THE PRIVATE KEY, or every sealed secret becomes unrecoverable:
kubectl get secret -n kube-system -l sealedsecrets.bitnami.com/sealed-secrets-key \
  -o yaml > sealed-secrets-key-BACKUP.yaml
```

```bash
# Guardrails: make the rule enforceable, not aspirational
gitleaks detect --no-banner --redact                    # pre-commit and in CI
grep -rlE '^kind: Secret' --include='*.yaml' apps/ \
  | xargs -r grep -lE '^\s*(data|stringData):' \
  && { echo "plaintext Secret manifest committed"; exit 1; }

# Is etcd encryption actually on, and who can read secrets?
kubectl auth can-i get secrets -n prod --as system:serviceaccount:prod:default
kubectl get rolebindings,clusterrolebindings -A -o json \
  | jq -r '.items[] | select(.roleRef.name|test("admin|edit|cluster-admin")) | .metadata.name'

# Rotation reaches the Pod only if something restarts it or it re-reads the file
kubectl rollout restart deploy/payments -n prod
# or run Reloader and annotate: reloader.stakater.com/auto: "true"
```

## Interview tips

- State the tension first - GitOps wants everything in Git, secrets must not be in Git - then name the three resolutions: encrypt it, reference it, or eliminate it. That structure is the answer.
- Say the eliminate option is the best one where it applies: workload identity federation and Vault dynamic secrets mean there is no long-lived credential to store at all. Leading with that rather than with a tool is the senior move.
- For SOPS versus Sealed Secrets, give the differentiators: SOPS leaves keys readable so diffs are reviewable and uses an external KMS; Sealed Secrets needs no KMS but its private key is cluster state you **must back up**, and losing it makes every sealed secret unrecoverable.
- For ESO, insist the operator itself authenticates with workload identity - if ESO holds a static token you have relocated the problem, not solved it.
- Volunteer the Kubernetes update semantics: a synced `Secret` does not restart anything, and env vars are fixed at container start - so pair rotation with Reloader or a rollout, or mount files and re-read them. This is the detail that separates people who have run it from people who have configured it once.
- Mention that a `Secret` is base64, not encryption, and that the surrounding controls are what make it acceptable: KMS encryption at rest on etcd, tight RBAC on `get secrets`, and files over env vars.
- Bring up the GitOps-specific failure modes unprompted: Argo CD self-heal fighting an operator-managed Secret (`ignoreDifferences`), sync ordering so the operator exists first, and the **bootstrap** chicken-and-egg for the operator's own credential.
- Close with enforcement rather than intention: `gitleaks` in pre-commit and CI, a check that fails on a committed `kind: Secret` with values, and the rule that a leaked credential is rotated **first** and cleaned from history second. See [how do you manage secrets in CI/CD pipelines](./how-do-you-manage-secrets-in-ci-cd-pipelines.md), [rotating secrets without downtime](./how-do-you-rotate-secrets-without-downtime.md), [ConfigMaps and Secrets in Kubernetes](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md), [what is GitOps](../devops-tools-and-automation/what-is-gitops.md), and [troubleshooting a GitOps pipeline that will not sync](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
