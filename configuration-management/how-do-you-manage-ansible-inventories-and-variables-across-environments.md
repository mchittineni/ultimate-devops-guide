---
title: "How do you manage Ansible inventories and variables across environments?"
id: 469
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
  - cloud-engineering
---

# How do you manage Ansible inventories and variables across environments?

**Short answer:** One inventory per environment, variables layered by scope, and nothing environment-specific inside a role. Concretely: an inventory directory per environment (`inventories/prod/`, `inventories/staging/`) each containing hosts grouped by function, with **`group_vars/`** and **`host_vars/`** files next to it - so `inventories/prod/group_vars/webservers.yml` holds production web settings and the role itself only ships safe defaults. Use a **static** inventory (INI or YAML) when the hosts are stable, and a **dynamic** inventory plugin (`amazon.aws.aws_ec2`, `azure.azcollection.azure_rm`, `community.general.gcp_compute`) when the cloud is the source of truth, so hosts and groups are built from tags at run time. Precedence is the part interviewers test: role `defaults/` is the weakest, then inventory group_vars, then host_vars, then play/task vars, with `-e` (extra vars) beating everything - which is why `-e` is the right tool for a one-off override and the wrong place for permanent configuration.

## Detail

### Inventory layout that scales

```text
inventories/
├── prod/
│   ├── hosts.yml                 # or aws_ec2.yml for a dynamic source
│   ├── group_vars/
│   │   ├── all.yml               # everything in prod
│   │   ├── webservers.yml        # per-function
│   │   ├── dbservers.yml
│   │   └── vault.yml             # encrypted secrets for prod
│   └── host_vars/
│       └── db-01.example.com.yml # the one host that is different
└── staging/  ... same shape, different values
```

The reason for one directory per environment rather than one file with `prod_web`/`staging_web` groups: **you cannot accidentally target the wrong environment**, because `-i inventories/staging` simply does not contain production hosts. That accident is the single most expensive Ansible mistake, and the layout prevents it structurally. Add `ansible.cfg` per environment or a wrapper that requires `-i` explicitly, and never set a default inventory pointing at production.

### Grouping: function, environment, location, and the group-of-groups trick

Group by **what a host is**, then compose:

```yaml
all:
  children:
    webservers:
      hosts:
        web-[01:04].prod.example.com:
    dbservers:
      hosts:
        db-01.prod.example.com: { mysql_role: primary }
        db-02.prod.example.com: { mysql_role: replica }
    eu_west_1: # location grouping, overlapping membership is fine
      children: { webservers: {}, dbservers: {} }
```

A host can belong to many groups, and variables from all of them merge (alphabetically by group name unless you set `ansible_group_priority`) - which is why two groups defining the same variable is a bug waiting to be discovered. Keep each variable owned by exactly one group where you can.

Naming conventions for very large inventories, which is a real interview question: use a consistent, sortable, machine-parseable scheme - `<env>-<role>-<location>-<index>` (`prod-web-euw1-01`) - group names in lowercase with underscores (hyphens are not valid Python identifiers and break some var lookups), and ranges (`web-[01:20]`) instead of twenty lines. Consistency matters more than the specific scheme, because patterns and `--limit` are how you will target work later.

### Static versus dynamic inventory

|          | Static                                      | Dynamic                                              |
| -------- | ------------------------------------------- | ---------------------------------------------------- |
| Source   | A file you maintain                         | A plugin querying the cloud/CMDB at run time         |
| Truth    | Drifts as soon as the cloud changes         | Always current                                       |
| Grouping | Hand-written                                | Built from **tags**, regions, instance state         |
| Good for | On-premises, network devices, stable fleets | Autoscaled instances, ephemeral hosts, large estates |
| Risk     | Stale hosts, missing new ones               | A tagging mistake changes who you target             |

Prefer inventory **plugins** (`aws_ec2.yml` with `keyed_groups`) over the legacy `*_inventory.py` scripts. The killer feature is `keyed_groups`: instances tagged `Environment=prod` and `Role=web` automatically land in `tag_Environment_prod` and `tag_Role_web`, so your playbooks target groups that maintain themselves. The corollary worth saying: **your tagging discipline becomes your inventory correctness**, so enforce tags in Terraform or with policy.

You can also mix - a dynamic cloud inventory plus a static file for the load balancers and network gear - by passing `-i` twice or pointing at a directory containing both.

### Variable precedence, the part that gets asked

From weakest to strongest (abridged to the levels that matter in practice):

1. Role `defaults/main.yml` ← the role's public API
2. Inventory `group_vars/all`
3. Inventory `group_vars/<group>`
4. Inventory `host_vars/<host>`
5. Play `vars`, `vars_files`, `vars_prompt`
6. Role `vars/main.yml` ← high, which is why it is for internals only
7. Block/task `vars`
8. `set_fact` / registered variables
9. **`-e` / `--extra-vars`** ← beats everything

Two practical consequences: put anything a caller should change in `defaults/`, not `vars/`; and treat `-e` as a deliberate override for a run (`-e "app_version=1.9.1"`), not as configuration - configuration belongs in `group_vars` under version control where it is reviewable.

`ansible-inventory --graph --vars` and `ansible -m debug -a 'var=hostvars[inventory_hostname]'` are how you prove what a host actually resolved to. Use them instead of arguing about precedence from memory.

### Passing parameters into a playbook

Four mechanisms, each with a purpose:

