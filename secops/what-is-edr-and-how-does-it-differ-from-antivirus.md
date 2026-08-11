---
title: "What is EDR and how does it differ from antivirus?"
id: 175
category: "SecOps and Threat Detection"
difficulty: "Beginner"
tags:
  - devops
  - secops
  - interview-questions
---

# What is EDR and how does it differ from antivirus?

**Short answer:** Traditional antivirus blocks known-bad files by signature. EDR (Endpoint Detection and Response) continuously records endpoint behaviour - process trees, network connections, file and registry activity - detects suspicious patterns, and gives responders the ability to investigate and act remotely. Antivirus asks "is this file bad?"; EDR asks "is this behaviour bad?" and keeps the evidence either way.

## Detail

| Capability            | Antivirus       | EDR                                                    |
| --------------------- | --------------- | ------------------------------------------------------ |
| Detection basis       | file signatures | behaviour, process lineage, heuristics                 |
| Historical visibility | none            | continuous telemetry, queryable                        |
| Response              | quarantine file | isolate host, kill process, collect artifacts remotely |
| Fileless attacks      | largely blind   | in scope (script interpreters, LOLBins)                |
| Analyst workload      | low             | high - it produces detections to triage                |

**XDR and MDR, briefly.** XDR extends the same idea beyond the endpoint, correlating endpoint, identity, email, and cloud telemetry in one product. MDR is a service: someone else's analysts watch your EDR/XDR around the clock. The distinction matters in interviews because organisations frequently buy EDR and then discover nobody is watching it at 3am.

**On Linux servers and containers, be careful.** Kernel-module agents have caused outages and are a poor fit for container hosts; prefer eBPF-based sensors. In Kubernetes, host-level EDR sees processes but often lacks pod attribution, which is why platform teams pair it with a container-aware runtime sensor (Falco, Tetragon) that maps events to namespace, pod, and image.

**Immutable infrastructure changes the response.** On a cattle host, "isolate and rebuild" is the containment action, and the agent's real value is the telemetry it recorded before you replaced the node. Persistence-focused detections matter less; credential-theft and lateral-movement detections matter more.

**Operational costs to name honestly:** agent CPU and memory overhead, kernel compatibility testing in your image pipeline, telemetry egress and retention cost, and the analyst time to triage what it finds. An unmonitored EDR is a compliance checkbox, not a control.

## Interview tips

- The signature-versus-behaviour one-liner is the answer; add "and it retains telemetry for investigation".
- Mention eBPF sensors and container attribution - it shows you have deployed this on modern infrastructure, not just laptops.
- Expect: "do you need EDR if hosts are immutable and short-lived?" - yes for detection and forensics, but response shifts to rebuild.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[What is Docker Compose?]] (`#9`): [What is Docker Compose?](../docker/what-is-docker-compose.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
