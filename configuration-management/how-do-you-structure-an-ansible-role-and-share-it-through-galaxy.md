---
title: "How do you structure an Ansible role and share it through Galaxy?"
id: 468
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
  - infrastructure-as-code
---

# How do you structure an Ansible role and share it through Galaxy?

**Short answer:** A role is a directory with a fixed layout that Ansible loads by convention: **`tasks/main.yml`** (what it does), **`handlers/main.yml`** (restart-style actions triggered by `notify`), **`defaults/main.yml`** (the role's public inputs at the **lowest** variable precedence, so callers can override them freely), **`vars/main.yml`** (internal values at high precedence - use sparingly), **`templates/`** (Jinja2 `.j2` files), **`files/`** (static copies), **`meta/main.yml`** (dependencies, supported platforms, Galaxy metadata), and **`molecule/`** plus `README.md` for tests and documentation. You create one with `ansible-galaxy role init <name>`, call it from a playbook under `roles:` or with `include_role`/`import_role`, and share it by pushing to a Git repository and either importing it into Ansible Galaxy or - the modern approach - packaging roles and plugins together as a **collection** (`namespace.collection`) installed from a `requirements.yml`. The distinction interviewers listen for: **`defaults/` is for values you expect callers to change; `vars/` is for values you do not.**

## Detail

### The layout, and why each directory exists

```text
roles/nginx/
├── defaults/main.yml   # public API, LOWEST precedence  -> callers override easily
├── vars/main.yml       # internal constants, HIGH precedence -> hard to override
├── tasks/main.yml      # the work; split into included files as it grows
├── handlers/main.yml   # `notify:`-triggered actions, run once at the end of the play
├── templates/          # *.j2 rendered with Jinja2 (variables + logic)
├── files/              # static files copied verbatim
├── meta/main.yml       # dependencies, galaxy_info, platform support
├── library/            # custom modules shipped with the role
├── filter_plugins/     # custom Jinja2 filters
├── molecule/default/   # converge + verify scenarios (the role's test suite)
└── README.md           # variables table and example usage
```

Ansible auto-loads `main.yml` from each of these directories, which is why the names are not negotiable. Anything else in `tasks/` must be pulled in explicitly with `include_tasks` (dynamic, evaluated at runtime, works with loops and conditionals) or `import_tasks` (static, pre-processed - so tags and handlers behave differently). Knowing that pair is a common follow-up: **import is static, include is dynamic**, and the same distinction applies to `import_role` versus `include_role`.

### Templates versus roles - the question that trips people

They are different kinds of thing, and interviewers ask the comparison to see whether you understand both. A **template** is a single Jinja2 file rendered with variables at run time by the `template` module - the mechanism for generating a config file. A **role** is a packaging unit: a bundle of tasks, handlers, defaults, files, and templates that installs and configures something end to end. A role usually _contains_ templates. Templates are also where `when`-style logic sneaks into configuration - loops over a list of upstreams, conditional blocks per environment - and where you should use `| default(...)` so a missing variable produces a sane file rather than a broken one. Always render config through a template with `validate:` where the tool supports it (`nginx -t`, `visudo -c`), so a bad render cannot break the service.

### Handlers, idempotency, and modules over shell

- **Handlers** run at the **end of the play**, once, no matter how many tasks notified them - which is exactly what you want when six tasks all change nginx config. `meta: flush_handlers` forces them to run earlier when ordering matters. Handler names are the contract, so keep them stable; `listen:` lets several handlers respond to one topic.
- **Idempotency** is the core property: run the playbook twice and the second run reports zero changes. Modules (`package`, `service`, `copy`, `template`, `lineinfile`, `user`) are written to check state first. `command`/`shell` are **not** idempotent, which is why every `shell` task needs `creates:`, `removes:`, or a `when:` guard plus `changed_when:` - otherwise it reports "changed" forever and your drift reporting becomes meaningless. Saying "use a module; if you must use shell, make it idempotent by hand" is the expected answer to "what does idempotent mean in Ansible?"

### Role dependencies and reuse

`meta/main.yml` can declare `dependencies:`, which run **before** the role's own tasks. Use it sparingly - implicit dependency chains make playbooks hard to reason about, and a dependency listed in two roles runs once per unique parameter set, which surprises people. Explicit ordering in the playbook is usually clearer.

For genuinely shared plugins - custom modules, filters, lookups - the modern home is a **collection**, because a collection can carry roles, modules, plugins, and playbooks together with one version. That answers "if several roles depend on custom plugins, how do you manage them?": put the plugins in a collection, version it, and have the roles depend on the collection rather than copying `filter_plugins/` into each role.

### Galaxy, collections, and versioning

- **Initialise**: `ansible-galaxy role init nginx` or `ansible-galaxy collection init acme.platform`.
- **Metadata**: `meta/main.yml` `galaxy_info` needs `author`, `description`, `license`, `min_ansible_version`, `platforms`, and `galaxy_tags` before Galaxy will accept it.
- **Publish a role**: push to a public Git repository, tag a semver release, then `ansible-galaxy role import <github-user> <repo>` (or connect the repository in the Galaxy UI). Galaxy resolves versions from Git tags, so **tags are your versions**.
- **Publish a collection**: `ansible-galaxy collection build` then `... publish acme-platform-1.4.0.tar.gz --api-key=...`, to Galaxy or to a private Automation Hub / Nexus / Artifactory.
- **Consume with a lock**: a `requirements.yml` pinned to versions, installed in CI. Never rely on "whatever Galaxy has today".

```yaml
# requirements.yml - pinned, so builds are reproducible
collections:
  - name: community.general
    version: "9.5.1"
  - name: acme.platform
    source: https://automation-hub.example.com/api/galaxy/content/published/
    version: "1.4.0"
roles:
  - src: https://github.com/acme/ansible-role-nginx.git
    scm: git
    version: v3.2.0 # a tag, not a branch
    name: nginx
```

Private roles work exactly the same way through Git sources, which is the usual enterprise pattern - a role repository per component, semver tags, and a `requirements.yml` in each playbook repository.

### Testing a role

This is what separates a role you wrote from a role people trust. **Molecule** creates an instance (Docker, Podman, or a cloud driver), runs the role (`converge`), asserts the result (`verify`, with Ansible assertions or Testinfra), and - critically - runs `idempotence`, which applies the role twice and fails if the second run reports changes. Add `ansible-lint` and `yamllint` in CI, and a matrix across the platforms you claim to support in `meta/main.yml`. A role with a Molecule scenario and an idempotence check is a role you can upgrade without fear.

## Example

```yaml
# roles/nginx/defaults/main.yml - the role's public API, lowest precedence
nginx_package: nginx
nginx_worker_processes: auto
nginx_client_max_body_size: 16m
nginx_upstreams: []
# - name: api
#   servers: ["10.0.1.10:8080", "10.0.1.11:8080"]
nginx_manage_firewall: true
```

```yaml
# roles/nginx/tasks/main.yml - modules, guards, and a validated template
- name: Install nginx
  ansible.builtin.package:
    name: "{{ nginx_package }}"
    state: present
  notify: Restart nginx

- name: Render nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: "0644"
    validate: "nginx -t -c %s" # a bad render fails the task, not the service
  notify: Reload nginx

- name: Open HTTP and HTTPS
  ansible.posix.firewalld:
    service: "{{ item }}"
    permanent: true
    immediate: true
    state: enabled
  loop: [http, https]
  when: nginx_manage_firewall | bool

- name: Ensure nginx is running and enabled at boot
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true # "started AND enabled" - the interview favourite

- name: OS-specific extras
  ansible.builtin.include_tasks: "{{ ansible_os_family | lower }}.yml"
  # dynamic include: chosen at runtime, so one role handles Debian and RedHat
```

```yaml
# roles/nginx/handlers/main.yml - run once, at the end of the play
- name: Restart nginx
  ansible.builtin.service: { name: nginx, state: restarted }

- name: Reload nginx
  ansible.builtin.service: { name: nginx, state: reloaded }
  listen: "nginx config changed" # several tasks can notify one topic
```

```yaml
# roles/nginx/meta/main.yml - what Galaxy needs, plus dependencies
galaxy_info:
  author: acme-platform
  description: Install and configure nginx as a reverse proxy
  license: MIT
  min_ansible_version: "2.15"
  platforms:
    - { name: EL, versions: ["8", "9"] }
    - { name: Ubuntu, versions: ["jammy", "noble"] }
  galaxy_tags: [nginx, web, proxy]
dependencies:
  - role: acme.platform.base_hardening # runs BEFORE this role's tasks
    vars: { hardening_profile: web }
```

```bash
# Create, test, publish, consume
ansible-galaxy role init roles/nginx
ansible-lint roles/nginx && yamllint roles/nginx
molecule test                       # create -> converge -> idempotence -> verify -> destroy

git tag v3.2.0 && git push --tags   # Galaxy resolves versions from tags
ansible-galaxy role import acme ansible-role-nginx

ansible-galaxy collection init acme.platform
ansible-galaxy collection build && \
  ansible-galaxy collection publish acme-platform-1.4.0.tar.gz --api-key "$AH_TOKEN"

# in a playbook repository, pinned and installed in CI
ansible-galaxy install -r requirements.yml -p roles/ --force
```

## Interview tips

- Recite the directory layout and, for each one, say what Ansible does with it automatically. The load-`main.yml`-by-convention point is what shows you understand roles rather than having copied one.
- Make the `defaults/` versus `vars/` distinction explicitly in precedence terms: `defaults` is the lowest precedence and therefore the role's public API; `vars` is high precedence and hard to override, so keep it for internals. This is the most commonly asked role detail.
- Answer "what is the difference between a template and a role?" cleanly - a template is one Jinja2 file rendered at run time, a role is the packaging unit that usually contains templates - and mention `validate:` on the `template` task as a production habit.
- Explain handlers as end-of-play, once-per-play, `notify`-driven, with `meta: flush_handlers` when you need them earlier. Interviewers ask this to check you know the ordering.
- Define idempotency and immediately give the caveat: `command`/`shell` are not idempotent, so they need `creates`, `removes`, `when`, or `changed_when`. That caveat is the answer they are actually looking for.
- Know `import_*` versus `include_*` - static versus dynamic - because it comes up as soon as you mention splitting `tasks/`.
- For Galaxy, describe the whole flow: `role init`, `galaxy_info` metadata, a semver Git tag, `role import` or a collection `build`/`publish`, and consumption through a **pinned** `requirements.yml`. Mention private Automation Hub / Git sources for internal roles.
- Answer the shared-custom-plugins question with collections rather than copying plugin directories into every role.
- Close on Molecule with an idempotence scenario plus `ansible-lint` in CI - very few candidates mention testing roles at all. See [what is Ansible](../infrastructure-as-code/what-is-ansible.md), [managing Ansible inventories and variables across environments](./how-do-you-manage-ansible-inventories-and-variables-across-environments.md), [debugging and safely testing a playbook](./how-do-you-debug-and-safely-test-an-ansible-playbook.md), and [running Ansible at scale](./how-do-you-run-ansible-at-scale-across-thousands-of-hosts.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
