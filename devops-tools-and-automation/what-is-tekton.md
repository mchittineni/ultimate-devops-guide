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

**Short answer:** Tekton is a Kubernetes-native CI/CD framework where pipelines are custom resources — Tasks, Pipelines, and their Runs — so builds execute as pods in the cluster and are managed with the same tooling as any other Kubernetes workload.

## Detail

**Resource model**

- **Step** — a single container execution.
- **Task** — an ordered set of steps that run in one pod, sharing a workspace.
- **Pipeline** — a graph of Tasks with parameters, results passed between them, and `runAfter` ordering or implicit parallelism.
- **TaskRun / PipelineRun** — an execution instance, with its own logs and status.
- **Workspace** — shared storage (PVC, ConfigMap, Secret, or emptyDir) mounted across Tasks.
- **Triggers** — EventListener, TriggerBinding, and TriggerTemplate turn a webhook into a PipelineRun.

**Why Kubernetes-native matters.** Pipelines are YAML in Git, versioned and reviewed. Executions are pods, so they use existing cluster autoscaling, RBAC, network policy, node selection, and monitoring. There is no separate CI server to operate, patch, and scale. Tekton Hub provides reusable Tasks (git-clone, kaniko, buildah, ko).

**Trade-offs.** It is a framework rather than a product: there is no rich built-in UI (Tekton Dashboard is basic), the YAML is verbose compared with GitHub Actions, and you assemble the developer experience yourself. Products like OpenShift Pipelines and Jenkins X build on it to close that gap.

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
      taskRef: { name: git-clone }
      workspaces: [{ name: output, workspace: source }]
      params:
        - { name: url, value: $(params.repo-url) }
        - { name: revision, value: $(params.revision) }
    - name: test
      runAfter: [clone]
      taskRef: { name: golang-test }
      workspaces: [{ name: source, workspace: source }]
    - name: build-image
      runAfter: [test]
      taskRef: { name: kaniko }
      workspaces: [{ name: source, workspace: source }]
```

## Interview tips

- "Pipelines as Kubernetes CRDs, builds as pods" is the one-line summary.
- Tekton Chains for supply-chain provenance is a strong detail to raise.
- Be honest that most teams choose GitHub Actions or GitLab CI unless they specifically need Kubernetes-native execution.

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
