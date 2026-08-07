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

**Tools:** Argo CD and Flux for Kubernetes; Crossplane or Terraform controllers extend the model to cloud infrastructure.

**Challenges to acknowledge:** secret management (sealed secrets, SOPS, or an external secrets operator), promotion between environments, and the temptation to hand-edit clusters during incidents - which the controller will undo.

## Interview tips

- Pull-based reconciliation and the credential inversion is the key architectural point.
- "How do you handle secrets in Git?" is the guaranteed follow-up - have SOPS or External Secrets ready.
- Mention that drift correction means break-glass changes must also go through Git, or be explicitly excluded.

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
