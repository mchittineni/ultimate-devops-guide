---
title: "What is Cloud Computing?"
id: 21
category: "Cloud Platforms"
difficulty: "Beginner"
tags:
  - devops
  - cloud-platforms
  - interview-questions
---

# What is Cloud Computing?

**Short answer:** Cloud computing is the on-demand delivery of compute, storage, networking, and higher-level services over the internet, billed by consumption, with the provider operating the physical infrastructure.

## Detail

The defining characteristics (as codified by NIST):

- **On-demand self-service** — provision resources through an API without talking to anyone.
- **Broad network access** — reachable over standard protocols from anywhere.
- **Resource pooling** — multi-tenant infrastructure with tenant isolation.
- **Rapid elasticity** — scale out in minutes, scale in when demand falls.
- **Measured service** — metered usage and pay-as-you-go billing.

**Deployment models:** public (AWS, Azure, GCP), private (dedicated to one organisation), hybrid (connected public and private), and multi-cloud (more than one public provider, usually for resilience, negotiating leverage, or regulatory reasons).

The economic shift is from capital expenditure to operating expenditure, and from capacity planned 18 months ahead to capacity adjusted hourly. The engineering shift is bigger: infrastructure becomes an API, which is what makes infrastructure as code, autoscaling, and ephemeral environments possible at all.

The **shared responsibility model** is the concept interviewers probe: the provider secures _of_ the cloud (physical facilities, hypervisor, managed service internals); you secure _in_ the cloud (your data, identity and access management, network configuration, patching of anything you run yourself). The boundary moves depending on the service — with a managed database the provider patches the engine, with EC2 you patch the OS.

## Interview tips

- Name the shared responsibility model explicitly; it is the most-tested cloud concept.
- Cloud is not automatically cheaper — it is elastic. Steady, predictable load can be cheaper on-premises.
- Mention the trade-offs: vendor lock-in, egress costs, and the operational cost of doing it badly.

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
