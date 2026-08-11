---
title: "What questions should you ask your interviewer?"
id: 275
category: "Interview Experience"
difficulty: "Beginner"
tags:
  - devops
  - interview-experience
  - interview-questions
---

# What questions should you ask your interviewer?

**Short answer:** Ask about on-call and incident practice, how changes reach production, who owns the platform, and what the last serious outage taught them. These are genuine due diligence - a DevOps role is defined far more by the operational culture than by the tool list - and they double as a final signal that you think like an operator. "No questions" is the one answer that costs you.

## Detail

**This is still part of the interview.** The questions you ask reveal what you consider important. Asking about on-call load and deployment frequency tells the interviewer you have run production systems; asking only about salary and remote policy tells them something else.

**They also protect you.** DevOps roles vary enormously behind identical job descriptions. The same title can mean building a self-service platform, or being a ticket queue for other teams' deployments. These questions surface which one it is before you accept.

**Operational reality - the highest-signal area:**

- How does the on-call rotation work? How many people are in it, and what does a typical week look like?
- Roughly how many pages a week, and what proportion are actionable?
- Is there compensation or time back for on-call?
- What happened in your last significant incident, and what changed as a result?
- Are postmortems written, and are they blameless in practice or just in name?

The answer to "what did your last outage change" is enormously revealing. A team that can name concrete follow-up actions has a real learning culture; a vague answer usually means incidents recur.

**Delivery and autonomy:**

- How often do you deploy to production, and how long does a change take from merge to live?
- Can a developer deploy without a DevOps engineer being involved?
- What does the approval or change-management process look like?
- How much of the week goes to planned work versus interruptions and tickets?

That last one is the single best predictor of job satisfaction in this field. If the honest answer is "mostly tickets", you are joining a service desk regardless of the title.

**Team, ownership, and scope:**

- Who owns the platform, and who owns the applications running on it?
- Is this role building a platform for other teams, or supporting a specific product?
- Why is the role open - growth, or backfill? (Both are fine; the follow-up is what you learn from.)
- How is the team split between platform, SRE, and embedded engineers?
- What does success look like in this role at three and twelve months?

**Technical direction:**

- What is the biggest source of toil right now, and is anyone funded to remove it?
- How much technical debt is there in the platform, and is there time allocated to it?
- What is the migration or modernisation you know is coming?
- How do you handle cost - does anyone own the cloud bill?

**Questions to skip.** Anything answered on the careers page. Compensation in an early technical round - that is the recruiter's conversation. And avoid interrogating the interviewer about their own tooling choices in a way that reads as criticism; "why did you pick Jenkins over GitHub Actions?" is fine, "you're still on Jenkins?" is not.

**Adjust by round.** Ask the technical interviewer about architecture, toil, and on-call; ask the hiring manager about scope, success criteria, and team structure; ask HR about process, timeline, and compensation. Asking the right person the right question is itself a signal.

**Read the room on quantity.** Two or three good questions beat a list of ten. Have five or six prepared, ask the ones the conversation has not already answered, and say so - "you covered my main question about on-call earlier, so instead I'd like to ask about..." shows you were listening.

## Example

```text
BY ROUND — pick 2-3 that the conversation has not already answered

  TECHNICAL INTERVIEWER
    "What's the biggest source of toil for the team right now?"
    "How often do you deploy, and can a developer ship without you?"
    "What did your last significant incident change about how you work?"
    "What does the on-call week actually look like — pages per week?"

  HIRING MANAGER
    "Is this role building a platform for other teams, or supporting one product?"
    "What does success look like at three months and at twelve?"
    "How is the week split between planned work and interruptions?"
    "Why is the role open?"

  HR / RECRUITER
    "What are the remaining rounds and the expected timeline?"
    "How is on-call compensated?"
    "What's the range for this level?"

WHAT THE ANSWERS TELL YOU

  "We deploy every two weeks, with a CAB approval"
      → change-heavy, slow feedback; expect release-engineering work

  "Developers deploy themselves; we own the paved road"
      → genuine platform role; the good version of this job

  "On-call is the whole team, roughly two pages a week, comp time given"
      → healthy rotation, alerts are tuned

  "On-call is just you, and it's pretty noisy"
      → unowned alerting and no rotation depth; negotiate or walk

  "We don't really do postmortems, we just fix it"
      → incidents will recur, and you will be the one fixing them
```

## Interview tips

- Never say "no, I think you've covered everything." Have at least two questions ready even for a 20-minute screen.
- Lead with on-call and incident practice. It is the most useful information you can get and the strongest signal you can send.
- "What did your last outage change?" is the single best question in this list. Listen for specifics.
- Ask about the planned-work-versus-tickets split before accepting. It determines what the job actually is.
- Take notes on the answers. It reads as seriousness, and you will need the comparison if you get multiple offers.
- Reference something from earlier in the conversation. It proves you listened and turns the close into a discussion rather than a checklist.
- Save compensation for the recruiter, and do not skip it - just put it in the right round.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
