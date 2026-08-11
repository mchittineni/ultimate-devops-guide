---
title: "How do you investigate a sudden spike in your cloud bill?"
id: 506
category: "Cloud Cost Optimization"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
  - aws-engineering
  - infrastructure-monitoring
---

# How do you investigate a sudden spike in your cloud bill?

**Short answer:** Treat it as an incident with a timeline. **Narrow it down** in Cost Explorer (or Azure Cost Analysis / GCP Billing reports): group by **service**, then by **usage type**, then by **account/subscription**, then by **region**, then by **tag**, each time following the biggest delta - four clicks usually identify the exact line item. **Fix the time window** by switching to daily or hourly granularity to find the day (and hour) it started. **Correlate with change**: what deployed, what scaled, what was created, and by whom - CloudTrail/Activity Log answers that. Then classify what you found, because the response differs: **legitimate growth** (more traffic, a new feature), **a mistake** (an oversized instance, a forgotten environment, a debug log level left on, a cross-region data path), or **abuse** (leaked credentials mining crypto, or a public bucket being scraped). The costs that surprise people most are rarely compute: **data transfer** (cross-AZ, cross-region, NAT gateway processing, egress to the internet), **logging and observability ingest**, **NAT gateway per-GB charges**, and **untagged orphans** - idle load balancers, unattached volumes, old snapshots, and idle Elastic IPs.

## Detail

### The investigation, in order

```text
1. WHAT   Cost Explorer -> group by SERVICE, daily granularity, last 30 days
             -> the service with the biggest delta, not the biggest total
2. WHICH  same view -> group by USAGE TYPE within that service
             -> e.g. "NatGateway-Bytes", "DataTransfer-Regional-Bytes", "BoxUsage:r6i.4xlarge"
3. WHERE  group by ACCOUNT/SUBSCRIPTION, then REGION
             -> a spike in a region nobody deploys to is a strong abuse signal
4. WHO    group by TAG (team, service, environment). Untagged = your next work item
5. WHEN   hourly granularity -> the exact hour it started
6. WHY    CloudTrail / Activity Log around that hour: what was created or changed, by whom
7. ACT    classify: growth / mistake / abuse -> different response for each
```

The discipline that matters: follow the **delta**, not the total. The biggest line on the bill is usually your biggest workload and is expected; the thing that changed is what you are looking for.

### What actually causes spikes, ranked by how often it surprises teams

| Cause                                | Signature                                                    | Fix                                                                                                                                          |
| ------------------------------------ | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **NAT gateway data processing**      | `NatGateway-Bytes` climbing with container or S3 traffic     | **VPC endpoints** - a gateway endpoint for S3/DynamoDB is free; interface endpoints for ECR, Logs, Secrets Manager. Often removes most of it |
| **Cross-AZ data transfer**           | `DataTransfer-Regional-Bytes`                                | Keep chatty components AZ-local, use topology-aware routing, and per-AZ NAT gateways                                                         |
| **Internet egress**                  | `DataTransfer-Out-Bytes`                                     | CloudFront in front (cheaper per GB and cached), compression, and check for an unintended public download path                               |
| **Log and metric ingest**            | CloudWatch/Log Analytics/Datadog line items                  | Retention policies on every log group, drop debug logs, sample, and fix metric cardinality                                                   |
| **A left-on debug log level**        | Ingest doubling with no traffic change, starting at a deploy | Revert; add a check that DEBUG is not shipped to production                                                                                  |
| **Oversized or forgotten resources** | Steady step change, one account                              | Right-size from observed usage; delete the environment nobody owns                                                                           |
| **Orphans**                          | Slow accumulation, low per-item cost                         | Unattached EBS volumes, old snapshots, idle load balancers, unused Elastic IPs, idle endpoints                                               |
| **Ungoverned autoscaling**           | Cost tracks a retry storm or a runaway job                   | Scaling ceilings, budgets, and a circuit breaker - a cost-DDoS is real                                                                       |
| **Compromised credentials**          | Sudden GPU/compute in an unused region                       | Treat as a security incident **first**: revoke, rotate, investigate, then clean up                                                           |
| **CI/CD**                            | Weekday-shaped spikes in build accounts                      | Ephemeral runners, cache hits, scale to zero, Spot for retryable stages                                                                      |

The two most frequently missed are **NAT processing** and **observability ingest**, because neither is a resource anyone provisioned - they are side effects of architecture and configuration.

### Tags are the whole game

You cannot attribute what is not tagged, so cost work always turns into tagging work. The workable version:

