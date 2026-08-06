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

**Short answer:** FinOps is the operational discipline of bringing financial accountability to variable cloud spend — a collaboration between engineering, finance, and business to make cost a measurable, owned engineering attribute.

## Detail

**The three phases**, which run continuously per workload rather than sequentially:

1. **Inform** — visibility and allocation. Tagging, showback dashboards, budgets, forecasts, and unit economics so every team can see what it spends.
2. **Optimise** — right-sizing, commitment purchases, spot adoption, storage lifecycle, architectural change, and waste elimination.
3. **Operate** — continuous governance: policies, anomaly alerting, regular review cadence, and cost as a factor in design decisions.

**Core principles** (from the FinOps Foundation): teams need to collaborate; everyone takes ownership of their cloud usage; a centralised team drives FinOps practice; reports should be accessible and timely; decisions are driven by the business value of cloud, not by cost alone; and take advantage of the variable cost model.

**Unit economics is the maturity marker.** Total spend rising is meaningless in isolation. Cost per transaction, per customer, or per thousand requests tells you whether efficiency is improving. A business doubling revenue while cloud spend rises 40% is winning.

**Practical implementation:** enforce tagging in IaC, publish per-team dashboards, set budget alerts and anomaly detection, review a cost report in the regular engineering cadence, add cost estimates to architecture decisions (Infracost in pull requests), and give teams a target they own.

**The cultural point:** cost decisions belong with the engineers who create them, because they are the only ones who can act on them. Finance provides the framework; engineering makes the calls.

## Interview tips

- Inform → optimise → operate is the structure that shows you know the framework.
- Unit economics over absolute spend is the insight that separates FinOps from cost-cutting.
- Infracost in pull requests is a concrete, modern practice worth naming.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
