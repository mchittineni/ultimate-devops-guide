---
title: "What is inside a Helm chart, and how do you customise one?"
id: 450
category: "Container Orchestration Advanced"
difficulty: "Intermediate"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
  - kubernetes
  - cicd
---

# What is inside a Helm chart, and how do you customise one?

**Short answer:** A chart is a directory with a fixed shape: `Chart.yaml` (name, version, appVersion, dependencies), `values.yaml` (the default, documented inputs), `templates/` (Go-templated manifests plus `_helpers.tpl` for shared snippets and `NOTES.txt` for post-install output), `charts/` (vendored subchart dependencies), and optionally `crds/` and `values.schema.json`. `helm template` renders those templates with your values and prints the YAML; `helm install`/`upgrade` renders the same thing and then sends it to the API server, recording a **release revision** so `helm rollback` can go back. You customise a chart **without forking it** by layering values - `-f prod-values.yaml --set image.tag=1.9.0` - and where the chart has no knob for what you need, by adding your own manifests alongside it (a wrapper chart with the public chart as a dependency, or Kustomize applied to the rendered output) rather than editing someone else's templates.

## Detail

### The layout, and what each file is for

```text
mychart/
├── Chart.yaml          # apiVersion: v2, name, version (chart), appVersion (app), dependencies
├── Chart.lock          # resolved dependency digests - commit this
├── values.yaml         # defaults + documentation; this IS the chart's public API
├── values.schema.json  # optional JSON Schema: rejects bad values at install time
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── _helpers.tpl    # named templates (fullname, labels) - not rendered itself
│   ├── NOTES.txt       # printed after install: how to reach the app
│   └── tests/          # `helm test` hooks
├── crds/               # installed before templates, NOT templated, never upgraded by Helm
└── charts/             # subcharts pulled by `helm dependency update`
```

Two details worth knowing precisely. Files whose name starts with `_` are **not** rendered as manifests, which is why helpers live in `_helpers.tpl`. And `Chart.yaml` carries **two** versions: `version` is the chart's own semver (bump it on any template change) and `appVersion` is the application's version (usually the default image tag) - conflating them is a common review comment.

### `helm template` versus `helm install`

|                         | `helm template`                                   | `helm install` / `upgrade`                  |
| ----------------------- | ------------------------------------------------- | ------------------------------------------- |
| Talks to the cluster    | No (unless `--validate`)                          | Yes                                         |
| Output                  | YAML on stdout                                    | Applied objects + a stored release revision |
| Uses `lookup` functions | Return empty                                      | Work                                        |
| Runs hooks              | No                                                | Yes                                         |
| Good for                | CI diffing, GitOps rendering, debugging templates | Actually deploying, plus rollback history   |

`helm template` is how you debug: render locally, read the YAML, and see exactly what your values produced. `helm install --dry-run --debug` is the same thing with server-side validation and the computed values printed. In GitOps setups it is common to render with `helm template` and commit or sync the output, so Argo CD/Flux applies plain manifests and the diff is readable.

### Customising a public chart - four options, in order of preference

1. **Values files.** The intended mechanism. Layer them: `-f base.yaml -f prod.yaml --set image.tag=$SHA`, where later files win key by key and `--set` wins over everything. Read the upstream `values.yaml` as the contract; most good charts expose `resources`, `nodeSelector`, `tolerations`, `podAnnotations`, `extraEnv`, `extraVolumes`, and `podSecurityContext` for exactly this reason.
2. **A wrapper (umbrella) chart.** Declare the public chart as a dependency in your `Chart.yaml`, put your overrides under its name in your `values.yaml`, and add your own extra manifests in your `templates/`. This answers "how do you add extra Kubernetes manifests to a public chart?" - you do not touch the chart, you ship a parent that carries both. Aliases let you install the same subchart twice with different values.
3. **Post-rendering.** `helm upgrade --post-renderer ./kustomize.sh` pipes the rendered manifests through Kustomize, so you can patch anything the chart did not parameterise without forking.
4. **Fork.** Last resort. You inherit the maintenance and lose upstream fixes. If you fork, record why in the repository.

Parent-child value rules interviewers probe: subchart values are set under the subchart's name, `global:` is visible to all subcharts, and a parent's value beats the subchart's default.

### Secrets in a chart

Never put real secrets in `values.yaml` - it lands in Git and in the release object. Options: reference an existing Secret by name (`existingSecret:` is the convention good charts expose), inject with `--set` from the pipeline's secret store at deploy time, `helm-secrets`/SOPS for encrypted values files, or let the External Secrets Operator create the Secret and point the chart at it. Remember that `helm get values` and the release Secret in the namespace expose whatever you passed, so `--set password=...` is visible to anyone with read access there.

### The mechanics that bite in production

