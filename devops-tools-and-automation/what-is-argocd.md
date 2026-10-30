---
title: "What is ArgoCD?"
id: 88
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
---

# What is ArgoCD?

**Short answer:** Argo CD is a declarative GitOps continuous delivery controller for Kubernetes. It watches Git repositories for manifests, compares them with live cluster state, and syncs the difference - automatically or on approval - with a UI showing health and drift.

## Detail

**Core concepts**

- **Application** - a CRD mapping a Git repo path (plus target revision) to a destination cluster and namespace.
- **Sync** - applying the desired state. `automated` sync can include `prune` (delete resources removed from Git) and `selfHeal` (revert manual cluster changes).
- **Sync status** - `Synced` or `OutOfSync`; **health status** - `Healthy`, `Progressing`, `Degraded`, computed per resource type with customisable Lua health checks.
- **Sync waves and hooks** - order resources within a sync (`PreSync` for migrations, waves for dependencies).
- **ApplicationSet** - generates many Applications from a template: one per cluster, per Git directory, or per pull request.
- **Projects** - RBAC and guardrails restricting which repos, clusters, and resource kinds a team may use.

**Manifest sources:** plain YAML, Kustomize, Helm, or Jsonnet - Argo renders them and applies the result.

**Multi-cluster.** One Argo CD instance can manage many clusters, or you can run "app of apps" hierarchies where a root Application bootstraps everything else, which makes cluster rebuild a single command.

**Progressive delivery** comes from the sibling project **Argo Rollouts**, which adds canary and blue/green strategies with automated analysis and rollback.

**Architecture - useful when debugging.** The **repo-server** clones Git and renders manifests (Helm, Kustomize, plugins), so rendering errors and slow syncs usually show up there; the **application-controller** compares rendered and live state and performs syncs (sharded across replicas for large fleets); the **API server** backs the UI, CLI, and SSO; **Redis** caches rendered manifests and cluster state; and the **ApplicationSet controller** generates Applications. Argo CD 3.x (from 2025) tightened defaults - annotation-based resource tracking instead of the `app.kubernetes.io/instance` label, and fine-grained RBAC that no longer lets `update`/`delete` on an Application cascade to its managed resources - so check the version before copying older configuration.

**Argo CD versus Flux.** Both are CNCF-graduated GitOps controllers. Argo CD is an application-centric product with a UI, multi-cluster management from one instance, and its own RBAC/SSO layer; Flux is a set of composable controllers (`GitRepository`, `Kustomization`, `HelmRelease`) that usually runs in each cluster and relies on Kubernetes RBAC, with no first-party UI. Teams that want a portal for developers lean Argo CD; teams that want GitOps as pure Kubernetes APIs lean Flux.

**Limitations to name:** it reconciles desired state but does not order cross-application workflows (use sync waves, hooks, or a pipeline), a central instance holding credentials for every cluster is a high-value target, and the repo-server can become a bottleneck when rendering large Helm charts across hundreds of Applications.

## Example

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: api, namespace: argocd }
spec:
  project: platform
  source:
    repoURL: https://github.com/org/k8s-config.git
    targetRevision: main
    path: apps/api/overlays/production
  destination: { server: https://kubernetes.default.svc, namespace: production }
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
    retry: { limit: 5, backoff: { duration: 10s, factor: 2 } }
```

## Interview tips

- `selfHeal` and `prune` are the two flags every Argo CD question eventually reaches - know exactly what each does and its risk.
- ApplicationSet is the answer to managing dozens of clusters or environments.
- Pair Argo CD (delivery) with Argo Rollouts (progressive release) in your answer.
- Expect "Argo CD or Flux?" - answer with the trade-off (UI and central multi-cluster management versus composable per-cluster controllers), not a preference.
- Knowing which component does what (repo-server renders, application-controller syncs) is what lets you debug a slow or failing sync quickly.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
