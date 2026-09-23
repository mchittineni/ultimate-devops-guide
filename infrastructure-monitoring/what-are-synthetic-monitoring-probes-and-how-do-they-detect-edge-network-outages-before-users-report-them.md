---
title: "What are Synthetic Monitoring probes and how do they detect edge network outages before users report them?"
id: 691
category: "Infrastructure Monitoring"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - monitoring
  - synthetic
  - blackbox
  - availability
quiz:
  stem: "Why does Real User Monitoring (RUM) fail to alert during a catastrophic DNS outage that completely blocks users in a region from reaching your application?"
  options:
    - "RUM only works on mobile phones"
    - "Because blocked users cannot load the application JavaScript bundle required to execute and transmit RUM telemetry back to your monitoring servers"
    - "DNS servers automatically disable RUM tracking"
    - "RUM metrics can only be computed once per month"
  answer: 2
  explanation: "RUM relies on client-side JavaScript executing in the user's browser. If a DNS failure prevents users from loading the site entirely, no RUM telemetry is ever generated."
---

# What are Synthetic Monitoring probes and how do they detect edge network outages before users report them?

**Short answer:** Synthetic monitoring uses automated headless browsers or API agents located in global cloud regions to periodically simulate real user interactions (login, search, checkout), verifying uptime, SSL validity, and performance before real users are impacted.

## Detail

Real User Monitoring (RUM) only works when users are actively clicking on your site. If an edge routing failure blocks 100% of traffic from Europe, **RUM sees zero errors because zero users can reach the site to report metrics!**

### How Synthetic Probes Solve This

Probing agents run in 20 global AWS/GCP regions outside your network:

1. **API & Endpoint Checks**: Sends HTTP `GET /health` every 60 seconds; checks status code, response payload string, and TLS certificate expiration.
2. **Multi-Step Browser Journeys**: Headless Chromium (Playwright/Puppeteer) scripts that:
   - Load the homepage.
   - Log into a test account.
   - Add an item to the shopping cart.
   - Verify payment gateway loads.
3. **Instant Regional Detection**: If the probe running in Frankfurt fails while Tokyo succeeds, alerts fire immediately pinpointing a localized European routing or CDN outage.

### Limitations

- **Probes live in data centres**, not on consumer ISPs or mobile networks, so a last-mile problem can be invisible to them; RUM and probes from ISP-hosted vantage points cover that gap.
- **They test what you scripted**: a checkout journey with a test card does not exercise every payment method or every user segment.
- **Flakiness costs trust**: require failures from two or more locations before paging, and keep scripts maintained as the UI changes.
- **Side effects**: synthetic transactions must use test accounts and be excluded from business metrics and SLI denominators (tag them, e.g. `synthetic=true`).

## Example

```typescript
// Playwright browser check (runs as-is with @playwright/test; hosted tools such as Checkly run the same code)
import { test, expect } from "@playwright/test";

test("checkout journey", async ({ page }) => {
  await page.goto("https://shop.example.com/");
  await page.getByRole("link", { name: "Sign in" }).click();
  await page.getByLabel("Email").fill(process.env.SYNTHETIC_USER!);
  await page.getByLabel("Password").fill(process.env.SYNTHETIC_PASSWORD!);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.getByRole("button", { name: "Add to cart" }).first().click();
  await page.goto("https://shop.example.com/checkout");
  await expect(page.getByText("Payment details")).toBeVisible({ timeout: 10_000 });
});
```

## Interview tips

- Limitation of RUM: zero traffic during catastrophic outages means zero RUM errors emitted.
- Automated headless browsers (Playwright) executing multi-step user transactions.
- Probing from multiple global geographic regions.
- Detecting localized CDN, DNS, and ISP routing failures proactively.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
