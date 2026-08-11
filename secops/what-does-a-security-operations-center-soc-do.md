---
title: "What does a Security Operations Center (SOC) do?"
id: 169
category: "SecOps and Threat Detection"
difficulty: "Beginner"
tags:
  - devops
  - secops
  - interview-questions
---

# What does a Security Operations Center (SOC) do?

**Short answer:** A SOC is the function that monitors, detects, triages, and responds to security events across an organisation. In practice it runs a tiered queue - automated detections feed analysts who validate and enrich, escalate real incidents to responders, and feed every closed case back into better detections.

## Detail

**The tiers, and what they exist to protect.** Tier 1 triages alerts against a playbook and closes the noise. Tier 2 investigates what survives, pivoting across data sources to establish scope. Tier 3 (threat hunting and detection engineering) looks for what no alert fired on, and writes the detection so it fires next time. The tiering exists so that expensive expertise is not consumed by password-reset alerts - and modern SOCs push Tier 1 work into automation rather than into people.

**The metrics that matter:** mean time to detect, mean time to triage, mean time to contain, false-positive rate per detection rule, and detection coverage against a framework such as MITRE ATT&CK. "Alerts closed per analyst" is a metric that rewards closing tickets without investigating.

**Build, buy, or hybrid.** A 24/7 in-house SOC needs roughly 8–12 analysts to cover the rota sustainably, which is out of reach for most organisations. Common shape: an MDR provider covers nights and weekends against your telemetry, while an internal team owns detection engineering, cloud-specific context, and response decisions - because an external provider cannot authorise taking your payment service offline.

**Where DevOps meets the SOC.** The SOC depends on telemetry your platform produces: audit logs from the cloud control plane and Kubernetes API, flow logs, identity provider logs, endpoint agents, and application logs with usable correlation IDs. If a service ships no audit trail, it is invisible to detection - which makes log coverage a platform requirement, not a security wish.

**Alert fatigue is the failure mode.** A queue no one can clear is functionally the same as no SOC. Tune or delete rules that produce mostly false positives, and treat "this detection is unactionable" as a valid reason to remove it.

## Interview tips

- Describe the tiers and the escalation path - vague "monitors for threats" answers land poorly.
- Naming MTTD/MTTC and detection coverage shows you think about SOC effectiveness, not just staffing.
- Good follow-up to be ready for: "what telemetry would you onboard first?" - identity provider and cloud audit logs, because almost every cloud incident is visible there.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
