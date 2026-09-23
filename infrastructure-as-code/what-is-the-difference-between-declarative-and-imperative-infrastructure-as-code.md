---
title: "What is the difference between declarative and imperative Infrastructure as Code?"
id: 553
category: "Infrastructure as Code"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - iac
  - declarative
  - imperative
  - ansible
  - terraform
quiz:
  stem: "What is the primary benefit of declarative IaC over imperative bash scripts when applying changes repeatedly?"
  options:
    - "Declarative code compiles directly to C libraries"
    - "Declarative tools are inherently idempotent: they inspect the existing state and execute only the delta needed to match desired state"
    - "Declarative code cannot be stored in Git repositories"
    - "Declarative scripts execute without network connectivity"
  answer: 2
  explanation: "Declarative tools compute the diff between desired state and reality. If the resource already exists in the desired configuration, running the tool makes zero changes (idempotency)."
---

# What is the difference between declarative and imperative Infrastructure as Code?

**Short answer:** Declarative IaC specifies the desired end state of infrastructure without describing how to get there (e.g., Terraform, CloudFormation); Imperative IaC specifies the exact sequence of step-by-step commands to achieve that state (e.g., Bash scripts, AWS CLI commands).

## Detail

The distinction defines how tools handle convergence and drift:

| Feature           | Declarative (Terraform, Kubernetes, CloudFormation)         | Imperative (Bash, AWS CLI, Python Boto3)                      |
| ----------------- | ----------------------------------------------------------- | ------------------------------------------------------------- |
| Focus             | **What** the system should look like                        | **How** to execute specific changes                           |
| Execution         | Tool determines dependency graph and reconciles differences | Operator defines the exact procedural order                   |
| Repeatability     | Idempotent: running twice results in no changes             | Non-idempotent unless manually scripted with guard checks     |
| Drift Remediation | Compares state to reality and restores desired state        | Blindly repeats commands; may fail if resource already exists |

Most real tools blur the line. Ansible is procedural (tasks run in order) but its modules are declarative (`state: present`). Pulumi and the AWS CDK let you write loops and functions in TypeScript or Python, but they produce a declarative desired-state model that an engine diffs, so they behave declaratively at apply time.

### Trade-offs

Declarative tools give idempotency, drift detection, and a reviewable plan, at the cost of needing a state model (a state file, or the cloud's own API as in Kubernetes), and of being awkward for genuinely sequential operations - a database failover, a data migration, a rolling restart with checks between steps. Imperative scripts are simple and explicit for one-off, ordered procedures, but every re-run is a new risk unless each step is guarded.

## Example

```bash
# Imperative: describes the steps. Run it twice and you get two instances.
aws ec2 run-instances --image-id ami-0123456789abcdef0 --instance-type t3.micro \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web}]'
```

```hcl
# Declarative: describes the end state. Run it twice and the second plan is empty.
resource "aws_instance" "web" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  tags          = { Name = "web" }
}
```

## Interview tips

- Define both by what you write: the destination (declarative) versus the route (imperative).
- Tie declarative to idempotency and drift detection, and explain the mechanism - the tool compares desired state to current state and executes only the difference.
- Show nuance: Ansible modules are declarative inside a procedural playbook; Pulumi/CDK are imperative languages generating a declarative model.
- Give a case where imperative is the right tool - an ordered, one-off operational procedure - so the answer does not sound dogmatic.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Idempotency in configuration management and why is it essential for infrastructure stability?]] (`#583`): [What is Idempotency in configuration management and why is it essential for infrastructure stability?](../configuration-management/what-is-idempotency-in-configuration-management-and-why-is-it-essential-for-infrastructure-stability.md)
- [[How does Ansible architecture work without agents and how does it execute tasks over SSH?]] (`#584`): [How does Ansible architecture work without agents and how does it execute tasks over SSH?](../configuration-management/how-does-ansible-architecture-work-without-agents-and-how-does-it-execute-tasks-over-ssh.md)
- [[What is the difference between mutable and immutable infrastructure in modern deployment patterns?]] (`#586`): [What is the difference between mutable and immutable infrastructure in modern deployment patterns?](../configuration-management/what-is-the-difference-between-mutable-and-immutable-infrastructure-in-modern-deployment-patterns.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
