---
title: "How does Ansible architecture work without agents and how does it execute tasks over SSH?"
id: 584
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - ansible
  - architecture
  - agentless
  - ssh
quiz:
  stem: "What software prerequisites must be present on a remote target Linux host for standard Ansible management?"
  options:
    - "An active Ansible Daemon process running on port 8080"
    - "A standard SSH server (OpenSSH) and a Python interpreter"
    - "A local Docker engine and Kubernetes cluster"
    - "An active PostgreSQL database connection"
  answer: 2
  explanation: "Ansible's agentless architecture connects via standard OpenSSH and executes dynamically generated module payloads using the target's existing Python interpreter."
---

# How does Ansible architecture work without agents and how does it execute tasks over SSH?

**Short answer:** Ansible is agentless; it uses SSH (or WinRM) to connect to target hosts, generates standalone temporary Python scripts containing the task module and parameters, transfers them over SFTP/SCP, executes them on the target, and parses the returned JSON results.

## Detail

Unlike Puppet or Chef which require installing, upgrading, and securing a background daemon (agent) on every target node, Ansible operates completely agentless.

### The Step-by-Step Execution Lifecycle

1. **Inventory Parsing**: Ansible reads inventory files (`hosts.ini`, dynamic cloud plugins) and variable files.
2. **Playbook Compilation**: Compiles the play, resolves variable precedence, and determines task ordering.
3. **Module Packaging**: For each task (e.g. `ansible.builtin.copy`), Ansible packages the Python module code, its `module_utils` dependencies, and the arguments into a self-contained payload (the **AnsiballZ** wrapper, a zipped Python script).
4. **SSH Transfer & Execution**:
   - Opens an SSH connection to the remote host.
   - Writes the script to a temporary directory (e.g., `~/.ansible/tmp/...`) via SFTP or SCP - or, with `pipelining = True`, skips the file entirely and streams the payload to the interpreter's stdin, cutting SSH round trips per task.
   - Executes the script using the remote host's Python interpreter, found by interpreter discovery (`/usr/bin/python3` on modern distributions) or set with `ansible_python_interpreter`.
5. **Output Parsing & Cleanup**:
   - The script emits a JSON string to `stdout` containing `{"changed": true, "rc": 0}`.
   - Ansible deletes the remote temporary directory. With OpenSSH `ControlPersist` (on by default in Ansible's SSH arguments) the connection is kept open and reused for the next task instead of reconnecting.

### Exceptions to "SSH + Python"

- **Windows** hosts are managed over WinRM or OpenSSH, and modules are PowerShell, not Python.
- **Network devices** (`network_cli`, `netconf`, `httpapi` connections) run the module logic on the **control node** and send CLI/API commands to a device that has no Python at all.
- **`raw`** and `script` modules work without Python on the target - which is how you bootstrap Python onto a minimal host.

### Trade-offs of the agentless model

No agent means no daemon to install, patch, or secure, and nothing running between runs. The price: configuration is enforced only when a run happens (no continuous convergence unless you schedule runs, or use `ansible-pull` on each host), every task costs network round trips so large fleets need tuning (`forks`, pipelining, fact caching), and the control node needs SSH reachability and credentials to every host - making it a high-value target.

## Example

```bash
# Watch the mechanism: -vvv shows the SSH command, the temp dir, and the payload execution
ansible web-01 -m ansible.builtin.ping -vvv
# <web-01> SSH: EXEC ssh -C -o ControlMaster=auto -o ControlPersist=60s ...
# <web-01> PUT .../AnsiballZ_ping.py TO /home/deploy/.ansible/tmp/.../AnsiballZ_ping.py
# <web-01> EXEC /bin/sh -c '/usr/bin/python3 .../AnsiballZ_ping.py && sleep 0'
# web-01 | SUCCESS => {"changed": false, "ping": "pong"}

# Bootstrap a host that has no Python yet, then use normal modules
ansible new-host -m ansible.builtin.raw -a 'dnf install -y python3' --become
```

```ini
# ansible.cfg - fewer round trips per task
[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=300s
```

## Interview tips

- Walk the per-task lifecycle: build the AnsiballZ payload, copy (or pipe) it, execute with the remote Python, read JSON back, clean up.
- Name the prerequisites precisely - SSH access and a Python interpreter - and the exceptions (Windows/PowerShell, network devices, `raw`).
- Mention pipelining and ControlPersist as the reasons Ansible is not as slow as "SSH per task" suggests; note pipelining requires `requiretty` to be disabled in sudoers.
- Give the trade-off: no agent to manage, but no continuous enforcement and a control node that holds keys to everything.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
