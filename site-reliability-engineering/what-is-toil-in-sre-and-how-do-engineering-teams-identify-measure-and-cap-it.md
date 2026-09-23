---
title: "What is Toil in SRE and how do engineering teams identify, measure, and cap it?"
id: 643
category: "Site Reliability Engineering (SRE)"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - sre
  - toil
  - automation
  - google-sre
quiz:
  stem: "According to Google SRE guidelines, which of the following activities qualifies as 'Toil'?"
  options:
    - "Writing a Terraform module to automate VPC creation"
    - "Conducting a blameless post-mortem analysis"
    - "Manually executing an SSH script every morning to clean up disk space on servers"
    - "Designing a multi-region failover architecture"
  answer: 3
  explanation: "Toil is manual, repetitive, automatable, and scales with service growth. Manually SSHing into servers to delete logs produces no enduring value and should be automated."
---

# What is Toil in SRE and how do engineering teams identify, measure, and cap it?

**Short answer:** Toil is work that is repetitive, manual, tactical, lacks enduring value, and scales linearly as the service grows (e.g. manual user resets, certificate installs); Google SRE mandates that engineering teams spend at most 50% of their time on toil, reserving 50%+ for engineering project work.

## Detail

Not all administrative work is toil. Writing code to automate onboarding is engineering; manually clicking buttons to onboard 50 users every Monday is toil.

### Characteristics of Toil

1. **Manual**: Running commands by hand.
2. **Repetitive**: Doing the exact same task repeatedly.
3. **Automatable**: Tasks that could be accomplished by a script or software agent.
4. **Tactical & Lacks Enduring Value**: Once finished, the service is not permanently improved.
5. **Scales Linearly**: If traffic doubles, toil tasks double.

### The 50% Rule

- SRE teams must cap toil at **50% of their time**.
- The remaining **50%+ must be dedicated to pure engineering** (building automation, architectural improvements, reliability tooling).
- If toil exceeds 50%, excess operational work is shifted back to the product development team, creating an incentive for product teams to build self-service and stability.

### Measuring It

Toil is invisible until it is counted. Tag tickets and pages as toil, run a periodic time survey (hours per person per week), and track the trend rather than a single snapshot. Prioritise automation by frequency x duration x people affected. The trade-off: automation itself has a build and maintenance cost, so a task done twice a year for ten minutes is usually cheaper to leave manual and well documented.

## Example

```text
Quarterly toil review - platform team (6 engineers, ~240 h/week)

Task                              Freq/week  Mins  Hours/week  Action
Manual TLS certificate renewals        12     20       4.0     cert-manager (this quarter)
Access requests to prod namespaces     30     10       5.0     self-service via IdP groups
Restarting stuck consumer pods          8     15       2.0     fix root cause (offset bug)
Disk clean-up on build agents          10     15       2.5     ephemeral runners
Total measured toil                                    ~55 h   = 23% of capacity (cap 50%)
```

## Interview tips

- Definition: manual, repetitive, automatable, lacks enduring value, scales linearly.
- Distinguishing toil from engineering work.
- The 50% toil cap rule.
- Routing excess operational toil back to development teams to incentivize automation.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?]] (`#675`): [What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?](../incident-management/what-are-incident-severity-levels-sev-1-to-sev-4-and-how-do-they-govern-response-slas-and-war-rooms.md)
- [[What are Automated Remediation and Self-Healing systems and when should automation halt?]] (`#679`): [What are Automated Remediation and Self-Healing systems and when should automation halt?](../incident-management/what-are-automated-remediation-and-self-healing-systems-and-when-should-automation-halt.md)
- [[How do you choose an SLO target?]] (`#177`): [How do you choose an SLO target?](../slo-engineering/how-do-you-choose-an-slo-target.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
