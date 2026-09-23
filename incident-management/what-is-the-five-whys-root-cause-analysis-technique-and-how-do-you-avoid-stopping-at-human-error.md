---
title: "What is the Five Whys root cause analysis technique and how do you avoid stopping at human error?"
id: 678
category: "Incident Management"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - incident-management
  - five-whys
  - root-cause
  - post-mortem
quiz:
  stem: "In an effective Five Whys root-cause investigation, why is concluding that 'the operator made a human error' considered a failure of the analysis?"
  options:
    - "Because human operators are legally immune from blame"
    - "Human error is a symptom of poor system design; the analysis must discover why the system permitted a single human mistake to cause catastrophic failure without guardrails"
    - "The Five Whys technique can only be applied to computer hardware"
    - "Software systems never involve human operators"
  answer: 2
  explanation: "Resilient systems must tolerate human error. An investigation that blames the human fails to address why automated guardrails, permissions, or validation checks were missing."
---

# What is the Five Whys root cause analysis technique and how do you avoid stopping at human error?

**Short answer:** The Five Whys is an iterative interrogative technique that asks 'Why?' repeatedly to peel away superficial symptoms and identify underlying systemic and process failures, ensuring the investigation does not stop at superficial 'human error'.

## Detail

Originated by Sakichi Toyoda and popularised through Taiichi Ohno's Toyota Production System, the Five Whys prevents superficial incident conclusions by repeatedly asking why the previous answer was possible. "Five" is a rule of thumb - stop when you reach something the organisation can change, not at a fixed count.

### The Golden Rule

If your Five Whys ends in **'The engineer made a mistake'**, your analysis failed.
A resilient system must be designed so that a single human mistake cannot crash production. Ask instead: why did the action seem reasonable at the time, and why did the system allow it with no guardrail or warning?

### Limitations

A single chain of whys implies one linear root cause, but real incidents have several contributing factors. Ask "why?" down **each branch** (here: why the export was manual, _and_ why the disk filled with no alert), and treat the result as a set of contributing factors. Different investigators also produce different chains from the same facts, which is why modern practice (e.g. Learning from Incidents approaches) uses the Five Whys as a prompt inside a broader, blameless review rather than as the whole method.

## Example

```text
Incident: production database went down

Branch A - why was the export needed?
  Why 1  Production went down.        -> The primary database ran out of disk space.
  Why 2  Why did it run out of space? -> A 500 GB export file was written to the data volume.
  Why 3  Why was it written there?    -> An engineer ran a manual export script whose default
                                         output path was the current directory (/var/lib/postgresql).
  Why 4  Why a manual export in prod? -> Marketing needed anonymised statistics and there was
                                         no self-service reporting path.
  Why 5  Why no self-service path?    -> Analytics requests were never prioritised on any roadmap.
  Fix    Read-replica-backed reporting tool; export script refuses to write to data volumes.

Branch B - why did a filling disk become an outage?
  Why 1  Why no warning?              -> No filesystem alert on the database data volume.
  Why 2  Why not?                     -> The monitoring template only covered the root partition.
  Fix    Predictive disk-fill alert on every volume; separate volume for ad-hoc files.

NOT a conclusion: "the engineer should have specified an output path".
```

## Interview tips

- Iterative questioning to drill past symptoms to systemic causes.
- Never stopping at 'human error' (human error is a symptom, not root cause).
- Uncovering missing automated guardrails, tooling gaps, and monitoring blind spots.
- Originated from the Toyota Production System.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
