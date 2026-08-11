---
title: "How do you troubleshoot a GitOps pipeline that will not sync?"
id: 428
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - kubernetes
  - version-control
  - cicd
---

# How do you troubleshoot a GitOps pipeline that will not sync?

**Short answer:** Follow the controller's own reconciliation chain and stop at the first broken link: **can it reach and authenticate to Git** (bad deploy key, expired token, private repository, wrong branch or revision), **did the manifests render** (a Kustomize or Helm templating error - nothing is applied), **did the API server accept them** (RBAC on the controller's service account, admission webhook denial, immutable field, missing CRD), **is it healthy but reporting `OutOfSync`** (drift, a mutating webhook, or a field the controller keeps fighting over), or **is it stuck `Progressing`** because the workload never becomes healthy. ArgoCD's `app get` and Flux's `get all` plus `describe` name the failing stage in one command - read that before touching Git, because the most common causes are credentials and rendering, not the manifests themselves.

## Detail

### Step 1: read the controller's status

- **ArgoCD**: `argocd app get <app>` shows sync status, health, and the per-resource condition; `argocd app logs`/the `application-controller` logs give the underlying error; `argocd app diff` shows live versus desired.
- **Flux**: `flux get all -A` lists every `GitRepository`, `Kustomization`, and `HelmRelease` with a Ready condition and a message; `flux logs --level=error` and `kubectl describe kustomization` give the detail.

The status message is nearly always specific (`authentication required`, `error unmarshaling JSON`, `admission webhook denied the request`, `Deployment.apps "x" is invalid: field is immutable`). Diagnose from it rather than guessing.

### Step 2: the source layer

