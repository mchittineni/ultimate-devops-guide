---
title: "What is the MITRE ATT&CK framework?"
id: 172
category: "SecOps and Threat Detection"
difficulty: "Intermediate"
tags:
  - devops
  - secops
  - interview-questions
---

# What is the MITRE ATT&CK framework?

**Short answer:** ATT&CK is a curated knowledge base of adversary behaviour, organised as tactics (the attacker's goal — initial access, persistence, exfiltration) and techniques (how the goal is achieved), observed in real intrusions. Teams use it as a shared vocabulary and, more practically, as a coverage map: which techniques can we detect, and where are the gaps?

## Detail

**Tactic versus technique versus procedure.** Tactic = why (Persistence). Technique = how, in general (T1098 Account Manipulation). Sub-technique = a specific variant (T1098.001 Additional Cloud Credentials). Procedure = how a particular group actually did it. Detections map to techniques; playbooks map to tactics.

**Matrices to know:** Enterprise (with Cloud, Containers, and Identity Provider platforms — the relevant ones for DevOps), Mobile, and ICS. The Containers matrix covers exactly what a Kubernetes platform team is asked about: escape to host, deploy container, hijack compute resources.

**How teams actually use it:**

- **Coverage heat map** — colour each technique by detection confidence. Honest maps have large grey areas; maps that are entirely green are usually self-assessed generously.
- **Detection metadata** — tag every rule with its technique so coverage is derived from the rule set rather than maintained by hand.
- **Purple-team planning** — pick techniques a relevant threat group is known to use, emulate them, and check what fired.
- **Post-incident review** — reconstruct the intrusion as a technique chain, then ask which link should have been detected.

**Its limits.** ATT&CK describes post-compromise behaviour, so it is a poor fit for vulnerability management or for business-logic abuse. Techniques vary enormously in detectability, which makes raw "we cover 60% of techniques" close to meaningless — weight by relevance to your environment and by what your telemetry can actually see.

**Related models.** The Cyber Kill Chain is coarser and more linear; D3FEND catalogues defensive countermeasures and pairs well with ATT&CK when you are choosing what to build next.

## Example

```text
Cloud intrusion mapped to ATT&CK — each step is a detection opportunity

T1078.004  Valid Accounts: Cloud Accounts     ← leaked CI access key used from new ASN
T1098.001  Additional Cloud Credentials       ← attacker creates a second access key
T1580      Cloud Infrastructure Discovery     ← burst of Describe*/List* API calls
T1525      Implant Internal Image             ← poisoned image pushed to the registry
T1530      Data from Cloud Storage Object     ← mass GetObject on a data bucket
```

## Interview tips

- Get tactic/technique/procedure straight — mixing them up is the most common slip.
- Mention the Containers and Identity Provider matrices; it shows you have looked past the generic Enterprise view.
- Be honest about the coverage-percentage trap: weighted, telemetry-aware coverage beats a green heat map.

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
