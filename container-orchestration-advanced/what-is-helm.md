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

# 83. What is Helm?

**Short answer:** Helm is the package manager for Kubernetes. It packages manifests into versioned, parameterised **charts**, renders them with user-supplied values, and installs them as tracked **releases** that can be upgraded and rolled back.

## Detail

**Why it exists.** Deploying an application usually means a Deployment, Service, Ingress, ConfigMap, ServiceAccount, HPA, and PodDisruptionBudget — repeated per environment with small differences. Helm turns that into one templated chart plus a values file per environment.

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

**Useful features:** `--atomic` (roll back automatically if the upgrade fails), `--wait` (block until resources are Ready), hooks (`pre-install`, `post-upgrade`) for migrations, `helm template` to render locally for inspection or GitOps, `helm lint`, and `helm test`.

**Criticism worth knowing.** Go templating over YAML is error-prone for complex logic, which is why alternatives exist — Kustomize (overlay patching, no templating), Timoni, and cdk8s. Many teams use Helm to consume third-party charts and Kustomize for their own applications.

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
  --namespace prod --atomic --timeout 5m
helm history api && helm rollback api 3
```

## Interview tips

- Release revisions and `helm rollback` are the differentiators over raw manifests.
- `--atomic` plus `--wait` is the answer to "how do you make Helm deployments safe?"
- Know the Helm-versus-Kustomize debate and have a reasoned preference.

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
