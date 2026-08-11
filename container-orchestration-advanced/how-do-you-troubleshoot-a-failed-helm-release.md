---
title: "How do you troubleshoot a failed Helm release?"
id: 412
category: "Container Orchestration Advanced"
difficulty: "Intermediate"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
  - kubernetes
  - devops-tools-and-automation
---

# How do you troubleshoot a failed Helm release?

**Short answer:** Separate the three failure layers, because each has a different fix. **Template failures** never reach the cluster - render locally with `helm template` or `helm install --dry-run --debug` and fix the chart. **Apply failures** mean the API server rejected the manifest (schema, immutable field, admission webhook) - `helm install --debug` prints the rejection verbatim. **Runtime failures** mean the objects were created but the Pods are unhealthy, so it is an ordinary Kubernetes debugging job (`describe pod`, events, logs) and Helm is only the messenger. Then know the two operational traps: a release stuck in `pending-install`/`pending-upgrade` needs `helm rollback` or `--force`, and `--wait --atomic --timeout` is what turns a half-applied release into a clean automatic rollback.

## Detail

### Layer 1: the chart never rendered

Render before you deploy - it costs nothing and catches most authoring errors:

```bash
helm template myrel ./chart -f values-prod.yaml | less
helm lint ./chart -f values-prod.yaml
```

Typical causes: a `nil` pointer because a values key is missing (`nil pointer evaluating interface {}.image`) - fix with `default` or `required` so the failure message is human; whitespace and indentation errors from `{{-` misuse producing invalid YAML; a missing `.Values` path after a chart upgrade renamed it; and type surprises where `"true"` and `true`, or `8080` and `"8080"`, are not interchangeable. `required "message" .Values.x` and a `values.schema.json` turn silent misrenders into clear errors at install time.

### Layer 2: rendered, but the API server refused it

`helm install --dry-run=server` (server-side dry run) validates against the real API, including admission webhooks. Common rejections:

- **Immutable field updates.** A Deployment's `spec.selector`, a Service's `clusterIP`, a Job's `spec.template`, a StatefulSet's `volumeClaimTemplates` - changing these needs the object deleted and recreated, not upgraded. `helm upgrade` reports `field is immutable` and stops.
- **Admission webhooks** - a policy engine (Kyverno, Gatekeeper) denying a Pod without resource limits or a non-compliant image registry. The message names the policy. See [how do you enforce Kubernetes admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md).
- **CRDs missing or ordering problems.** Helm installs CRDs from `crds/` before templates but does not upgrade them; a chart whose custom resources are applied before its operator's CRDs exist fails with `no matches for kind`.
- **Ownership conflicts.** `invalid ownership metadata` means an object already exists and was not created by this release - typically created manually or by a previous release with a different name. Adopt it by adding the correct `meta.helm.sh/release-name` annotations and `app.kubernetes.io/managed-by: Helm` label, or delete it.
- **RBAC** - the identity running Helm (often a CI service account) lacks permission for one kind. The error is a plain `forbidden`.

### Layer 3: installed, but the Pods are unhealthy

Here Helm reports success (or a `--wait` timeout) and the real problem is the workload: `Pending` from resource requests or PVCs, `ImagePullBackOff` from a wrong tag or missing pull secret, `CrashLoopBackOff` from configuration, or a readiness probe that never passes. Debug it as Kubernetes, not as Helm - see [how do you troubleshoot a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md). Two Helm-specific notes: `--wait` waits for readiness and will time out on a bad probe, and a failing **hook** Job (`pre-install`, `pre-upgrade`) fails the whole release - `--no-hooks` on a debug run isolates whether the hook or the workload is at fault.

### The state machine, and getting unstuck

Helm stores each release revision as a Secret in the release namespace. Its status matters:

