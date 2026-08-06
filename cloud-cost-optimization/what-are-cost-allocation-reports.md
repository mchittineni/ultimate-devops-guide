---
title: "What are cost allocation reports?"
id: 95
category: "Cloud Cost Optimization"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
---

# What are cost allocation reports?

**Short answer:** Cost allocation reports break cloud spend down by dimensions such as account, service, tag, and team, so costs can be attributed to the group that incurred them — enabling showback, chargeback, and informed optimisation.

## Detail

**Data sources.** AWS Cost and Usage Report (hourly or resource-level line items delivered to S3, the most detailed source available), Cost Explorer for interactive analysis, Azure Cost Management exports, and GCP billing export to BigQuery. Third-party platforms (CloudHealth, Cloudability, Vantage) and the open-source OpenCost and Kubecost add Kubernetes-level attribution.

**Dimensions that matter:** linked account, service, region, resource ID, usage type, purchase option (on-demand/spot/reserved), and — most importantly — your own tags.

**Showback vs chargeback.** Showback reports each team's spend for visibility without moving budget; chargeback actually bills it to their cost centre. Showback is the usual starting point because it drives behaviour without the political overhead.

**The hard part: shared costs.** Kubernetes clusters, NAT gateways, data transfer, logging platforms, and support fees serve many teams. You need an agreed allocation rule — proportional to usage, evenly split, or absorbed centrally — documented and applied consistently. For Kubernetes, OpenCost attributes node cost to namespaces and workloads by their resource requests, which is the standard approach.

**Amortisation.** Report upfront reservation payments spread over the commitment term rather than as a spike in the purchase month; otherwise a team's monthly trend is meaningless.

**Make it actionable.** A report nobody acts on is overhead. Pair it with unit economics — cost per customer, per transaction, per environment — which is what makes cost a comparable engineering metric rather than a raw total.

## Interview tips

- Unit cost metrics (cost per transaction) are the mature answer; absolute spend rising is fine if unit cost is falling.
- Shared-cost allocation is the question that reveals whether you have actually done this.
- Mention amortised versus unblended cost — it shows familiarity with real billing data.

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
