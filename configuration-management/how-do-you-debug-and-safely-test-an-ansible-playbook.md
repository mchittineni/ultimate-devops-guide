---
title: "How do you debug and safely test an Ansible playbook?"
id: 471
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
  - scripting-and-automation
---

# How do you debug and safely test an Ansible playbook?

**Short answer:** Work outwards from cheap and safe to expensive and risky. **`--syntax-check`** and `ansible-lint` catch structural mistakes with no hosts involved. **`--list-hosts`** confirms you are aiming at the right machines - the check that prevents the worst class of mistake. **`--check --diff`** is a dry run that shows what would change, line by line, without changing it. **`-vvv`** shows the module arguments and the raw JSON result (and `-vvvv` adds the connection detail). **`--start-at-task`** and `--step` let you resume or single-step instead of re-running an hour of work. Inside the playbook, `register` a result and `debug` it, use `assert` to fail fast on bad assumptions, and wrap risky sequences in **`block`/`rescue`/`always`** so a failure has a defined recovery path. And the thing that makes all of this unnecessary most of the time: **use modules rather than `shell`**, because modules are idempotent and report `changed` honestly, so a second run proving "0 changed" is your real test.

## Detail

### The command-line ladder

| Flag                            | What it does                                                     | When                                 |
| ------------------------------- | ---------------------------------------------------------------- | ------------------------------------ |
| `--syntax-check`                | Parses the playbook, no connection                               | First, always. Free                  |
| `--list-hosts` / `--list-tasks` | Shows the resolved target set and task list                      | **Before anything destructive**      |
| `--check`                       | Dry run: modules report what they _would_ do                     | Reviewing a change                   |
| `--diff`                        | Shows the actual textual difference for file/template/lineinfile | With `--check`, or during a real run |
| `-v` … `-vvvv`                  | Verbosity: results → module args + JSON → connection detail      | When a task fails inexplicably       |
| `--step`                        | Confirm each task interactively                                  | Nervous first run on production      |
| `--start-at-task "name"`        | Skip ahead to a named task                                       | Resuming a long playbook after a fix |
| `--tags` / `--skip-tags`        | Run a subset                                                     | Iterating on one section             |
| `--limit host`                  | Narrow the blast radius                                          | Canary one host first                |
| `--flush-cache`                 | Drop the fact cache                                              | Facts look stale                     |

`--check --diff --limit one-host` is the standard "I am about to touch production" invocation. Then `--limit` a canary, then a batch, then the fleet.

**`--check` has limits you must state**: a task whose result feeds later tasks may skip and leave subsequent tasks unable to run; `command`/`shell` tasks are skipped entirely unless you set `check_mode: false`; and a task that depends on a package installed by an earlier (skipped) task will fail. So a clean `--check` is evidence, not proof. `check_mode: false` on read-only gathering tasks makes dry runs far more useful.

### Watching a run in progress

The question "which command or flag lets you view the log while a playbook is executing?" has two good answers: raise verbosity (`-v`/`-vvv`) so output streams as tasks complete, and set **`ANSIBLE_LOG_PATH`** (or `log_path` in `ansible.cfg`) so everything is written to a file you can `tail -f` from another terminal. For long-running remote commands, `poll: 0` with `async:` plus `async_status` lets you start the work and check on it rather than staring at a blocked task. Callback plugins (`ANSIBLE_STDOUT_CALLBACK=yaml` or `debug`) make the output dramatically more readable, and `ANSIBLE_DISPLAY_SKIPPED_HOSTS=false` cuts the noise.

### Debugging inside the playbook

- **`register` + `debug`** - capture a result and print it. `debug: var=result` prints structure; `debug: msg="..."` prints a formatted line; `verbosity: 2` on a debug task means it only prints under `-vv`, so you can leave diagnostics in place.
- **`assert`** - fail early with a clear message when an assumption is wrong (a variable is undefined, a version is too low, a disk is too small). Much better than a confusing failure ten tasks later.
- **`failed_when` / `changed_when`** - correct a module's or command's idea of success. A `shell` task that exits 1 for a benign reason should not fail the play; a task that always reports `changed` makes drift reporting worthless.
- **`ignore_errors: true`** - use sparingly and always with a follow-up check, otherwise it hides real failures.
- **The `debugger`** - `debugger: on_failed` (or `ANSIBLE_ENABLE_TASK_DEBUGGER=True`) drops you into an interactive prompt at the failed task where you can inspect `task_vars`, change them (`task.args['x']='y'`), and `redo`. Very few candidates know this exists.
- **`ansible -m setup`** - dump the facts for a host. Half of all "why did my `when` not match?" problems are a fact you assumed rather than checked.

