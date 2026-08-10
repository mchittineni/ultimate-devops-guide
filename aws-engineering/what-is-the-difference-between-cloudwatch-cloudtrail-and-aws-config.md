---
title: "What is the difference between CloudWatch, CloudTrail, and AWS Config?"
id: 483
category: "AWS Engineering"
difficulty: "Beginner"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - monitoring-and-logging
  - security-and-compliance
---

# What is the difference between CloudWatch, CloudTrail, and AWS Config?

**Short answer:** They answer three different questions. **CloudWatch** answers _"how is it behaving?"_ - metrics, logs, alarms, and dashboards about the performance and health of resources and applications. **CloudTrail** answers _"who did what?"_ - an audit log of API calls, with the identity, source IP, parameters, timestamp, and result, for every action against the AWS control plane (and optionally data-plane events such as individual S3 object reads). **AWS Config** answers _"what does the configuration look like now, what did it look like then, and is it compliant?"_ - a versioned inventory of resource configurations plus rules that evaluate them continuously. In practice you use all three together on any real incident: CloudWatch alerts you that latency spiked, CloudTrail tells you someone modified a security group twelve minutes earlier, and Config shows you exactly what the rule set was before and after.

## Detail

### The comparison

|             | CloudWatch                                                              | CloudTrail                                                   | AWS Config                                               |
| ----------- | ----------------------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------- |
| Question    | How is it performing?                                                   | Who called which API?                                        | What is the configuration, and was it compliant?         |
| Data        | Metrics, logs, traces (via X-Ray), events                               | API events with identity and parameters                      | Configuration items, relationships, change history       |
| Time model  | Time series, near real time                                             | Event stream, ~5-15 min to the console/S3                    | Snapshots + change timeline                              |
| Retention   | Metrics 15 months (rolled up); logs per log-group retention **you set** | 90 days in Event history; indefinite in an S3 trail          | As long as you keep the S3 delivery + Config history     |
| Alerting    | **Alarms** (the primary mechanism)                                      | Via CloudWatch Logs metric filters or EventBridge            | Config rules → EventBridge/SNS, Security Hub             |
| Typical use | Autoscaling triggers, on-call alerts, dashboards, log search            | Security investigation, forensics, "who deleted the bucket?" | Drift detection, compliance evidence, resource inventory |
| Cost driver | Ingested/stored log volume, custom metrics, dashboards, alarms          | Management events free (one trail); data events per event    | Per configuration item recorded, per rule evaluation     |

Also in the same family and often confused: **EventBridge** (formerly CloudWatch Events) routes events to targets in near real time - the mechanism for reacting automatically; **X-Ray** is distributed tracing; **Security Hub** aggregates findings from Config, GuardDuty, and Inspector; and **CloudWatch Logs Insights** is the query engine over your logs.

### CloudWatch: the part most candidates get wrong

**Memory and disk usage are not EC2 metrics.** The hypervisor can see CPU, network, and EBS I/O, but it cannot see inside the guest - so `mem_used_percent` and `disk_used_percent` require the **CloudWatch agent** installed on the instance, publishing custom metrics (usually into the `CWAgent` namespace). This is the answer to "how do you monitor memory on a VM and alert above 80%?" and to "which service do you use to monitor a CPU spike?" - CloudWatch for CPU out of the box, CloudWatch **agent** for memory and disk. Getting this right is a strong signal; assuming memory is there by default is a common tell.

Other essentials:

- **Custom metrics**: `put-metric-data` or the embedded metric format (EMF), which lets you emit metrics as structured log lines from an application and have CloudWatch extract them - cheaper and simpler than an API call per metric.
- **Alarms**: threshold, anomaly detection, composite (combine several alarms to cut noise), and metric math. Set `treat_missing_data` deliberately - the default can leave you blind when an instance stops reporting entirely.
- **Logs**: log groups with a **retention policy** (the default is never expire, which is the single most common CloudWatch cost surprise), metric filters to turn a log pattern into a metric and therefore an alarm, subscription filters to stream elsewhere, and Logs Insights for querying.
- **Log groups versus log streams**: a group is the container with retention and permissions (usually one per application or service); a stream is a sequence from one source (one instance, one Lambda execution environment).

