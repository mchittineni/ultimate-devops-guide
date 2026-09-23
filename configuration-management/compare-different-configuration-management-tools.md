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

**How to choose.** Weigh: can you install agents? How large is the estate? Does compliance require continuous enforcement and reporting? What does the team already know? And critically - how much of the estate could be made immutable instead?

## Example

The same intent - nginx installed and running - in each tool:

```yaml
# Ansible (push, run on demand)
- hosts: web
  become: true
  tasks:
    - ansible.builtin.package: { name: nginx, state: present }
    - ansible.builtin.service: { name: nginx, state: started, enabled: true }
```

```puppet
# Puppet / OpenVox (agent pulls a catalogue every 30 minutes by default)
package { 'nginx': ensure => installed }
-> service { 'nginx': ensure => running, enable => true }
```

```ruby
# Chef (agent runs the recipe on its interval)
package 'nginx'
service 'nginx' do
  action [:enable, :start]
end
```

```yaml
# Salt state (minion applies on highstate, schedule, or event)
nginx:
  pkg.installed: []
  service.running:
    - enable: true
    - require:
      - pkg: nginx
```

**Ecosystem and licensing, as of 2026.** Ansible (ansible-core, GPL) is backed by Red Hat/IBM, with Ansible Automation Platform as the commercial layer. Puppet is owned by Perforce, which since 2025 ships official Puppet binaries under a commercial EULA (free only for small estates); the community fork **OpenVox**, maintained by Vox Pupuli from the Apache-2.0 code, is the open-source path. Chef is owned by Progress (Chef Infra client is Apache-2.0, commercial distributions are licensed). Salt is open source under Broadcom (via VMware). Licensing and ownership now belong in a tool-selection conversation.

**The honest modern answer:** for greenfield cloud work, most configuration moves into container images and Kubernetes manifests, with Terraform provisioning and Ansible filling the remaining gaps (golden-image builds, network appliances, legacy VMs). Full-fat configuration management is now most valuable in large, long-lived, regulated estates.

## Interview tips

- Answer with selection criteria, then a recommendation - a raw feature table alone reads as memorised.
- Naming the shift towards immutable infrastructure shows current thinking.
- Team familiarity is a legitimate deciding factor; say so, because it is true in practice.
- Be current on the Puppet licensing change and the OpenVox fork - it is exactly the kind of recent ecosystem shift that interviewers use to check whether you follow the field.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
