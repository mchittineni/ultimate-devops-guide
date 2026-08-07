---
title: "What is Infrastructure Automation?"
id: 86
category: "DevOps Tools and Automation"
difficulty: "Beginner"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
---

# What is Infrastructure Automation?

**Short answer:** Infrastructure automation is the use of code and tooling to provision, configure, scale, and repair infrastructure without manual intervention - covering everything from creating a VPC to rotating credentials and replacing failed nodes.

## Detail

**The layers**

- **Provisioning** - Terraform, CloudFormation, Pulumi, Crossplane create the resources.
- **Configuration** - Ansible, Puppet, or image baking with Packer bring them to a desired state.
- **Orchestration** - Kubernetes schedules and supervises workloads.
- **Deployment** - CI/CD pipelines and GitOps controllers ship application changes.
- **Operations** - autoscaling, automated patching, certificate rotation, backup jobs, and self-healing controllers.

**Why it matters beyond speed.** Manual change is the largest single source of production incidents. Automation makes change reviewable (a pull request), reversible (a revert), and consistent (the same code produced every environment). It also makes the system's design legible - the repository _is_ the documentation.

**Maturity progression:** manual → scripted → declarative and version-controlled → self-service (developers provision through a platform without tickets) → fully autonomous (the system detects and corrects its own drift and failures).

**What to automate first:** whatever is done most often, is riskiest by hand, or blocks other people. Environment creation, deployment, and certificate renewal usually top that list.

**Guardrails matter as much as automation.** Automated change with no policy checks propagates a mistake faster than a human could. Pair automation with plan review, policy as code, staged rollout, and the ability to revert.

## Interview tips

- Frame it as making change safe and reviewable, not merely fast.
- The maturity ladder is a useful structure for an open-ended question.
- Name the risk - automation scales mistakes too - and the guardrails you use.

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
