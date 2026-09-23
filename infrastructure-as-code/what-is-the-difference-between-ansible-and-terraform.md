---
title: "What is the difference between Ansible and Terraform?"
id: 29
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# What is the difference between Ansible and Terraform?

**Short answer:** Terraform provisions and manages the lifecycle of infrastructure declaratively with state; Ansible configures what runs inside and on top of that infrastructure procedurally without state. They are complements, not competitors.

## Detail

|                | Terraform                                          | Ansible                                           |
| -------------- | -------------------------------------------------- | ------------------------------------------------- |
| Primary job    | Provisioning infrastructure                        | Configuration management, app deployment          |
| Model          | Declarative, desired state                         | Procedural tasks that are individually idempotent |
| State          | Explicit state file, tracks and destroys resources | Stateless; queries current system each run        |
| Language       | HCL                                                | YAML playbooks                                    |
| Agent          | None (provider APIs)                               | None (SSH/WinRM)                                  |
| Change preview | `terraform plan`                                   | `--check --diff`                                  |
| Deletion       | Knows what it created; `destroy` works             | No inherent record; removal must be scripted      |
| Best at        | VPCs, clusters, databases, DNS, IAM                | Packages, config files, services, rolling ops     |

The important structural difference is **state**. Terraform knows exactly which resources it owns, so removing a resource block deletes real infrastructure. Ansible has no such ledger - deleting a task from a playbook simply stops managing that thing.

**The common pattern:** Terraform builds the VPC, subnets, load balancers, and instances, then hands the inventory to Ansible to configure the instances. In a container world the split shifts - Terraform builds the cluster, and configuration moves into images and Kubernetes manifests, reducing Ansible's role to node-level or legacy estate work.

The overlap is real at the edges: Ansible has cloud modules (`amazon.aws.ec2_instance` with `state: present/absent`) and Terraform can bootstrap instances with `user_data`. Using Ansible for provisioning works for small estates but gives you no plan and no record of what to delete; using Terraform for in-guest configuration means provisioners, which are a last resort.

## Example

```hcl
# Terraform: create the instances and publish an inventory for Ansible
resource "aws_instance" "web" {
  for_each      = toset(["a", "b"])
  ami           = data.aws_ami.al2023.id
  instance_type = "t3.small"
  tags          = { Name = "web-${each.key}", Role = "web" }
}

output "web_private_ips" {
  value = [for i in aws_instance.web : i.private_ip]
}
```

```bash
# Ansible: configure what runs on them, discovered by tag rather than hard-coded
terraform apply
ansible-inventory -i inventory/aws_ec2.yml --graph        # amazon.aws.aws_ec2 plugin, filtered on tag:Role=web
ansible-playbook -i inventory/aws_ec2.yml web.yml --check --diff
ansible-playbook -i inventory/aws_ec2.yml web.yml
```

## Interview tips

- Refuse the false dichotomy: "they solve different problems, and most estates run both."
- Say why Terraform should not be used for in-guest configuration (provisioners are an escape hatch, not a design).
- Mention that immutable infrastructure - bake an image with Packer, replace instead of configure - reduces the need for runtime configuration management altogether.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
