---
title: "What is Puppet?"
id: 52
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
---

# What is Puppet?

**Short answer:** Puppet is a declarative, agent-based configuration management tool. Nodes run an agent that periodically fetches a compiled catalogue from a Puppet server and enforces the described state, correcting drift on every run.

## Detail

**Architecture.** The agent (default every 30 minutes) sends facts about the node (collected by Facter) to the Puppet server. The server compiles a **catalogue** - the resolved desired state for that node - from manifests and Hiera data, and returns it. The agent applies it and reports back. Communication is mutually authenticated TLS with certificates issued by the Puppet CA.

**Language.** Puppet's DSL is declarative: you describe resources (`package`, `file`, `service`, `user`, `exec`) and their relationships. The order in the file does not determine execution order - dependencies do, expressed with `require`, `before`, `notify`, `subscribe`, or the chaining arrows.

**Structure**

- **Manifests** (`.pp`) - resource declarations.
- **Classes and modules** - reusable units, shared through Puppet Forge.
- **Hiera** - hierarchical data lookup that separates configuration data from code, so the same module serves dev, staging, and production.
- **Facter** - node facts available as variables.
- **Roles and profiles** - the standard pattern: profiles wrap technology modules, roles compose profiles, nodes get exactly one role.

Puppet's strength is continuous enforcement at large scale with strong reporting and compliance evidence. Its cost is the DSL learning curve and running the server infrastructure.

## Example

```puppet
class profile::nginx (
  Integer $worker_processes = 4,
) {
  package { 'nginx':
    ensure => installed,
  }

  file { '/etc/nginx/nginx.conf':
    ensure  => file,
    content => epp('profile/nginx.conf.epp', { 'workers' => $worker_processes }),
    owner   => 'root',
    mode    => '0644',
    require => Package['nginx'],
    notify  => Service['nginx'],      # restart only when the file changes
  }

  service { 'nginx':
    ensure => running,
    enable => true,
  }
}
```

## Interview tips

- Declarative and relationship-driven - explain that file order does not imply execution order.
- Roles and profiles is the design pattern interviewers expect from anyone who has run Puppet at scale.
- Contrast with Ansible: pull/agent/continuous enforcement versus push/agentless/on-demand.

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
