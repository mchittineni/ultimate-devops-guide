---
title: "What DevOps interview questions does Capgemini ask?"
id: 323
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - capgemini
  - configuration-management
  - kubernetes
  - aws-engineering
  - azure-engineering
  - infrastructure-as-code
  - version-control
  - database-management-in-devops
  - cicd
---

# What DevOps interview questions does Capgemini ask?

## Questions

### Round 1 — internals (6+ years overall, 3 in DevOps)

- **How do you assign memory to a Pod, how do you make sure it never hits a memory constraint, and what do you do when it does?**
- **How do you pass variables into an Azure pipeline, and how do you parameterise a pipeline?**
- **What is an availability zone? Explain the physical layout on the ground, in depth.**
- **How does MySQL interact with Azure Key Vault so that the traffic stays private and nothing traverses the public internet?**
- **What is the difference between `git fetch` and `git pull` — what happens in the background in each case?**
- **What happens under the hood when you run `git add`? The file is staged, but how does Git know what to do, and what changes in Git's object database?**

### Round 2 — Ansible, Kubernetes, AWS (9 years, 5 in DevOps)

**Ansible**

- **What is an Ansible playbook?**
- **How do you install Ansible on Ubuntu and on RedHat, and how do you start the services?**
- **How do you create three users and map them to the `prod`, `task`, and `QA` groups in a single task?**
- **How do you include and pass input parameters into a playbook?**
- **What are Ansible roles?**
- **What are templates used for in Ansible?**
- **What is the difference between a template and a role?**
- **How do you initialise a role and publish it to Ansible Galaxy for public use?**
- **How do you encrypt a playbook?**
- **How do you execute an encrypted Vault file?**
- **How do you use an environment variable to supply a password?**
- **How do you take a MySQL dump of encrypted data using an Ansible playbook, step by step?**
- **How do you run a play against all database servers except one?**
- **How do you shut down every server using a single ad-hoc command?**
- **How do you reduce playbook execution time against an RDBMS server, and how do you configure that from the Ansible side?**
- **How do you increase the debug log level?**
- **What is the difference between a static and a dynamic inventory?**

**Kubernetes**

- **What is the architecture of Kubernetes?**
- **What does `kubectl apply` do, and how are Services used with it?**
- **Walk me through a Deployment YAML file.**
- **What are labels and annotations, and how do they differ in purpose?**
- **How does traffic from outside reach a workload inside the cluster?**
- **What is the controller manager responsible for?**
- **What are node affinity and anti-affinity, and when do you use each?**
- **How do you run two Pods where one depends on the other, and how do you configure that ordering?**
- **What are taints and tolerations?**
- **Why would you taint a worker node?**
- **How do you limit resources in Kubernetes?**
- **Explain blue-green deployment.**
- **Explain canary deployment.**
- **What is the CSI, and what problem does it solve?**

**AWS**

- **What are Lambda and Step Functions, and when do you use each?**
- **What are the autoscaling policy types and what is each one for?**
- **What is the target tracking value — the "target" — in an autoscaling policy?**
- **Which IAM role do you use to grant access to AWS services from a workload?**
- **How do you attach an IAM role to a Kubernetes service account, end to end?**
- **How do you create a secret for a service account?**
- **What is the difference between static and dynamic storage provisioning?**
- **What kind of error do you get from a malformed Pod label?**

### Round 3 — AWS, RDS, and Terraform scenarios

- **What is the difference between a NAT gateway and an internet gateway?**
- **Your Pod is stuck in `Pending`. What are your troubleshooting steps?**
- **What is the difference between an RDS secondary (standby) and a read-only replica?**
- **Have you built RDS yourself, or only operated one somebody else built?**
- **As your client, I want the RDS configured so only one user can access it at a time. How would you configure that, and where would you set it?**
- **What is the process for upgrading an RDS database engine — say MySQL 7.0 to 8.0 or above?**
- **In a multi-account setup where resources live in one account and users in another, how do you configure access?**
- **You answered from the IAM angle — what about the VPC side of that same problem?**
- **How do you migrate an EC2 instance from one region to another?**
- **You try to create an EC2 instance and get an error that the IP address allocation has been exceeded. How do you troubleshoot and fix it?**
- **Can a subnet's CIDR be extended after it has been created?**
- **Once the new subnet exists and the instance is created there, will it be able to communicate with the older instances?**
- **What Terraform provisioners are there, and what is each used for?**
- **How do you remove a lock from the Terraform state file?**
- **You created an EC2 instance manually in the console and now want to manage it with Terraform. How do you do that?**
- **If `terraform import` handles existing AWS resources that Terraform did not create, what is the point of a data source?**
- **What are the different Service types in Kubernetes?**
- **In a multi-cloud environment, how would you stop a Pod from being scheduled onto a particular node?**
- **Explain PersistentVolumeClaims.**

## Example

