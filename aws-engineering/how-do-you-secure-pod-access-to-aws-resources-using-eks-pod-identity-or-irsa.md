---
title: "How do you secure pod access to AWS resources using EKS Pod Identity or IRSA?"
id: 247
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# How do you secure pod access to AWS resources using EKS Pod Identity or IRSA?

**Short answer:** Secure pod access to AWS resources (S3, DynamoDB, Secrets Manager) using **EKS Pod Identity** or **IRSA (IAM Roles for Service Accounts)** to assign least-privilege IAM roles directly to Kubernetes Service Accounts, eliminating static AWS access keys stored in Kubernetes secrets.

## Detail

Running Kubernetes workloads on AWS EKS requires authenticating pods against AWS APIs without hardcoding long-lived `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` credentials.

### 1. EKS Pod Identity (Modern Approach)

Introduced at AWS re:Invent 2023, EKS Pod Identity simplifies IAM authentication for pods:

- **Mechanism:** Uses the EKS Pod Identity Agent DaemonSet running on worker nodes. The agent intercepts AWS SDK credential calls from pods via a local link endpoint (`169.254.170.23`).
- **Advantages over IRSA:**
- No OIDC provider configuration required per cluster.
- IAM Trust Policy trusts the `pods.eks.amazonaws.com` service principal rather than individual OIDC URLs.
- Simplifies multi-cluster IAM role sharing across environments.
- Adds session tags (cluster, namespace, service account) automatically, so one role can use ABAC conditions such as `aws:PrincipalTag/kubernetes-namespace`.
- Supports cross-account access natively: an association can name a target role in another account, and EKS performs the role chaining.

**Limitations.** Pod Identity requires the `eks-pod-identity-agent` add-on on EC2-based nodes and does not work for Pods on Fargate, and it only exists on EKS - so IRSA remains the answer for Fargate Pods and for self-managed or non-EKS clusters. Both require a reasonably current AWS SDK in the container.

### 2. IRSA (IAM Roles for Service Accounts - Legacy/Standard)

- **Mechanism:** Uses OpenID Connect (OIDC) identity federation.
- **Flow:**

1. EKS cluster acts as an OIDC Identity Provider in AWS IAM.
2. Kubernetes ServiceAccount is annotated with `eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/MyPodRole`.
3. EKS Pod Mutating Webhook injects a projected service account token volume and `AWS_ROLE_ARN` environment variable into the pod.
4. AWS SDK exchanges the OIDC token for temporary STS credentials (`sts:AssumeRoleWithWebIdentity`).

### 3. Comparison Matrix

| Feature                 | EKS Pod Identity                                 | IRSA                                                       |
| ----------------------- | ------------------------------------------------ | ---------------------------------------------------------- |
| **IAM Trust Principal** | `pods.eks.amazonaws.com`                         | OIDC Provider URL (`oidc.eks.region.amazonaws.com/id/...`) |
| **Cluster Dependency**  | Managed EKS Add-on Agent                         | OIDC Provider per cluster                                  |
| **Role Reusability**    | High (Easily reuse across multiple EKS clusters) | Requires adding each OIDC URL to IAM Trust Policy          |
| **Fargate Pods**        | Not supported                                    | Supported                                                  |
| **Outside EKS**         | No                                               | Any cluster with a public OIDC issuer                      |
| **Session tags / ABAC** | Automatic (cluster, namespace, SA)               | Not added by default                                       |

## Example

**1. IAM Role Trust Policy for **EKS Pod Identity**:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "pods.eks.amazonaws.com"
      },
      "Action": [
        "sts:AssumeRole",
        "sts:TagSession"
      ]
    }
  ]
}
```

**2. Kubernetes ServiceAccount and a Job using **EKS Pod Identity** (no annotation needed - the association lives in the EKS API):**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: s3-reader-sa
  namespace: production

---
apiVersion: batch/v1
kind: Job
metadata:
  name: s3-reader-check
  namespace: production
spec:
  backoffLimit: 1
  template:
    spec:
      serviceAccountName: s3-reader-sa
      restartPolicy: Never
      containers:
        - name: app
          image: amazon/aws-cli:2.27.0 # pin a version rather than :latest
          command: ["aws", "s3", "ls", "s3://company-prod-data-bucket/"]
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
```

**3. Associating Pod Identity with AWS CLI:**

```bash
aws eks create-pod-identity-association \
    --cluster-name prod-eks-cluster \
    --namespace production \
    --service-account s3-reader-sa \
    --role-arn arn:aws:iam::123456789012:role/S3ReaderProductionRole
```

## Interview tips

- Highlight that **EKS Pod Identity** is the recommended modern AWS standard because it eliminates per-cluster OIDC setup and simplifies cross-cluster IAM role sharing.
- Explain the security flaw of node-level IAM roles (Instance Profiles): every pod on the node inherits the node's IAM permissions unless IRSA or Pod Identity is enforced.
- Mention `sts:AssumeRoleWithWebIdentity` for IRSA vs `sts:AssumeRole` with `sts:TagSession` for EKS Pod Identity.
- Know the limits: Pod Identity does not cover Fargate Pods or non-EKS clusters, which is where IRSA is still the answer.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
- [[What are the core trade-offs between Multi-Cloud, Hybrid-Cloud, and Single-Cloud architectures?]] (`#542`): [What are the core trade-offs between Multi-Cloud, Hybrid-Cloud, and Single-Cloud architectures?](../cloud-platforms/what-are-the-core-trade-offs-between-multi-cloud-hybrid-cloud-and-single-cloud-architectures.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
