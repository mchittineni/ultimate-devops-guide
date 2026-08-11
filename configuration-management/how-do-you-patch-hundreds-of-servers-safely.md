---
title: "How do you patch hundreds of servers safely?"
id: 430
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
  - linux-administration
  - security-and-compliance
  - scripting-and-automation
---

# How do you patch hundreds of servers safely?

**Short answer:** Patch in **waves with health gates**, never all at once. Concretely: know your inventory and current patch level, pin to a **frozen repository snapshot** so every host gets an identical set of packages, test on a canary group, then roll in batches (`serial` in Ansible, or an instance-refresh percentage) taking each host **out of the load balancer before patching and back in only after a health check passes**. Handle reboots explicitly - `needs-restarting`/`checkrestart` tells you whether the kernel or a library actually requires one - and stop the whole run on the first batch failure rather than continuing into a fleet-wide outage. On modern estates the better answer is often not to patch at all: **rebuild an immutable image and replace the instances**, because that removes both the drift and the partial-failure problem.

## Detail

### Before you patch anything

- **Inventory that is actually accurate** - a dynamic inventory from the cloud API or a CMDB, not a static file, or you will patch 340 of 400 hosts and never know which 60 you missed.
- **Know the current state.** Which hosts are at which package versions, which have pending reboots, which are lagging. This is also your compliance evidence.
- **Pin the package set.** Point every host at a **snapshot** of the repository (a mirror with a date-stamped snapshot, `--releasever` pinning, or a Satellite/Pulp content view) so hosts patched on Tuesday and Thursday get identical packages. Otherwise "the same playbook" produces different results per host and you cannot reproduce a failure.
- **Decide scope explicitly.** Security-only updates (`dnf update --security`, `unattended-upgrade` with security origins) is a far smaller change than a full `upgrade`, and for most fleets is the right default cadence.

### The rollout mechanics

1. **Canary first** - a handful of non-critical hosts, ideally covering each distinct role and OS version. Bake for hours or a day, not minutes.
2. **Batches with a gate.** Ansible's `serial` (with a percentage or a ramp such as `[1, 5, "25%"]`) plus `max_fail_percentage: 0` and `any_errors_fatal` so the run stops rather than continuing. Order matters for clustered services: never take two members of a quorum in the same batch.
3. **Drain, patch, verify, return.** For anything behind a load balancer: deregister the host, wait for connections to drain, patch, reboot if needed, run a real health check, then re-register. `pre_tasks`/`post_tasks` with a `delegate_to` on the load balancer is the idiomatic Ansible shape.
4. **Reboots on purpose.** Detect need (`needs-restarting -r` on RHEL, `/var/run/reboot-required` on Debian) rather than rebooting blindly or never. Kernel and glibc updates need a reboot; a userspace library often just needs its services restarted (`needs-restarting -s`, `checkrestart`). Live-patching (kpatch, Canonical Livepatch) defers kernel reboots but does not eliminate them.
5. **Verify, don't assume.** After each batch: the service is up and serving, the package version is what you expected, error rates and latency are normal, and the reboot actually completed (`wait_for_connection` plus an application-level check, not just SSH being back).
6. **Stop on failure and leave the fleet in a known state.** A partially-patched fleet is acceptable and recoverable; a fleet where 200 hosts are broken because the run kept going is not.

### Rollback, honestly

Package rollback is weaker than people assume. `dnf history undo` and `apt install pkg=version` work for simple cases; they do not reliably undo a configuration migration, a database schema change made by a package, or a kernel that changed a driver. So plan around it:

- **Snapshot before patching** where the platform allows - an EBS snapshot, a VM snapshot, or an LVM/btrfs/ZFS snapshot with a boot-time rollback path.
- **For immutable fleets**, rollback is redeploying the previous image - which is the strongest reason to prefer that model.
- **Keep the previous kernel installed** so you can boot the old one from GRUB.
- Decide the abort criteria and who can call it **before** the run starts.

### The three ways teams actually do this

| Approach                                                                        | Good for                                          | Cost                                                  |
| ------------------------------------------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------- |
| **Ansible/Chef/Puppet against live hosts**                                      | Long-lived VMs, mixed estates, pets               | Drift persists; partial failures; rollback is weak    |
| **Managed patch services** (SSM Patch Manager, Azure Update Manager, Satellite) | Compliance reporting, scheduled windows, mixed OS | Less control over ordering; still mutating live hosts |
| **Immutable image replacement** (Packer + instance refresh)                     | Autoscaled, stateless fleets                      | Needs an image pipeline and stateless workloads       |

