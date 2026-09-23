---
title: "What is Helm and how do Helm charts manage templating, dependencies, and rollbacks in Kubernetes?"
id: 629
category: "DevOps Tools and Automation"
difficulty: "Beginner"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - helm
  - kubernetes
  - package-manager
  - templating
quiz:
  stem: "Where does modern Helm (v3+) store release metadata and revision history inside a Kubernetes cluster?"
  options:
    - "Inside a dedicated MySQL database"
    - "As Kubernetes Secrets (gzipped, base64-encoded release records) located in the target release namespace"
    - "In a centralized Tiller pod running in kube-system"
    - "On the local developer's laptop hard drive"
  answer: 2
  explanation: "Helm v3 eliminated the insecure Tiller daemon and stores release history directly as Kubernetes Secrets in the target application namespace - encoded, not encrypted, so protect read access to them."
---

# What is Helm and how do Helm charts manage templating, dependencies, and rollbacks in Kubernetes?

**Short answer:** Helm is the package manager for Kubernetes that bundles declarative YAML manifests into parameterizable, versioned archives called Charts, managing releases, variable interpolation (`values.yaml`), dependencies, and stateful rollbacks (`helm rollback`).

## Detail

Managing raw Kubernetes manifests across environments (dev, staging, prod) leads to duplicated, drifting YAML. Helm packages them once and parameterises the differences.

### Core concepts

1. **Chart** - a versioned package: `Chart.yaml` (name, `version` of the chart, `appVersion` of the software), `values.yaml` (defaults), and `templates/` rendered with Go templates plus Sprig functions (`{{ .Values.replicaCount }}`, `{{ include "app.labels" . }}`). Charts are distributed from classic HTTP repositories or, increasingly, as **OCI artefacts** in a container registry (`oci://registry.example.com/charts/api`).
2. **Values** - configuration layered at install time: chart defaults, then `-f values-prod.yaml` files, then `--set` overrides. A `values.schema.json` can validate them.
3. **Release** - one installed instance of a chart in a namespace, with a numbered **revision** for every install, upgrade, or rollback.
4. **Dependencies** - declared in `Chart.yaml` (`dependencies:` with version ranges and `condition:` toggles), vendored into `charts/` by `helm dependency update`, and pinned in `Chart.lock`.

### Release storage and rollback

- Helm 3 removed Tiller; the client talks to the API server with the user's own RBAC. Release records are stored in the release's namespace as **Secrets** of type `helm.sh/release.v1` named `sh.helm.release.v1.<release>.v<revision>`. They are gzipped and base64-encoded, _not_ encrypted - anyone who can read Secrets in that namespace can read the rendered manifests and values, so avoid putting plaintext secrets in values.
- `helm upgrade` renders the new revision and applies it; `helm rollback api 2` re-applies the manifests stored in revision 2 as a **new** revision (so history shows 1, 2, 3, then 4 = copy of 2).
- **What rollback does not undo**: database migrations, data written by the new version, CRD changes (Helm installs CRDs from `crds/` but never upgrades or deletes them), and anything created by hooks. Treat rollback as a manifest revert, not a time machine.

### Helm 4

Helm 4 went GA in November 2025, and Helm 3 receives only security fixes until February 2027. The changes that affect pipelines: **server-side apply** is the default for new releases (existing releases keep their previous apply method unless you opt in), `--wait` uses kstatus-based readiness, `--atomic` is renamed `--rollback-on-failure` and `--force` becomes `--force-replace` (the old flags still work with deprecation warnings), and plugins can be WebAssembly. Charts using `apiVersion: v2` continue to work.

**Trade-offs.** Go templating over YAML is whitespace-sensitive and hard to read at scale; heavily parameterised charts become their own programming language. Helm's three-way merge can still be surprised by fields other controllers own. Many teams combine it with Kustomize (post-render) or let Argo CD/Flux render the chart so Git, not Helm's release history, is the source of truth.

## Example

```bash
# Render locally and validate before anything touches the cluster.
helm lint ./chart -f values-prod.yaml
helm template api ./chart -f values-prod.yaml | kubeconform -strict -

# Install or upgrade from an OCI registry, rolling back automatically if it never gets healthy.
helm upgrade --install api oci://registry.example.com/charts/api --version 1.9.0 \
  -n payments --create-namespace -f values-prod.yaml \
  --wait --timeout 5m --rollback-on-failure        # Helm 4 name for --atomic

helm history api -n payments
# REVISION  STATUS      CHART      DESCRIPTION
# 1         superseded  api-1.8.0  Install complete
# 2         deployed    api-1.9.0  Upgrade complete
helm rollback api 1 -n payments                    # creates revision 3 = revision 1's manifests

kubectl get secret -n payments -l owner=helm       # where the release history lives
```

## Interview tips

- Define chart, values, and release, and explain values layering (defaults, `-f`, `--set`).
- Say where release state lives - Secrets in the release namespace, encoded but not encrypted - and that Tiller is long gone.
- Explain what `helm rollback` really does (a new revision re-applying old manifests) and what it cannot undo: migrations, data, CRDs.
- Show currency: Helm 4 with server-side apply by default, `--rollback-on-failure`, and OCI registries for charts.
- Mention the templating trade-off and how GitOps controllers or Kustomize complement Helm.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
