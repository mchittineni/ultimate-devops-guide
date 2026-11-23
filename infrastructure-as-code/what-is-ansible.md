---
title: "What is Ansible?"
id: 28
category: "Infrastructure as Code"
difficulty: "Beginner"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# What is Ansible?

**Short answer:** Ansible is an agentless configuration management and automation tool that connects over SSH (or WinRM) and applies idempotent tasks described in YAML playbooks against an inventory of hosts.

## Detail

**Agentless** is its defining trait: nothing is installed on the managed nodes beyond Python and SSH access, which makes adoption trivial compared with agent-based tools.

Core concepts:

- **Inventory** - the hosts and groups to manage, static (INI/YAML) or dynamic (queried from a cloud API).
- **Playbook** - an ordered list of plays; each play maps hosts to tasks.
- **Task** - one invocation of a module, which should be idempotent.
- **Module** - the unit of work (`apt`, `copy`, `template`, `service`, `user`, `kubernetes.core.k8s`); over 3,000 exist across collections.
- **Role** - the reusable packaging format: tasks, handlers, templates, defaults, and variables in a conventional directory layout.
- **Handler** - a task triggered only when something actually changed (restart a service after a config change).
- **Ansible Vault** - encrypts sensitive variables at rest inside the repository.

Ansible shines at configuration management, application deployment, and orchestrated multi-step operations (rolling restarts, patching runs). It can provision cloud resources, but Terraform is generally the better fit for that half of the problem, because Ansible keeps no state: it cannot plan a diff against what exists or notice that a resource was removed from the playbook.

**Play execution order: `pre_tasks`, roles, `tasks`, `post_tasks`.** Inside one play, Ansible runs sections in a fixed order regardless of how they are written in the file:

1. `pre_tasks`, then any handlers they notified
2. `roles`, then `tasks`, then handlers notified by either of those two (roles and tasks share one flush)
3. `post_tasks`, then any handlers they notified

`pre_tasks` exist for work that must happen _before_ roles touch the host: refresh the package cache, `assert` prerequisites such as free disk space or OS version, silence monitoring, or drain the host from the load balancer. `post_tasks` do the reverse: poll a health endpoint, put the host back into the pool, re-enable alerts. Because handlers are flushed at the end of each stage, a service restart notified in `pre_tasks` happens before roles start, not at the end of the play. Combined with `serial:` (a few hosts per batch), `delegate_to:` (run the load-balancer call on the balancer or `localhost`) and `max_fail_percentage:`, this is how a patching play becomes a zero-downtime rolling update.

The trade-offs of the push/SSH model: runs are only as current as the last execution (no continuous enforcement unless you schedule it, for example with AWX/Ansible Automation Platform), large fleets need tuning (`forks`, pipelining, fact caching), and idempotency is only as good as the modules - `command`/`shell` tasks are not idempotent unless you add `creates:` or `changed_when:`.

## Example

```yaml
- name: Configure web servers
  hosts: webservers
  become: true
  vars:
    app_port: 8080

  tasks:
    - name: Install nginx
      ansible.builtin.package:
        name: nginx
        state: present

    - name: Deploy configuration
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        validate: nginx -t -c %s
      notify: Restart nginx

    - name: Ensure nginx is running
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: Restart nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

```bash
ansible-playbook -i inventory/prod site.yml --check --diff   # dry run
```

A rolling patch play using `pre_tasks` and `post_tasks` around the roles:

```yaml
- name: Patch web tier safely
  hosts: webservers
  become: true
  serial: 5 # five hosts per batch
  max_fail_percentage: 0 # stop the rollout if any host in a batch fails

  pre_tasks:
    - name: Check there is room to patch
      ansible.builtin.assert:
        that: (ansible_facts.mounts | selectattr('mount', 'equalto', '/') | first).size_available > 2 * 1024 ** 3
        fail_msg: "Less than 2 GiB free on / - not patching this host"

    - name: Refresh the apt cache
      ansible.builtin.apt:
        update_cache: true

    - name: Take the host out of the load balancer
      community.general.haproxy:
        state: disabled
        backend: web
        host: "{{ inventory_hostname }}"
        drain: true
      delegate_to: "{{ groups['loadbalancers'][0] }}"

  roles:
    - os_patching
    - nginx

  post_tasks:
    - name: Wait until the app is healthy
      ansible.builtin.uri:
        url: "http://{{ inventory_hostname }}:8080/healthz"
        status_code: 200
      register: health
      retries: 20
      delay: 5
      until: health.status == 200

    - name: Put the host back into the load balancer
      community.general.haproxy:
        state: enabled
        backend: web
        host: "{{ inventory_hostname }}"
      delegate_to: "{{ groups['loadbalancers'][0] }}"
```

## Interview tips

- Idempotency and handlers are the concepts to demonstrate - a task that always reports `changed` is a bug.
- `--check --diff` for dry runs, and `serial:` for rolling updates without downtime.
- Vault (or an external secrets manager) is the expected answer on secrets in playbooks.
- "What are `pre_tasks`?" comes up often. State the order (`pre_tasks`, roles, `tasks`, `post_tasks`, with handlers flushed after each stage) and give a concrete use, such as draining a host from the load balancer before roles restart services.

**Telling it as a STAR story** (an adaptable example)

- **Situation:** A patching playbook restarted nginx on all 30 web servers at once while they were still in the load balancer, and users saw errors.
- **Task:** Make patching safe enough to run during business hours.
- **Action:** Added `serial: 5`, used `pre_tasks` to assert free disk space, refresh the package cache and drain each host from the load balancer with `delegate_to`, let the roles patch and restart services through handlers, and used `post_tasks` to poll the health endpoint before re-enabling the host. `max_fail_percentage` stopped the run if a batch failed.
- **Result:** Patching became zero-downtime, and a bad package later stopped the rollout after the first five hosts instead of all thirty.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
