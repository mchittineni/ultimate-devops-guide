---
title: "What is Psychological Safety and why is it the strongest predictor of high-performing engineering teams?"
id: 682
category: "DevOps Culture and Practices"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - devops-culture-and-practices
  - culture
  - psychological-safety
  - google-aristotle
  - leadership
quiz:
  stem: "What was the primary conclusion of Google's multi-year Project Aristotle study on high-performing teams?"
  options:
    - "Teams with the highest average individual IQ scores consistently outperformed other teams"
    - "Psychological safety—the feeling that team members can take risks and make mistakes without fear of punishment—was the single most important predictor of success"
    - "Remote teams are incapable of delivering enterprise software"
    - "Teams must use identical programming languages to collaborate"
  answer: 2
  explanation: "Project Aristotle proved that psychological safety outweighed all other factors (including individual talent, seniority, and workload) in determining team success and innovation."
---

# What is Psychological Safety and why is it the strongest predictor of high-performing engineering teams?

**Short answer:** Psychological safety is the shared belief that team members will not be punished, humiliated, or ostracized for speaking up with ideas, questions, concerns, or mistakes; the concept comes from Amy Edmondson's research, and Google's Project Aristotle found it the most important of the five team dynamics it identified. DORA's research points the same way, finding that a generative, high-trust (Westrum) culture predicts software delivery performance.

## Detail

Google studied more than 180 of its teams (Project Aristotle, published 2015-16) to understand why some teams succeeded while others failed. They found that **who was on the team mattered far less than how the team interacted** - psychological safety ahead of dependability, structure and clarity, meaning, and impact.

### Key Findings of Psychological Safety

- **Willingness to Admit Errors**: In psychologically safe teams, engineers report outages and bugs immediately without fear, allowing faster mitigation. In fearful teams, bugs are hidden until catastrophic failure.
- **Innovation & Experimentation**: Engineers feel safe proposing radical architectural refactors or challenging senior leadership's assumptions.
- **Blameless Learning**: Failures are treated as systemic learning opportunities rather than personal incompetence.

### Behaviors that Foster Psychological Safety

- Leaders admitting their own mistakes and knowledge gaps publicly.
- Active listening and equal conversational turn-taking in meetings.
- Banning toxic brilliant jerks who demean colleagues.

**What it is not.** Psychological safety is not comfort or low standards. Edmondson pairs it with accountability: high safety with high standards is the "learning zone"; high safety with low standards is the "comfort zone". It is also a correlation from survey research, so "strongest predictor" should be stated with that caveat - it enables good practices rather than replacing them.

## Example

Measure it rather than assume it - items from Edmondson's team psychological safety survey (1-7 agreement; reverse-scored items marked):

```yaml
survey: team-psychological-safety
scale: 1-7
items:
  - text: "If you make a mistake on this team, it is often held against you."
    reverse: true
  - text: "Members of this team are able to bring up problems and tough issues."
  - text: "It is safe to take a risk on this team."
  - text: "It is difficult to ask other members of this team for help."
    reverse: true
  - text: "No one on this team would deliberately act in a way that undermines my efforts."
reporting: team-level averages only, never individual responses
```

## Interview tips

- Google's Project Aristotle identifying psychological safety as #1 driver of team success.
- Engineers feeling safe to take risks, admit errors, and ask questions without fear.
- Correlation with fast incident reporting vs hiding mistakes in toxic teams.
- Leadership modeling vulnerability and encouraging healthy disagreement.
- Distinguish safety from comfort: high safety plus high standards is the goal, not niceness.
- Credit Amy Edmondson for the concept and mention DORA's culture findings alongside Project Aristotle.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
