---
title: "What is Infrastructure Drift?"
id: 160
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Infrastructure Drift?

**Short answer:** Infrastructure drift is divergence between the infrastructure described in code and the infrastructure actually running - usually caused by manual changes, external automation, or failed applies - undermining reproducibility and hiding risk.

## Detail

**Causes**

- Emergency manual changes during an incident that are never back-ported to code.
- Console changes made because they were faster than a pull request.
- Other automation (autoscalers, cloud services, security tooling) modifying resources.
- Partially failed applies leaving resources half-configured.
- Provider-side defaults that change between versions.

**Why it matters.** Drift means your code no longer describes reality, so a future apply may revert a critical fix or destroy something unexpected. Disaster recovery rebuilds produce a subtly different environment. Security posture becomes unverifiable - the code says the bucket is private, the console says otherwise.

**Detection**

- `terraform plan` on a schedule in CI, alerting when a non-empty diff appears against unchanged code. This is the simplest effective control.
- Purpose-built tools: `driftctl`, Terraform Cloud drift detection, or provider-native services such as AWS Config and CloudFormation drift detection.
- GitOps controllers detect drift continuously by design, and Argo CD reports resources as `OutOfSync`.

**Prevention and remediation**

- Remove or tightly restrict console write access in production; make the pipeline the only path.
- Automatic reconciliation where it is safe - Argo CD's `selfHeal`, or a scheduled re-apply.
- Use `ignore_changes` deliberately for fields legitimately managed elsewhere (autoscaled desired counts, tags applied by other systems).
- Import genuinely-needed manual changes back into code (`terraform import`) rather than reverting blindly.
- A break-glass process for emergencies that includes a mandatory follow-up to reconcile code with reality.

## Example

```bash
# Scheduled drift check - fails CI when live infrastructure diverges from code
terraform plan -detailed-exitcode -lock=false
# exit 0 = no drift, 2 = drift detected, 1 = error
```

## Interview tips

- `-detailed-exitcode` on a schedule is a concrete, immediately usable answer.
- Emphasise process alongside tooling: break-glass access with mandatory reconciliation afterwards.
- Note that automatic reconciliation is not always safe - reverting a fix during an incident is a real risk.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
