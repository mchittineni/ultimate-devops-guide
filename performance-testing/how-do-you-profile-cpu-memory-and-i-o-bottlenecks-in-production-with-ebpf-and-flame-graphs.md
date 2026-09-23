---
title: "How do you profile CPU, memory, and I/O bottlenecks in production with eBPF and flame graphs?"
id: 614
category: "Performance Testing"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - performance-testing
  - ebpf
  - profiling
  - flame-graphs
  - performance
  - bcc
quiz:
  stem: "What does a wide horizontal plateau at the very top of a CPU Flame Graph indicate?"
  options:
    - "The application has entered a deadlocked state"
    - "A specific function is consuming a large percentage of total CPU time directly on the processor without delegating to child functions"
    - "The network socket buffer has overflowed"
    - "The function was compiled without optimization flags"
  answer: 2
  explanation: "On a Flame Graph, width corresponds directly to CPU time. A wide box with nothing on top of it means that specific leaf function is directly burning CPU cycles."
---

# How do you profile CPU, memory, and I/O bottlenecks in production with eBPF and flame graphs?

**Short answer:** eBPF (originally "extended Berkeley Packet Filter", now just a name) runs verified, sandboxed programs inside the Linux kernel to sample CPU stack traces and trace I/O and memory events with typically around 1% overhead at a low sampling rate; Flame Graphs visualize sampled call stacks where horizontal width represents relative CPU time spent.

## Detail

Instrumenting profilers (like Python `cProfile`, or JVM agents that wrap every method) can add tens of percent overhead and alter runtime behaviour (the observer effect). Sampling in the kernel with eBPF costs little enough to run continuously in production, and needs no code change or restart.

### How eBPF Profiling Operates

1. An eBPF program hooks into kernel tracepoints or hardware performance counters (e.g. sampling CPU instruction pointers at 99Hz).
2. It captures kernel and user-space call stacks directly in kernel memory buffers.
3. Userspace tools (bpftrace, BCC, Parca, Grafana Pyroscope, the OpenTelemetry eBPF profiler) aggregate the stack traces into folded format or a profile store.

### Beyond CPU

- **Off-CPU time** (`offcputime`): where threads block - locks, I/O, sleeps. A service that is slow but not busy shows nothing on a CPU flame graph.
- **Disk I/O** (`biolatency`, `biosnoop`): per-request block I/O latency histograms.
- **Memory** (`memleak`, page-fault tracing): outstanding allocations by stack, useful for leaks.

**Limitations.** Stack walking needs frame pointers or unwind tables - binaries built with `-fomit-frame-pointer` produce broken stacks unless the profiler supports DWARF/`.eh_frame` unwinding. JIT and interpreted runtimes (JVM, Node.js, Python) need symbol maps or runtime-aware profilers to show function names. And eBPF needs a reasonably recent kernel (BTF/CO-RE for portable tools) plus root or `CAP_BPF`/`CAP_PERFMON`.

### Reading a Flame Graph

- **X-axis**: Not time - frames are sorted alphabetically to merge identical stacks (width is proportional to the percentage of time spent in that function and its children). **Wider boxes = more CPU consumption**.
- **Y-axis**: Call stack depth (bottom is root, top is the executing function).
- Look for **wide plateaus at the top of the flame**: these represent leaf functions consuming substantial CPU without calling other functions (the primary optimization targets).

## Example

Sample all CPUs at 99 Hz for 30 seconds and render a flame graph with Brendan Gregg's FlameGraph scripts:

```bash
# bpftrace: count kernel+user stacks per process
sudo bpftrace -e 'profile:hz:99 { @[kstack, ustack, comm] = count(); }
  interval:s:30 { exit(); }' > stacks.bt

git clone https://github.com/brendangregg/FlameGraph
./FlameGraph/stackcollapse-bpftrace.pl stacks.bt > stacks.folded
./FlameGraph/flamegraph.pl stacks.folded > cpu.svg     # open in a browser

# Off-CPU and disk latency with BCC tools (package names vary: bpfcc-tools, bcc-tools)
sudo offcputime-bpfcc -f 30 > offcpu.folded
sudo biolatency-bpfcc 10 1
```

## Interview tips

- eBPF executing in-kernel for sub-1% overhead production tracing.
- Flame graph axes: width = CPU time percentage; height = call stack depth.
- Wide plateaus on top identifying CPU hog functions.
- Tools: BCC, bpftrace, Parca, Brendan Gregg's FlameGraph toolkit.
- Mention off-CPU analysis: a slow service waiting on locks or I/O looks idle on a CPU flame graph.
- Name the frame-pointer problem and symbolisation for JIT runtimes - it is the usual reason a first flame graph is useless.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How does Docker BuildKit work and what caching and build features does it unlock?]] (`#515`): [How does Docker BuildKit work and what caching and build features does it unlock?](../docker/how-does-docker-buildkit-work-and-what-caching-and-build-features-does-it-unlock.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
