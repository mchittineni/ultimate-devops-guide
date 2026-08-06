---
title: "Compare different Configuration Management tools"
id: 55
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
---

# Compare different Configuration Management tools

**Short answer:** Ansible is agentless, YAML-based, and easiest to adopt; Puppet is declarative, agent-based, and strongest at continuous enforcement and compliance; Chef is Ruby-based with the best testing story; Salt is fastest at scale with event-driven automation.

## Detail

|                   | Ansible                                         | Puppet                                              | Chef                                       | Salt                               |
| ----------------- | ----------------------------------------------- | --------------------------------------------------- | ------------------------------------------ | ---------------------------------- |
| Model             | Push                                            | Pull (agent)                                        | Pull (agent)                               | Push/pull (minion or SSH)          |
| Agent required    | No                                              | Yes                                                 | Yes                                        | Optional                           |
| Language          | YAML + Jinja                                    | Puppet DSL                                          | Ruby DSL                                   | YAML + Jinja                       |
| Style             | Procedural tasks, idempotent modules            | Declarative                                         | Declarative with imperative escape hatches | Declarative                        |
| Learning curve    | Lowest                                          | Moderate                                            | Highest                                    | Moderate                           |
| Scale strength    | Hundreds to low thousands                       | Very large fleets                                   | Large fleets                               | Very large, fastest execution      |
| Drift enforcement | On demand                                       | Continuous (every 30 min)                           | Continuous                                 | Continuous or event-driven         |
| Secrets           | Vault                                           | Hiera + eyaml                                       | Encrypted data bags                        | Pillar                             |
| Testing           | Molecule                                        | rspec-puppet, Litmus                                | Test Kitchen, ChefSpec, InSpec             | kitchen-salt                       |
| Best fit          | Ad-hoc automation, orchestration, mixed estates | Regulated environments needing enforcement evidence | Complex logic, strong test discipline      | Huge fleets, event-driven response |

**How to choose.** Weigh: can you install agents? How large is the estate? Does compliance require continuous enforcement and reporting? What does the team already know? And critically — how much of the estate could be made immutable instead?

**The honest modern answer:** for greenfield cloud work, most configuration moves into container images and Kubernetes manifests, with Terraform provisioning and Ansible filling the remaining gaps (golden-image builds, network appliances, legacy VMs). Full-fat configuration management is now most valuable in large, long-lived, regulated estates.

## Interview tips

- Answer with selection criteria, then a recommendation — a raw feature table alone reads as memorised.
- Naming the shift towards immutable infrastructure shows current thinking.
- Team familiarity is a legitimate deciding factor; say so, because it is true in practice.

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
