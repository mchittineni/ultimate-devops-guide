---
title: "What is Kustomize and how does it achieve overlay configuration without templating?"
id: 630
category: "DevOps Tools and Automation"
difficulty: "Beginner"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - kustomize
  - kubernetes
  - gitops
  - overlays
quiz:
  stem: "What is the primary difference in philosophy between Helm and Kustomize?"
  options:
    - "Helm only works on AWS, while Kustomize only works on GCP"
    - "Helm uses parameterizable Go text templates, while Kustomize customizes plain valid YAML manifests using declarative patches and overlays"
    - "Kustomize requires an external agent daemon running in the cluster"
    - "Helm cannot deploy deployments"
  answer: 2
  explanation: "Helm turns manifests into Go text templates with variable substitution. Kustomize avoids templating completely, modifying valid base YAML files using declarative overlay patches."
---

# What is Kustomize and how does it achieve overlay configuration without templating?

**Short answer:** Kustomize is a template-free Kubernetes configuration management tool built into `kubectl` that uses a base and overlay inheritance structure to customize plain YAML manifests using JSON patches and strategic merges without template syntax.

## Detail

Helm turns manifests into Go text templates that are not valid YAML until rendered. Kustomize takes the opposite approach: every input is plain, valid Kubernetes YAML, and environment differences are expressed as declarative transformations over it.

### Base and overlay layout

```text
base/
  deployment.yaml
  service.yaml
  kustomization.yaml
overlays/
  dev/
    kustomization.yaml    (1 replica, dev image tag, dev ConfigMap values)
  prod/
    kustomization.yaml    (10 replicas, resource limits patch, adds an HPA)
```

A `kustomization.yaml` lists `resources` (files or other kustomizations - including remote bases pinned to a Git ref) and the transformations to apply.

### How it customises without templates

- **Patches** (`patches:`), in two forms:
  - **Strategic merge patches** - a partial manifest that Kustomize merges into the matching object using Kubernetes-aware rules (lists of containers are merged by `name`, not replaced).
  - **JSON 6902 patches** - explicit `op`/`path`/`value` operations, for precise edits the merge semantics cannot express.
- **Built-in transformers**: `images` (retag without touching the Deployment), `replicas`, `namespace`, `namePrefix`/`nameSuffix`, `labels` (the replacement for the deprecated `commonLabels`), and `replacements` for copying a value from one field to another.
- **Generators**: `configMapGenerator` and `secretGenerator` append a content hash to the name, so changing a value rolls the Pods that reference it automatically.
- **Components** package optional features (e.g. "enable tracing") that several overlays can include.

Note that the older `patchesStrategicMerge` and `patchesJson6902` fields are deprecated in favour of the single `patches` field, and `kustomize edit fix` migrates old files.

### Why GitOps teams like it

- Bases stay valid YAML, so they can be linted, diffed, and reviewed as-is.
- It is built into `kubectl` (`kubectl apply -k`, `kubectl kustomize`), and Argo CD and Flux render it natively.
- `kustomize build overlays/prod` produces the exact output that will be applied, which is easy to diff in a pull request.

**Limitations.** No conditionals or loops, so highly variable configuration gets verbose; deep overlay chains become hard to follow; and the Kustomize version embedded in `kubectl` lags the standalone release. It is not a package manager - there is no release history or versioned distribution - so third-party software is still usually installed from Helm charts, which Kustomize can inflate with `helmCharts`.

## Example

```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: payments
resources:
  - ../../base
  - hpa.yaml
images:
  - name: registry.example.com/api
    newTag: "1.9.0"
labels:
  - pairs: { env: prod }
    includeSelectors: false
patches:
  # Strategic merge: a partial Deployment, merged by container name.
  - patch: |-
      apiVersion: apps/v1
      kind: Deployment
      metadata: { name: api }
      spec:
        template:
          spec:
            containers:
              - name: api
                resources:
                  requests: { cpu: 500m, memory: 512Mi }
                  limits: { memory: 512Mi }
  # JSON 6902: an explicit operation on one field.
  - target: { kind: Deployment, name: api }
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 10
configMapGenerator:
  - name: api-config
    literals: [LOG_LEVEL=info]
```

```bash
kustomize build overlays/prod | kubeconform -strict -   # review exactly what will be applied
kubectl diff -k overlays/prod                            # compare with the live cluster
```

## Interview tips

- Contrast the philosophies: Helm templates text, Kustomize transforms valid YAML.
- Explain base and overlays, then name both patch types and when to use each.
- Mention generators with hash suffixes - they make config changes roll Pods automatically.
- Show currency: `patches` replaces `patchesStrategicMerge`/`patchesJson6902`, and `labels` replaces `commonLabels`.
- Be fair about limitations - no logic, no packaging - and say that Helm plus Kustomize together is common.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