### CloudTrail: what it does and does not capture

- **Management events** (control plane) are on by default in Event history for 90 days, free for the first copy. Creating an instance, changing a policy, deleting a bucket.
- **Data events** (data plane) - S3 object-level `GetObject`/`PutObject`, Lambda `Invoke`, DynamoDB item operations - are **off by default** and charged per event, because volume is enormous. Turn them on selectively for sensitive buckets. This is why "who read that object?" often cannot be answered retroactively.
- **Insights events** detect unusual API call rates.
- An **organisation trail** delivering to a **dedicated log-archive account** with object lock is the pattern to describe: centralised, immutable, and outside the reach of someone who compromises a workload account. Enable log file validation so tampering is detectable.

CloudTrail is where "who did this?" lives, and the practical answer for a specific event is `aws cloudtrail lookup-events` for the last 90 days, or **Athena over the S3 trail** for anything older or for aggregate questions.

### AWS Config: inventory, history, and drift

Config records a **configuration item** each time a resource changes, keeps the relationships between resources, and lets you ask "what did this security group look like on 3 March?" - which is the question an auditor asks and which neither CloudWatch nor CloudTrail answers directly. On top of that:

- **Config rules** (managed or custom via Lambda/Guard) evaluate compliance continuously: `s3-bucket-public-read-prohibited`, `encrypted-volumes`, `required-tags`, `rds-multi-az-support`.
- **Conformance packs** bundle rules to a framework (CIS, PCI DSS), which is how you produce continuous compliance evidence rather than a pre-audit scramble.
- **Remediation actions** can auto-fix a violation via SSM Automation - useful for tagging or closing a public bucket, dangerous for anything that could cause an outage, so choose per rule.
- **Advanced queries** (SQL over the inventory) answer "how many unencrypted volumes exist across all accounts?" without a script per account.

The classic pairing question - _"if a resource is deleted, how do you identify which one it was?"_ - is answered with both: **Config** shows the resource's last recorded configuration and that it is now deleted (so you know exactly what it was), and **CloudTrail** shows who called `Delete*`, when, and from where. Config gives you the _what_, CloudTrail gives you the _who_.

### Putting them together on a real incident

```text
02:14  CloudWatch alarm: p99 latency > 2s, 5xx rate rising          -> "something is wrong"
02:16  CloudWatch Logs Insights: connection timeouts to the database -> "where"
02:18  CloudTrail lookup-events on ec2:AuthorizeSecurityGroupIngress
       / RevokeSecurityGroupIngress in the last hour                 -> "who changed what"
       => user "contractor-x" revoked 5432 from the app SG at 02:09
02:20  Config timeline for sg-0abc: before/after diff confirms it     -> "exactly what changed"
02:21  revert, then: Config rule + EventBridge alert on future
       security-group changes, and an SCP restricting who can make them
```

That narrative is a better answer than three definitions, and it is what an interviewer is really checking.

### Cost control, since it is asked

- **Set log retention on every log group.** Unbounded retention is the biggest avoidable CloudWatch bill.
- Sample or downgrade debug logging; use EMF instead of thousands of `PutMetricData` calls; delete unused custom metrics and dashboards.
- Turn CloudTrail **data events** on only for the buckets that need them, and consider S3 access logs where cheaper.
- In Config, limit the recorder to the resource types you care about rather than "all supported types" in every region, and be aware that a chatty resource (Auto Scaling groups, for example) generates configuration items on every change.
- Export long-term logs to S3 with lifecycle tiering rather than keeping years in CloudWatch Logs.

## Example