- **`--extra-vars`** for run-time values: a version to deploy, a target batch, a feature toggle. Accepts JSON or `@file.json`.
- **`vars_prompt`** for interactive input (fine for humans, useless in CI).
- **`vars_files`** to load a values file, including an encrypted one.
- **Role parameters** - `roles: [{ role: nginx, nginx_worker_processes: 4 }]` or `include_role` with `vars:` - which take high precedence and are the clean way to reuse one role twice with different settings in the same play.

For CI, `--extra-vars "@release.json"` keeps the invocation short and the values reviewable as a file.

### Targeting: `--limit` and patterns

`ansible-playbook site.yml -i inventories/prod --limit 'webservers:!web-03*'` is the answer to "run against all database servers except one" - the `:!` exclusion operator on a pattern. Other useful forms: `group1:group2` (union), `group1:&group2` (intersection), `~web-\d+` (regex), `--limit @failed.retry` to re-run only the hosts that failed. Combine with `--list-hosts` **before** running anything destructive; confirming the target list is a habit worth demonstrating in an interview.

### Secrets in inventory

Keep encrypted values in a dedicated `group_vars/<env>/vault.yml` and reference them from plain-text variables (`db_password: "{{ vault_db_password }}"`), so `grep` still shows you _where_ a secret is used without decrypting anything. Better still, look them up from a real secret manager at run time. See the dedicated answer on Ansible Vault.

## Example

```ini
# inventories/prod/hosts (INI form - compact, still common)
[webservers]
web-[01:04].prod.example.com

[dbservers]
db-01.prod.example.com mysql_role=primary
db-02.prod.example.com mysql_role=replica

[eu_west_1:children]
webservers
dbservers

[all:vars]
ansible_user=deploy
ansible_ssh_common_args='-o ProxyJump=bastion.prod.example.com'
```

```yaml
# inventories/prod/aws_ec2.yml - dynamic, grouped from tags
plugin: amazon.aws.aws_ec2
regions: [eu-west-1, eu-west-2]
filters:
  tag:Environment: prod
  instance-state-name: running
keyed_groups:
  - key: tags.Role # -> tag_Role_web, tag_Role_db
    prefix: tag_Role
  - key: placement.availability_zone
    prefix: az
hostnames: [tag:Name, private-ip-address]
compose:
  ansible_host: private_ip_address # never route through public IPs
cache: true
cache_plugin: jsonfile
cache_timeout: 300
```

```yaml
# inventories/prod/group_vars/webservers.yml - environment values live HERE, not in the role
nginx_worker_processes: 8
nginx_client_max_body_size: 64m
nginx_upstreams:
  - name: api
    servers: ["10.20.1.10:8080", "10.20.1.11:8080"]
app_java_opts: "-Xms2g -Xmx2g -XX:MaxRAMPercentage=75"
db_password: "{{ vault_prod_db_password }}" # indirection: greppable, still encrypted
```

```bash
# Prove what a host resolves to, before you run anything
ansible-inventory -i inventories/prod --graph
ansible-inventory -i inventories/prod --host web-01.prod.example.com --vars
ansible webservers -i inventories/prod -m debug -a 'var=nginx_worker_processes'

# Target precisely - and check the list first
ansible-playbook site.yml -i inventories/prod --limit 'dbservers:!db-02*' --list-hosts
ansible-playbook site.yml -i inventories/prod --limit 'webservers:&eu_west_1' --check --diff

# One-off override for a run; permanent values belong in group_vars
ansible-playbook deploy.yml -i inventories/prod -e "app_version=1.9.1" -e @release.json

# Retry only what failed
ansible-playbook site.yml -i inventories/prod --limit @site.retry
```

## Interview tips

- Lead with the structural safety argument: one inventory directory per environment so you cannot target production by accident, with `group_vars`/`host_vars` beside each inventory. That reasoning matters more than the file format.
- Say plainly that roles carry only safe defaults and environment values live in inventory `group_vars`. It is the rule that keeps a role reusable.
- Be able to order the precedence chain, and give the two consequences: put caller-facing values in `defaults/` not `vars/`, and use `-e` for run-time overrides rather than as configuration. If you are unsure of an exact position, say "`-e` wins, role `defaults` loses, inventory sits between" - that is the part they care about.
- For static versus dynamic, answer in terms of source of truth and then volunteer `keyed_groups` building groups from tags - plus the consequence that your tagging discipline becomes your inventory correctness.
- Prefer inventory **plugins** over legacy inventory scripts, and mention caching (`cache_timeout`) because a dynamic inventory on a large estate is otherwise slow on every run.
- Answer the "run against all database servers except one" question with `--limit 'dbservers:!db-02*'`, and mention `--list-hosts`, `--check --diff`, and `@site.retry`. Showing that you verify the target list first reads as operational maturity.
- Cover the four ways to pass parameters (`--extra-vars`, `vars_prompt`, `vars_files`, role params) and say which you would use in CI.
- Mention `ansible-inventory --graph --vars` as the way to settle precedence arguments with evidence. See [how do you handle secrets in Ansible with Vault](./how-do-you-handle-secrets-in-ansible-with-vault.md), [structuring an Ansible role](./how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md), [running Ansible at scale](./how-do-you-run-ansible-at-scale-across-thousands-of-hosts.md), and [patching hundreds of servers safely](./how-do-you-patch-hundreds-of-servers-safely.md).

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
