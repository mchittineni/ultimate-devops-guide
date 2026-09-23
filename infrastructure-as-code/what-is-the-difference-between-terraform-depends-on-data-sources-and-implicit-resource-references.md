---
title: "What is the difference between Terraform depends_on, data sources, and implicit resource references?"
id: 549
category: "Infrastructure as Code"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - iac
  - terraform
  - dependencies
  - graph
quiz:
  stem: "When is using an explicit `depends_on` argument necessary in a Terraform configuration?"
  options:
    - "Whenever creating more than two resources in the same file"
    - "When a resource has a behavioral dependency on another resource (such as an IAM policy attachment) that is not referenced via an attribute"
    - "When referencing an output from a data source"
    - "To force Terraform to execute in reverse alphabetical order"
  answer: 2
  explanation: "Terraform's graph automatically orders resources linked by attribute references (`aws_vpc.main.id`). `depends_on` is only required when a hidden dependency exists (e.g., an IAM role attachment must finish before a VM starts)."
---

# What is the difference between Terraform depends_on, data sources, and implicit resource references?

**Short answer:** Implicit references establish dependencies naturally when one resource references an attribute of another (`vpc_id = aws_vpc.main.id`); Data sources query existing infrastructure outside the current state; `depends_on` is an explicit override used only when hidden dependencies exist that Terraform's DAG cannot infer.

## Detail

Terraform builds a Directed Acyclic Graph (DAG) to determine the parallel execution order of resource creation.

### 1. Implicit Dependencies (Preferred)

```hcl
resource "aws_subnet" "web" {
  vpc_id     = aws_vpc.main.id # Terraform automatically creates aws_vpc.main first!
  cidr_block = "10.0.1.0/24"
}
```

Terraform automatically knows `aws_vpc.main` must be created before `aws_subnet.web`.

### 2. Data Sources

Queries resources provisioned elsewhere (e.g. by another team or cloud console):

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}
```

Data sources are normally read during `plan`. If a data source depends on something not yet known (an attribute of a resource being created, or an explicit `depends_on`), Terraform defers the read to `apply` and everything downstream shows as "known after apply" - which is why `depends_on` on a data source makes plans noisier and less useful.

### 3. Explicit `depends_on` (Use Sparingly)

Used only when an application depends on a permission or background service that is not referenced in the resource's arguments:

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  depends_on    = [aws_iam_role_policy_attachment.s3_access]
}
```

Without `depends_on`, the EC2 instance might boot before IAM permissions are attached, causing startup script failures.

### Trade-offs

`depends_on` is coarse: it makes the dependant wait for _every_ change to the whole target (on a module, every resource inside it), serialises work that could run in parallel, and on data sources defers reads to apply time. Prefer an implicit reference whenever one exists - even passing an attribute through purely to create the edge is clearer than `depends_on` - and leave a comment explaining any `depends_on` you keep.

## Example

```hcl
resource "aws_iam_role" "app" {
  name               = "app"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json # implicit: data source -> role
}

resource "aws_iam_role_policy_attachment" "s3_read" {
  role       = aws_iam_role.app.name # implicit: role -> attachment
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_instance_profile" "app" {
  name = "app"
  role = aws_iam_role.app.name
}

resource "aws_instance" "app" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.app.name # implicit: profile -> instance
  # the boot script needs S3 access, but nothing here references the attachment:
  depends_on = [aws_iam_role_policy_attachment.s3_read] # hidden, behavioural dependency
}
```

```bash
terraform graph | grep -E 'aws_instance.app|s3_read'   # inspect the edges Terraform built
```

## Interview tips

- Explain the DAG: references create edges, Terraform walks the graph in parallel (default 10) and orders only what is connected.
- Say implicit references are preferred and `depends_on` is for behavioural dependencies with no data flow - the IAM attachment before boot is the classic example.
- Know that `depends_on` on a data source defers the read to apply time, and on a module waits for everything inside it.
- Distinguish data sources (read-only lookups, not managed, not destroyed) from resources.
- Likely follow-up: "what does a dependency cycle error mean?" - two resources reference each other; break it by splitting a resource (for example separate security group rule resources) or removing one reference.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between mutable and immutable infrastructure in modern deployment patterns?]] (`#586`): [What is the difference between mutable and immutable infrastructure in modern deployment patterns?](../configuration-management/what-is-the-difference-between-mutable-and-immutable-infrastructure-in-modern-deployment-patterns.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)
- [[How do you design least-privilege identity in the cloud?]] (`#217`): [How do you design least-privilege identity in the cloud?](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