- **Authentication.** A rotated deploy key or expired token is the most common cause of a pipeline that stopped working with no commits changed. Check the credentials secret and that the key is still authorised on the repository. For HTTPS, a token with the wrong scope fails the same way.
- **Revision.** Is the controller watching the branch, tag, or semver range you think? A pinned `targetRevision` that no longer exists, or a branch that was renamed to `main`, produces a "revision not found" that is easy to miss.
- **Path.** A moved or renamed directory means the controller reconciles an empty set - and with `prune: true` that is worse than a failure, because an empty desired state can delete resources. This is the argument for pruning with care and for `--dry-run` checks in CI.
- **Network.** Egress from the cluster to the Git host, a proxy, or a self-signed CA the controller does not trust. Signature verification (Flux's `verify` or a signed-commit policy) will also reject unsigned commits by design.

### Step 3: the rendering layer

Nothing is applied when rendering fails, so this looks like "the controller is ignoring my commit":

- Kustomize errors - a missing file in `resources`, a patch that does not match any target, a strategic-merge patch with no name/kind.
- Helm errors - a missing values key, `nil` pointer in a template, or a chart version that no longer exists in the repository. See [how do you troubleshoot a failed Helm release](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md).
- Reproduce locally with the exact same inputs: `kustomize build ./overlays/prod` or `helm template`. If it fails on your laptop, the cluster is not the problem.

### Step 4: the apply layer

- **RBAC.** The controller's service account must be able to create every kind you ship, in every namespace you target. A new CRD or a new namespace commonly breaks this, and the error is a plain `forbidden`.
- **Admission webhooks.** A policy engine denying the resource (missing resource limits, disallowed registry) shows as `admission webhook ... denied the request` - the message names the policy. See [how do you enforce Kubernetes admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md).
- **CRD ordering.** Custom resources applied before their CRD exists fail with `no matches for kind`. Fix with sync waves (ArgoCD `argocd.argoproj.io/sync-wave`) or dependency ordering (Flux `dependsOn`), and install CRDs in their own earlier layer.
- **Immutable fields.** Changing a Deployment's selector or a Service's `clusterIP` cannot be applied - the controller will retry for ever. It needs a delete-and-recreate, which you should do deliberately and, for anything stateful, with a plan.
- **Server-side apply conflicts.** Another controller (an HPA, a mutating webhook, a legacy script) owns a field, so you get `conflict` or a permanent `OutOfSync`.

### Step 5: healthy but permanently `OutOfSync`

This is the most instructive case, and the answer is almost always **something else is mutating the resource**:

- An **HPA** setting `replicas` while `replicas` is also in Git. Remove it from Git, or use `ignoreDifferences` on that field.
- **Mutating webhooks** (sidecar injection, default annotations) adding fields the controller then wants to remove.
- **Defaulted fields** the API server fills in that your manifest omits.
- **Someone changed it by hand.** With `selfHeal` enabled the controller reverts them - which is correct - but it is worth seeing the pattern in the diff and having the conversation.

Configure `ignoreDifferences` narrowly for the legitimate cases, not broadly, or you lose the drift detection that is the entire point.

### Step 6: stuck `Progressing`

The manifests applied cleanly and the workload is not healthy - an image that does not exist, a failing probe, unschedulable Pods, a PVC pending. At that point it is ordinary Kubernetes debugging and the GitOps controller is only reporting it. See [how do you troubleshoot a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).

### Prevention

Validate in CI before merge (`kustomize build`, `helm template`, `kubeconform` against the cluster's API version, policy tests), which converts most of the above into pull-request failures. Use sync waves or `dependsOn` for ordering, keep prune deliberate and never point a live application at a path that may be empty, alert on `Ready != True` and on sync duration, and monitor credential expiry. And remember the operating rule that makes GitOps work at all: **fix the repository, not the cluster** - a manual `kubectl edit` will be reverted, and rollback is `git revert`. See [what is GitOps](./what-is-gitops.md) and [what is ArgoCD](./what-is-argocd.md).

## Example

```bash
# ArgoCD: what does the controller say, and what is the actual diff?
argocd app get checkout
# Sync Status:  OutOfSync
# Health:       Degraded
# CONDITION     ComparisonError: rpc error ... authentication required
argocd app diff checkout                      # live vs desired, field by field
kubectl -n argocd logs deploy/argocd-repo-server --tail=50 | grep -i 'error\|denied'

# Flux: one command names the failing stage
flux get all -A
# NAME                    READY  MESSAGE
# gitrepository/platform  False  failed to checkout: authentication required
# kustomization/apps      False  dependency 'flux-system/infra' is not ready
flux logs --level=error --since=30m
kubectl describe kustomization apps -n flux-system | tail -20

# Reproduce the rendering locally - if it fails here, the cluster is innocent
kustomize build ./clusters/prod/apps | kubeconform -strict -kubernetes-version 1.31.0 -
helm template checkout ./chart -f values-prod.yaml >/dev/null

# Permanently OutOfSync? Find who else is writing the field.
kubectl get deploy checkout -n prod -o yaml | yq '.metadata.managedFields[].manager'
# argocd-controller
# horizontal-pod-autoscaler      <- there it is: replicas is contested
```

```yaml
# ArgoCD: ordering, narrow drift exceptions, and a bounded retry
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: checkout
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "2" # CRDs and namespaces go in wave 0/1
spec:
  source:
    repoURL: https://github.com/acme/platform.git
    targetRevision: main # must exist - a stale pin fails silently to humans
    path: clusters/prod/apps/checkout
  destination: { server: https://kubernetes.default.svc, namespace: prod }
  syncPolicy:
    automated: { prune: true, selfHeal: true } # selfHeal reverts manual edits by design
    retry:
      limit: 5
      backoff: { duration: 30s, factor: 2, maxDuration: 10m }
  ignoreDifferences: # narrow: the HPA legitimately owns replicas
    - group: apps
      kind: Deployment
      jsonPointers: ["/spec/replicas"]
```

## Interview tips

- Answer as a chain - source, render, apply, health - and say you read the controller's status message first. Candidates who start by re-editing YAML have not used a GitOps controller in anger.
- Name credential expiry as the top cause of "it worked yesterday with no changes". Rotated deploy keys and expired tokens account for a large share of real incidents.
- The permanently-`OutOfSync` case is the best discriminator: explain that something else is mutating the resource, give the HPA-versus-Git `replicas` conflict as the canonical example, and mention `managedFields` as the way to find the other writer.
- Say that `prune` plus an empty or moved path is dangerous, because the desired state becomes "nothing". It is a genuinely scary failure mode and shows operational awareness.
- Mention CRD ordering with sync waves or `dependsOn`. It is the most common first-deployment failure for anything operator-based.
- Restate the operating rule - fix the repository, not the cluster; rollback is `git revert` - because it is the cultural half of the answer interviewers are checking for.
- Close on prevention in CI: `kustomize build`, `helm template`, `kubeconform`, and policy tests before merge, so rendering failures never reach the cluster.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
