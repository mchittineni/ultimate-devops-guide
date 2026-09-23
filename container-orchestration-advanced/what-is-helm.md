---
title: "What is Helm?"
id: 83
category: "Container Orchestration Advanced"
difficulty: "Intermediate"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
---

# What is Helm?

**Short answer:** Helm is the package manager for Kubernetes. It packages manifests into versioned, parameterised **charts**, renders them with user-supplied values, and installs them as tracked **releases** that can be upgraded and rolled back.

## Detail

**Why it exists.** Deploying an application usually means a Deployment, Service, Ingress, ConfigMap, ServiceAccount, HPA, and PodDisruptionBudget - repeated per environment with small differences. Helm turns that into one templated chart plus a values file per environment.

**Structure**

```text
mychart/
  Chart.yaml         # name, version, appVersion, dependencies
  values.yaml        # default configuration
  templates/         # Go-templated manifests
    deployment.yaml
    _helpers.tpl     # named template snippets
  charts/            # vendored subcharts
```

**Releases.** `helm install` records the rendered manifests and values as a release secret in the cluster. `helm upgrade` creates a new revision, `helm rollback` restores a previous one, and `helm history` lists them. This revision tracking is Helm's key operational value over `kubectl apply`.

**Useful features:** `--rollback-on-failure` (Helm 4's name for Helm 3's `--atomic`: roll back automatically if the upgrade fails), `--wait` (block until resources are Ready), OCI registries for distributing charts (`helm push`, `oci://` references), hooks (`pre-install`, `post-upgrade`) for migrations, `helm template` to render locally for inspection or GitOps, `helm lint`, and `helm test`.

**Criticism worth knowing.** Go templating over YAML is error-prone for complex logic, which is why alternatives exist - Kustomize (overlay patching, no templating), Timoni, and cdk8s. Many teams use Helm to consume third-party charts and Kustomize for their own applications.

**Versions.** Helm 4 was released in November 2025 with a redesigned plugin system (including WebAssembly plugins), server-side apply support, kstatus-based waiting, and several renamed flags (`--atomic` → `--rollback-on-failure`, `--force` → `--force-replace`). Existing `apiVersion: v2` charts keep working. Helm 3 receives security fixes only until February 2027, so CI pipelines pinned to Helm 3 flags need updating.

## Example

```yaml
# templates/deployment.yaml
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          resources: {{- toYaml .Values.resources | nindent 12 }}
```

```bash
helm upgrade --install api ./mychart -f values-prod.yaml \
  --namespace prod --rollback-on-failure --wait --timeout 5m   # Helm 3: --atomic
helm history api && helm rollback api 3
```

## Interview tips

- Release revisions and `helm rollback` are the differentiators over raw manifests.
- `--rollback-on-failure` (formerly `--atomic`) plus `--wait` is the answer to "how do you make Helm deployments safe?" - and knowing the Helm 4 rename shows you are current.
- Know the Helm-versus-Kustomize debate and have a reasoned preference.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
