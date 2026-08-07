---
title: "How do you cut a cloud bill without hurting reliability?"
id: 278
category: "Cloud Cost Optimization"
difficulty: "Advanced"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
---

# How do you cut a cloud bill without hurting reliability?

**Short answer:** Work the levers in order of risk, not size: **delete waste** (orphaned volumes, idle environments, forgotten NAT gateways), **right-size** against observed p95 usage, **fix the architecture** that generates the spend (chatty cross-AZ traffic, un-tiered storage, retry storms), and only then **commit** with Savings Plans or reservations. Attach every change to an SLO so the reliability cost is visible, and hand each line item to a named owning team - unowned spend never goes down.

## Detail

**Find out what you are actually paying for.** Aggregate bills lie. Use the Cost and Usage Report (or Azure/GCP equivalents) in a query engine, joined to your tag taxonomy, and split by team, environment, and service. The first pass usually finds that 60-80% of spend sits in a handful of line items, and that a large slice is untagged - which means unowned.

**The ladder, lowest risk first:**

1. **Waste with no consumer.** Unattached EBS volumes, old snapshots, idle load balancers, elastic IPs, dev clusters running at 3am, log retention set to "forever". No reliability trade-off at all - this is pure deletion, and it is where you start to buy credibility.
2. **Right-sizing.** Compare requested to consumed over 2-4 weeks and resize to p95 plus headroom, not to average. In Kubernetes this is VPA recommendations feeding your manifests; on VMs it is instance-family changes (and moving to Graviton/ARM where the workload allows, for a double-digit price-performance win). Right-sizing _does_ touch reliability, so it must be gradual and reversible.
3. **Architecture.** Usually the biggest and most durable savings, and the part cost tools cannot do for you: cross-AZ and egress traffic that a topology-aware routing change removes, S3 objects that belong in Infrequent Access or Glacier, a metrics pipeline retaining high-cardinality series nobody queries, N+2 redundancy on a service whose SLO justifies N+1, a Lambda over-provisioned because someone tuned memory once and never revisited.
4. **Commitments.** Savings Plans, Reserved Instances, and Committed Use Discounts pay 20-60% but lock you in for 1-3 years. Commit only to the _floor_ of your usage after steps 1-3, otherwise you are buying a discount on waste. Layer Spot / preemptible capacity for anything interruptible - CI runners, batch, stateless workers behind a queue - with on-demand fallback.

**Where cost cutting breaks reliability, and how to keep it honest.** Every candidate saving gets a stated reliability hypothesis: "dropping this read replica costs us failover capacity in one AZ", "moving to Spot means 2-minute interruptions". Test it against the SLO and error budget. If a service is comfortably inside budget, it is over-provisioned for its target and the saving is free. If it is burning budget, cost work waits. This framing - **error budget as the arbiter** - is what separates FinOps from a spreadsheet exercise.

**Make it stick.** A one-off cleanup regresses within two quarters. What holds:

- **Showback per team**, in the tools they already read, with unit economics - cost per request, per tenant, per build - not just absolute dollars.
- **Anomaly alerts** on daily spend per tag, routed to the owning team, not to finance.
- **Guardrails in the pipeline**: policy-as-code rejecting untagged resources, instance types outside an allowlist, or storage without lifecycle rules; `infracost` posting the delta on every infrastructure pull request.
- **A quarterly commitment review** as the usage floor changes.

## Example

```sql
-- Top spend by team and service, with untagged exposure made obvious.
SELECT
  COALESCE(resource_tags_user_team, 'UNTAGGED') AS team,
  line_item_product_code                        AS service,
  ROUND(SUM(line_item_unblended_cost), 2)       AS cost_usd
FROM cur.line_items
WHERE bill_billing_period_start_date = DATE '2026-07-01'
GROUP BY 1, 2
HAVING SUM(line_item_unblended_cost) > 500
ORDER BY cost_usd DESC
LIMIT 25;
```

```bash
# Step 1: waste with no consumer.
aws ec2 describe-volumes --filters Name=status,Values=available \
  --query 'Volumes[].[VolumeId,Size,CreateTime]' --output table   # unattached disks

aws logs describe-log-groups \
  --query 'logGroups[?!retentionInDays].logGroupName'             # retained forever

# Step 4: commit only to the observed floor.
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT --lookback-period-in-days SIXTY
```

```yaml
# Guardrail: no untagged resources, enforced before spend exists.
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-cost-tags
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-team-label
      match: { any: [{ resources: { kinds: [Deployment, StatefulSet] } }] }
      validate:
        message: "team and cost-center labels are required"
        pattern:
          metadata:
            labels:
              team: "?*"
              cost-center: "?*"
```

## Interview tips

- Present the ladder - waste, right-sizing, architecture, commitments - and say explicitly that you commit last, because committing early locks in waste.
- Use the error budget as the arbiter of "is this saving safe". It is the answer that shows you understand the reliability side rather than just the invoice.
- Right-size to p95 with headroom, not to the average. Averages are how you cause an outage while saving money.
- Name unit economics (cost per request, per tenant, per deploy). Absolute spend rising while unit cost falls is a healthy business, and being able to say that is a senior signal.
- Have a concrete number ready from your own experience, with the mechanism: "cross-AZ chatter was 18% of the bill; topology-aware routing removed most of it."
- Mention tagging enforcement and anomaly alerting as the durability story. Interviewers know one-off cleanups regress.

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
