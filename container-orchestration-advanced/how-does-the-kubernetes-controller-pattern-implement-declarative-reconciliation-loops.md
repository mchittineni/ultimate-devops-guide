---
title: "How does the Kubernetes Controller Pattern implement declarative reconciliation loops?"
id: 622
category: "Container Orchestration Advanced"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - controllers
  - reconciliation
  - architecture
quiz:
  stem: "Why did Kubernetes architect its controllers to be level-triggered rather than edge-triggered?"
  options:
    - "Level-triggered systems consume zero network bandwidth"
    - "Level-triggered controllers inspect current state against desired state on every pass, ensuring self-healing even if intermediate event notifications were missed during network drops"
    - "Edge-triggered controllers cannot run on multi-core processors"
    - "Level-triggered systems do not require etcd storage"
  answer: 2
  explanation: "If a controller relies purely on edge-triggered notifications, a missed network event causes permanent desynchronization. Level-triggered loops inspect current reality vs desired state repeatedly."
---

# How does the Kubernetes Controller Pattern implement declarative reconciliation loops?

**Short answer:** A controller is a loop that watches the API for the objects it owns, compares the declared desired state (`spec`) with the observed actual state, and takes the smallest action that moves reality towards the spec - then reports what it saw in `status`. Kubernetes controllers are **level-triggered**: an event only tells them _which object_ to look at, and the reconcile function always recomputes from current state rather than from the event. That makes them self-healing after missed events, restarts, or partial failures, at the cost of needing every action to be idempotent and safe to repeat.

## Detail

**The loop.**

```text
   watch events (add/update/delete)          periodic resync / requeue
              │                                         │
              ▼                                         ▼
     informer cache  ──enqueue key "ns/name"──>  rate-limited work queue
                                                        │
                                                        ▼
                                     reconcile(key): read desired + actual from cache
                                                        │
                                          diff ──> act via API (create/update/delete)
                                                        │
                                          write status ─┘  (requeue on error, with back-off)
```

1. **Observe.** An informer lists the resource once, then keeps a long-running **watch** open to the API server (an HTTP streaming response of JSON events, not a WebSocket), feeding a local cache. Reads come from the cache, so controllers do not hammer the API server.
2. **Queue.** Event handlers enqueue only the object's key. The work queue de-duplicates keys, so ten rapid changes to one Deployment cause one reconcile, and it rate-limits retries with exponential back-off.
3. **Reconcile.** For a ReplicaSet with `replicas: 5` and three matching Pods, the controller computes `+2` and creates two Pods with an `ownerReference` back to the ReplicaSet. It does not remember what it did last time; it recomputes from the current state each pass.
4. **Report.** It writes `status` (for example `readyReplicas`, conditions, `observedGeneration`) so humans and other controllers can see progress.

**Level-triggered versus edge-triggered.** An edge-triggered system acts on transitions ("a Pod died - create one"); miss the event and the system stays wrong forever. A level-triggered controller acts on the difference between current and desired state; if a Pod died while the controller was restarting, the next reconcile sees four Pods instead of five and fixes it. Periodic resyncs and requeues are a safety net for the same reason.

**Design rules that follow.**

- **Idempotent actions**: reconcile can run many times for the same state; creating "one more Pod" must be based on counting, not on the event.
- **Owner references and garbage collection**: children point at their parent, so deleting the parent cascades without the controller tracking children itself.
- **Finalizers** for cleanup of external resources before an object disappears.
- **One writer per field**: controllers write `status`, users write `spec`; overlapping writers fight (the HPA and a GitOps tool both setting `replicas` is the classic example).
- **Leader election** so only one replica of a controller acts at a time.

**Trade-offs.** Level-triggered reconciliation is eventually consistent: there is always a lag between a change and convergence, and a controller acting on a stale cache can make a decision that the next pass corrects. It is also only as good as its observation - if actual state lives outside Kubernetes (a cloud load balancer, a database), the controller must query it or it will not notice drift.

## Example

```go
// controller-runtime: a level-triggered reconcile for a custom resource
func (r *WidgetReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var w examplev1.Widget
    if err := r.Get(ctx, req.NamespacedName, &w); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err) // deleted: nothing to do
    }

    // Desired: a Deployment with w.Spec.Replicas. Create or update it idempotently.
    dep := &appsv1.Deployment{ObjectMeta: metav1.ObjectMeta{Name: w.Name, Namespace: w.Namespace}}
    _, err := controllerutil.CreateOrUpdate(ctx, r.Client, dep, func() error {
        dep.Spec.Replicas = &w.Spec.Replicas
        // ...selector and template...
        return controllerutil.SetControllerReference(&w, dep, r.Scheme) // GC cascades
    })
    if err != nil {
        return ctrl.Result{}, err // requeued with exponential back-off
    }

    // Report what we observed, not what we hoped
    w.Status.ReadyReplicas = dep.Status.ReadyReplicas
    w.Status.ObservedGeneration = w.Generation
    return ctrl.Result{}, r.Status().Update(ctx, &w)
}
```

## Interview tips

- Describe observe → diff → act → report, and say that events only select which object to reconcile.
- Explain level- versus edge-triggered with the "missed event during a restart" example.
- Name the client-go machinery: informers and their cache, the de-duplicating rate-limited work queue, and resyncs.
- State the design rules: idempotent reconcile, owner references, finalizers, status versus spec ownership.
- Be honest about the trade-off: eventual consistency and reliance on accurate observation of external state.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
