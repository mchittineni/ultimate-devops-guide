---
title: "What is GitOps and how does it fundamentally change release management?"
id: 508
category: "Core DevOps Concepts"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - core-devops-concepts
  - gitops
  - argocd
  - kubernetes
  - declarative
quiz:
  stem: "What is the primary security benefit of pull-based GitOps compared to push-based CI/CD?"
  options:
    - "Deployments complete faster because containers start simultaneously"
    - "The CI system does not need persistent credentials or firewall access into the target cluster"
    - "Git repositories automatically encrypt all application secrets on push"
    - "Pull-based deployment eliminates the need for Kubernetes RBAC"
  answer: 2
  explanation: "In pull-based GitOps, an agent running inside the cluster pulls manifests from Git, meaning no external CI system needs cluster admin credentials or open inbound ports."
---

# What is GitOps and how does it fundamentally change release management?

**Short answer:** GitOps is an operational framework where Git is the single source of truth for declared infrastructure and application state, coupled with automated software agents in the target environment that pull changes and continuously reconcile actual state with desired state.

## Detail

Unlike traditional push-based CI/CD where pipelines possess cluster-admin credentials and run imperative deploy scripts, GitOps reverses the control flow into a **pull-based reconciliation model**.

### Push vs Pull Architecture

| Dimension       | Push Model (Classic CI/CD)                    | Pull Model (GitOps)                                                                         |
| --------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Credentials     | Cluster credentials stored in CI runner       | Agent inside the cluster needs only read access to Git; no cluster credentials leave it     |
| Drift Detection | Fire-and-forget; manual drift goes undetected | Continuous reconciliation loop corrects drift automatically                                 |
| Rollbacks       | Triggering a new pipeline build/deployment    | `git revert` triggers rollback on the next reconciliation                                   |
| Audit Trail     | Pipeline logs scattered across CI jobs        | Git history records every change; tamper-evident with protected branches and signed commits |

The OpenGitOps principles summarise it: state is **declarative**, **versioned and immutable**, **pulled automatically**, and **continuously reconciled**. An in-cluster agent (such as Argo CD or Flux) periodically queries (or is notified by webhook about) the Git repository, computes a diff against live cluster objects, and applies synchronization. If an operator makes an ad-hoc change with `kubectl edit`, the controller detects the deviation and overwrites it back to the Git state.

**How release management changes.** A release becomes a pull request that bumps an image tag or digest in an environment's config; promotion between environments is a PR from one overlay to the next (often automated by image-update tooling); approval is code review; and "what is running in production?" is answered by reading a branch.

**Limitations.** Secrets cannot live in Git as plain text (use SOPS, Sealed Secrets, or External Secrets Operator); imperative steps such as database migrations still need a hook or job; multi-environment promotion needs its own tooling; and an unreachable Git host blocks deploys, including emergency fixes, unless you have a break-glass path.

## Example

Flux reconciling a path in Git every minute, pruning resources removed from Git:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: deploy-config
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/acme/deploy-config
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: payments-prod
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: deploy-config
  path: ./apps/payments/overlays/prod
  prune: true          # delete what was deleted from Git
  wait: true           # release is "done" only when workloads are healthy
```

## Interview tips

- Mentioning Git as the single source of truth for desired state.
- Reversing the security boundary: cluster pulls state from Git instead of CI holding cluster admin credentials.
- Continuous convergence and automatic drift remediation.
- Knowing the limits: secrets management, migrations, and promotion between environments.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[What is the difference between declarative and imperative Infrastructure as Code?]] (`#553`): [What is the difference between declarative and imperative Infrastructure as Code?](../infrastructure-as-code/what-is-the-difference-between-declarative-and-imperative-infrastructure-as-code.md)
- [[What is Cloud Drift and how do you continuously detect and reconcile it in production?]] (`#555`): [What is Cloud Drift and how do you continuously detect and reconcile it in production?](../infrastructure-as-code/what-is-cloud-drift-and-how-do-you-continuously-detect-and-reconcile-it-in-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
