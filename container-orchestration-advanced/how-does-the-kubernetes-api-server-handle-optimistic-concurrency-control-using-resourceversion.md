---
title: "How does the Kubernetes API server handle optimistic concurrency control using resourceVersion?"
id: 624
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - kubernetes
  - etcd
  - concurrency
  - api-server
quiz:
  stem: "What error status code does the Kubernetes API server return when two clients attempt to update the same resource concurrently with conflicting `resourceVersion` values?"
  options:
    - "HTTP 404 Not Found"
    - "HTTP 409 Conflict"
    - "HTTP 502 Bad Gateway"
    - "HTTP 301 Moved Permanently"
  answer: 2
  explanation: "The API server enforces optimistic concurrency control. Submitting an update with a stale `resourceVersion` is rejected with HTTP 409 Conflict, requiring the client to re-fetch and retry."
---

# How does the Kubernetes API server handle optimistic concurrency control using resourceVersion?

**Short answer:** Every object carries `metadata.resourceVersion`, which the API server derives from etcd's revision for the key's last modification. An update (`PUT`) must send the `resourceVersion` it read; the API server turns that into an etcd compare-and-swap transaction, and if anyone else has written the object in between, the write is rejected with **HTTP 409 Conflict** and the client must re-read, re-apply its change, and retry. No locks are held, so readers and writers never block each other - the cost is that busy objects produce conflicts clients must handle.

## Detail

**The lost-update problem.** Two controllers read Pod `foo`, both with labels `env: prod`. A adds `tier: frontend` and writes the whole object; B adds `version: v2` and writes the whole object. Without concurrency control, B's write silently erases A's label.

**How `resourceVersion` prevents it.**

1. A reads `foo` with `resourceVersion: "10542"` and sends an update carrying `"10542"`.
2. The API server issues an etcd transaction: "write only if the key's mod revision is still 10542". It succeeds; the object now has a new, higher `resourceVersion`.
3. B's update also carries `"10542"`. The transaction's comparison fails and the API server returns `409 Conflict`: `Operation cannot be fulfilled on pods "foo": the object has been modified; please apply your changes to the latest version and try again`.
4. B re-reads, reapplies its change to the fresh object, and retries - client-go wraps this in `retry.RetryOnConflict`.

**Rules worth knowing.**

- `resourceVersion` is **opaque**. Clients may compare two values for equality but must not parse it or assume ordering; etcd revisions are an implementation detail.
- An update that omits `resourceVersion` is an unconditional overwrite for most resources - which is exactly the lost-update risk.
- **Patches avoid most conflicts.** JSON merge patch and strategic merge patch are applied by the server to the latest version, so a patch that touches only its own fields does not need `resourceVersion` (you can include it to make the patch conditional).
- **Server-side apply** adds field ownership on top: each field records its manager, and a conflict is reported when you try to change a field another manager owns, unless you `--force-conflicts`. That is a different, field-level 409 from the whole-object `resourceVersion` conflict.
- `resourceVersion` also anchors **list and watch**: a watch resumes from a given version, and a version older than the watch cache or etcd compaction window returns `410 Gone`, forcing the client to re-list. Informers handle this automatically.
- `metadata.generation` is different: it increments only on spec changes and pairs with `status.observedGeneration` so controllers can report which spec they have acted on.

**Trade-offs.** Optimistic concurrency scales well because nothing is locked, but hot objects (a shared ConfigMap, a busy status field) generate conflict storms. The mitigations are patches instead of full updates, splitting status writes into the `status` subresource, and designing controllers so that retrying is cheap and idempotent.

## Example

```bash
kubectl get pod foo -o jsonpath='{.metadata.resourceVersion}{"\n"}'     # e.g. 10542

# Conditional replace: fails with 409 if someone else wrote after 10542
kubectl get pod foo -o json | jq '.metadata.labels.tier = "frontend"' > foo.json
kubectl replace -f foo.json
# Error from server (Conflict): Operation cannot be fulfilled on pods "foo": the object has been modified

# A patch touching only its own field does not need the version
kubectl patch pod foo --type=merge -p '{"metadata":{"labels":{"version":"v2"}}}'
```

```go
// client-go: re-read and retry on 409
err := retry.RetryOnConflict(retry.DefaultRetry, func() error {
    cm, err := client.CoreV1().ConfigMaps("prod").Get(ctx, "app-config", metav1.GetOptions{})
    if err != nil {
        return err
    }
    cm.Data["feature"] = "on"
    _, err = client.CoreV1().ConfigMaps("prod").Update(ctx, cm, metav1.UpdateOptions{})
    return err // a Conflict error triggers another attempt with a fresh read
})
```

## Interview tips

- Describe it as compare-and-swap: the `resourceVersion` you read must still be current when you write, or you get 409 Conflict.
- Say that `resourceVersion` is opaque and must not be parsed or ordered by clients.
- Contrast full updates with patches and server-side apply - patches sidestep most conflicts, and SSA adds field-level ownership conflicts.
- Mention `retry.RetryOnConflict` and that controllers must be idempotent because retries are normal.
- Connect it to watches: resuming from a `resourceVersion`, and `410 Gone` when it has been compacted.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
