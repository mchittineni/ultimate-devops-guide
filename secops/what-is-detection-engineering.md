---
title: "What is detection engineering?"
id: 171
category: "SecOps and Threat Detection"
difficulty: "Advanced"
tags:
  - devops
  - secops
  - interview-questions
---

# What is detection engineering?

**Short answer:** Detection engineering applies software engineering discipline to detections: threats are modelled, rules are written as code in version control, validated against real attack telemetry, deployed through CI, and measured in production for precision and coverage. It replaces "enable the vendor's rule pack" with an owned, testable detection portfolio.

## Detail

**The lifecycle:** pick a threat (from a threat model, an incident, or an ATT&CK technique relevant to your stack) → confirm the telemetry exists to see it → write the detection → generate the behaviour in a lab and confirm it fires → tune against 30 days of production data to measure false positives → ship with a playbook → review on a schedule and retire what no longer earns its keep.

**Detect behaviour, not artifacts.** An IP address, a file hash, or a specific tool name is trivially changed by an attacker. `kubectl exec` into a production Pod by an identity that never does that, a service account authenticating from a new ASN, a container spawning a shell - these survive tool changes. This is the "pyramid of pain": the higher up you detect, the more expensive it is for the adversary to adapt.

**Validation is what distinguishes it from rule-writing.** Use Atomic Red Team, Stratus Red Team (cloud-native), or Caldera to execute the technique in a controlled environment and assert the rule fires. Unvalidated rules routinely turn out to reference a field the source does not populate.

**Measure two things.** _Precision_ - of alerts this rule raised, how many were real, tracked per rule so bad rules are visible. _Coverage_ - which techniques you can see at all, usually mapped onto an ATT&CK matrix heat map, with honesty about which gaps are telemetry gaps rather than rule gaps.

**Tuning is not suppression.** Excluding a noisy source wholesale creates a blind spot an attacker can occupy. Prefer narrowing the rule's logic (specific service account plus specific namespace plus expected schedule) and record why.

## Example

```yaml
# Falco: shell spawned inside a container - behavioural, tool-agnostic
- rule: Shell in container
  desc: A shell was executed inside a container, excluding known debug workflows
  condition: >
    spawned_process and container
    and shell_procs
    and not container.image.repository in (allowed_debug_images)
    and not k8s.ns.name = "platform-debug"
  output: >
    Shell in container (user=%user.name container=%container.name
    image=%container.image.repository cmd=%proc.cmdline pod=%k8s.pod.name)
  priority: WARNING
  tags: [container, mitre_execution, T1059]
```

```bash
# Validate it: generate the behaviour, then assert the detection fired
stratus detonate aws.execution.ec2-user-data
```

## Interview tips

- The pyramid-of-pain argument for behavioural over artifact-based detection is the core idea to articulate.
- Naming Atomic Red Team or Stratus Red Team for validation, and per-rule precision tracking, marks real experience.
- Expect: "how do you know what you cannot see?" - ATT&CK coverage mapping, and treating telemetry gaps as platform work.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
