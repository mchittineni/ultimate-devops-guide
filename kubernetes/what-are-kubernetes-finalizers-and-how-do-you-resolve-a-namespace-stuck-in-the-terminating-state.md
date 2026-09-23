---
title: "What are Kubernetes Finalizers and how do you resolve a namespace stuck in the Terminating state?"
id: 529
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - troubleshooting
  - finalizers
  - controllers
quiz:
  stem: "Why does a Kubernetes resource remain visible with a deletionTimestamp rather than disappearing immediately after a delete command?"
  options:
    - "etcd requires 24 hours of disk compaction before releasing keys"
    - "One or more entries in `metadata.finalizers` have not yet been cleared by their reconciling controllers"
    - "The Kubelet must reboot the worker node before confirming deletion"
    - "The resource is waiting for a cluster backup snapshot to complete"
  answer: 2
  explanation: "Finalizers notify controllers to execute cleanup logic (e.g. deleting cloud load balancers or storage volumes). The API server will not remove the object from etcd until the finalizer list is empty."
---

# What are Kubernetes Finalizers and how do you resolve a namespace stuck in the Terminating state?

**Short answer:** A finalizer is a string in an object's `metadata.finalizers` list that tells the API server "do not remove this object until some controller has finished cleaning up". A delete request only sets `metadata.deletionTimestamp`; the object stays, visible and read-only apart from its finalizers, until every controller removes its entry, and then the API server deletes it. A namespace sticks in `Terminating` when something it contains cannot be cleaned up - usually an unavailable aggregated API or webhook that stops discovery, or a custom resource whose controller is gone or failing. Fix the cause first; forcibly removing finalizers is a last resort because it can orphan real cloud resources.

## Detail

**The mechanism.** Controllers add their finalizer when they create something outside the object's own lifetime - a cloud load balancer for a `Service`, a disk for a PV, an external database for an operator's CR. On delete:

1. The API server sets `deletionTimestamp` (and honours the grace period), but does not delete.
2. Each controller watching the object sees the timestamp, performs its cleanup, and removes **its own** finalizer with an update.
3. When `metadata.finalizers` is empty, the API server deletes the object from etcd.

Built-in examples: `kubernetes.io/pvc-protection` (a PVC in use by a Pod is not deleted), `kubernetes.io/pv-protection`, `foregroundDeletion` (the owner waits until its dependents are gone), and `service.kubernetes.io/load-balancer-cleanup`.

**How namespace deletion works.** A namespace has its own finalizer in `spec.finalizers` (`kubernetes`). The namespace controller discovers **every** namespaced resource type the API server serves - including those from CRDs and aggregated APIs - deletes all objects of each type in the namespace, waits for their finalizers, and only then removes the `kubernetes` finalizer.

**Common causes of a stuck namespace.**

1. **An unavailable aggregated APIService** (for example, metrics-server or a custom API server whose Pods are down). Discovery fails for that group, so the controller cannot prove the namespace is empty and refuses to finish.
2. **A custom resource whose finalizer is never removed**, because the operator was uninstalled before its CRs were deleted, or its cleanup fails (for example, an external load balancer that will not delete due to missing IAM permissions).
3. **A failing admission webhook** that rejects the controller's updates to remove finalizers.

**Diagnose from the namespace status.** The namespace's `status.conditions` state the reason directly: `NamespaceDeletionDiscoveryFailure` (an API group is unavailable), `NamespaceContentRemaining` (objects still exist, with counts by type), and `NamespaceFinalizersRemaining` (which finalizers are pending).

**Resolution order.**

1. Read the conditions and list what remains.
2. Fix the cause: restore the APIService's backing Pods, or delete a stale `APIService` whose service no longer exists; reinstall the operator long enough for it to clean up its CRs; fix the webhook.
3. Only if the controller can never run again, remove the finalizer from the **specific stuck object**, after cleaning up whatever external resource it guarded by hand.
4. Forcing the namespace's own `kubernetes` finalizer through the `/finalize` endpoint is the very last step. It removes the namespace object but can leave orphaned objects in etcd that reappear if a namespace with the same name is created later.

## Example

```bash
# 1. Why is it stuck? The conditions say.
kubectl get ns stuck-namespace -o jsonpath='{range .status.conditions[*]}{.type}: {.message}{"\n"}{end}'

# 2. Unavailable aggregated APIs block discovery
kubectl get apiservice | grep -v True

# 3. What is left inside?
kubectl api-resources --verbs=list --namespaced -o name \
  | xargs -n 1 kubectl get --show-kind --ignore-not-found -n stuck-namespace

# 4. Last resort on one object, after cleaning up its external resource by hand
kubectl patch widgets.example.com my-widget -n stuck-namespace \
  --type=merge -p '{"metadata":{"finalizers":null}}'

# 5. Very last resort: force the namespace finalizer
kubectl get ns stuck-namespace -o json | jq '.spec.finalizers = []' \
  | kubectl replace --raw "/api/v1/namespaces/stuck-namespace/finalize" -f -
```

## Interview tips

- Define the mechanism: delete sets `deletionTimestamp`, controllers do cleanup and remove their own finalizer, the API server deletes when the list is empty.
- Give real finalizers - `pvc-protection`, load-balancer cleanup, `foregroundDeletion` - to show you have met them.
- For a stuck namespace, say "read the namespace conditions" first; they name discovery failures and remaining content.
- Name the classic causes: a dead aggregated APIService, and an operator uninstalled before its custom resources.
- Stress the trade-off of force-removing finalizers: it can orphan load balancers, disks, or DNS records that keep costing money, so clean those up yourself.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does the Kubernetes Controller Pattern implement declarative reconciliation loops?]] (`#622`): [How does the Kubernetes Controller Pattern implement declarative reconciliation loops?](../container-orchestration-advanced/how-does-the-kubernetes-controller-pattern-implement-declarative-reconciliation-loops.md)
- [[What is the difference between client-go Informers, Listers, and Reflector components?]] (`#625`): [What is the difference between client-go Informers, Listers, and Reflector components?](../container-orchestration-advanced/what-is-the-difference-between-client-go-informers-listers-and-reflector-components.md)
- [[What are Kubernetes Admission Webhook failure policies and how do you prevent self-locking outage loops?]] (`#628`): [What are Kubernetes Admission Webhook failure policies and how do you prevent self-locking outage loops?](../container-orchestration-advanced/what-are-kubernetes-admission-webhook-failure-policies-and-how-do-you-prevent-self-locking-outage-loops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
