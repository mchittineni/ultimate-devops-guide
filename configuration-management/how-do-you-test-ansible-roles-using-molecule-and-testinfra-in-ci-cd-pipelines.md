---
title: "How do you test Ansible roles using Molecule and testinfra in CI/CD pipelines?"
id: 588
category: "Configuration Management"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - ansible
  - testing
  - molecule
  - testinfra
  - cicd
quiz:
  stem: "What does the `idempotence` phase of a `molecule test` execution specifically verify?"
  options:
    - "That the role installs in under ten seconds"
    - "That executing the role a second time against the target results in zero changed tasks"
    - "That the Docker daemon has not run out of memory"
    - "That all YAML files pass indentation checks"
  answer: 2
  explanation: "Molecule's idempotence check applies the role a second consecutive time and asserts that `changed=0`. If any task reports a change, the test fails because the role is not truly idempotent."
---

# How do you test Ansible roles using Molecule and testinfra in CI/CD pipelines?

**Short answer:** Molecule automates testing of Ansible roles by spinning up ephemeral test instances (containers or VMs), applying the role, testing idempotency (verifying zero changes on re-run), and executing assertion tests (Ansible `assert` tasks by default, or Testinfra) before destroying the test environment. Linting (`ansible-lint`, `yamllint`) runs as a separate CI step - Molecule dropped its built-in `lint` stage.

## Detail

Testing Ansible roles in production leads to catastrophic configuration breakages. Molecule provides a standardized test harness:

### The Molecule Test Matrix Lifecycle

```bash
molecule test
```

Executes the following automated phases:

1. **`dependency`**: Downloads required Galaxy collections and roles.
2. **`cleanup` / `destroy`**: Clears any leftovers from a previous run.
3. **`syntax`**: `ansible-playbook --syntax-check` on the converge playbook.
4. **`create`** and **`prepare`**: Launch clean ephemeral instances (Podman/Docker containers or VMs via the `molecule-plugins` drivers, or your own playbooks with the default `delegated` driver) and prepare them.
5. **`converge`**: Applies the role against the instances.
6. **`idempotence`**: Runs the role a second time and **fails if any task reports 'changed'**!
7. **`side_effect`** (optional): Simulate failures - restart a service, kill a node - before verifying.
8. **`verify`**: Asserts system state. The default verifier is Ansible itself (a `verify.yml` of `assert`/`uri` tasks); the Testinfra verifier (`verifier: name: testinfra`, installed separately) runs Python `pytest` assertions:

   ```python
   def test_nginx_is_installed(host):
       nginx = host.package("nginx")
       assert nginx.is_installed

   def test_nginx_running_and_enabled(host):
       nginx = host.service("nginx")
       assert nginx.is_running
       assert nginx.is_enabled
   ```

9. **`cleanup` / `destroy`**: Cleans up and deletes test instances.

### Limits and trade-offs

Containers are fast but are not real machines: no real systemd by default (you need a systemd-enabled image and extra privileges), no kernel modules, different networking - so roles that manage services, firewalls, or kernels may need VM-based scenarios or a cloud driver, which are slower and cost money. A green Molecule run proves the role converges and is idempotent on the images you tested, not on every host in production; keep the platform matrix aligned with `meta/main.yml`.

## Example

```yaml
# roles/nginx/molecule/default/molecule.yml
driver:
  name: podman # from molecule-plugins[podman]
platforms:
  - name: el9
    image: docker.io/geerlingguy/docker-rockylinux9-ansible:latest # systemd-enabled image
    command: /usr/sbin/init
    systemd: always
  - name: noble
    image: docker.io/geerlingguy/docker-ubuntu2404-ansible:latest
    command: /lib/systemd/systemd
    systemd: always
provisioner:
  name: ansible
verifier:
  name: testinfra # tests live in molecule/default/tests/test_*.py
```

```yaml
# .github/workflows/role-ci.yml
name: role-ci
on: [pull_request]
jobs:
  molecule:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
      - run: pip install ansible-core ansible-lint yamllint molecule "molecule-plugins[podman]" pytest-testinfra
      - run: yamllint . && ansible-lint # linting is its own step, not a Molecule stage
      - run: molecule test --all
        env:
          PY_COLORS: "1"
          ANSIBLE_FORCE_COLOR: "1"
```

## Interview tips

- Walk the lifecycle in order and put the weight on `idempotence` - the second converge must report `changed=0`.
- Know that the default verifier is Ansible and Testinfra is optional; say when you would pick each (Testinfra for rich pytest assertions, Ansible verify to stay in one language).
- Mention that `molecule lint` no longer exists - run `ansible-lint` and `yamllint` as separate CI steps.
- Be honest about container fidelity: systemd, kernel, and firewall behaviour may need VM scenarios.
- Likely follow-up: "how do you test multiple distributions?" - multiple `platforms` in one scenario, or a CI matrix over scenarios.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?]] (`#536`): [How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?](../cicd/how-do-you-detect-isolate-and-eradicate-flaky-tests-in-a-ci-cd-pipeline.md)
- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
