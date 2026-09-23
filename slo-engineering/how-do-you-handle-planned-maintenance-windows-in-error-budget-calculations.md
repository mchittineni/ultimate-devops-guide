---
title: "How Do You Handle Planned Maintenance Windows in Error Budget Calculations?"
id: 720
category: "SLO Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - slo-engineering
  - error-budgets
  - maintenance-windows
quiz:
  stem: "From a modern Site Reliability Engineering (SRE) perspective, why do teams often choose to count planned maintenance downtime against their internal error budgets?"
  options:
    - "To ensure that cloud providers refund the cost of running compute nodes."
    - "Because users experience unavailability regardless of whether downtime was scheduled, which incentivizes engineering zero-downtime architectures."
    - "Because Kubernetes does not support rolling updates or blue-green deployments."
    - "To automatically cancel customer subscription agreements without penalties."
  answer: 2
  explanation: "Users are impacted by unavailability whether planned or unplanned. Counting planned downtime against internal error budgets incentivizes teams to engineer zero-downtime deployment and migration patterns."
---

# How Do You Handle Planned Maintenance Windows in Error Budget Calculations?

**Short answer:** Planned maintenance windows should either be included in internal error budgets to drive zero-downtime engineering practices or explicitly scheduled and excluded from commercial customer SLAs via defined contract terms, clear advance notices, and metric blackout tags.

## Detail

### The Philosophical Tension: SRE vs Operations

Traditional IT operations assumed systems must periodically go offline for database migrations, OS patching, or hardware upgrades. These were designated as 'planned maintenance windows' and excluded from uptime calculations.

Google SRE practices challenge this assumption: modern distributed architectures should leverage blue-green deployments, canary rollouts, read replicas, and rolling restarts to achieve zero customer-impacting downtime during maintenance.

### Two Differing Approaches

#### 1. Internal SLOs (Engineering Discipline)

- **Philosophy**: Planned downtime is still downtime to the user. An outage burns user goodwill regardless of whether it was scheduled in advance.
- **Implementation**: Count planned maintenance against the internal error budget.
- **Outcome**: Forces engineering teams to invest in zero-downtime database schema migrations (e.g., expand/contract pattern) and redundant infrastructure rather than relying on maintenance crutches.

#### 2. Commercial Customer SLAs (Legal & Contractual)

- **Philosophy**: B2B enterprise contracts often grant vendors 4 to 8 hours of monthly maintenance windows during off-peak weekend hours without incurring financial penalties or service credit liabilities.
- **Implementation**: The metrics collection engine filters out designated maintenance intervals using maintenance blackout tags or synthetic test suppressions.

```text
[Incident Event Detected]
            │
    Is Window Tagged as
 "Scheduled Maintenance"?
            ├─── YES ──► Exclude from Legal SLA Report
            │        ──► Retain in Engineering SRE Error Budget Review
            │
            └─── NO  ──► Deduct from Error Budget & SLA Uptime
```

### Best Practices for Maintenance Management

- **Advance Notification**: Require at least 5 business days advance notification to customers before scheduling maintenance.
- **Off-Peak Scheduling**: Restrict windows to predefined low-traffic periods (e.g., Sunday 02:00–04:00 UTC).
- **Time Caps**: Put strict contractual limits on maintenance hours (e.g., maximum 4 hours per calendar month). Excess maintenance time counts as unexcused downtime.

### Real-World Production Scenario

A legacy banking API requires a 2-hour offline database upgrade. The commercial SLA permits 4 hours of off-peak weekend maintenance, so customer credits are not triggered. However, the SRE team logs the 2 hours against their internal quarterly SLO budget. Because the entire quarter's error budget is exhausted by the maintenance, product feature deployments are frozen until the team implements online schema migration tooling.

## Example

```promql
# Commercial SLA view: exclude announced maintenance using a gauge that is 1 during windows
# (exported by the change-management system, e.g. maintenance_window_active{service="banking-api"})
# a minute counts as "up" if the probe succeeded OR a window was active
avg_over_time(
  clamp_max(
    min(probe_success{service="banking-api"})
      + on() (max(maintenance_window_active{service="banking-api"}) or on() vector(0)),
    1
  )[30d:1m]
)

# Internal SLO view: the same probe with NO exclusion - users were down either way
avg_over_time(min(probe_success{service="banking-api"})[30d:1m])
```

Both numbers come from the same raw data; only the report layer differs. Alert silences for the window go in Alertmanager (`amtool silence add service=banking-api --duration=2h --comment="CHG-1234"`), which suppresses notifications without altering stored metrics.

## Interview tips

- Differentiate clearly between internal SRE SLOs (which should minimize or eliminate maintenance exclusions) and contractual B2B SLAs (which routinely include them).
- Explain modern techniques that eliminate planned downtime, such as zero-downtime database migrations (gh-ost, pg_repack, expand/contract).
- Describe how monitoring platforms (Datadog, Prometheus, New Relic) implement downtime schedules to suppress alert notifications without corrupting raw metric stores.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