The senior answer names the third and explains _why_: patching mutates state and can half-fail, whereas replacing an instance is a deployment you already know how to roll back. Where hosts are stateful or long-lived, configuration management remains the pragmatic tool - and it belongs in the image build too. See [what is immutable infrastructure and how do you adopt it](../infrastructure-as-code/what-is-immutable-infrastructure-and-how-do-you-adopt-it.md) and [how do you run Ansible at scale across thousands of hosts](./how-do-you-run-ansible-at-scale-across-thousands-of-hosts.md).

### Making it continuous rather than a quarterly panic

Patch on a schedule the fleet is used to (weekly security, monthly full) so the path is exercised constantly; auto-apply security updates on non-critical tiers; report coverage and mean time to patch as metrics; and drive urgency from **exploitability**, not CVE count - a critical remote code execution on an internet-facing host is an incident, a medium in a package you do not load is a ticket. See [how do you prioritise vulnerabilities without blocking delivery](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md).

## Example

```yaml
# Batched, gated, load-balancer-aware patching that stops on the first failure
- name: Patch web tier
  hosts: web
  become: true
  serial: [1, 5, "25%"] # canary -> small batch -> ramp
  max_fail_percentage: 0 # any failure stops the whole run
  order: shuffle # avoid always hitting the same host first
  vars:
    patch_snapshot: "2026-08-01" # frozen repo snapshot: identical packages for all

  pre_tasks:
    - name: Remove from the load balancer and let connections drain
      community.aws.elb_target_group_info: # (delegate to a control host)
      delegate_to: localhost
      # ...deregister this instance, then:
    - name: Wait for in-flight requests to finish
      ansible.builtin.wait_for: { timeout: 45 }

  tasks:
    - name: Apply security updates only, from the pinned snapshot
      ansible.builtin.dnf:
        name: "*"
        state: latest
        security: true
        releasever: "{{ patch_snapshot }}"
      register: patch_result

    - name: Does anything actually require a reboot?
      ansible.builtin.command: needs-restarting -r
      register: needs_reboot
      changed_when: false
      failed_when: needs_reboot.rc not in [0, 1]

    - name: Reboot only if required, and wait for the app - not just for SSH
      when: needs_reboot.rc == 1
      block:
        - ansible.builtin.reboot: { reboot_timeout: 900 }
        - ansible.builtin.uri:
            url: "http://127.0.0.1:8080/healthz"
            status_code: 200
          retries: 30
          delay: 10

  post_tasks:
    - name: Return to the load balancer only after a real health check
      ansible.builtin.uri: { url: "http://127.0.0.1:8080/healthz", status_code: 200 }
    # ...then re-register the target and confirm it reaches healthy state
```

```bash
# Know the fleet before and after - this is also your compliance evidence
ansible web -m ansible.builtin.shell -a 'dnf updateinfo list security --quiet | wc -l' \
  --one-line | sort -k2 -n | tail          # who is furthest behind?

ansible web -m ansible.builtin.shell -a 'needs-restarting -r; echo rc=$?' --one-line
ansible web -m ansible.builtin.shell -a 'uname -r; rpm -q openssl' --one-line | sort -u
# a single unexpected version here means the pinning or the inventory is wrong

# Rollback options, weakest to strongest
dnf history list && sudo dnf history undo last     # simple package cases only
sudo grub2-reboot 1 && sudo reboot                # boot the previous kernel
aws ec2 create-snapshot --volume-id vol-0abc ...   # take this BEFORE patching
```

## Interview tips

- Lead with waves and health gates. "I would run it across all 400 hosts overnight" is the answer this question is designed to catch.
- The repository snapshot / pinning point is the detail that marks experience: without it, the same playbook produces different package sets on different days and failures are irreproducible.
- Say the load-balancer dance explicitly - deregister, drain, patch, health-check, re-register - and note that clustered services need batch ordering so you never take two quorum members at once.
- Handle reboots as a decision, not a default: detect with `needs-restarting -r` or `/var/run/reboot-required`, and distinguish a kernel update from a library update that only needs a service restart.
- Be honest about rollback being weak for packages, and give the real mitigations: snapshots, keeping the previous kernel, and image replacement.
- `serial` plus `max_fail_percentage: 0` is the concrete Ansible answer - it shows you know how to make a run stop rather than plough on.
- Volunteer the immutable alternative and why it is better where the workload allows: replacing an instance is a deployment with a known rollback, whereas patching mutates state and can half-fail.
- Close on cadence and prioritisation: frequent small patch runs beat quarterly big ones, and urgency comes from exploitability and exposure rather than CVE counts. See [how do you manage services in Linux](../linux-administration/how-do-you-manage-services-in-linux.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
