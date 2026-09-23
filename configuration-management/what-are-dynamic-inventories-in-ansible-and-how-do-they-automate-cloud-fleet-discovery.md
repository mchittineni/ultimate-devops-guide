---
title: "What are Dynamic Inventories in Ansible and how do they automate cloud fleet discovery?"
id: 587
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - ansible
  - inventory
  - cloud
  - dynamic-inventory
quiz:
  stem: "Why are static inventory files (`hosts.ini`) unsuitable for configuration management in modern cloud autoscaling environments?"
  options:
    - "Ansible cannot parse plain text files"
    - "Instances are dynamically created and destroyed with ephemeral IP addresses, causing static inventories to drift instantly"
    - "Static inventories only work on Windows servers"
    - "Cloud providers block access to files ending in `.ini`"
  answer: 2
  explanation: "Autoscaling groups continuously spin up and terminate instances with dynamic private IPs. Dynamic inventory plugins query cloud APIs in real-time to discover live instances by tag."
---

# What are Dynamic Inventories in Ansible and how do they automate cloud fleet discovery?

**Short answer:** Dynamic Inventories query cloud provider APIs (AWS EC2, Azure VMs, GCP Compute) at runtime to discover currently running instances based on tags, regions, and autoscaling groups, eliminating brittle static IP lists.

## Detail

In auto-scaled cloud environments, virtual machines are created and destroyed continuously. Maintaining a static `hosts.ini` with hard-coded IP addresses is impossible.

### How Dynamic Inventory Plugins Work

Ansible uses YAML-configured inventory plugins (`amazon.aws.aws_ec2`, `azure.azcollection.azure_rm`, `google.cloud.gcp_compute`), shipped in their cloud collections. The config file name must end in the plugin's expected suffix (`aws_ec2.yml`/`aws_ec2.yaml`), or the plugin silently ignores it:

```yaml
# aws_ec2.yaml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
filters:
  instance-state-name: running
keyed_groups:
  - key: tags.Environment
    prefix: env
  - key: tags.Role
    prefix: role
```

### Execution

When you run `ansible-playbook -i aws_ec2.yaml deploy.yml`:

1. The plugin calls the AWS EC2 `DescribeInstances` API.
2. Dynamically groups hosts into groups like `env_production` and `role_webserver`.
3. Targets only healthy, currently running instances without requiring manual inventory updates.

### Trade-offs

- **Tags become targeting.** A mistyped or missing `Environment` tag moves a host into (or out of) the group a playbook targets, so enforce tags in Terraform or with cloud policy.
- **API cost and latency.** Every run calls the cloud APIs across all listed regions; on large estates enable the inventory cache (`cache: true`, `cache_timeout`) to avoid slow runs and rate limiting, accepting that the cache can be briefly stale.
- **Credentials.** The control node needs read access to the cloud API (an instance profile, OIDC, or a scoped role), in addition to SSH access to the hosts.

## Example

```yaml
# inventories/prod/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions: [us-east-1, eu-west-1]
filters:
  instance-state-name: running
  tag:Environment: production
keyed_groups:
  - key: tags.Role
    prefix: role # -> role_webserver, role_db
  - key: placement.region
    prefix: region
hostnames:
  - tag:Name
  - private-ip-address
compose:
  ansible_host: private_ip_address # connect over the private network
cache: true
cache_plugin: ansible.builtin.jsonfile
cache_connection: /tmp/aws_inventory_cache
cache_timeout: 300
```

```bash
ansible-galaxy collection install amazon.aws           # the plugin lives in the collection
ansible-inventory -i inventories/prod/aws_ec2.yml --graph
ansible-playbook -i inventories/prod/aws_ec2.yml deploy.yml --limit role_webserver --list-hosts
```

## Interview tips

- Explain the mechanism: the plugin queries the cloud API at run time and builds hosts, groups (`keyed_groups`), and host variables (`compose`) from instance metadata.
- Point out that tagging discipline becomes inventory correctness, and how you would enforce it.
- Mention caching for large estates, and the file-name suffix requirement - a classic "why is my inventory empty?" cause.
- Prefer inventory plugins over legacy `ec2.py`-style inventory scripts.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
