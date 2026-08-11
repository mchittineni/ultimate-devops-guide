---
title: "How do you run a major incident as incident commander?"
id: 292
category: "Incident Management"
difficulty: "Advanced"
tags:
  - devops
  - incident-management
  - interview-questions
---

# How do you run a major incident as incident commander?

**Short answer:** You coordinate, you do not debug. Declare the incident and take the role out loud, assign the three other roles (operations lead, communications lead, scribe), keep one channel of record, drive on a fixed cadence of "what do we know / what are we doing / who owns it", prioritise **mitigation over root cause** - roll back, fail over, shed load - and hand off the role rather than working past your effectiveness. The commander's output is decisions and clarity, not fixes.

## Detail

**Declare early, and make the role explicit.** The most common failure in a major incident is that four people debug in parallel for forty minutes with nobody deciding anything. Say the words: "I am incident commander for this incident." Over-declaring costs a few minutes of process; under-declaring costs an hour of confusion. Declaring also starts the clock on the artifacts you will need later - a channel, a document, a timeline.

**The roles, from the ICS model that Google and PagerDuty both adapted:**

- **Incident commander (IC)** - owns the incident, makes decisions, holds the state of the world. Does not type into production.
- **Operations lead (OL)** - the only person making changes to the system. Everything goes through them so the timeline stays accurate and nobody applies two conflicting fixes.
- **Communications lead (CL)** - updates the status page, stakeholders, and support on a fixed cadence, so the IC is not interrupted by "any news?".
- **Scribe** - timestamps every finding, action, and decision in the channel. Without this, the review a week later is reconstruction from memory.

At small scale one person may hold two roles, but the IC and OL must be different people once the incident is genuinely major. If you find yourself in a terminal, you have stopped being IC.

**Run it on a cadence.** Every 15-30 minutes, and immediately after any significant change, run the same loop aloud: _what do we know, what have we ruled out, what are we doing now, who owns it, and when do we next check in._ This is what converts a room full of theories into a sequence of tested hypotheses. Keep a live "current state" pinned in the channel and update it - people joining an hour in must not need to read 400 messages.

**Mitigate before you diagnose.** The question is "how do we stop the customer impact", not "why is this happening". The mitigation menu, roughly in order of speed: **roll back** the most recent change (the answer surprisingly often), **disable the feature flag**, **fail over** to another region or replica, **shed load** or rate-limit, **scale up**, **drain the bad node or pod**, **serve degraded** from cache. Understanding causes is the post-incident review's job. Resisting the urge to find root cause first is the hardest discipline of the role.

**Communicate on a schedule, not on progress.** Publish the first customer-facing update within minutes even when it says only "we are investigating reports of errors on checkout" - silence is read as incompetence. Then update every 30 minutes whether or not anything changed, with impact in customer terms, and never with a speculative ETA. Internally, keep stakeholders in a separate channel with the CL, not in the operational one.

**Manage the humans.** Pull in a second pair of eyes early rather than late; the cost of an extra engineer is far below the cost of a missed cause. Watch for tunnel vision and ask for the disconfirming evidence ("what would we see if that theory were wrong?"). Explicitly hand off the IC role after two or three hours or when you notice your own degradation - a documented handoff with a state summary is normal practice, not an admission of failure. And say clearly at the start that the review will be blameless, because people withhold information when they fear consequences.

**Close it deliberately.** Declare mitigation and recovery as two separate events. Then: confirm the metrics are actually back to baseline, publish a final customer update, capture the timeline while it is fresh, schedule the review within a few days, and file the immediate follow-up actions with owners before everyone disperses. Actions without an owner and a date do not happen.

## Example

```text
Channel #inc-2026-08-07-checkout-errors   (one channel of record)

09:12  IC: Declaring SEV1. I am IC. @dana OL, @sam CL, @kai scribe.
       Impact: checkout 5xx ~40% since 09:04. Status page: investigating.
09:14  CL: status page updated - "elevated errors on checkout, investigating".
09:16  IC: What do we know? Ruled out? Doing now?
       Known: 5xx from checkout-api, DB p99 up 20x. Deploy at 09:02.
       Ruled out: no infra events, no traffic spike.
       Doing: OL rolling back checkout-api to 1.8.2. Owner @dana. Check in 09:26.
09:23  OL: rollback complete. 5xx falling: 40% -> 6%.
09:31  IC: mitigation confirmed, error rate 0.3% = baseline. NOT resolved -
       cause unknown, keeping incident open, deploy freeze on checkout.
09:35  CL: customer update - service restored, monitoring.
10:05  IC: recovery confirmed, 30 min at baseline. Resolving.
       Review Fri 11:00. Follow-ups filed: SEV-441 (missing migration gate,
       @dana, 14 Aug), SEV-442 (add canary analysis to checkout, @kai, 21 Aug).
```

```markdown
<!-- Pinned and continuously updated: the state of the world for anyone joining -->

**INC-2026-08-07 checkout errors** · SEV1 · IC @maya · started 09:04

- **Impact:** ~40% of checkout requests failing; ~2,100 customers affected
- **Current theory:** migration in release 1.9.0 caused a lock contention spike
- **Ruled out:** traffic spike, infra events, upstream payment provider
- **In progress:** rollback to 1.8.2 (@dana), DB lock analysis (@kai)
- **Next check-in:** 09:26
```

## Interview tips

- Say "the IC coordinates and does not debug" in the first breath, and add that if you are in a terminal you are no longer IC. That one line demonstrates the whole role.
- Name the four roles and what each one protects the IC from. Interviewers listen for the comms lead specifically, because it is what stops stakeholder interruption.
- Be explicit that mitigation precedes diagnosis, and give the mitigation menu with rollback first.
- The fixed cadence loop - know / ruled out / doing / owner / next check-in - is worth quoting verbatim. It shows you have actually run one.
- Mention handing off the IC role after a few hours. Candidates who claim to run an eight-hour incident alone reveal inexperience.
- Close on the artifacts: timeline captured live, blameless review scheduled, follow-ups with owners and dates before people disperse.
- Have a real incident ready in this structure, and be honest about what went wrong in your handling of it. The self-critique is usually what earns the mark.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#20`): [What is the difference between Continuous Delivery and Continuous Deployment?](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
