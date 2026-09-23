---
title: "What is Tekton?"
id: 89
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
---

# What is Tekton?

**Short answer:** Tekton is a Kubernetes-native CI/CD framework where pipelines are custom resources - Tasks, Pipelines, and their Runs - so builds execute as pods in the cluster and are managed with the same tooling as any other Kubernetes workload.

## Detail

**Resource model**

- **Step** - a single container execution.
- **Task** - an ordered set of steps that run in one pod, sharing a workspace.
- **Pipeline** - a graph of Tasks with parameters, results passed between them, and `runAfter` ordering or implicit parallelism.
- **TaskRun / PipelineRun** - an execution instance, with its own logs and status.
- **Workspace** - shared storage (PVC, ConfigMap, Secret, or emptyDir) mounted across Tasks.
- **Triggers** - EventListener, TriggerBinding, and TriggerTemplate turn a webhook into a PipelineRun.

**Why Kubernetes-native matters.** Pipelines are YAML in Git, versioned and reviewed. Executions are pods, so they use existing cluster autoscaling, RBAC, network policy, node selection, and monitoring. There is no separate CI server to operate, patch, and scale. Reusable Tasks (git-clone, buildah, ko) are published on **Artifact Hub** - the old Tekton Hub was deprecated and its public instance shut down in January 2026 - and are pulled in at run time with **resolvers** (hub, bundles, git, cluster) rather than installed by hand. Cluster-scoped `ClusterTask`s have been removed in favour of the cluster resolver.

**Trade-offs.** It is a framework rather than a product: there is no rich built-in UI (Tekton Dashboard is basic), the YAML is verbose compared with GitHub Actions, and you assemble the developer experience yourself. Products like OpenShift Pipelines build on it to close that gap.

**Where it fits:** platform teams building an internal CI/CD offering on Kubernetes, and organisations that want builds isolated in their own cluster with strict supply-chain controls (Tekton Chains signs artifacts and generates provenance).

## Example

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata: { name: build-and-deploy }
spec:
  params:
    - { name: repo-url, type: string }
    - { name: revision, type: string }
  workspaces: [{ name: source }]
  tasks:
    - name: clone
      taskRef: # fetched from Artifact Hub at run time via the hub resolver
        resolver: hub
        params:
          - { name: type, value: artifact }
          - { name: kind, value: task }
          - { name: name, value: git-clone }
          - { name: version, value: "0.9" }
      workspaces: [{ name: output, workspace: source }]
      params:
        - { name: url, value: $(params.repo-url) }
        - { name: revision, value: $(params.revision) }
    - name: test
      runAfter: [clone]
      taskRef: { name: golang-test }
      workspaces: [{ name: source, workspace: source }]
    - name: build-image # buildah: kaniko's upstream repository was archived in 2025
      runAfter: [test]
      taskRef: { name: buildah }
      workspaces: [{ name: source, workspace: source }]
```

## Interview tips

- "Pipelines as Kubernetes CRDs, builds as pods" is the one-line summary.
- Tekton Chains for supply-chain provenance is a strong detail to raise.
- Knowing that Tekton Hub is gone (Artifact Hub plus resolvers now) and that kaniko's original repository was archived shows your knowledge is current.
- Be honest that most teams choose GitHub Actions or GitLab CI unless they specifically need Kubernetes-native execution.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
