---
title: "How Do You Implement Automated Drift Detection and Remediation in AWS CloudFormation?"
id: 738
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - cloudformation
  - drift-detection
  - iac
quiz:
  stem: "What does a CloudFormation stack status of 'DRIFTED' signify?"
  options:
    - "The CloudFormation template contains invalid YAML syntax."
    - "One or more actual cloud resource configurations differ from the property values declared in the stack template due to manual or out-of-band changes."
    - "The AWS account has reached its maximum EC2 quota limit."
    - "The stack has been scheduled for permanent deletion."
  answer: 2
  explanation: "A status of 'DRIFTED' means that someone or something modified, added, or removed properties on live cloud resources directly outside of CloudFormation management."
---

# How Do You Implement Automated Drift Detection and Remediation in AWS CloudFormation?

**Short answer:** CloudFormation drift detection compares the actual runtime configuration of deployed AWS resources against their template-defined expected state. Automated remediation runs drift detection on a schedule (EventBridge Scheduler or the AWS Config `cloudformation-stack-drift-detection-check` rule), routes the results through EventBridge, and reverts drift - most safely with a **drift-aware change set** (`--deployment-mode REVERT_DRIFT`, added in November 2025) that previews and then restores template values - or opens a pull request when the manual change should become the new truth.

## Detail

### The Problem of Infrastructure Drift

Infrastructure as Code (IaC) assumes that templates represent the single source of truth for deployed cloud environments. In reality, emergency out-of-band changes in the AWS Console, manual security group edits, or automated scaling adjustments introduce **configuration drift**.

Drift degrades security compliance and can cause future IaC deployments to fail unexpectedly.

### How CloudFormation Drift Detection Works

1. CloudFormation queries the resource properties defined in the stack template.
2. CloudFormation makes read calls to the underlying resource APIs (e.g., `DescribeSecurityGroups`, `DescribeVolumes`).
3. It performs a property-by-property comparison and marks the stack status:
   - `IN_SYNC`: All properties match.
   - `DRIFTED`: One or more properties have been manually modified, added, or deleted outside CloudFormation.

### Building Automated Drift Remediation

```text
[EventBridge Cron Schedule (Daily)]
               │
               ▼
[Lambda: DetectStackDrift API]
               │
               ▼
[EventBridge: CloudFormation Drift Detected]
               │
               ├─ Alert SecOps via Slack / SNS
               └─ Trigger Remediation Lambda / Systems Manager Automation
```

### Remediation Strategies

- **Revert via CloudFormation**: create a **drift-aware change set** with `--deployment-mode REVERT_DRIFT`; it shows a three-way diff (new template, last-deployed template, actual state) and, when executed, puts drifted properties back to the template values. This keeps CloudFormation as the only writer, unlike a Lambda that edits resources directly.
- **Targeted Lambda / SSM Automation**: for a narrow, high-risk class of drift (an open security group), a function can remove the offending rule immediately and let the next deployment reconcile.
- **GitOps Reconciliation**: For teams treating code as supreme, drift triggers a pipeline that opens an automated GitHub pull request or notifies the on-call engineer to synchronize template definitions with reality.
- **AWS Config Integration**: Pair CloudFormation with AWS Config managed rules (e.g., `cloudformation-stack-drift-detection-check`) to maintain continuous compliance records.

**Limitations.** Drift detection covers only supported resource types and properties, only properties explicitly set in the template (defaults are not compared), and nothing CloudFormation does not manage. It is also rate-limited, so run it per stack on a schedule rather than continuously.

### Real-World Production Scenario

During a security audit, a DevOps team discovers an engineer manually opened port 22 to `0.0.0.0/0` on a production security group to debug an outage. An AWS Config rule running daily drift checks identifies the discrepancy against the CloudFormation template, fires an EventBridge alert, and triggers an automated Lambda function that removes the rogue ingress rule within 60 seconds.

## Example

```bash
# 1. Detect drift for a stack and wait for the result
ID=$(aws cloudformation detect-stack-drift --stack-name payments-prod \
  --query StackDriftDetectionId --output text)
aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id "$ID" \
  --query '[DetectionStatus,StackDriftStatus,DriftedStackResourceCount]'

# 2. See exactly which properties changed
aws cloudformation describe-stack-resource-drifts --stack-name payments-prod \
  --stack-resource-drift-status-filters MODIFIED DELETED \
  --query 'StackResourceDrifts[].[LogicalResourceId,PropertyDifferences[].PropertyPath]'

# 3. Revert drift safely: a drift-aware change set, reviewed before execution
aws cloudformation create-change-set --stack-name payments-prod \
  --change-set-name revert-drift-$(date +%s) \
  --use-previous-template --deployment-mode REVERT_DRIFT \
  --capabilities CAPABILITY_NAMED_IAM
aws cloudformation describe-change-set --stack-name payments-prod \
  --change-set-name "$CHANGE_SET" --query 'Changes[].ResourceChange.[LogicalResourceId,Action]'
aws cloudformation execute-change-set --stack-name payments-prod --change-set-name "$CHANGE_SET"
```

```bash
# Continuous check via AWS Config (managed rule), which needs a role CloudFormation drift APIs can use
aws configservice put-config-rule --config-rule '{
  "ConfigRuleName": "cfn-stack-drift",
  "Source": {"Owner": "AWS", "SourceIdentifier": "CLOUDFORMATION_STACK_DRIFT_DETECTION_CHECK"},
  "InputParameters": "{\"cloudformationRoleArn\":\"arn:aws:iam::123456789012:role/config-cfn-drift\"}",
  "MaximumExecutionFrequency": "TwentyFour_Hours"
}'
```

## Interview tips

- Explain that drift detection only inspects supported resource types and supported properties, not unmanaged third-party state.
- Contrast reactive drift detection (CloudFormation drift API) with proactive preventative controls (Service Control Policies and IAM denying manual Console modifications).
- Discuss the trade-off between automated auto-remediation (which might overwrite emergency hotfixes) versus notification-driven manual review.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
