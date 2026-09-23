---
title: "What are WebAssembly (Wasm) and WASI and what role do they play alongside containers in cloud computing?"
id: 698
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - wasm
  - wasi
  - webassembly
  - cloud-native
  - containers
quiz:
  stem: "What is the primary operational performance advantage of WebAssembly (Wasm) micro-modules over traditional Linux container images for edge computing?"
  options:
    - "Wasm modules can only be written in Python"
    - "Wasm modules execute inside secure memory sandboxes with sub-millisecond startup times and kilobyte memory footprints, eliminating container cold starts"
    - "Wasm requires hardware virtualization hypervisors"
    - "Wasm modules cannot communicate over networks"
  answer: 2
  explanation: "Because Wasm does not require initializing Linux namespaces, cgroups, or virtual filesystems, it boots in microseconds with minimal RAM, making it optimal for event-driven edge workloads."
---

# What are WebAssembly (Wasm) and WASI and what role do they play alongside containers in cloud computing?

**Short answer:** WebAssembly is a portable, sandboxed bytecode format; WASI (the WebAssembly System Interface) gives Wasm modules controlled access to things like files, clocks, and sockets through explicitly granted capabilities. Outside the browser, Wasm offers very fast start-up (typically milliseconds or less), small artefacts, and one binary for every CPU architecture - which makes it attractive for edge functions, plugins, and short-lived serverless handlers. It complements rather than replaces containers: the ecosystem, language support, and system-interface coverage are still narrower than Linux.

## Detail

**How it differs from a container**

| Dimension     | Linux container (OCI)                                 | Wasm module (+ WASI)                                                |
| ------------- | ----------------------------------------------------- | ------------------------------------------------------------------- |
| Isolation     | Kernel namespaces and cgroups; shares the host kernel | Language-level sandbox inside a runtime process; no kernel access   |
| Start-up      | Tens to hundreds of milliseconds (plus image pull)    | Typically sub-millisecond to a few milliseconds                     |
| Artefact size | Megabytes to gigabytes                                | Kilobytes to a few megabytes                                        |
| Portability   | Per CPU architecture (multi-arch images)              | One binary for x86, Arm, and others                                 |
| System access | Full POSIX inside the container                       | Nothing by default; capabilities granted explicitly                 |
| Ecosystem     | Any Linux software                                    | Languages with good Wasm targets (Rust, Go, C/C++, others maturing) |

**WASI versions.** WASI Preview 1 was a POSIX-like set of calls. WASI 0.2 (Preview 2) is built on the **Component Model**: modules declare typed interfaces in WIT, can be composed with components written in other languages, and gain standard interfaces such as `wasi:http` and `wasi:sockets`. Tooling support for 0.2 differs between runtimes, so check what your runtime and language toolchain implement.

**Where it runs in cloud-native stacks**

- **Edge and serverless platforms** - Cloudflare Workers (V8 isolates, which also run Wasm), Fastly Compute, Fermyon/Spin-based platforms: per-request isolation with negligible cold start.
- **Kubernetes** - containerd shims from the `runwasi` project (for example for Spin or WasmEdge) let a node run Wasm workloads; a `RuntimeClass` selects the shim, and the Wasm artefact is distributed as an OCI image. SpinKube packages this for clusters.
- **Plugins and extensions** - Envoy and Istio Wasm filters, database UDFs, and policy engines use Wasm to run untrusted extension code safely in-process.

**Limitations:** threads, networking, and GPU access are still maturing; debugging and profiling tools lag behind native; many existing libraries assume a full OS; and a Wasm sandbox protects the host from the module but not the module from its own logic bugs.

The often-quoted Solomon Hykes remark (that Docker might not have been needed if Wasm and WASI had existed in 2008) is about isolation and portability, and he later clarified he expected the two to coexist - which is how it has played out.

## Example

```yaml
# Kubernetes: schedule a Wasm workload through a runwasi-based containerd shim
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: wasmtime-spin
handler: spin # must match the shim configured in containerd on the node
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-wasm
spec:
  replicas: 2
  selector: { matchLabels: { app: hello-wasm } }
  template:
    metadata: { labels: { app: hello-wasm } }
    spec:
      runtimeClassName: wasmtime-spin
      containers:
        - name: hello
          image: ghcr.io/example/hello-spin:1.0.0 # OCI artefact containing the .wasm component
          command: ["/"]
```

## Interview tips

- Frame Wasm as a complement to containers: best where start-up time, density, or sandboxing untrusted code matter.
- Explain the capability model - a WASI module gets no filesystem or network access unless the host grants it - rather than only saying "it is sandboxed".
- Mention the Component Model and WASI 0.2 to show you know where the standard is heading, and be honest that support varies by runtime.
- Name the practical limits: library and language coverage, threads and networking maturity, and debugging tools.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