- A small mandatory set: `Environment`, `Team`/`CostCentre`, `Service`, `Owner`.
- **Enforced at creation**, not audited afterwards - an SCP or Azure Policy denying resource creation without the tags, plus `default_tags` in the Terraform provider so IaC-created resources are covered automatically.
- **Cost allocation tags activated** in the billing console, or they do not appear in Cost Explorer at all (a genuinely common gap - the tags exist but were never activated, so reports show nothing).
- A dashboard of **untagged spend** as the metric to drive down.

For Kubernetes, tags stop at the node - a cluster looks like one line item on the bill. **OpenCost or Kubecost** splits it by namespace, workload, and label, which is the only way to answer "which team's spend is this?" in a shared cluster.

### Preventing the next one

Detection beats investigation:

- **AWS Budgets / Azure Budgets / GCP budget alerts** per account and per team, on both actual and **forecast** spend, so you hear about it on day two rather than in the monthly invoice.
- **Cost Anomaly Detection** (AWS) or the equivalent - ML-based, per service and per tag, and much better than a fixed threshold at catching a new spike inside normal-looking totals.
- **Guardrails**: SCPs restricting expensive instance families and unused regions (which also shrinks the blast radius of leaked credentials), scaling ceilings, and IAM that does not let everyone create anything anywhere.
- **Non-production scheduled to zero** out of hours - typically the single largest easy saving, and it also prevents forgotten environments running for months.
- **Show the numbers to the teams that create them.** A weekly per-team cost report changes behaviour more than any central optimisation project, because the people who can fix a query or a log level are the ones who see the line item.

### Classify before you act

- **Growth**: the spend is proportional to value delivered. Then the work is efficiency, not reduction - commitments (Savings Plans/Reserved Instances) for the steady baseline, Spot for tolerant workloads, and right-sizing.
- **Mistake**: fix it, then close the gap that allowed it - a policy, a default, a check in CI, or an alert.
- **Abuse**: this is a security incident. Revoke the credential immediately, review CloudTrail for what it did, rotate anything it could have read, then delete the resources. Do not start by deleting the instances - you destroy the evidence. GuardDuty findings for credentials used from an unusual location are the usual first signal.

And say the constraint out loud: cost reduction must not silently reduce reliability. Cutting a NAT gateway to one AZ, removing a standby, shrinking retention below your compliance requirement, or dropping to a single AZ are all real savings with real consequences - make the trade-off explicit and get it agreed rather than quietly shipping it.

## Example

```bash
# 1. What changed? Group by service, daily, and look at the DELTA not the total.
aws ce get-cost-and-usage \
  --time-period Start=2026-07-11,End=2026-08-10 \
  --granularity DAILY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[-3:].{date:TimePeriod.Start,
            top:Groups|sort_by(@,&to_number(Metrics.UnblendedCost.Amount))[-5:]}'

# 2. Which usage type inside that service? This is where the real answer lives.
aws ce get-cost-and-usage \
  --time-period Start=2026-08-01,End=2026-08-10 --granularity DAILY \
  --metrics UnblendedCost --filter '{"Dimensions":{"Key":"SERVICE",
      "Values":["Amazon Elastic Compute Cloud - Compute","Amazon Virtual Private Cloud"]}}' \
  --group-by Type=DIMENSION,Key=USAGE_TYPE

# 3. Which account and region? A region nobody deploys to is an abuse signal.
aws ce get-cost-and-usage --time-period Start=2026-08-01,End=2026-08-10 \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=LINKED_ACCOUNT Type=DIMENSION,Key=REGION

# 4. Who owns it? And how much is untagged?
aws ce get-cost-and-usage --time-period Start=2026-08-01,End=2026-08-10 \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=TAG,Key=Team
```

```bash
# 5. Correlate with change - the step people skip
aws cloudtrail lookup-events --start-time 2026-08-06T00:00:00Z \
  --lookup-attributes AttributeKey=EventName,AttributeValue=RunInstances \
  --query 'Events[].{t:EventTime,who:Username}' --output table

aws cloudtrail lookup-events --start-time 2026-08-06T00:00:00Z \
  --lookup-attributes AttributeKey=EventName,AttributeValue=CreateNatGateway

# NAT processing is usually the hidden one - confirm it with the metric
aws cloudwatch get-metric-statistics --namespace AWS/NATGateway \
  --metric-name BytesOutToDestination --statistics Sum --period 86400 \
  --start-time "$(date -u -d '-14 days' +%FT%TZ)" --end-time "$(date -u +%FT%TZ)" \
  --dimensions Name=NatGatewayId,Value=nat-0abc123
```

