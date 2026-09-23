---
title: "What is FinOps?"
id: 142
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is FinOps?

**Short answer:** FinOps is the operational discipline of bringing financial accountability to variable cloud spend - a collaboration between engineering, finance, and business to make cost a measurable, owned engineering attribute.

## Detail

**The three phases**, which run continuously per workload rather than sequentially:

1. **Inform** - visibility and allocation. Tagging, showback dashboards, budgets, forecasts, and unit economics so every team can see what it spends.
2. **Optimise** - right-sizing, commitment purchases, spot adoption, storage lifecycle, architectural change, and waste elimination.
3. **Operate** - continuous governance: policies, anomaly alerting, regular review cadence, and cost as a factor in design decisions.

**Core principles** (from the FinOps Foundation, reworded in the 2025 framework to cover technology spend beyond public cloud): teams need to collaborate; business value drives technology decisions; everyone takes ownership for their technology usage; FinOps data should be accessible, timely, and accurate; FinOps should be enabled centrally; and take advantage of the variable cost model of the cloud. The 2025 framework also adds **scopes**, so the same practice can cover cloud, SaaS, licensing, data centre, and AI spend.

**Unit economics is the maturity marker.** Total spend rising is meaningless in isolation. Cost per transaction, per customer, or per thousand requests tells you whether efficiency is improving. A business doubling revenue while cloud spend rises 40% is winning.

**Practical implementation:** normalise billing data (the FinOps Foundation's FOCUS specification is now supported by the major clouds' cost exports), enforce tagging in IaC, publish per-team dashboards, set budget alerts and anomaly detection, review a cost report in the regular engineering cadence, add cost estimates to architecture decisions (Infracost in pull requests), and give teams a target they own.

**The cultural point:** cost decisions belong with the engineers who create them, because they are the only ones who can act on them. Finance provides the framework; engineering makes the calls.

## Example

```sql
-- Unit economics from a FOCUS-format cost export: cost per 1,000 orders, per team, per month
SELECT
  date_trunc('month', c.ChargePeriodStart)              AS month,
  c.Tags['team']                                         AS team,
  sum(c.EffectiveCost)                                   AS cost,
  sum(c.EffectiveCost) / (max(o.orders) / 1000.0)        AS cost_per_1k_orders
FROM focus_costs c
JOIN monthly_orders o
  ON o.month = date_trunc('month', c.ChargePeriodStart)
GROUP BY 1, 2
ORDER BY 1, 3 DESC;
```

## Interview tips

- Inform → optimise → operate is the structure that shows you know the framework.
- Unit economics over absolute spend is the insight that separates FinOps from cost-cutting.
- Infracost in pull requests is a concrete, modern practice worth naming.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
