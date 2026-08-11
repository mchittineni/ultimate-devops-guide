---
title: "What is Salt (SaltStack)?"
id: 54
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
---

# What is Salt (SaltStack)?

**Short answer:** Salt is a configuration management and remote execution framework built on a very fast messaging bus, able to run commands across tens of thousands of nodes in seconds, in either agent (minion) or agentless (SSH) mode.

## Detail

**Architecture.** A Salt master communicates with **minions** over ZeroMQ, giving Salt its signature speed for ad-hoc remote execution across huge fleets. `salt-ssh` provides an agentless mode, and multi-master and syndic topologies scale it further.

**Concepts**

- **States** - desired configuration in YAML with Jinja templating, stored in `.sls` files (the "state tree").
- **Grains** - static facts about a minion (OS, CPU, roles), used for targeting.
- **Pillar** - secure, per-minion data, the right place for secrets and environment-specific values.
- **Targeting** - select minions by glob, grain, pillar, subnet, or compound expressions.
- **Reactor and beacons** - beacons emit events (a file changed, a service died) and the reactor responds automatically, enabling genuine event-driven automation.
- **Salt Mine and orchestration** - cross-node data sharing and multi-node workflow coordination.

Salt's differentiators are raw execution speed and the event-driven reactor system. Its trade-offs are a more complex master setup than Ansible and a smaller ecosystem than Ansible or Puppet.

## Example

```yaml
# /srv/salt/nginx/init.sls
nginx:
  pkg.installed: []
  service.running:
    - enable: True
    - require:
      - pkg: nginx
    - watch:
      - file: /etc/nginx/nginx.conf

/etc/nginx/nginx.conf:
  file.managed:
    - source: salt://nginx/files/nginx.conf.jinja
    - template: jinja
    - context:
        workers: {{ grains['num_cpus'] }}
```

```bash
salt '*' test.ping                       # remote execution across the fleet
salt -G 'os:Ubuntu' state.apply nginx    # target by grain
```

## Interview tips

- Speed at scale and the reactor/beacon event system are Salt's distinctive selling points.
- Pillar is the secrets answer; grains are facts, not secrets.
- Be ready to say why most teams still pick Ansible: simplicity and ubiquity beat raw speed for typical fleet sizes.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
