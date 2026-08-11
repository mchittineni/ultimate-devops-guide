---
title: "How do you automate EC2 log shipping to S3 with IAM boundaries and CloudWatch?"
id: 236
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# How do you automate EC2 log shipping to S3 with IAM boundaries and CloudWatch?

**Short answer:** Automate EC2 log shipping to S3 by installing CloudWatch Agent or Fluent Bit on EC2 instances, assigning an IAM Instance Profile restricted by IAM Permission Boundaries, streaming logs to CloudWatch Logs or Kinesis Data Firehose, and leveraging S3 Lifecycle policies for long-term retention.

## Detail

Shipping EC2 application and system logs to S3 is a core production architecture requirement for security compliance, audit trails, and cost-effective log storage.

### 1. Log Collection Agent

- **CloudWatch Agent / Fluent Bit:** Installed on EC2 instance via user data script or Golden AMI (AMI baking with Packer).
- **Log Files Configured:** Tail application logs (`/var/log/nginx/access.log`, `/var/log/syslog`) and stream them to CloudWatch Log Groups or Kinesis Firehose.

### 2. IAM Roles & Permission Boundaries

To adhere to enterprise least privilege, the EC2 instance role must be constrained:

- **IAM Role & Instance Profile:** Grants `logs:PutLogEvents`, `logs:CreateLogStream`, and `s3:PutObject` permissions.
- **IAM Permission Boundary:** Attached to the role to ensure admin users or automated pipelines cannot escalate permissions beyond log shipping boundaries.

### 3. Delivery Pipelines: Direct vs Kinesis Firehose vs CloudWatch Export

- **Option A (Direct CloudWatch agent to CloudWatch → S3 Export):** CloudWatch Log Subscription Filters export logs periodically to S3.
- **Option B (Fluent Bit / Vector → Kinesis Data Firehose → S3):** High-throughput, low-latency streaming directly to S3 with dynamic partitioning by date/hour/environment.

## Example

IAM Policy with Permission Boundary restrictiveness and Fluent Bit config snippet:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowLogShippingToS3",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::company-prod-logs-bucket/ec2-logs/*"
    },
    {
      "Sid": "AllowCloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/ec2/*"
    }
  ]
}
```

Fluent Bit configuration on EC2 instance (`/etc/fluent-bit/fluent-bit.conf`):

```ini
[INPUT]
    Name        tail
    Path        /var/log/nginx/access.log
    Tag         nginx.access

[OUTPUT]
    Name        s3
    Match       nginx.*
    bucket      company-prod-logs-bucket
    region      us-east-1
    total_file_size 10M
    upload_timeout  1m
    use_put_object  On
```

## Interview tips

- Emphasize **IAM Permission Boundaries**: explain that while an IAM Policy specifies what actions are allowed, a Permission Boundary sets the maximum allowable permissions, preventing privilege escalation.
- Discuss **S3 Lifecycle rules**: move logs from S3 Standard to S3 Infrequent Access (IA) after 30 days, Glacier Flexible Retrieval after 90 days, and expire/delete after retention requirements (e.g., 365 days).
- Address high-volume log cost management: gzip compression, buffering before writing to S3, and avoiding writing micro-batches to save on S3 `PutObject` API call costs.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