```text
Capgemini — DevOps Engineer, three reported rounds

  ROUND 1 (3 yrs DevOps, internals)        6 questions
    Pod memory, Azure pipeline variables, availability-zone layout,
    MySQL <-> Key Vault privately, fetch vs pull internals, git add internals

  ROUND 2 (5 yrs DevOps, systematic)       39 questions
    Ansible                          17    roles, templates, Vault, Galaxy,
                                           inventories, ad-hoc, tuning
    Kubernetes                       14    architecture, affinity, taints,
                                           blue-green, canary, CSI
    AWS                               8    Lambda + Step Functions, ASG
                                           policies, IRSA, provisioning

  ROUND 3 (AWS/RDS/Terraform scenarios)    19 questions
    RDS deep-dive (5), cross-account access (2), EC2 region move,
    IP exhaustion + subnet CIDR (3), Terraform (4), Kubernetes (4)

THE OUTLIER
  Round 2's Ansible block is the most thorough in this whole collection.
  If Capgemini is your target and Ansible is weak, that is the gap to close.
```

## Interview tips

- The `git add` internals question is rare and highly rewarding. Say it precisely: `git add` computes the SHA-1 (or SHA-256) of the file's contents, writes a compressed blob into `.git/objects`, and records the path, mode, and that hash in the index at `.git/index`. Nothing is committed yet — the commit is what creates the tree and commit objects pointing at those blobs. Mention that identical content produces the same blob, so Git deduplicates automatically. See [what Git is](../version-control/what-is-git.md).
- Follow through on `fetch` versus `pull` with the same object-level framing: `fetch` downloads objects and moves the remote-tracking ref, leaving `HEAD` and the working tree untouched; `pull` then runs a merge or rebase to move your local branch. See [git merge, rebase, and cherry-pick](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md).
- On the Ansible block, be precise about the two-word distinctions. A template is a single Jinja2 file rendered onto a target; a role is a directory structure bundling tasks, handlers, templates, files, vars, and defaults for reuse. `ansible-galaxy init <name>` scaffolds a role. Static inventory is a checked-in file; dynamic inventory is a plugin or script that queries the cloud API so autoscaled hosts appear automatically. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- Several Ansible answers are one flag each, so know them cold: `--limit '!dbserver3'` or a pattern like `db:!db3` to exclude a host; `-vvv` for debug verbosity; `ansible all -m shell -a "shutdown -h now" -b` for the ad-hoc shutdown; `ansible-vault encrypt` plus `--ask-vault-pass` or `--vault-password-file` to run it; and `forks`, `pipelining`, plus `strategy: free` and `serial` to cut execution time. For passwords from the environment, a `lookup('env', 'DB_PASSWORD')` is the expected form.
- Creating three users mapped to three groups in one task is a loop question — a single `ansible.builtin.user` task with `loop` over a list of dictionaries carrying `name` and `groups`. Interviewers ask it to see whether you reach for a loop or write three tasks.
- The RDS single-user requirement is the trickiest question in round three and it has no clean managed answer, which is the point. Give the layers: restrict network reach with a security group allowing one source, grant privileges to exactly one database user, cap `max_connections` or the user's `MAX_USER_CONNECTIONS` in a parameter group, and use IAM database authentication so access is auditable. Then say plainly that RDS cannot enforce a hard single-session lock, so the honest answer is a combination of controls — naming the limitation scores better than inventing a setting. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- Secondary versus read replica: a Multi-AZ standby is a synchronous copy you cannot read from, existing purely for failover; a read replica is asynchronous, readable, can live in another region, and can be promoted. Say that the standby costs availability and the replica buys read throughput.
- The IP-exhaustion chain has two crisp facts you must get right: a subnet's CIDR **cannot** be resized after creation — you add a new subnet, or extend the VPC with an additional CIDR block — and instances in a new subnet in the same VPC **can** talk to older ones, because local routing between subnets is automatic, subject to route tables, NACLs, and security groups. Also mention that AWS reserves five addresses per subnet, and that on EKS the VPC CNI assigning an IP per Pod is the usual reason a subnet runs dry. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- Cross-account access is deliberately asked twice, from two angles. IAM: a role in the resource account with a trust policy naming the user account, assumed via `sts:AssumeRole`. VPC: the network path is separate — peering, Transit Gateway, or PrivateLink — because IAM authorises the API call but does not create connectivity. Making that separation explicit is what the follow-up is fishing for. See [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md).
- `import` versus data source is a genuinely good question: `import` brings a resource under Terraform's management so it will be changed or destroyed by your configuration, while a data source only _reads_ something owned elsewhere and never modifies it. Ownership is the distinction. See [importing existing cloud infrastructure into Terraform](../infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md).
- For the state lock, `terraform force-unlock <LOCK_ID>` is the command, but say the safety rule first: confirm no apply is genuinely running, because breaking a live lock is how state gets corrupted. See [recovering a lost or corrupted Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- Blocking a Pod from a node has three mechanisms and naming all three is the complete answer: taint the node so only tolerating Pods land there, use node affinity or anti-affinity on the workload, or exclude it by label with `nodeSelector`. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- Pod `Pending` almost always means the scheduler cannot place it: insufficient CPU or memory, no node matching the selector or affinity, an untolerated taint, or an unbound PVC. `kubectl describe pod` and read the events — say that first. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- MySQL reaching Key Vault privately is a private-endpoint question: a private endpoint for Key Vault inside the VNet, private DNS zone resolution so the vault's hostname resolves to the private address, and the vault firewall set to deny public access. The Azure equivalent of a VPC endpoint. See [defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
