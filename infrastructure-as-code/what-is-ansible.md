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

Ansible shines at configuration management, application deployment, and orchestrated multi-step operations (rolling restarts, patching runs). It can provision cloud resources, but Terraform is generally the better fit for that half of the problem.

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

## Interview tips

- Idempotency and handlers are the concepts to demonstrate - a task that always reports `changed` is a bug.
- `--check --diff` for dry runs, and `serial:` for rolling updates without downtime.
- Vault (or an external secrets manager) is the expected answer on secrets in playbooks.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
