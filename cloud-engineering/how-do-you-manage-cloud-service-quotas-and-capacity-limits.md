---
title: "How do you manage cloud service quotas and capacity limits?"
id: 777
category: "Cloud Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-engineering
  - interview-questions
  - quotas
  - capacity-planning
  - aws
---

# How do you manage cloud service quotas and capacity limits?

**Short answer:** Treat limits as three different things. **Quotas** are per-account (or subscription, or project) ceilings you can usually raise on request: vCPUs, IP addresses, Lambda concurrency. **API rate limits** throttle control-plane calls. **Physical capacity** is whether the provider actually has the instance type in that zone right now, which no quota increase fixes. Manage them by monitoring utilisation against every quota that matters, alerting at 70-80%, raising limits ahead of launches and **in your DR region**, managing quota values as code for new accounts, and reserving capacity (capacity reservations, GPU capacity blocks) for anything you cannot afford to be refused.

## Detail

**Quotas (soft limits).** Every provider caps resources per account and region: running vCPUs per instance family, Elastic IPs, VPCs, NAT gateways, load balancers, Lambda concurrency, GPU counts, and so on. Most are adjustable through AWS Service Quotas, Azure Quotas, or Google Cloud Quotas. Some are hard limits that cannot change and have to be designed around (for example the maximum rules per security group). Increases can take minutes or days, and large GPU requests may need a business case, so you request them before you need them.

**API rate limits.** Control-plane APIs are throttled, often per account and region with token-bucket semantics (`RequestLimitExceeded`, `ThrottlingException`, HTTP 429). They bite during bulk automation - a Terraform apply across hundreds of resources, a deployment tool polling `Describe*` calls, autoscalers in many clusters sharing one account. Fix them with SDK retries with backoff and jitter, fewer polling loops, and spreading workloads across accounts.

**Capacity.** `InsufficientInstanceCapacity` means the zone has no spare hardware of that type at that moment, whatever your quota says. Mitigate it with instance-type and zone flexibility (Karpenter, EC2 Fleet, attribute-based instance selection), **On-Demand Capacity Reservations** (or Azure capacity reservations, GCP reservations) for must-have capacity, and **EC2 Capacity Blocks for ML** or the equivalents for scarce GPUs.

**Making it operational**

- **Monitor utilisation, not just the limit.** AWS publishes usage metrics in the `AWS/Usage` CloudWatch namespace that can be alarmed against the quota with the `SERVICE_QUOTA()` metric-math function. Azure and GCP expose usage-versus-limit through their quota APIs and monitoring. Trusted Advisor and similar checks cover the common ones.
- **Pre-raise for known events and for failover.** A DR region with default quotas cannot absorb a full failover: the standby scales up, hits the vCPU quota, and your RTO blows up. Make DR-region quotas part of the DR checklist and test them during game days.
- **Quotas as code.** Set them in Terraform (`aws_servicequotas_service_quota`) or with Service Quotas request templates in AWS Organizations, so every new account in the landing zone starts with the limits it needs.
- **Use account boundaries.** Quotas are per account and region, so splitting workloads across accounts isolates them. A runaway batch job in one account cannot use up the API rate limit or Lambda concurrency of the production account.
- **Fail clearly.** When a scale-up is refused, the reason sits in the ASG activity history, the Kubernetes events, or the deployment log. Alert on those messages, not only on missing capacity.

**Trade-offs.** Reservations guarantee capacity but cost money whether or not you use it (pair them with Savings Plans for the discount). Very high quotas reduce friction but also raise the ceiling on what a leaked credential or a runaway loop can spend, so keep budgets and anomaly detection alongside them.

## Example

```bash
# What is the quota, and how close are we? (Running On-Demand Standard vCPUs: L-1216C47A)
aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A \
  --query 'Quota.Value'
aws service-quotas request-service-quota-increase --service-code ec2 \
  --quota-code L-1216C47A --desired-value 1024 --region us-west-2   # the DR region too

# Alarm at 80% of the quota using the usage metric and SERVICE_QUOTA() metric math.
aws cloudwatch put-metric-alarm --alarm-name ec2-vcpu-quota-80pct \
  --comparison-operator GreaterThanThreshold --threshold 80 --evaluation-periods 1 \
  --metrics '[
    {"Id":"usage","ReturnData":false,"MetricStat":{"Period":300,"Stat":"Maximum",
      "Metric":{"Namespace":"AWS/Usage","MetricName":"ResourceCount","Dimensions":[
        {"Name":"Service","Value":"EC2"},{"Name":"Type","Value":"Resource"},
        {"Name":"Resource","Value":"vCPU"},{"Name":"Class","Value":"Standard/OnDemand"}]}}},
    {"Id":"pct","Expression":"(usage / SERVICE_QUOTA(usage)) * 100","ReturnData":true}]'
```

```hcl
# Quotas as code: new accounts and the DR region get the same limits as production.
resource "aws_servicequotas_service_quota" "ec2_vcpu" {
  service_code = "ec2"
  quota_code   = "L-1216C47A"
  value        = 1024
}

resource "aws_servicequotas_service_quota" "lambda_concurrency" {
  service_code = "lambda"
  quota_code   = "L-B99A9384" # concurrent executions
  value        = 5000
}
```

## Interview tips

- Separate quotas, API rate limits, and physical capacity, because each one has a different fix. Treating `InsufficientInstanceCapacity` as a quota problem is a common mistake.
- Say that you monitor usage against quotas and alert well before the limit, instead of discovering limits during an incident.
- The DR-region quota is the point that lands best: a standby region with default limits cannot take the failover.
- Mention capacity reservations and GPU capacity blocks for capacity you must have, and instance or zone flexibility for everything else.
- Note that the account boundary is also a quota boundary. That is one reason landing zones split workloads into many accounts.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What are the Three Ways of DevOps?]] (`#783`): [What are the Three Ways of DevOps?](../core-devops-concepts/what-are-the-three-ways-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Engineering](./README.md) · [All topics](../README.md)
