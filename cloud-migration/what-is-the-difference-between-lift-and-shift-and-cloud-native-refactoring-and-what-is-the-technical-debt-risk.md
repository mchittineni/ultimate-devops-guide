---
title: "What is the difference between Lift-and-Shift and Cloud-Native Refactoring and what is the technical debt risk?"
id: 693
category: "Cloud Migration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cloud-migration
  - lift-and-shift
  - refactoring
  - technical-debt
quiz:
  stem: "What is the most common operational failure when organizations execute a rapid 'Lift-and-Shift' cloud migration without post-migration optimization?"
  options:
    - "Cloud providers shut down VMs after 30 days"
    - "Cloud infrastructure costs explode because statically oversized on-premise VMs run 24/7 on expensive cloud IaaS without autoscaling or managed services"
    - "Virtual machines lose all network connectivity"
    - "The application source code is deleted"
  answer: 2
  explanation: "On-premise hardware was sized for peak capacity. Lifting and shifting oversized VMs directly to cloud IaaS without rightsizing or autoscaling leads to severe cloud bill shock."
---

# What is the difference between Lift-and-Shift and Cloud-Native Refactoring and what is the technical debt risk?

**Short answer:** Lift-and-Shift moves legacy VMs directly to cloud IaaS without modernization, offering rapid data center evacuation; Cloud-Native Refactoring redesigns apps into containerized, stateless microservices; Lift-and-Shift incurs a high risk of inflated cloud bills if left un-optimized.

## Detail

Many organisations choose lift-and-shift with the promise: _"We will move everything to EC2 first, and modernise in phase 2."_ Phase 2 often never gets funded, because once the data centre is closed the urgency disappears.

### How the two approaches differ

|                | Lift-and-shift (rehost)                                           | Cloud-native refactoring                                                                  |
| -------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Change         | VMs replicated as-is (AWS MGN, Azure Migrate)                     | Application redesigned: containers or serverless, managed data stores, stateless services |
| Speed          | Weeks per wave                                                    | Months per application                                                                    |
| Risk           | Low technical risk during the move                                | Higher: new architecture, new failure modes                                               |
| Cloud benefits | Few: no autoscaling, same patching, same single points of failure | Elasticity, managed HA, faster delivery                                                   |
| Cost profile   | Often _higher_ than on-premises if left unoptimised               | Pay closer to actual demand, after significant investment                                 |

### The technical debt trap of lift-and-shift

- **Cloud bill shock**: on-premises VMs were sized for peak and for hardware headroom. Copying a 64-core, 512 GB VM to an equivalent on-demand instance that runs 24/7 is frequently more expensive than the depreciated hardware it replaced.
- **Carried-over fragility**: the application still cannot scale horizontally, still has single-VM failure modes, and still needs manual OS patching - now on infrastructure you pay for by the hour.
- **New dependencies across a WAN**: if part of the system stays on-premises, chatty calls that used to be sub-millisecond now cross a hybrid link.
- **Licensing surprises**: bring-your-own-licence rules for Windows Server, SQL Server, and Oracle on shared cloud tenancy can change the economics.

### When lift-and-shift is the right call

- A hard deadline: data-centre lease expiry, hardware end-of-life, or an acquisition exit.
- Stable, low-change applications that will be retired or replaced within a couple of years.
- As step one of a deliberate "migrate, then modernise" plan - with the modernisation funded up front.

**Making it safe**: right-size from measured utilisation during migration (not after), turn on cost visibility from day one, buy commitments (Savings Plans, reservations) only after sizing settles, replatform the easy wins (managed databases, load balancers) in the same wave, and put the phase-2 refactoring budget in the business case so it cannot quietly disappear.

**The refactoring risk**: refactoring during a deadline-driven migration combines two large risks. Refactor where the application's business value and change rate justify it, ideally once it is already running in the cloud and you have real telemetry.

## Example

```bash
# Post-migration right-sizing: what does the lifted fleet actually use?
aws compute-optimizer get-ec2-instance-recommendations \
  --filters name=Finding,values=Overprovisioned \
  --query 'instanceRecommendations[].{id:instanceArn,now:currentInstanceType,
           rec:recommendationOptions[0].instanceType,
           savings:recommendationOptions[0].savingsOpportunity.estimatedMonthlySavings.value}' \
  --output table
# i-0a1...  m5.16xlarge -> m7g.4xlarge   ~ $1,650/month   <- sized for 2019 on-prem peak
```

## Interview tips

- Define both clearly, then go straight to the trade-off: speed and low migration risk versus cost and missing cloud benefits.
- Explain why lift-and-shift bills rise: peak-sized VMs running 24/7 at on-demand rates.
- Say when rehost is right - hard deadlines, stable or short-lived apps - and how you contain the debt: right-size, replatform quick wins, funded phase 2.
- Warn against refactoring under a deadline; sequence it after the move with real telemetry.
- A concrete right-sizing example (Compute Optimizer findings) shows you have done the follow-through.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