### `block` / `rescue` / `always` - and `release_on`

Ansible's error handling mirrors try/except/finally:

```yaml
- block:          # try
    - ...tasks...
  rescue:         # except: runs only if a task in the block failed
    - ...recovery...
  always:         # finally: runs regardless
    - ...cleanup...
```

Inside `rescue` you get `ansible_failed_task` and `ansible_failed_result`, which is how you log _what_ failed. Use this for anything with a partial-completion risk: take a database out of the load balancer, upgrade it, and in `rescue` put it back and roll the change back; in `always` re-enable monitoring. Blocks also let you apply `become`, `when`, and `tags` to a group of tasks at once.

Note the naming trap: there is **no `release_on` keyword** in Ansible. If an interviewer offers it alongside `block`/`rescue`, the honest and correct answer is that error handling is `block`/`rescue`/`always`, and the term they may be reaching for is either `always` (guaranteed cleanup) or `any_errors_fatal`/`max_fail_percentage` (stop the whole play when failures exceed a threshold). Saying that plainly is better than inventing a definition.

### Idempotency as the real test

The strongest test of a playbook is running it twice. The second run should report **`changed=0`**; anything still changing is either a genuinely non-idempotent task or a module you are using wrongly. Common culprits and fixes:

- `shell`/`command` with no `creates:`, `removes:`, `when:`, or `changed_when:` - always reports changed.
- `lineinfile` with a loose regexp that rewrites the file each time - use `template` for whole files.
- `file` with a mode expressed as `755` instead of `"0755"` - YAML reads the unquoted form as a decimal number.
- `git` with `force: yes` on every run, or `pip`/`npm` without a version.

**Molecule** automates this: it creates a container or VM, converges the role, runs an **idempotence** check (a second converge that must report no changes), verifies with assertions or Testinfra, and destroys. Add `ansible-lint` and `yamllint` in CI and you have a role you can change with confidence.

### Common failures and what they actually mean

- **"command not found" from `yum`/`apt`/`dnf`** - almost never the package manager missing. It means you used the wrong module for the OS (`apt` on RHEL), or the target lacks Python/the right interpreter, or `PATH` differs under a non-interactive shell. Use `ansible.builtin.package` for cross-platform work, set `ansible_python_interpreter` where auto-detection guesses wrong, and use `become: true` for privileged operations.
- **A playbook that runs for hours** - check `forks` (default 5 is far too low), enable pipelining and SSH multiplexing, cut fact gathering (`gather_facts: false` or a fact cache), and stop looping `shell` where a module with a `loop` and batching would do. Diagnose with `ANSIBLE_CALLBACKS_ENABLED=profile_tasks` to see exactly which tasks consume the time - that is the answer to "a playbook has been running for two hours, what do you do?": profile it, check whether it is actually progressing (`tail` the log path), confirm no task is waiting on an interactive prompt, and only then decide between waiting and aborting.
- **A timeout on one host out of twenty** - that host, not the playbook: SSH reachability, DNS, a full disk, a hung package manager holding a lock (`/var/lib/dpkg/lock`), or a slow provider. `--limit` to that host with `-vvvv`, and consider `serial:` plus `max_fail_percentage` so one bad host does not abort the fleet.
- **Passing data between tasks and blocks** - `register` a variable and reference it later; it persists for the host across the play, including across blocks. For cross-host values, read `hostvars['other-host'].myvar`; for values needed in later plays, `set_fact` with `cacheable: true`.

## Example

```bash
# The safe escalation, in order
ansible-playbook site.yml -i inventories/prod --syntax-check
ansible-lint site.yml roles/
ansible-playbook site.yml -i inventories/prod --list-hosts --list-tasks   # confirm the target
ansible-playbook site.yml -i inventories/prod --check --diff --limit web-01
ansible-playbook site.yml -i inventories/prod --limit web-01              # canary
ansible-playbook site.yml -i inventories/prod --limit 'webservers:!web-01'

# Watch it, profile it, resume it
ANSIBLE_LOG_PATH=./run.log ANSIBLE_STDOUT_CALLBACK=yaml \
  ANSIBLE_CALLBACKS_ENABLED=profile_tasks \
  ansible-playbook site.yml -i inventories/prod &
tail -f ./run.log

ansible-playbook site.yml -i inventories/prod --start-at-task "Configure nginx"
ansible-playbook site.yml -i inventories/prod --step
ansible-playbook site.yml -i inventories/prod -vvv --limit db-07   # one sick host
```

