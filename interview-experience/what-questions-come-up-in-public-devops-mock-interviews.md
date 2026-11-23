---
title: "What questions come up in public DevOps mock interviews?"
id: 805
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - mock-interviews
  - aws-engineering
  - kubernetes
  - infrastructure-as-code
  - cicd
  - docker
---

# What questions come up in public DevOps mock interviews?

## Questions

Eight publicly recorded DevOps and cloud mock interviews, worked through question by question: 194 questions in all, from senior AWS rounds to a Kubernetes troubleshooting drill. Each round links to its source recording, and every question links to the answer in this guide that covers it. Where a recording showed a weak or wrong answer, the linked page covers the correct one, and the most common mistakes are collected in the tips below.

Unlike the employer rounds elsewhere in this section, these interviews were recorded to be watched, so they lean towards scenario and design questions and follow-ups that probe a first answer. That makes them a good rehearsal for the "why?" and "what if?" that follow your opening answer.

### Round 1 — Senior AWS DevOps — architecture, EKS, and Terraform at scale

[Source recording](https://www.youtube.com/watch?v=USTMvk53wvM) · 61 questions

- [How would you architect a highly available and fault-tolerant application on AWS?](../cloud-native-architecture/how-do-you-design-a-secure-highly-available-three-tier-architecture.md)
- [Why did you choose EKS over ECS or plain EC2 for this architecture?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [Why would ECS not be a good choice here, given that many enterprises run HA, fault-tolerant workloads on ECS?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [Give a scenario where ECS is better suited than EKS.](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [Which is cheaper, ECS or EKS, and why?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [There is no option to create a subnet as 'public' or 'private'. What configuration makes a subnet public or private?](../aws-engineering/how-does-a-private-subnet-reach-the-internet.md)
- [Is an internet gateway attached to a subnet or to a VPC?](../aws-engineering/how-does-a-private-subnet-reach-the-internet.md)
- [If a private subnet needs internet access, is the outbound route defined in the public subnet's route table or the private subnet's?](../aws-engineering/how-does-a-private-subnet-reach-the-internet.md)
- [What options do you have to connect an on-premises network to AWS (hybrid networking)?](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md)
- [We already have VPC peering. What problem does Transit Gateway solve, and why use it instead of peering?](../aws-engineering/how-do-aws-transit-gateway-and-vpc-peering-compare-for-enterprise-interconnectivity.md)
- [Why is VPC peering cheaper than Transit Gateway when connecting only two VPCs?](../aws-engineering/how-do-aws-transit-gateway-and-vpc-peering-compare-for-enterprise-interconnectivity.md)
- [Design a disaster recovery solution for an e-commerce website, with the DR region geographically isolated from the primary.](../backup-and-disaster-recovery/what-are-rto-and-rpo-and-how-do-they-drive-disaster-recovery-architecture-tiers.md)
- [How would you serve the e-commerce site globally (for example US and India) with minimal latency, with each region served from a nearby data center and with separate writes and databases per region?](../aws-engineering/how-do-you-architect-multi-region-active-active-deployments-on-aws-with-dynamodb-global-tables.md)
- [Name security best practices for each area: networking, compute, storage and databases.](../security-and-compliance/what-is-infrastructure-security.md)
- [For a cost-conscious customer who can't afford Shield, WAF and similar services, what bare-minimum things would you do to keep the cloud secure?](../aws-engineering/what-baseline-security-controls-would-you-apply-to-an-aws-account-on-a-tight-budget.md)
- [If a database must sit in a public subnet so a third party can access it, how do you extend access without compromising security?](../aws-engineering/what-is-aws-privatelink-and-how-does-it-enable-secure-cross-vpc-service-consumption.md)
- [Which AWS service (with an agent on EC2) reports which installed packages are vulnerable to which CVEs?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [List and summarize the pillars of the AWS Well-Architected Framework.](../aws-engineering/what-are-the-pillars-of-the-aws-well-architected-framework.md)
- [How do you enable cross-account access, for example an EC2 instance in account A accessing an S3 bucket or KMS key in account B?](../aws-engineering/how-does-aws-iam-evaluate-a-request.md)
- [What issues have you faced setting up cross-account access, and how did you resolve them?](../aws-engineering/how-does-aws-iam-evaluate-a-request.md)
- [What steps are needed to host a website (for example abc.com) publicly on S3?](../aws-engineering/how-do-you-secure-and-manage-the-lifecycle-of-an-s3-bucket.md)
- [As a cloud engineer, what FinOps or cost-optimization measures would you implement for a cost-sensitive customer?](../cloud-cost-optimization/how-do-you-cut-a-cloud-bill-without-hurting-reliability.md)
- [Is AWS Trusted Advisor free?](../cloud-cost-optimization/what-are-zombie-cloud-resources-and-how-do-you-identify-and-automate-their-cleanup.md)
- [For a batch job that must run at 11:30 PM to pull data from a database, transform it and push it to another pipeline, would you still use a Spot instance?](../cloud-cost-optimization/what-is-spot-instance-pricing.md)
- [What if the required Spot instance type is not available in that region?](../cloud-cost-optimization/what-is-spot-instance-pricing.md)
- [CloudFormation vs Terraform: when would you choose one over the other?](../aws-engineering/when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md)
- [If your infrastructure is AWS-only (no other cloud or on-prem), would you still choose Terraform over CloudFormation?](../aws-engineering/when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md)
- [What types of load balancers does AWS offer, and when would you use each?](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md)
- [When would you use API Gateway versus an Application Load Balancer, for example for serverless apps?](../aws-engineering/when-do-you-use-amazon-api-gateway-versus-an-application-load-balancer.md)
- [Your application runs fully on AWS (Route 53, load balancers, Auto Scaling groups, EKS/ECS, RDS) and a customer reports it isn't working. How do you investigate and remediate?](../interview-experience/how-do-you-answer-scenario-based-troubleshooting-questions.md)
- [What Docker image best practices do you follow?](../docker/how-do-you-harden-a-container-image-and-a-dockerfile.md)
- [Where do you host images, and how do you keep ECR from accumulating unlimited images and driving up cost?](../aws-engineering/how-do-you-control-image-sprawl-and-storage-cost-in-amazon-ecr.md)
- [Developers say an image works on their machine but not on ECS/EKS. How do you ensure it runs the same in the cloud?](../docker/why-does-a-container-image-that-works-locally-fail-on-kubernetes-or-ecs.md)
- [Who handles the security of Docker images before they reach ECR, and how?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)
- [You can't trust developers to scan locally. How do you enforce security controls in the pipeline?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)
- [How do you reduce the overall size of a Docker image?](../docker/how-do-you-reduce-docker-image-size-and-build-time.md)
- [How do you upgrade EKS clusters with zero downtime?](../aws-engineering/how-do-you-upgrade-an-amazon-eks-cluster-safely.md)
- [If the EKS upgrade fails and the application stops working, what are your next steps?](../aws-engineering/how-do-you-upgrade-an-amazon-eks-cluster-safely.md)
- [Have you run stateful applications on Kubernetes? Give an example.](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [AWS offers DocumentDB (MongoDB-compatible) as a managed service. Why deploy MongoDB on Kubernetes instead?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [Does Kubernetes support blue/green deployment, and how would you configure it?](../advanced-devops-cloud/what-is-blue-green-deployment.md)
- [What Kubernetes best practices (cost, security, etc.) do you follow?](../kubernetes/what-kubernetes-production-best-practices-do-you-follow-for-reliability-security-and-cost.md)
- [Kubernetes Secrets are only base64-encoded. How do you secure something like a database password used by an application pod?](../devsecops/how-do-you-manage-kubernetes-secrets-in-a-gitops-workflow.md)
- [What Kubernetes troubleshooting scenarios have you faced, and how do you approach them?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)
- [Services can already expose pods. Why do we need Ingress, and how is it different from a Service?](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md)
- [What tool do you use to deploy applications to EKS/Kubernetes?](../devops-tools-and-automation/what-is-argocd.md)
- [Kubernetes already has YAML manifests. Why add the complexity of Helm charts?](../devops-tools-and-automation/what-is-helm-and-how-do-helm-charts-manage-templating-dependencies-and-rollbacks-in-kubernetes.md)
- [What are Kubernetes probes, and how do liveness and readiness probes differ?](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md)
- [Why does a pod need a restart to pick up an updated ConfigMap value, and how can you make it pick up changes automatically?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)
- [For an enterprise landing zone with 15-20 accounts, multiple environments and multiple regions, how would you structure the Terraform directory?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [Do you use open-source Terraform or Terraform Enterprise/Cloud, and do you face challenges with open source?](../infrastructure-as-code/how-do-you-run-terraform-through-a-ci-cd-pipeline.md)
- [With open-source Terraform, how do you deploy something like an EC2 instance to production? Do you apply from your local machine?](../infrastructure-as-code/how-do-you-run-terraform-through-a-ci-cd-pipeline.md)
- [If the customer needs the infrastructure deployed in 5 minutes, would you still go through all these stages?](../infrastructure-as-code/how-do-you-run-terraform-through-a-ci-cd-pipeline.md)
- [When creating infrastructure that needs secrets (SSH keys for EC2, username and password for RDS), where are the secrets stored and how do you keep them from being exposed?](../infrastructure-as-code/how-do-you-keep-secrets-out-of-terraform-state.md)
- [The random-generated secret still ends up in the Terraform state file. How do you keep sensitive values out of state?](../infrastructure-as-code/how-do-you-keep-secrets-out-of-terraform-state.md)
- [With 10 engineers working on the same Terraform code, how do you make sure they don't overwrite each other's changes?](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)
- [How do Terraform Enterprise/Cloud workspaces differ from local CLI workspaces?](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)
- [When a Terraform apply fails or doesn't work as expected, how do you roll back the infrastructure?](../infrastructure-as-code/what-do-terraform-init-plan-apply-and-refresh-actually-do.md)
- [How much of your day-to-day work is driven or assisted by AI?](../devops-tools-and-automation/how-do-you-use-ai-assistants-and-agents-safely-in-day-to-day-devops-work.md)
- [Where do you see yourself in 5 years: hands-on DevOps, management, or architecture?](../interview-experience/how-do-you-answer-where-do-you-see-yourself-in-five-years-in-a-devops-interview.md)
- [How do you reduce friction between DevOps engineers and developers without compromising the work?](../devops-culture-and-practices/what-is-team-collaboration-in-devops.md)

### Round 2 — Cloud engineer — global design, caching, upgrades, and GitOps

[Source recording](https://www.youtube.com/watch?v=y2Xogl5V3aA) · 23 questions

- [Which AWS services have you worked with?](../aws-engineering/what-are-the-core-aws-services-a-devops-engineer-uses-daily.md)
- [How would you architect a highly available, fault-tolerant, globally accessed, low-latency and secure e-commerce application on AWS?](../interview-experience/how-do-you-handle-a-devops-system-design-round.md)
- [CloudFront handles static caching. How would you cache database data that changes rarely (e.g. once or twice a month)?](../scalability-and-high-availability/what-are-the-main-caching-strategies-and-how-do-you-keep-a-cache-consistent-with-the-database.md)
- [Why did you choose EKS over a more AWS-native service like ECS? What does EKS give you that ECS cannot handle?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [How would you make this infrastructure disaster-proof if the primary database or EKS cluster fails, so users see no impact?](../backup-and-disaster-recovery/how-do-you-execute-a-disaster-recovery-failover-with-minimal-rto-and-rpo.md)
- [Given this e-commerce app cannot afford downtime but is cost-sensitive, how would you design DR specifically?](../backup-and-disaster-recovery/what-are-rto-and-rpo-and-how-do-they-drive-disaster-recovery-architecture-tiers.md)
- [Walk me through the full CI/CD and DevOps setup you would build for this e-commerce application: tools, stages and integrations.](../aws-engineering/how-do-you-architect-an-end-to-end-production-devops-project-on-aws.md)
- [What is the need for GitOps/Argo CD? Why not deploy the traditional way with Helm or plain Kubernetes YAML?](../devops-tools-and-automation/what-is-gitops.md)
- [How would you observe the entire infrastructure: frontend, backend and databases?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [How would you trace requests flowing between pods in your EKS cluster? Which tool would you use?](../advanced-devops-cloud/what-is-tracing-in-observability.md)
- [Have you considered ingress in this infrastructure, and have you worked with a specific ingress controller such as the AWS ALB Ingress Controller?](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md)
- [With many microservices, do you see a need for service discovery or a tool like Istio?](../cloud-native-architecture/what-is-service-mesh.md)
- [Tell me about a recent challenge in your DevOps/cloud work, or something you are proud of.](../interview-experience/how-do-you-answer-tell-me-about-a-challenge-you-faced-in-a-devops-interview.md)
- [If the cluster upgrade had failed partway, what was your rollback or contingency plan to keep the application running?](../aws-engineering/how-do-you-upgrade-an-amazon-eks-cluster-safely.md)
- [What does a typical day look like for you as a DevOps engineer?](../interview-experience/how-do-you-describe-your-day-to-day-responsibilities-as-a-devops-engineer.md)
- [A healthcare customer's production infrastructure (EKS, ECS or EC2) must cut cloud costs by at least 30% within 4-8 weeks. How would you approach it?](../cloud-cost-optimization/how-do-you-cut-a-cloud-bill-without-hurting-reliability.md)
- [Have you faced drift between your Terraform/CloudFormation code and the actual cloud state, and how did you handle it?](../infrastructure-as-code/what-is-cloud-drift-and-how-do-you-continuously-detect-and-reconcile-it-in-production.md)
- [During a production outage, the CEO wants it fixed ASAP and the fix needs an infrastructure change. Do you make it quickly in the AWS console or properly through Terraform?](../infrastructure-as-code/what-is-cloud-drift-and-how-do-you-continuously-detect-and-reconcile-it-in-production.md)
- [For one-time infrastructure that won't be updated for about five years, would you still use IaC or just create it in the console?](../infrastructure-as-code/what-is-infrastructure-as-code.md)
- [With hundreds of AWS accounts in a landing zone/Control Tower setup (UAT, prod, security, logging, etc.), how would you structure your Terraform directories?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [Two (or more) engineers are working on the same Terraform repo and infrastructure. How do you make sure they don't step on each other's work?](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)
- [Are you referring to Terraform Cloud/Enterprise workspaces or local CLI workspaces?](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)
- [With AI and MCP on the rise, how will AI change the DevOps role, and what is your plan for adopting AI tools over the next six months?](../devops-tools-and-automation/how-do-you-use-ai-assistants-and-agents-safely-in-day-to-day-devops-work.md)

### Round 3 — Senior DevOps — e-commerce design, disaster recovery, and security

[Source recording](https://www.youtube.com/watch?v=mg1ZqahIpVw) · 23 questions

- [Design a globally accessible e-commerce application on AWS that is highly scalable, robust and highly available. Which AWS services would you use?](../cloud-native-architecture/how-do-you-design-a-secure-highly-available-three-tier-architecture.md)
- [When would you choose a monolith over microservices (EKS/ECS vs plain EC2), and which is more beneficial?](../cloud-native-architecture/what-is-the-difference-between-a-monolith-and-microservices.md)
- [Which is more complicated, Kubernetes or a monolith? With a large team of 10-12 developers and DevOps engineers, would you choose a monolith, microservices or EKS?](../cloud-native-architecture/what-is-the-difference-between-a-monolith-and-microservices.md)
- [How would you monitor this whole e-commerce ecosystem? Would you use AWS services only, or external tools too?](../infrastructure-monitoring/what-are-monitoring-tools.md)
- [If CloudWatch and X-Ray already have the required features, why would you need Datadog at all?](../infrastructure-monitoring/what-are-monitoring-tools.md)
- [If an AWS region or availability zone goes down, how would you design and automate the system so the global application is not impacted?](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md)
- [What best practices and measures would you take to secure this e-commerce application and its cloud infrastructure?](../cloud-native-architecture/how-do-you-design-a-secure-highly-available-three-tier-architecture.md)
- [The customer is cost-sensitive. Give about five key cost-optimization measures across the AWS services you would use (compute, storage, databases, etc.).](../cloud-cost-optimization/how-do-you-cut-a-cloud-bill-without-hurting-reliability.md)
- [The enterprise has on-premises systems that need access to the e-commerce servers and databases in AWS. How would you set up that connectivity?](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md)
- [What is a StatefulSet and how is it different from a Deployment?](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md)
- [Give an example of where you have used a StatefulSet.](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [How do you create a multi-stage Docker build?](../docker/how-does-docker-multi-stage-building-optimize-container-security-and-image-size.md)
- [What Kubernetes troubleshooting scenarios have you faced in production?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)
- [With thousands of pods in a microservices setup, how have you implemented centralized logging in your EKS/Kubernetes cluster so developers and DevOps engineers can access logs?](../monitoring-and-logging/how-do-the-elk-and-efk-stacks-fit-together.md)
- [What is GitOps and Argo CD, and how do they differ from traditional CI/CD pipelines?](../devops-tools-and-automation/what-is-gitops.md)
- [What deployment strategies can you implement in Kubernetes?](../devops-tools-and-automation/what-are-deployment-strategies.md)
- [An application on EKS needs access to DynamoDB tables and S3 buckets, but no access key or secret key may be configured in the application. How do you meet this requirement?](../aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md)
- [To deploy an application across Kubernetes clusters, would you use a Helm chart or plain Kubernetes manifests? Which is easier?](../devops-tools-and-automation/what-is-helm-and-how-do-helm-charts-manage-templating-dependencies-and-rollbacks-in-kubernetes.md)
- [In a multi-account AWS landing zone (log archive, security, networking, and prod/dev application accounts), what Terraform directory structure would you use to build infrastructure and deploy applications across all accounts?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [Why would you write custom Terraform modules when official, AWS/HashiCorp-verified modules already exist?](../infrastructure-as-code/what-are-terraform-modules-and-what-are-the-best-practices-for-module-reusability.md)
- [Have you used dynamic blocks in Terraform? What are they and what is a use case?](../infrastructure-as-code/what-is-the-difference-between-terraform-dynamic-blocks-and-count-for-each-loops.md)
- [How would you design a near-perfect DevOps pipeline, from the developer checking in code to production deployment, using any tools?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)
- [Follow-up: what deployment tool would you use to deploy the Docker image to an EKS cluster?](../devops-tools-and-automation/what-is-argocd.md)

### Round 4 — Senior DevOps — S3 and cross-account access, Kubernetes, Terraform, Git, and Linux

[Source recording](https://www.youtube.com/watch?v=Qy0aCdwaRx4) · 35 questions

- [Which AWS services have you used in your work?](../aws-engineering/what-are-the-core-aws-services-a-devops-engineer-uses-daily.md)
- [How would you restrict access to a specific object in an S3 bucket for a specific user?](../aws-engineering/how-do-you-secure-and-manage-the-lifecycle-of-an-s3-bucket.md)
- [An application on EC2 in AWS account A needs to read data (e.g. product icons) stored in an S3 bucket in account B. How do you set this up?](../aws-engineering/how-does-aws-iam-evaluate-a-request.md)
- [With thousands of objects in S3, how do you give a user temporary access (10-15 minutes) to one particular object?](../aws-engineering/how-do-you-secure-and-manage-the-lifecycle-of-an-s3-bucket.md)
- [A static website hosted in an S3 bucket in ap-south-1 needs to fetch images from another static-website S3 bucket in us-west-2 (same account). How do you enable this?](../aws-engineering/how-do-you-secure-and-manage-the-lifecycle-of-an-s3-bucket.md)
- [A Lambda function in AWS account A must communicate with an application running on EC2 in account B. How do you set up this cross-account resource communication?](../aws-engineering/how-do-you-connect-many-vpcs-peering-transit-gateway-or-privatelink.md)
- [Explain the architecture of Kubernetes.](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [What types of Services are available in Kubernetes?](../kubernetes/what-is-the-difference-between-service-types-clusterip-nodeport-loadbalancer-and-externalname.md)
- [How do you ensure a monitoring agent (e.g. a Dynatrace agent) runs as one pod on every node?](../container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md)
- [Out of 10 pods, how do you make 5 of them get scheduled only on specific nodes?](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md)
- [What is the use of a namespace in Kubernetes?](../kubernetes/what-are-namespaces-in-kubernetes-and-what-do-they-isolate.md)
- [How do you enable communication between pod A in namespace A and pod B in namespace B, and how do you block it?](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md)
- [What is the difference between a Secret and a ConfigMap, and when would you use each?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)
- [Secrets are just base64-encoded, so I could store base64 data in a ConfigMap too. What extra benefits do Secrets give?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)
- [Can you delete a Docker image that a running container was created from?](../docker/can-you-delete-a-docker-image-that-a-container-is-still-using-and-what-happens-to-that-container.md)
- [If the image was force-deleted and you then stop the container, can you restart it? Will the application come back up?](../docker/can-you-delete-a-docker-image-that-a-container-is-still-using-and-what-happens-to-that-container.md)
- [What do HTTP 401 and 403 error codes mean (in Kubernetes or generally), and how do you troubleshoot them?](../api-gateway-and-service-mesh/what-do-the-common-http-status-codes-mean-and-how-do-you-debug-a-502-503-or-504.md)
- [How do you trigger a Jenkins pipeline automatically?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
- [What is a Jenkins multibranch pipeline?](../cicd/what-is-jenkins.md)
- [Non-production RDS databases run 24x7, but developers only work 9-5 on weekdays. How do you save cost by stopping them off-hours?](../cloud-cost-optimization/what-is-cloud-cost-optimization.md)
- [How do you manage the Terraform state file?](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)
- [How do you organize Terraform state for separate prod, staging and dev environments? Would you use one state file for all?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [How would you provision five identical EC2 instances with Terraform?](../infrastructure-as-code/what-is-the-difference-between-count-and-for-each-in-terraform.md)
- [A VPC (named 'demo VPC') was created manually. Your Terraform code creates a Lambda that must be in that VPC, and you only know its name. How do you pass the VPC ID at runtime?](../infrastructure-as-code/what-is-the-difference-between-terraform-depends-on-data-sources-and-implicit-resource-references.md)
- [Have you used dynamic blocks in Terraform?](../infrastructure-as-code/what-is-the-difference-between-terraform-dynamic-blocks-and-count-for-each-loops.md)
- [What are pre-tasks (pre hooks) in Ansible playbooks?](../infrastructure-as-code/what-is-ansible.md)
- [How do you increase disk space on a Linux EC2 server that uses an EBS volume?](../linux-administration/how-do-you-manage-disks-filesystems-and-lvm-on-linux.md)
- [How do you troubleshoot a Linux server with slow performance, and what commands would you use?](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md)
- [How do you manage versions of your application code in Git?](../version-control/how-do-you-version-releases-with-git-tags-and-how-do-you-fix-a-tag-that-is-already-pushed.md)
- [You pushed code with a tag today, found issues and fixed them. How do you edit the tag and push the changes?](../version-control/how-do-you-version-releases-with-git-tags-and-how-do-you-fix-a-tag-that-is-already-pushed.md)
- [How do you manage a hotfix release when a bug is found after deployment?](../version-control/what-is-git-branching-strategy.md)
- [Have you set up monitoring? Briefly explain how you set up Prometheus and Grafana and what you monitor.](../infrastructure-monitoring/how-do-you-monitor-a-kubernetes-cluster-end-to-end.md)
- [How do you troubleshoot pod errors like ImagePullBackOff or CrashLoopBackOff?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)
- [Which command shows which files are consuming the most disk space in a particular directory?](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md)
- [How do you make Jenkins use different agents (slaves) for different environments or branches, e.g. small T2/T3 instances for QA and C5.xlarge for production?](../cicd/what-are-jenkins-pipelines.md)

### Round 5 — DevOps generalist — Linux, Docker, Kubernetes, Terraform, AWS, and Jenkins

[Source recording](https://www.youtube.com/watch?v=fJVmo1R0CPc) · 16 questions

- [Which Linux commands do you use day-to-day as a DevOps engineer?](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md)
- [Explain zombie, orphan, and daemon processes in Linux.](../linux-administration/what-are-zombie-and-orphan-processes-in-linux-and-how-do-you-cleanly-handle-them.md)
- [You need to containerize a three-tier app (React frontend, Node.js backend, MySQL database). How would you write the Dockerfiles / setup?](../docker/how-do-you-containerise-a-three-tier-application-with-docker-and-docker-compose.md)
- [What is a multi-stage Docker build and why use it?](../docker/how-does-docker-multi-stage-building-optimize-container-security-and-image-size.md)
- [How can you optimize a Docker image/build for speed?](../docker/how-do-you-reduce-docker-image-size-and-build-time.md)
- [What does it mean to mark a resource as tainted in Terraform?](../infrastructure-as-code/how-do-you-stop-terraform-from-destroying-or-recreating-a-resource.md)
- [What is a Terraform state file conflict, how does it happen, and how do you solve it?](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)
- [Explain the usage of Pods, ReplicaSets, and Deployments.](../kubernetes/what-is-the-difference-between-a-deployment-and-a-replicaset-in-kubernetes.md)
- [What are labels and selectors, and when do you use them?](../kubernetes/what-are-labels-and-selectors-in-kubernetes-and-where-are-they-used.md)
- [A pod is in CrashLoopBackOff — when does it happen and how do you resolve it?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)
- [How many types of Services are there in Kubernetes?](../kubernetes/what-is-the-difference-between-service-types-clusterip-nodeport-loadbalancer-and-externalname.md)
- [How many types of load balancers does AWS offer?](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md)
- [What are the main components of Docker?](../docker/explain-docker-architecture.md)
- [What is the difference between high availability and downtime?](../scalability-and-high-availability/what-is-high-availability.md)
- [Explain AWS Regions, Availability Zones, and Edge Locations.](../cloud-platforms/what-are-cloud-availability-zones-and-how-are-they-engineered-for-fault-independence.md)
- [What is the Jenkins master-agent (controller-node) architecture?](../cicd/what-is-jenkins.md)

### Round 6 — Role walkthrough — day-to-day work, CI/CD, and shared clusters

[Source recording](https://www.youtube.com/watch?v=6GigmhdY4sA) · 9 questions

- [Introduce yourself and describe your current role as a DevOps engineer.](../interview-experience/how-do-you-answer-tell-me-about-yourself-in-a-devops-interview.md)
- [How do you organize your work, and what does your typical day-to-day look like?](../interview-experience/how-do-you-describe-your-day-to-day-responsibilities-as-a-devops-engineer.md)
- [Walk me through your CI/CD pipeline — what stages are involved and what is the end goal?](../cicd/what-is-ci-cd-pipeline.md)
- [If microservices from many development teams deploy to shared clusters, how do you manage the Kubernetes clusters?](../container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md)
- [Have you worked on multi-region deployments? How do you achieve them?](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md)
- [Tell me about a recent significant challenge you faced and how you solved it.](../interview-experience/how-do-you-answer-tell-me-about-a-challenge-you-faced-in-a-devops-interview.md)
- [What experience do you have with cloud cost optimization? Give an example.](../cloud-cost-optimization/how-do-you-cut-a-cloud-bill-without-hurting-reliability.md)
- [How do you create infrastructure, and do you have experience with Pulumi?](../infrastructure-as-code/what-is-pulumi-and-how-does-it-compare-to-terraform.md)
- [Is there anything else you would like the interviewer to know about you?](../interview-experience/what-questions-should-you-ask-your-interviewer.md)

### Round 7 — Single-question deep dive — explain your CI/CD pipeline

[Source recording](https://www.youtube.com/watch?v=DMYi1C7rYE0) · 10 questions

- [Explain your end-to-end CI/CD pipeline workflow (as a senior engineer would).](../aws-engineering/how-do-you-architect-an-end-to-end-production-devops-project-on-aws.md)
- [What checks run before code is merged to main, and why run secret scanning at the PR stage?](../devsecops/how-do-you-integrate-automated-secret-scanning-into-pre-commit-and-ci-pipelines-to-prevent-credential-leaks.md)
- [How does your CI pipeline authenticate to AWS?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [How do you build, scan and tag container images in the pipeline?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)
- [How does a new image actually reach the Kubernetes cluster, and how is it promoted from staging to production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [If both staging and prod values files live on the same branch, how does GitHub know one PR needs approval and the other doesn't?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [Why use canary deployments with Argo Rollouts instead of default rolling updates, and how is the traffic split actually implemented on AWS? (How does Argo CD talk to AWS?)](../api-gateway-and-service-mesh/how-do-you-implement-canary-releases-with-weighted-traffic-shifting-in-an-api-gateway.md)
- [How are application secrets handled in the deployment?](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md)
- [During a canary, old and new versions run at the same time. How does the database handle schema changes?](../database-management-in-devops/what-is-the-expand-and-contract-pattern-for-zero-downtime-database-schema-migrations.md)
- [What is your rollback strategy, and what actually triggers an automatic rollback?](../cicd/how-do-you-roll-back-a-failed-deployment-in-a-ci-cd-pipeline.md)

### Round 8 — Kubernetes troubleshooting drill

[Source recording](https://www.youtube.com/watch?v=18cdxTz8pCw) · 17 questions

- [A pod is in CrashLoopBackOff — what causes it and how do you troubleshoot it?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)
- [A pod is stuck in ImagePullBackOff / ErrImagePull — why does it happen and how do you fix it?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-imagepullbackoff.md)
- [A container is being OOMKilled — what does that mean and how do you handle it?](../kubernetes/how-do-requests-limits-and-qos-classes-work-in-kubernetes.md)
- [Pods are stuck in Pending — how do you troubleshoot it?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)
- [A worker node shows NotReady — what are the causes and how do you investigate?](../kubernetes/how-do-you-troubleshoot-a-kubernetes-node-that-is-notready.md)
- [A readiness probe is failing — what are the symptoms and how does the readiness probe work?](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md)
- [What is the difference between a liveness probe and a readiness probe, and what happens when a liveness probe fails?](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md)
- [Pods cannot resolve service names (DNS resolution failure) — how do you troubleshoot it?](../kubernetes/how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md)
- [A PersistentVolumeClaim is not binding / has issues — how do PV, PVC and StorageClass relate and how do you check?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [A PVC is full — how do you understand and handle it?](../kubernetes/how-does-persistent-storage-work-in-kubernetes.md)
- [A pod shows high CPU usage — what do you look at?](../kubernetes/how-do-requests-limits-and-qos-classes-work-in-kubernetes.md)
- [A pod shows high memory usage — how do you handle it?](../kubernetes/how-do-requests-limits-and-qos-classes-work-in-kubernetes.md)
- [A Service is not reachable — how do you troubleshoot it?](../kubernetes/how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md)
- [Ingress is not working — how does Ingress route traffic and what breaks when it fails?](../kubernetes/how-do-you-debug-a-kubernetes-ingress-that-is-not-routing-traffic.md)
- [A TLS certificate has expired on your Ingress — how do you detect and renew it?](../network-security/how-do-you-manage-tls-certificates-in-production.md)
- [A Secret is not being mounted into a pod — how do you troubleshoot it?](../kubernetes/how-do-you-troubleshoot-a-pod-that-fails-because-a-secret-or-configmap-cannot-be-mounted-or-referenced.md)
- [ConfigMap changes are not reflected in the running pods — how do you fix it?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)

## Example

```text
Public DevOps mock interviews — 8 rounds, 194 questions

  ROUND 1  Senior AWS DevOps            61   HA architecture, EKS vs ECS, VPC
                                             routing, Terraform across hundreds
                                             of accounts, secrets in state
  ROUND 2  Cloud engineer               23   global e-commerce design, caching,
                                             EKS upgrade rollback, GitOps
  ROUND 3  Senior DevOps                23   e-commerce design, DR, security
                                             baseline, IRSA, cross-region RDS
  ROUND 4  Senior DevOps                35   S3 and cross-account access, CORS,
                                             Secrets vs ConfigMaps, Git tags,
                                             disk resize, 401 vs 403
  ROUND 5  DevOps generalist            16   zombie/orphan/daemon processes,
                                             three-tier Compose, load balancers
  ROUND 6  Role walkthrough              9   day-to-day work, shared clusters,
                                             CI/CD stages, challenges
  ROUND 7  CI/CD deep dive              10   PR checks, OIDC to AWS, image
                                             signing, GitOps promotion, rollback
  ROUND 8  Kubernetes troubleshooting   17   CrashLoopBackOff, Pending, OOMKilled,
                                             probes, PVC full, ConfigMap reload

WHAT THE SAMPLE TELLS YOU
  Terraform state and Pod troubleshooting each come up six times; ECS
  versus EKS five times. Most mistakes in the recordings were not gaps
  in knowledge but confident answers to a slightly different question.
```

## Interview tips

- Separate the Pod states before you troubleshoot them. `Pending` is a scheduling problem (requests, taints, affinity, unbound PVCs), `ImagePullBackOff` is a registry or credentials problem, and `CrashLoopBackOff` means the container starts and then exits. Describing CrashLoopBackOff as "stuck in Pending" is the most common slip in these recordings. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- A failing readiness probe never restarts a container. It removes the Pod from Service endpoints; only the liveness probe restarts. Getting this backwards is a reliable way to lose a probe question. See [liveness, readiness, and startup probes](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- Taints repel; they do not attract. To pin a workload to particular nodes you need `nodeSelector` or node affinity, and you add a taint only if you also want to keep everything else off those nodes. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- Blue/green switches all traffic at once; shifting a weighted percentage is canary. Several answers described weighted shifting and called it blue/green. See [blue-green deployment](../advanced-devops-cloud/what-is-blue-green-deployment.md) and [canary releases with weighted traffic shifting](../api-gateway-and-service-mesh/how-do-you-implement-canary-releases-with-weighted-traffic-shifting-in-an-api-gateway.md).
- Keep Terraform answers current: the S3 backend locks natively with `use_lockfile` (no DynamoDB table needed), `terraform taint` gave way to `apply -replace`, and CLI workspaces are separate state files, not something you "push". See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md) and [stopping Terraform from destroying or recreating a resource](../infrastructure-as-code/how-do-you-stop-terraform-from-destroying-or-recreating-a-resource.md).
- Changing an EBS volume from gp2 to gp3 adds no space. Increase the size, then grow the partition and the filesystem on the instance. See [managing disks, filesystems, and LVM](../linux-administration/how-do-you-manage-disks-filesystems-and-lvm-on-linux.md).
- S3 is regional: it spreads data across availability zones, not regions. Cross-region protection needs Cross-Region Replication or AWS Backup copies, and that choice belongs to the DR tier you picked for the service. See [RTO, RPO, and DR tiers](../backup-and-disaster-recovery/what-are-rto-and-rpo-and-how-do-they-drive-disaster-recovery-architecture-tiers.md).
- CORS is a browser rule about origins, not a way for buckets to talk to each other, and a plain `<img>` tag does not need it. Replication is the wrong answer to a CORS question. See [securing an S3 bucket](../aws-engineering/how-do-you-secure-and-manage-the-lifecycle-of-an-s3-bucket.md).
- A Gateway Load Balancer is not an API front door. It works at layer 3, uses GENEVE, and exists to insert firewall and inspection appliances into the traffic path. See [layer 4 versus layer 7 load balancers](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md).
- GitOps is pull-based: an agent in the cluster reconciles from Git, so CI never holds cluster credentials and drift is corrected automatically. Running `helm upgrade` from a pipeline is push-based deployment, even when the chart lives in Git. See [GitOps](../devops-tools-and-automation/what-is-gitops.md).
- For behavioural questions, be honest about scope. Present production work as production work and labs as labs; some interview advice says to present course projects as your employer's work, and an interviewer's follow-up questions will expose that quickly. See [describing your day-to-day responsibilities](../interview-experience/how-do-you-describe-your-day-to-day-responsibilities-as-a-devops-engineer.md) and [answering "tell me about a challenge you faced"](../interview-experience/how-do-you-answer-tell-me-about-a-challenge-you-faced-in-a-devops-interview.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
