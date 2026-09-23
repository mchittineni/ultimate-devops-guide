---
title: "What is the difference between client-go Informers, Listers, and Reflector components?"
id: 625
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - kubernetes
  - client-go
  - informers
  - controllers
quiz:
  stem: "Why do Kubernetes controllers query objects using client-go Listers rather than making direct GET requests to the Kubernetes API server?"
  options:
    - "Listers bypass Kubernetes RBAC authentication"
    - "Listers read directly from a local in-memory cache synchronized via watches, avoiding API server network roundtrips and protecting etcd from read saturation"
    - "Listers can only run inside the master control plane nodes"
    - "API servers do not support GET requests"
  answer: 2
  explanation: "Direct API server queries would saturate etcd. Listers query a synchronized local in-memory cache maintained by Informers, providing instantaneous lookups with zero cluster load."
---

# What is the difference between client-go Informers, Listers, and Reflector components?

**Short answer:** They are three layers of client-go's caching machinery. The **Reflector** talks to the API server: it lists a resource once, then keeps a watch open from that `resourceVersion` and pushes every change into a `DeltaFIFO` queue. The **Informer** (in practice a `SharedIndexInformer`) pops those deltas, applies them to a thread-safe local cache called the **Indexer**, and calls your event handlers. A **Lister** is a typed, read-only view over that Indexer, so controller code can `Get` and `List` objects from memory instead of the API server. The result is that many controllers can watch the cluster with one list and one watch per resource type, at the cost of memory and of reading data that may be slightly stale.

## Detail

**Why the cache exists.** If every controller issued `GET` and `LIST` calls on each reconcile, API server and etcd load would grow with the number of controllers times the reconcile rate. Informers turn that into one initial list plus a stream of watch events per resource type, shared by every consumer in the process.

```text
API server ──LIST, then WATCH from resourceVersion──> Reflector ──> DeltaFIFO ──> Informer
                                                                                   │
                                                             updates ──> Indexer (cache) <── Lister (typed reads)
                                                                                   │
                                                              calls ──> event handlers ──> enqueue key ──> work queue ──> workers
```

**Reflector.** Performs the list, then a long-lived watch. If the watch breaks it resumes from the last seen `resourceVersion`; if that version is too old (`410 Gone`), it re-lists. Newer Kubernetes versions can serve the initial state as a stream on the watch itself ("watch list"), which avoids building one huge list response in memory. The Reflector knows nothing about your business logic.

**Informer / SharedIndexInformer.** Consumes deltas (`Added`, `Updated`, `Deleted`, `Replaced`, `Sync`), keeps the Indexer consistent, and fans out to registered `ResourceEventHandler`s (`OnAdd`, `OnUpdate`, `OnDelete`). "Shared" means one informer per type per process, created through a `SharedInformerFactory`, even if several controllers need Pods. It also supports **indexes** (for example, Pods by node name) and **transform functions** that strip fields such as `managedFields` before caching to save memory. A periodic resync replays cached objects to handlers so level-triggered controllers re-examine everything.

**Lister.** Generated, typed accessors (`podLister.Pods(ns).Get(name)`, `List(selector)`) over the Indexer. No network call, no API load. Objects returned are shared pointers into the cache - **never mutate them**; deep-copy first.

**Work queue.** Handlers should only enqueue a key (`namespace/name`); workers pop keys, read current state from the Lister, and reconcile. The rate-limited queue de-duplicates keys and retries with back-off.

**Trade-offs and gotchas.**

- **Staleness.** The cache lags the API server slightly, so a controller may act on an old view; writes guarded by `resourceVersion` (409 Conflict) and idempotent reconciles make that safe.
- **Memory.** Caching every Pod in a large cluster costs real memory per process; use label or field selectors, namespace-scoped informers, and transforms.
- **Startup.** Always `WaitForCacheSync` before starting workers, or the first reconciles see an empty cache and may "fix" things that are not broken.
- **Deletes you missed.** If a delete happened while the watch was down, the handler receives a `DeletedFinalStateUnknown` tombstone instead of the object - handle it.

## Example

```go
factory := informers.NewSharedInformerFactory(clientset, 10*time.Minute) // resync period
podInformer := factory.Core().V1().Pods()
podLister := podInformer.Lister()

queue := workqueue.NewTypedRateLimitingQueue(workqueue.DefaultTypedControllerRateLimiter[string]())
podInformer.Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
    AddFunc:    func(obj any) { enqueue(queue, obj) },
    UpdateFunc: func(_, obj any) { enqueue(queue, obj) },
    DeleteFunc: func(obj any) { enqueue(queue, obj) }, // may be a DeletedFinalStateUnknown
})

factory.Start(ctx.Done())
if !cache.WaitForCacheSync(ctx.Done(), podInformer.Informer().HasSynced) {
    log.Fatal("cache never synced")
}

// In a worker: read from memory, never mutate the cached object
pod, err := podLister.Pods("prod").Get("checkout-7d9f8c-x2k9p")
if err == nil {
    p := pod.DeepCopy()
    _ = p // modify the copy, then Update/Patch through the clientset
}
```

## Interview tips

- Give the one-line roles: Reflector lists and watches, Informer maintains the cache and dispatches events, Lister reads the cache.
- Explain the benefit in load terms: one list and one watch per type per process, shared by every controller.
- Mention the work queue and why handlers only enqueue keys.
- Name the gotchas: never mutate cached objects, wait for cache sync, handle tombstones, and watch memory in large clusters.
- Connect to `resourceVersion`: watches resume from it, and `410 Gone` forces a re-list.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