- `deployed` - the good state. `failed` - the upgrade did not complete; the previous revision may still be running.
- `pending-install`, `pending-upgrade`, `pending-rollback` - **Helm was interrupted** (a killed CI job, a timeout, a lost connection). The release is locked and further upgrades report `another operation (install/upgrade/rollback) is in progress`. Recovery: `helm rollback <release> <last-good-revision>`, or `helm upgrade --force`, or as a last resort delete the newest release Secret (`sh.helm.release.v1.<name>.v<n>`) so Helm forgets the stuck revision. Also worth knowing: a failed **first** install leaves nothing to roll back to, so the fix is `helm uninstall` then reinstall.
- `helm history <release>` shows revisions, statuses, and chart versions; `helm get manifest`, `helm get values --all`, and `helm diff upgrade` (the plugin) tell you what actually changed - which is usually the real question.

### Making failures self-correcting

Deploy with `--atomic --wait --timeout 10m` so any failure rolls back automatically instead of leaving a half-applied release; pin the chart version and the image digest; keep `--history-max` bounded; and prefer a GitOps controller for production, where the desired state is a manifest in Git and rollback is `git revert` rather than an imperative command a human must remember under pressure. See [what is Helm](./what-is-helm.md) and [what is GitOps](../devops-tools-and-automation/what-is-gitops.md).

## Example

```bash
# 1. Did it even render? (no cluster involved)
helm template checkout ./chart -f values-prod.yaml > /tmp/rendered.yaml
helm lint ./chart -f values-prod.yaml

# 2. Will the API server accept it? (server-side: includes admission webhooks)
helm upgrade --install checkout ./chart -f values-prod.yaml --dry-run=server --debug

# 3. What state is the release in, and what changed?
helm status checkout -n prod
helm history checkout -n prod
# REVISION  STATUS           CHART            DESCRIPTION
# 6         superseded       checkout-1.8.2   Upgrade complete
# 7         pending-upgrade  checkout-1.9.0   Preparing upgrade   <- interrupted
helm diff upgrade checkout ./chart -f values-prod.yaml   # plugin: the real diff

# 4. Unstick a pending release, oldest fix first
helm rollback checkout 6 -n prod
# still stuck? then:
helm upgrade checkout ./chart -f values-prod.yaml -n prod --force --wait --timeout 10m
# last resort - drop the stuck revision record
kubectl -n prod delete secret sh.helm.release.v1.checkout.v7

# 5. Objects exist but Pods are unhealthy -> it is a Kubernetes problem now
kubectl get pods -n prod -l app.kubernetes.io/instance=checkout
kubectl describe pod -n prod <pod> | grep -A10 Events
```

```yaml
# Chart hygiene that turns silent misrenders into clear errors
# values.yaml documents the contract; required/default make failures legible
image:
  repository: registry.example.com/checkout
  digest: "" # required below - fail fast rather than deploy :latest
---
# templates/deployment.yaml excerpt
image: "{{ .Values.image.repository }}@{{ required "image.digest is required" .Values.image.digest }}"
resources: {{- toYaml (.Values.resources | default dict) | nindent 12 }}
```

## Interview tips

- Answer in the three layers - template, apply, runtime - and say which tool belongs to each. It shows you localise a failure instead of retrying the command.
- `helm template` / `--dry-run=server` before deploying is the habit to state early; server-side dry run catching admission webhooks is the detail that shows depth.
- Know the pending-state trap and how to escape it. "A killed CI job leaves the release in `pending-upgrade`, and the fix is `helm rollback` or deleting the release Secret" is a very practical answer few candidates give.
- Mention immutable fields - Deployment selectors, Service `clusterIP`, `volumeClaimTemplates` - as the class of change Helm cannot upgrade through.
- Explain that Helm stores state as Secrets in the namespace. Candidates who still say "Tiller" are dating themselves by two major versions.
- Recommend `--atomic --wait --timeout` for CI, then note the trade-off: an atomic rollback hides the broken state you might have wanted to inspect, so debug runs should omit it.
- Distinguish "Helm succeeded but Pods are broken" clearly - at that point Helm is irrelevant and you are doing ordinary Pod debugging.
- Close on the production preference for GitOps, where rollback is `git revert` and the cluster state is not the product of someone's shell history.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
