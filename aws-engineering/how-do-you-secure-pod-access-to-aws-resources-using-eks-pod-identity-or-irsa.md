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

**2. Kubernetes ServiceAccount and Pod Deployment using **EKS Pod Identity**:**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: s3-reader-sa
  namespace: production

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-s3-reader
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: s3-reader
  template:
    metadata:
      labels:
        app: s3-reader
    spec:
      serviceAccountName: s3-reader-sa
      containers:
        - name: app
          image: amazon/aws-cli:latest
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

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
