---
title: "How do you run Ansible at scale across thousands of hosts?"
id: 283
category: "Configuration Management"
difficulty: "Advanced"
tags:
  - devops
  - configuration-management
  - interview-questions
---

# How do you run Ansible at scale across thousands of hosts?

**Short answer:** Stop treating it as one big play. Split the run into batches with `serial` and `max_fail_percentage`, use a **dynamic inventory** sourced from the cloud API rather than a static file, cache facts and skip gathering where you do not need them, push execution out to workers (AWX/Ansible Automation Platform, or a controller per region), and make the playbooks genuinely idempotent so a partial run is safe to repeat. Beyond a few thousand nodes, the honest answer is usually to bake images instead - configuration management scales worst exactly where mutable servers scale worst.

## Detail

**Why naive Ansible falls over.** The default `forks = 5` means five hosts at a time; fact gathering opens an SSH connection and runs a full setup module per host; every task is a separate round trip; and one failed host in a linear play can stall the rollout. At 2,000 hosts this becomes hours, and the failure mode is a half-configured estate.

**The mechanical fixes, in order of payoff:**

- **Raise `forks` and use pipelining.** `forks = 50-100` plus `pipelining = True` (which removes a file transfer per task) and `ControlPersist` SSH multiplexing typically gives a 3-10x speedup on its own. Watch controller CPU and file descriptors - the controller becomes the bottleneck before the network does.
- **Cache facts, or skip them.** `gathering = smart` with a `jsonfile` or Redis fact cache, `fact_caching_timeout`, and `gather_subset = !all,!any,network,hardware` for what you actually use. Plays that need no facts get `gather_facts: false`.
- **Batch with `serial` and cap failures.** `serial: [1, 10, "20%"]` gives you a canary host, then a small wave, then percentage waves - the same progressive-delivery shape you would use for an application. `max_fail_percentage: 5` aborts the rollout instead of grinding through 400 broken hosts.
- **Push work to the target.** Loops that run a task per item are round trips; use the module's native list support (`package: name: [a, b, c]`) or `loop` with `batch`. Avoid `shell` in a loop entirely.
- **Distribute execution.** AWX / Automation Platform with execution nodes per region removes latency and the single-controller ceiling; `ansible-pull` inverts the model so each host fetches and applies its own config on a timer, which scales essentially without limit at the cost of central visibility.

**The structural fixes that matter more:**

- **Dynamic inventory.** Static INI files rot. Use the `amazon.aws.aws_ec2`, `azure.azcollection.azure_rm`, or `google.cloud.gcp_compute` inventory plugins with `keyed_groups` from tags, so `role`, `environment`, and `region` groups build themselves.
- **Real idempotency.** Every task must be safe to re-run: no `shell` without `creates`/`changed_when`, no appending to files, templates instead of `lineinfile` pyramids. Then a failed batch is a retry rather than an investigation. Enforce it with a periodic `--check --diff` run whose _only_ acceptable result is zero changes - that is also your drift detector.
- **Layered variables with a strict precedence policy.** `group_vars/all` → `group_vars/<env>` → `host_vars`, and nothing important set at the command line. Write the precedence rules down; Ansible's 22-level ordering is a common source of "it worked in staging".
- **Version everything.** Pin collections in `requirements.yml`, pin the Ansible version in the execution environment image, and run playbooks from CI - not from an engineer's laptop with whatever collections they happen to have.
- **Test before the fleet.** `ansible-lint` in CI, Molecule scenarios per role, then a canary group of real hosts. A role change that reaches 2,000 hosts untested is an incident with a scheduler.

**Know when to stop.** If you are pushing configuration to thousands of long-lived mutable servers, the drift, the run time, and the blast radius all grow together. The scaling answer is immutable infrastructure: use Ansible (or Packer with an Ansible provisioner) to **build an image**, then roll instances by replacing them. Configuration management then runs at build time against one host, which is a problem that does not need any of the tuning above.

## Example

```ini
# ansible.cfg - the settings that decide whether a 2,000-host run takes 20 minutes or 4 hours.
[defaults]
forks = 100
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /var/tmp/ansible_facts
fact_caching_timeout = 7200
gather_subset = !all,!any,network,hardware
callbacks_enabled = profile_tasks   # find the slow task instead of guessing

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=300s -o PreferredAuthentications=publickey
```

```yaml
# Dynamic inventory: groups build themselves from cloud tags.
plugin: amazon.aws.aws_ec2
regions: [eu-west-1, us-east-1]
filters:
  instance-state-name: running
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: tags.Environment
    prefix: env
  - key: placement.availability_zone
    prefix: az
compose:
  ansible_host: private_ip_address
```

```yaml
# Progressive rollout: canary, small wave, percentage waves, with a failure cap.
- name: Roll the web tier
  hosts: role_web:&env_prod
  serial: [1, 10, "20%"]
  max_fail_percentage: 5
  gather_facts: false # this play needs no facts
  tasks:
    - name: Drain from the load balancer
      community.aws.elb_target_group_info: # ... deregister before touching the host
      delegate_to: localhost

    - name: Deploy config
      ansible.builtin.template:
        src: app.conf.j2
        dest: /etc/app/app.conf
        mode: "0640"
      notify: restart app

    - name: Wait for health before the next batch
      ansible.builtin.uri:
        url: "http://{{ inventory_hostname }}:8080/healthz"
        status_code: 200
      retries: 30
      delay: 2
```

```bash
# Drift detection: the only acceptable output is zero changed hosts.
ansible-playbook site.yml --check --diff --limit role_web | tee drift.log
ansible-playbook site.yml --list-hosts        # confirm the blast radius before running
ANSIBLE_STRATEGY=free ansible-playbook patch.yml   # independent hosts, no batch barrier
```

## Interview tips

- Give the mechanical wins with numbers - forks, pipelining, fact caching - then move to the structural ones. Only naming `forks` looks shallow; only naming architecture looks hand-wavy.
- `serial` plus `max_fail_percentage` is the answer to "how do you avoid breaking 2,000 hosts at once". Frame it as progressive delivery for infrastructure.
- Say that idempotency is what makes retries safe, and that `--check --diff` doubles as drift detection. Interviewers like a single mechanism serving two purposes.
- Mention `ansible-pull` or distributed execution nodes as the way past a single controller's ceiling.
- Volunteer the limit: past a certain scale, bake images and replace instances. Knowing when the tool is the wrong tool is the senior signal in this question.
- Have the variable-precedence trap ready - a value set in the wrong layer that made staging and prod diverge. It is a universally recognised war story.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
