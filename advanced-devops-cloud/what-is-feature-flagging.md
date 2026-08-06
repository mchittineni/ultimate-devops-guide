---
title: "What is Feature Flagging?"
id: 146
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Feature Flagging?

**Short answer:** Feature flagging wraps functionality in a runtime conditional so it can be turned on or off without deploying — decoupling deployment from release and enabling gradual rollout, instant kill switches, and experimentation.

## Detail

**Types of flag**, which differ in lifespan and who owns them:

- **Release flags** — hide incomplete work so it can be merged to trunk. Short-lived; removed once shipped.
- **Operational / kill switches** — disable an expensive or risky feature during an incident. Long-lived by design.
- **Experiment flags** — A/B tests with metric measurement. Removed when the experiment concludes.
- **Permission flags** — entitlement by plan or customer. Permanent, and arguably belongs in the authorisation system rather than the flag system.

**Why it matters for delivery.** Flags are what make trunk-based development practical: unfinished work merges continuously and stays dark. They also give you a rollback mechanism measured in seconds rather than the minutes a redeploy takes — during an incident, disabling a flag is almost always the fastest mitigation.

**Targeting** — flags can evaluate per user, per segment, per percentage, or per region, which is what enables progressive rollout: 1% of internal users, then 10% of customers, then everyone, watching metrics at each step.

**The main risk is debt.** Every flag is a branch in the code, and combinations multiply. Manage it deliberately: set an expiry date at creation, track flag age, alert on stale flags, and treat removal as part of finishing the feature — not optional cleanup.

**Implementation:** LaunchDarkly, Unleash, Flagsmith, or OpenFeature (the vendor-neutral standard) — with local caching and a safe default so an outage of the flag service does not take down your application.

## Example

```javascript
const enabled = await flags.getBooleanValue("new-checkout", false, {
  userId,
  plan,
});
return enabled ? newCheckout(cart) : legacyCheckout(cart); // default false = safe fallback
```

## Interview tips

- "Decouple deploy from release" is the phrase that captures the value.
- Flag debt and expiry dates is the operational reality most candidates omit.
- A safe default when the flag service is unreachable is a small detail that shows production thinking.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