```bash
# CloudWatch: memory needs the AGENT. This metric does not exist without it.
aws ssm send-command --document-name AWS-ConfigureAWSPackage \
  --targets "Key=tag:Environment,Values=prod" \
  --parameters '{"action":["Install"],"name":["AmazonCloudWatchAgent"]}'

aws cloudwatch put-metric-alarm --alarm-name prod-mem-high \
  --namespace CWAgent --metric-name mem_used_percent \
  --dimensions Name=InstanceId,Value=i-0abc123 \
  --statistic Average --period 300 --evaluation-periods 2 \
  --threshold 80 --comparison-operator GreaterThanThreshold \
  --treat-missing-data breaching \
  --alarm-actions arn:aws:sns:eu-west-1:111122223333:oncall

# Retention on every log group - the biggest avoidable cost
for g in $(aws logs describe-log-groups \
      --query 'logGroups[?!retentionInDays].logGroupName' --output text); do
  aws logs put-retention-policy --log-group-name "$g" --retention-in-days 30
done
```

```bash
# CloudTrail: who changed the security group, and from where?
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=RevokeSecurityGroupIngress \
  --start-time "$(date -u -d '-2 hours' +%FT%TZ)" \
  --query 'Events[].{t:EventTime,who:Username,src:CloudTrailEvent}' --output text \
  | head -20

# Older than 90 days, or an aggregate question -> Athena over the S3 trail
# SELECT useridentity.arn, eventname, sourceipaddress, eventtime
# FROM cloudtrail_logs
# WHERE eventname LIKE 'Delete%' AND eventtime > '2026-07-01'
# ORDER BY eventtime DESC LIMIT 100;
```

```bash
# Config: what did it look like before, and what is non-compliant now?
aws configservice get-resource-config-history \
  --resource-type AWS::EC2::SecurityGroup --resource-id sg-0abc123 \
  --query 'configurationItems[].[configurationItemCaptureTime,configurationItemStatus]' --output table

aws configservice describe-compliance-by-config-rule \
  --query 'ComplianceByConfigRules[?Compliance.ComplianceType==`NON_COMPLIANT`].ConfigRuleName'

# Inventory questions across the estate, in SQL
aws configservice select-resource-config \
  --expression "SELECT resourceId, resourceType, tags
                WHERE resourceType = 'AWS::EC2::Volume'
                AND configuration.encrypted = false"
```

```json
// EventBridge: react in near real time instead of noticing at the next audit
{
  "source": ["aws.config"],
  "detail-type": ["Config Rules Compliance Change"],
  "detail": {
    "messageType": ["ComplianceChangeNotification"],
    "newEvaluationResult": { "complianceType": ["NON_COMPLIANT"] },
    "configRuleName": ["s3-bucket-public-read-prohibited", "encrypted-volumes"]
  }
}
```

## Interview tips

- Answer with the three questions - how is it behaving, who did what, what is the configuration and was it compliant. That phrasing is memorable and it is exactly the distinction being tested.
- Volunteer that **memory and disk are not default EC2 metrics** and need the CloudWatch agent. It is the single most common gap in this topic and it answers two frequently-asked variants at once.
- Say that CloudTrail **data events are off by default and cost per event**, which is why "who read that S3 object?" is often unanswerable after the fact. Recommending selective data events on sensitive buckets shows judgement.
- Describe the organisation trail into a dedicated log-archive account with object lock and log file validation. That is the pattern auditors expect and it demonstrates you have thought about an attacker who reaches the workload account.
- Explain Config as inventory plus **history** plus rules, and use it to answer "what did this look like last month?" - the question neither of the other two services answers.
- For "a resource was deleted, which one and who did it?", pair the two: Config for the resource's last configuration, CloudTrail for the identity and the call. Interviewers ask this specifically to see whether you know they are complementary.
- Tell the incident narrative rather than three definitions - alarm, log query, CloudTrail lookup, Config diff, then the preventive control. It reads as experience.
- Close on cost: set retention on every log group, restrict Config's recorded resource types, and enable data events selectively. Unbounded log retention is the classic surprise bill. See [what is monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md), [designing a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md), [automating compliance checks](../security-and-compliance/how-do-you-automate-compliance-checks-for-pci-dss-soc-2-hipaa-and-gdpr.md), and [what is infrastructure drift](../advanced-devops-cloud/what-is-infrastructure-drift.md).

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
