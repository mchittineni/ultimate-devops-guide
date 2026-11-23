---
title: "What is GitOps?"
id: 87
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
---

# What is GitOps?

**Short answer:** GitOps is an operating model where the desired state of infrastructure and applications lives in Git, and an in-cluster controller continuously reconciles the running system towards that state - making Git the single source of truth and the only change interface.

## Detail

**The four principles** (from the OpenGitOps project):

1. **Declarative** - the entire system state is described declaratively.
2. **Versioned and immutable** - that state is stored in Git, with full history.
3. **Pulled automatically** - agents pull the desired state rather than being pushed to.
4. **Continuously reconciled** - agents detect and correct drift without human action.

**Pull versus push.** In traditional CD, the pipeline holds cluster credentials and pushes changes in. In GitOps, a controller inside the cluster pulls from Git. That inverts the security model - no external system needs cluster admin credentials - and means manual `kubectl` changes are automatically reverted.

**Benefits:** a complete audit trail (every change is a reviewed commit), trivial rollback (`git revert`), disaster recovery by pointing a fresh cluster at the repository, and consistency across many clusters.

**Repository structure.** The common pattern separates the application source repository from the configuration repository. CI builds and pushes an image, then updates the image tag in the config repo; the GitOps controller notices and deploys. This keeps deployment history distinct from code history.

**"Why not just run `helm upgrade` from CI?"** Because Helm and GitOps answer different questions. Helm is packaging and templating - one chart, per-environment values. GitOps is the delivery model - who applies the result, from where, and what keeps it true afterwards. They combine: Argo CD and Flux both render Helm charts natively. The difference with `helm upgrade` from a pipeline is that it is a one-shot push: the CI system needs cluster credentials, the release reflects whatever the pipeline ran rather than a reviewed commit, and once it finishes nothing notices if someone edits the cluster by hand. With GitOps, CI only commits a new image tag or values change, the in-cluster controller applies it, and drift is detected and reverted continuously.

**Tools:** Argo CD and Flux for Kubernetes; Crossplane or Terraform controllers extend the model to cloud infrastructure.

**Challenges to acknowledge:** secret management (sealed secrets, SOPS, or an external secrets operator), promotion between environments, and the temptation to hand-edit clusters during incidents - which the controller will undo. GitOps also describes desired state, not ordered procedures: database migrations, one-off jobs, and cross-cluster sequencing still need hooks, waves, or a pipeline around the controller.

## Example

```yaml
# Flux: pull a config repository and continuously reconcile one path of it.
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: { name: platform, namespace: flux-system }
spec:
  url: https://github.com/acme/platform-config.git
  ref: { branch: main }
  interval: 1m
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: apps, namespace: flux-system }
spec:
  sourceRef: { kind: GitRepository, name: platform }
  path: ./clusters/prod/apps
  interval: 10m # re-apply even without a commit: this is the drift correction
  prune: true # resources deleted from Git are deleted from the cluster
  wait: true
```

## Interview tips

- Pull-based reconciliation and the credential inversion is the key architectural point.
- "How do you handle secrets in Git?" is the guaranteed follow-up - have SOPS or External Secrets ready.
- Mention that drift correction means break-glass changes must also go through Git, or be explicitly excluded.
- If asked "why not Helm from Jenkins?", do not answer only with Helm's benefits (templating, reusable values) - that compares packaging, not delivery. The GitOps answer is no cluster credentials in CI, Git as the reviewed source of truth, and continuous drift correction; Helm charts still work underneath.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