```bash
# 6. Sweep for orphans - individually cheap, collectively significant
aws ec2 describe-volumes --filters Name=status,Values=available \
  --query 'Volumes[].{id:VolumeId,size:Size,type:VolumeType,created:CreateTime}' --output table
aws ec2 describe-addresses --query 'Addresses[?AssociationId==`null`].PublicIp'
aws ec2 describe-snapshots --owner-ids self \
  --query 'Snapshots[?StartTime<=`2025-08-10`].[SnapshotId,VolumeSize,StartTime]' --output table
aws elbv2 describe-target-groups --query 'TargetGroups[?length(LoadBalancerArns)==`0`].TargetGroupName'

# Unbounded log retention: the classic quiet spend
aws logs describe-log-groups \
  --query 'logGroups[?!retentionInDays].[logGroupName,storedBytes]' --output table
```

```bash
# 7. Prevent the next one: budgets on forecast, and anomaly detection per service
aws budgets create-budget --account-id 111122223333 --budget '{
  "BudgetName":"prod-monthly","BudgetType":"COST","TimeUnit":"MONTHLY",
  "BudgetLimit":{"Amount":"40000","Unit":"USD"},
  "CostFilters":{"TagKeyValue":["user:Environment$prod"]}}' \
  --notifications-with-subscribers '[{
    "Notification":{"NotificationType":"FORECASTED","ComparisonOperator":"GREATER_THAN",
      "Threshold":90,"ThresholdType":"PERCENTAGE"},
    "Subscribers":[{"SubscriptionType":"SNS","Address":"arn:aws:sns:eu-west-1:111122223333:finops"}]}]'

aws ce create-anomaly-monitor --anomaly-monitor '{
  "MonitorName":"per-service","MonitorType":"DIMENSIONAL","MonitorDimension":"SERVICE"}'

# Kubernetes: the bill says "EC2", the answer is per namespace
kubectl -n opencost port-forward svc/opencost 9003 &
curl -s 'localhost:9003/allocation?window=7d&aggregate=namespace' \
  | jq -r '.data[0] | to_entries | sort_by(-.value.totalCost)[:10]
           | .[] | "\(.value.totalCost|floor)\t\(.key)"'
```

## Interview tips

- Frame it as an incident with a timeline, and give the drill-down order: service → usage type → account → region → tag, at daily then hourly granularity. Having a repeatable order is the answer; naming a tool is not.
- Say **follow the delta, not the total**. It is the one-line summary of how to read a cost report and it separates people who have done this from people who have opened the console once.
- Volunteer the two hidden causes almost nobody provisions deliberately: **NAT gateway data processing** (fixed with VPC endpoints, and a gateway endpoint for S3 is free) and **observability ingest** (fixed with retention policies, sampling, and cardinality control).
- Always correlate with change - CloudTrail or the Activity Log around the hour it started. "Something got more expensive" is rarely spontaneous.
- Classify the finding into growth, mistake, or abuse, and give a different response for each. For abuse, say it is a **security incident first**: revoke and investigate before deleting resources, because deleting destroys the evidence.
- Make the tagging point concretely: enforce at creation with an SCP or Azure Policy plus Terraform `default_tags`, and remember cost allocation tags must be **activated** in billing or they never appear in reports. Track untagged spend as the metric.
- For Kubernetes, say the bill stops at the node and you need OpenCost/Kubecost to attribute by namespace and label.
- Finish on prevention: budgets on **forecast** as well as actual, anomaly detection, SCPs restricting unused regions and expensive instance families, non-production scheduled to zero, and per-team cost reports - because the people who can fix a query are the ones who need to see the number.
- State the guard rail: cost reduction must not silently trade away reliability or compliance retention. Make that trade-off explicit. See [how do you cut a cloud bill without hurting reliability](./how-do-you-cut-a-cloud-bill-without-hurting-reliability.md), [how to implement cost tagging strategy](./how-to-implement-cost-tagging-strategy.md), [real-time Kubernetes cost monitoring with OpenCost or Kubecost](./how-do-you-implement-real-time-kubernetes-cost-monitoring-using-opencost-or-kubecost.md), [what is FinOps](../advanced-devops-cloud/what-is-finops.md), and [what are VPC endpoints](../aws-engineering/what-are-vpc-endpoints-and-when-do-you-use-a-gateway-versus-an-interface-endpoint.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
