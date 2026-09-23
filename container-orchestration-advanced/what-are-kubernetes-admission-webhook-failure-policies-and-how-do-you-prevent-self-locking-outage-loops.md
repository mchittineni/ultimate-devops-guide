---
title: "What are Kubernetes Admission Webhook failure policies and how do you prevent self-locking outage loops?"
id: 628
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - kubernetes
  - admission-controller
  - webhooks
  - troubleshooting
  - outages
quiz:
  stem: "How can an engineering team prevent a failing Validating Admission Webhook from blocking its own controller pod from starting after a cluster reboot?"
  options:
    - "By disabling the Linux kernel on the API server"
    - "By configuring `namespaceSelector` to exempt `kube-system` and the webhook's own namespace from webhook evaluation"
    - "By running the API server inside Docker Desktop"
    - "By deleting etcd snapshots every hour"
  answer: 2
  explanation: "Exempting system and webhook namespaces ensures the API server allows the webhook's own pods to boot up without being intercepted by a dead validation endpoint."
---

# What are Kubernetes Admission Webhook failure policies and how do you prevent self-locking outage loops?

**Short answer:** `failurePolicy` decides what the API server does when it cannot get an answer from a webhook - it is down, times out, or returns an error. `Fail` rejects the request (policy is never bypassed, but the webhook becomes a hard dependency of every matching write); `Ignore` lets the request through unchecked. The self-locking outage happens when a `Fail` webhook matches the creation of **its own Pods**: if every webhook replica disappears at once - a node pool replacement, a bad rollout, an eviction storm - the replacement Pods cannot be admitted because the webhook that would admit them is not running. Prevent it by exempting the webhook's own namespace and system namespaces, running the webhook highly available, keeping timeouts short, and knowing the break-glass fix: delete the webhook configuration.

## Detail

**How the deadlock forms.**

1. A `ValidatingWebhookConfiguration` or `MutatingWebhookConfiguration` has `failurePolicy: Fail` and matches `CREATE` on `pods` in every namespace.
2. All webhook Pods go away at once - for example, every node is replaced during an upgrade, or the webhook's Deployment is rolled to a broken image.
3. The ReplicaSet controller tries to create new webhook Pods. Pod creation is an API write, so it goes through admission.
4. The API server calls the webhook Service, which has no endpoints. The call fails, and with `Fail` the Pod creation is rejected.
5. No webhook Pod can be created, so no Pod anywhere that the webhook matches can be created either - including CoreDNS, the CNI, and the controllers you need to fix things.

Note that restarting containers in **existing** Pods does not go through admission - the kubelet does it locally - which is why this outage often appears only when Pods are recreated, not on a simple reboot.

**Prevention.**

- **Exempt the webhook's own namespace and system namespaces** with `namespaceSelector` (the immutable `kubernetes.io/metadata.name` label is safe to use), or with `objectSelector` for the webhook's own Pods.
- **Scope the rules tightly.** Match only the resources and operations the policy needs; `matchConditions` (CEL, GA in 1.30) can skip requests - for example, from system service accounts - without calling the webhook at all.
- **Short `timeoutSeconds`** (the default is 10, the maximum 30). Every matching request waits this long when the webhook is slow, which can cascade into API server overload.
- **High availability**: at least two or three replicas, spread across nodes and zones, with a PodDisruptionBudget and a high `priorityClassName` so they are not the first to be evicted.
- **Choose the policy per webhook.** Security-critical policy (image signature verification, privileged-Pod denial) justifies `Fail` plus the controls above; convenience mutation (default labels) should usually be `Ignore`.
- **Prefer in-process policy where possible.** `ValidatingAdmissionPolicy` (GA in 1.30) and `MutatingAdmissionPolicy` (GA in 1.36) run CEL inside the API server, so they have no network dependency and cannot deadlock this way.
- **Monitor** `apiserver_admission_webhook_rejection_count` and webhook latency metrics, and alert on webhook endpoints going to zero.

**Recovery.** The API server never sends `ValidatingWebhookConfiguration` or `MutatingWebhookConfiguration` objects themselves to webhooks, so a cluster admin can always delete or patch the configuration. Remove it (or switch it to `Ignore`), let the webhook Pods start, then reapply it - and record the gap in enforcement.

## Example

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata: { name: gatekeeper-validating-webhook-configuration }
webhooks:
  - name: validation.gatekeeper.sh
    admissionReviewVersions: ["v1"]
    sideEffects: None
    failurePolicy: Fail
    timeoutSeconds: 3 # fail fast rather than stall the API server
    rules:
      - apiGroups: ["*"]
        apiVersions: ["*"]
        operations: ["CREATE", "UPDATE"]
        resources: ["*"]
    namespaceSelector: # never police the namespaces that must boot first
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: NotIn
          values: ["kube-system", "gatekeeper-system"]
    matchConditions: # skip node and control-plane identities without calling out
      - name: not-system-nodes
        expression: "!request.userInfo.username.startsWith('system:node:')"
    clientConfig:
      service: { name: gatekeeper-webhook-service, namespace: gatekeeper-system, path: /v1/admit }
```

```bash
# Is a webhook the reason writes are failing?
kubectl get events -A | grep -i 'failed calling webhook'
kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
kubectl -n gatekeeper-system get endpointslices     # no endpoints + Fail = blocked writes

# Break glass: remove the configuration, recover, then reapply from Git
kubectl get validatingwebhookconfiguration gatekeeper-validating-webhook-configuration -o yaml > /tmp/vwc.yaml
kubectl delete validatingwebhookconfiguration gatekeeper-validating-webhook-configuration
```

## Interview tips

- Define `failurePolicy` precisely: it applies when the webhook cannot answer, not when it denies. `Fail` is secure but makes the webhook a hard dependency; `Ignore` is available but bypassable.
- Walk the deadlock step by step, and point out that it triggers on Pod **creation**, which is why node replacement or a bad rollout exposes it.
- Give the prevention set: namespace and object selectors, `matchConditions`, short timeouts, HA with PDBs, and per-webhook choice of policy.
- Mention CEL admission policies as the structural fix for checks that do not need external data.
- Know the break-glass: webhook configuration objects are never themselves sent to webhooks, so you can always delete one.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