```yaml
# Debugging idioms that belong in real playbooks
- name: Check assumptions before doing anything
  ansible.builtin.assert:
    that:
      - app_version is defined
      - ansible_distribution_major_version | int >= 8
      - ansible_memtotal_mb >= 2048
    fail_msg: "Preconditions not met on {{ inventory_hostname }}"
    quiet: true

- name: Read current state (still runs in --check)
  ansible.builtin.command: /usr/local/bin/app --version
  register: app_current
  changed_when: false # read-only: never report a change
  failed_when: false # not installed yet is not a failure
  check_mode: false # make dry runs actually useful

- name: Show it only when asked for extra verbosity
  ansible.builtin.debug:
    var: app_current.stdout
    verbosity: 2

- name: Upgrade with a defined recovery path
  block:
    - name: Remove from the load balancer
      ansible.builtin.uri:
        url: "https://lb.example.com/api/drain/{{ inventory_hostname }}"
        method: POST
    - name: Deploy the new version
      ansible.builtin.package: { name: "app-{{ app_version }}", state: present }
      notify: Restart app
  rescue:
    - name: Report what failed
      ansible.builtin.debug:
        msg: "Failed at '{{ ansible_failed_task.name }}': {{ ansible_failed_result.msg | default('') }}"
    - name: Roll back to the previous version
      ansible.builtin.package: { name: "app-{{ app_previous_version }}", state: present }
  always:
    - name: Put it back in the load balancer either way
      ansible.builtin.uri:
        url: "https://lb.example.com/api/enable/{{ inventory_hostname }}"
        method: POST
```

```yaml
# Non-idempotent shell -> idempotent shell
- name: BAD - reports "changed" on every single run
  ansible.builtin.shell: /opt/app/bin/reindex.sh

- name: GOOD - guarded, honest about change, and skippable
  ansible.builtin.shell: /opt/app/bin/reindex.sh
  args:
    creates: /var/lib/app/.reindexed-{{ schema_version }}
  register: reindex
  changed_when: "'reindexed' in reindex.stdout"
```

```bash
# Molecule: the automated version of "run it twice"
molecule create && molecule converge
molecule idempotence     # a second converge that MUST report changed=0
molecule verify          # assertions / Testinfra
molecule test            # the whole cycle, including destroy - what CI runs
```

## Interview tips

- Present it as a ladder from cheap and safe to expensive and risky: `--syntax-check`, `ansible-lint`, `--list-hosts`, `--check --diff`, canary with `--limit`, then the fleet. Structure signals discipline.
- Name `--list-hosts` explicitly as the step that prevents targeting the wrong environment. Interviewers notice candidates who verify before acting.
- State the limits of `--check`: `command`/`shell` are skipped, dependent tasks can fail, and `check_mode: false` on read-only tasks makes dry runs genuinely useful. That nuance is the difference between reading docs and using the tool.
- For "how do you view the log while it runs?", give both answers - verbosity and `ANSIBLE_LOG_PATH`/`log_path` with `tail -f` - and mention `profile_tasks` for finding the slow task.
- Explain `block`/`rescue`/`always` as try/except/finally with a concrete example (drain, upgrade, roll back on failure, always re-enable). If `release_on` comes up, say honestly that it is not an Ansible keyword and offer `always` and `any_errors_fatal`/`max_fail_percentage` as what is probably meant. Being straight about that is better than bluffing.
- Define idempotency as "the second run reports changed=0" and name the usual culprits, especially unguarded `shell` and quoted-versus-unquoted file modes.
- Explain passing data between tasks with `register` (persists for the host across blocks) and `hostvars` for cross-host values.
- Diagnose "yum: command not found" as wrong-module-for-OS, missing interpreter, or a `PATH`/`become` issue, and recommend `ansible.builtin.package`.
- Mention the task debugger (`debugger: on_failed`) and Molecule's idempotence scenario - both are things most candidates have never used. See [structuring an Ansible role](./how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md), [managing inventories and variables](./how-do-you-manage-ansible-inventories-and-variables-across-environments.md), [running Ansible at scale](./how-do-you-run-ansible-at-scale-across-thousands-of-hosts.md), and [what is Ansible](../infrastructure-as-code/what-is-ansible.md).

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
