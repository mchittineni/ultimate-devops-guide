---
title: "What is OpenTelemetry Context Leaking and how do you prevent thread-local context pollution in asynchronous runtimes?"
id: 702
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - observability
  - opentelemetry
  - tracing
  - threading
  - context
quiz:
  stem: "Why does failing to close an OpenTelemetry `Scope` in a Java thread pool application cause distributed traces to display corrupted, cross-tenant data?"
  options:
    - "The OpenTelemetry Collector crashes on memory overflow"
    - "The thread returns to the pool with the old Span still attached to ThreadLocal storage, causing the next unrelated request on that thread to inherit the old TraceID"
    - "Prometheus metrics stop collecting CPU counters"
    - "The Java Virtual Machine deletes the application bytecode"
  answer: 2
  explanation: "If a ThreadLocal span scope is not closed in a `finally` block, reused worker threads retain the old context, contaminating subsequent requests with stale TraceIDs."
---

# What is OpenTelemetry Context Leaking and how do you prevent thread-local context pollution in asynchronous runtimes?

**Short answer:** OpenTelemetry keeps the "current span" in an implicit context - a `ThreadLocal` in Java, `contextvars` in Python, `AsyncLocalStorage` in Node.js. Context leaks when code makes a span current and never restores the previous context, so a pooled thread carries request A's span into request B; the opposite failure, context **loss**, happens when work hops to another thread or callback without the context. The fix is always to scope context with language constructs (`try`-with-resources, `with`, `context.with`) and to propagate it explicitly across executors, rather than relying on luck.

## Detail

**How the leak happens (Java)**

1. A worker thread handles request A and calls `span.makeCurrent()`, which stores A's context in a `ThreadLocal` and returns a `Scope`.
2. The code never calls `scope.close()` - an early return, an exception path, or a scope opened in one callback and never closed.
3. The thread goes back to the pool still holding A's context.
4. Request B runs on the same thread; any span it starts without an explicit parent becomes a child of A. Traces merge across unrelated requests, latency trees become nonsense, and attributes such as tenant ID or user ID can appear under the wrong request - a real data-handling problem, not only a cosmetic one.

**How context gets lost instead.** Submitting a `Runnable` to an `ExecutorService`, using `CompletableFuture.supplyAsync`, or running a callback on another event-loop tick starts the work with whatever context that thread has - usually none. The child span becomes a new root, and the trace breaks in two.

**Prevention**

- **Always scope.** `try (Scope s = span.makeCurrent()) { ... }` in Java, `with tracer.start_as_current_span(...)` in Python, `context.with(ctx, fn)` or `tracer.startActiveSpan(name, fn)` in Node.js. Never call `makeCurrent()` without a guaranteed `close()`.
- **End spans separately.** Closing the `Scope` restores context; `span.end()` records the span. Both are needed, typically `end()` in a `finally`.
- **Wrap executors.** `Context.taskWrapping(executor)` or `Context.current().wrap(runnable)` in Java carries context into pooled threads explicitly.
- **Prefer the auto-instrumentation agent** for common frameworks and thread pools - the Java agent instruments executors, reactive libraries, and servlet containers so propagation and cleanup are handled correctly.
- **Use the runtime's async-aware storage.** Python `contextvars` and Node.js `AsyncLocalStorage` follow the logical async flow rather than the OS thread; OpenTelemetry's Python and Node SDKs are built on them.
- **Test for it.** A leak detector in tests (the Java SDK's `StrictContextStorage` fails when a scope is not closed or is closed on the wrong thread) catches most of these before production.

**Trade-off.** Implicit context is convenient because instrumentation does not need to thread a context parameter through every call; the price is exactly this class of bug. Frameworks with explicit context (Go's `context.Context`) avoid leaks but need discipline to pass the context everywhere.

## Example

```java
// Correct: context restored on every path, span always ended, executor propagates context
Span span = tracer.spanBuilder("charge-card").startSpan();
try (Scope scope = span.makeCurrent()) {
    ExecutorService pool = Context.taskWrapping(Executors.newFixedThreadPool(8));
    Future<Receipt> f = pool.submit(() -> payments.charge(order)); // child of charge-card
    return f.get(2, TimeUnit.SECONDS);
} catch (Exception e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR);
    throw e;
} finally {
    span.end(); // scope already closed by try-with-resources
}
```

```bash
# Fail tests on leaked or mis-closed scopes (Java SDK testing utility)
java -Dio.opentelemetry.context.enableStrictContext=true -jar app-tests.jar
```

## Interview tips

- Distinguish **leak** (stale context carried into the next request) from **loss** (context missing after an async hop) - both come from the same implicit-context design.
- Say that `Scope` restores context and `span.end()` records the span; mixing them up is a common source of leaks.
- Mention executor wrapping and the auto-instrumentation agent as the practical fixes, and strict context storage in tests as the guard.
- Point out the privacy angle: leaked context can attach one tenant's attributes to another's trace.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