- **Release state lives in a Secret** in the release namespace (`sh.helm.release.v1.<name>.v<n>`), so `helm list` is only as good as your namespace and context. Lose the namespace, lose the history.
- **Hooks** (`helm.sh/hook: pre-upgrade`) run as separate objects and are **not** part of the release's rollback set - a failed migration hook leaves a Job behind and a release stuck `pending-upgrade`. Set `helm.sh/hook-delete-policy` accordingly.
- **`--atomic --timeout 5m`** makes a failed upgrade roll itself back automatically, and `--wait` blocks until resources are Ready. Use both in CI; without them a "successful" deploy just means the YAML was accepted.
- **CRDs in `crds/` are installed once and never upgraded or deleted by Helm.** Upgrading CRDs is your job, out of band. This surprises people during operator upgrades.
- **`--reuse-values` versus `--reset-values`**: `--reuse-values` carries forward what you set last time (and can silently keep a stale image tag); being explicit with full values files avoids the whole class of bug.
- **Ownership metadata**: adopting an existing object into a release needs the right `app.kubernetes.io/managed-by` and ownership annotations, otherwise you get "exists and cannot be imported".

### Helm versus Kustomize

Fair answer rather than tribal: Helm gives you packaging, versioning, distribution, and rollback history, at the cost of Go templating inside YAML. Kustomize gives you strongly typed, template-free overlays with no release concept. Many teams use both - Helm for third-party software, Kustomize for their own manifests, or Helm rendered then Kustomize-patched. Say that; it reads as experience rather than preference.

## Example

```yaml
# Chart.yaml - a wrapper chart: reuse upstream, add your own objects
apiVersion: v2
name: payments-platform
version: 1.4.0 # chart version - bump on template changes
appVersion: "2.7.1" # the application version
dependencies:
  - name: redis
    version: 19.6.4
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled # let environments switch it off
  - name: kube-prometheus-stack
    version: 61.3.2
    repository: https://prometheus-community.github.io/helm-charts
    alias: monitoring
```

```yaml
# values.yaml - the chart's public API, documented and safely defaulted
replicaCount: 2
image:
  repository: registry.example.com/payments
  tag: "" # empty -> falls back to .Chart.AppVersion in the template
  pullPolicy: IfNotPresent
resources:
  requests: { cpu: 250m, memory: 256Mi }
  limits: { memory: 256Mi }
existingSecret: payments-secrets # never put credentials in values
redis:
  enabled: true # subchart values live under the subchart name
  auth: { existingSecret: redis-auth }
global:
  environment: prod # visible to every subchart
```

```yaml
# templates/deployment.yaml - helpers, sane fallbacks, config-driven rollouts
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "payments.fullname" . }}
  labels: {{- include "payments.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels: {{- include "payments.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        # config change -> new pod template hash -> rolling update
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels: {{- include "payments.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          envFrom:
            - secretRef: { name: {{ .Values.existingSecret | quote }} }
          resources: {{- toYaml .Values.resources | nindent 12 }}
```

```bash
# Author and verify
helm lint . && helm dependency update
helm template payments . -f values-prod.yaml | kubectl apply --dry-run=server -f -
helm unittest .                       # or `helm test` after install

# Deploy safely: wait for readiness, auto-rollback on failure
helm upgrade --install payments . -n prod --create-namespace \
  -f values-prod.yaml --set image.tag="$GIT_SHA" \
  --atomic --timeout 5m

# Inspect and roll back
helm history payments -n prod
helm get values payments -n prod           # what was actually applied
helm diff upgrade payments . -f values-prod.yaml   # helm-diff plugin: review before applying
helm rollback payments 7 -n prod --wait
```

## Interview tips

- Recite the layout confidently - `Chart.yaml`, `values.yaml`, `templates/` with `_helpers.tpl` and `NOTES.txt`, `charts/`, `crds/` - and add the two details that show you have written charts: files starting with `_` are not rendered, and `version` versus `appVersion` mean different things.
- Explain `helm template` versus `helm install` as "render only" versus "render and record a revision", and mention that `template` cannot use `lookup` or run hooks. Then say `helm template` is your debugging tool.
- For "how do you customise a public chart?", give the ladder: values files, then a wrapper chart with the upstream as a dependency, then a post-renderer, and forking only as a last resort. The wrapper-chart answer is what interviewers are fishing for when they ask about adding extra manifests.
- Volunteer `--atomic --timeout --wait` for CI, because "the upgrade succeeded but the Pods never became Ready" is a real class of incident.
- Know where release state lives (a Secret in the namespace) and that CRDs in `crds/` are never upgraded by Helm - both are specific and both come up.
- Be clear about secrets: not in `values.yaml`, prefer an `existingSecret` reference, and remember `helm get values` exposes anything you passed with `--set`.
- Give a balanced Helm-versus-Kustomize answer rather than a preference. See [what is Helm](./what-is-helm.md), [troubleshooting a failed Helm release](./how-do-you-troubleshoot-a-failed-helm-release.md), [what is ArgoCD](../devops-tools-and-automation/what-is-argocd.md), and [ConfigMaps and Secrets](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
