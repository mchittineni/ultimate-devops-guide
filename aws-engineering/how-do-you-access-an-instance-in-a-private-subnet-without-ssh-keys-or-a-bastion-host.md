---
title: "How do you access an instance in a private subnet without SSH keys or a bastion host?"
id: 476
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - linux-administration
  - devsecops
---

# How do you access an instance in a private subnet without SSH keys or a bastion host?

**Short answer:** **SSM Session Manager.** The instance runs the SSM Agent and makes an **outbound** connection to the Systems Manager service; you call `aws ssm start-session` and AWS brokers the two. There is no inbound port, no security group rule, no public IP, no bastion, and **no SSH key** - authentication and authorisation are IAM, and every session is logged to CloudTrail and can be recorded in full to S3 or CloudWatch Logs. For a private subnet with no NAT gateway you add three interface VPC endpoints (`ssm`, `ssmmessages`, `ec2messages`) so the agent can reach the service privately. If you specifically want SSH semantics, **EC2 Instance Connect Endpoint** tunnels SSH/RDP to a private instance without a bastion, and Session Manager can also carry SSH and port forwarding. The framing that lands: replacing keys and bastions with IAM-authenticated, audited, outbound-only sessions removes a standing inbound attack surface and a key-distribution problem at the same time.

## Detail

### Why this beats a bastion

|                            | Bastion host + SSH keys                          | SSM Session Manager                                                                  |
| -------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------ |
| Inbound ports open         | 22 to the bastion, from somewhere                | **None**                                                                             |
| Public IP needed           | Yes, on the bastion                              | No                                                                                   |
| Credentials                | SSH private keys, distributed and rotated by you | IAM - short-lived, federated, no keys                                                |
| Audit                      | sshd logs on a host you must ship and protect    | CloudTrail for every session start, optional full session recording to S3/CloudWatch |
| Access control granularity | Unix users and key files                         | IAM policy, tag-based, with conditions                                               |
| Patching burden            | An extra internet-facing host to maintain        | None - the agent is on the instance                                                  |
| Offboarding someone        | Find and remove their key everywhere             | Remove the IAM permission                                                            |

The key-distribution problem is the real driver. Once ten engineers have keys on twenty hosts, nobody can answer "who can log into production?" - whereas `aws iam simulate-principal-policy` and CloudTrail answer it precisely with Session Manager.

### The four requirements

1. **SSM Agent** installed and running. Pre-installed on Amazon Linux 2/2023, recent Ubuntu LTS AMIs, and Windows Server AMIs; installable elsewhere.
2. **An instance profile** with `AmazonSSMManagedInstanceCore` (or an equivalent least-privilege policy).
3. **Network path to the SSM endpoints** - either a NAT gateway, or **interface VPC endpoints** for `ssm`, `ssmmessages`, and `ec2messages`. All three: `ssm` for the API, `ssmmessages` for the Session Manager data channel, `ec2messages` for the agent's message polling. Missing `ssmmessages` is the classic cause of "the instance shows as managed but sessions fail".
4. **IAM permission on the caller** (`ssm:StartSession` on the target, plus `ssm:TerminateSession` on your own sessions).

If an instance does not appear in Fleet Manager, work that list in order: agent running (`systemctl status amazon-ssm-agent`), instance profile attached, endpoint or NAT reachable, and the endpoint's security group allowing 443 from the instance.

### Hardening the access itself

- **Tag-based authorisation**: allow `ssm:StartSession` only where `ssm:resourceTag/Environment` matches what the role should reach, so a developer role cannot open a session on production.
- **Session recording**: send full session output to S3 (with KMS encryption) or CloudWatch Logs, and enable `kmsKeyId` for end-to-end encryption of the session. This is what makes it acceptable to compliance in place of a bastion with `auditd`.
- **Restrict what can run**: `Run Command` documents and the `ssm:SessionDocumentAccessCheck` condition, or a restricted shell profile, so sessions are not unconstrained root.
- **Idle timeout and preferences** set centrally in the `SSM-SessionManagerRunShell` document.
- **No long-lived credentials on the caller side either** - engineers assume a role via IAM Identity Center with MFA; CI uses OIDC.

### When you want actual SSH

Two mechanisms, and the distinction is worth knowing:

- **Session Manager as an SSH transport**: a `ProxyCommand` in `~/.ssh/config` runs `aws ssm start-session --document-name AWS-StartSSHSession`, so `ssh ec2-user@i-0abc123` works with all your normal SSH tooling (`scp`, `rsync`, agent forwarding, VS Code Remote). Still no inbound port, but you do need an SSH key on the instance - so it keeps the key problem.
- **EC2 Instance Connect Endpoint (EICE)**: a VPC-resident endpoint that tunnels SSH or RDP to private instances. Combined with EC2 Instance Connect, AWS pushes a **short-lived, 60-second** public key to the instance for you, so there is still no stored key. `aws ec2-instance-connect ssh --instance-id i-0abc --connection-type eice`. This is the closest thing to "SSH without keys and without a bastion".

**Port forwarding** is often what people actually need: `aws ssm start-session --document-name AWS-StartPortForwardingSessionToRemoteHost` gives you a local port tunnelled to a database in a private subnet, so you can point a local SQL client at a private RDS instance without exposing it, without a bastion, and with the session in CloudTrail. That is the clean answer to "reach a database in a private subnet without a NAT gateway, a NAT instance, or a bastion host".

### The other ways in, and when each applies

- **Patching or running a command on many hosts**: do not open a session at all - `ssm send-command` (or Run Command with a document, State Manager for continuous configuration, and Patch Manager for OS patching). This is also the answer to "the private-subnet instances cannot reach the internet - how do you patch them?": SSM Patch Manager over VPC endpoints, with the packages coming from a patch source you control (an internal repository or an S3-hosted mirror reached via the S3 gateway endpoint).
- **Kubernetes**: `kubectl debug node/...` or an ephemeral debug container, not SSH. For a private EKS API endpoint, reach it from inside the VPC or via a Session Manager port-forward.
- **Serial console** for a host that is wedged before the network comes up - it is the last resort when SSM cannot help because the OS never got that far.
- **GCP and Azure equivalents**, in case the interviewer moves platform: **IAP TCP forwarding** on GCP and **Azure Bastion** (or Azure Arc + Run Command) - same idea, brokered access with identity-based authorisation instead of an exposed port.

### What "no SSH access" looks like as a design

The mature end state: instances have **no** `key_name`, security groups have **no** inbound rules at all, there is no bastion in the account, and interactive access is an exception that is recorded. Routine work happens through automation - immutable images, deployments through the pipeline, and Run Command for the rare fleet-wide action. If someone needs a shell in production regularly, that is a signal about missing observability or missing automation, not a request for better SSH.

## Example

```hcl
# Instance with no key, no inbound rules, and no public IP - reachable via SSM only
resource "aws_iam_role" "app" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_instance_profile" "app" { role = aws_iam_role.app.name }

resource "aws_security_group" "app" {
  name   = "app"
  vpc_id = aws_vpc.this.id
  # NO ingress rules at all - the agent connects outbound
  egress { from_port = 443, to_port = 443, protocol = "tcp", cidr_blocks = [aws_vpc.this.cidr_block] }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = "t3.small"
  subnet_id              = aws_subnet.private["private-eu-west-1a"].id
  iam_instance_profile   = aws_iam_instance_profile.app.name
  vpc_security_group_ids = [aws_security_group.app.id]
  # key_name deliberately omitted: there is no SSH key to steal or rotate
}

# The three endpoints that make it work without a NAT gateway
resource "aws_vpc_endpoint" "ssm" {
  for_each            = toset(["ssm", "ssmmessages", "ec2messages"]) # all three required
  vpc_id              = aws_vpc.this.id
  service_name        = "com.amazonaws.${var.region}.${each.key}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [for s in aws_subnet.private : s.id]
  security_group_ids  = [aws_security_group.endpoints.id]
  private_dns_enabled = true
}
```

```json
// Tag-scoped session access: this role cannot open a session on production
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ssm:StartSession",
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringEquals": { "ssm:resourceTag/Environment": ["dev", "staging"] }
      }
    },
    {
      "Effect": "Allow",
      "Action": ["ssm:TerminateSession", "ssm:ResumeSession"],
      "Resource": "arn:aws:ssm:*:*:session/${aws:username}-*"
    }
  ]
}
```

```bash
# Interactive shell - no key, no inbound port, fully audited
aws ssm start-session --target i-0abc123def456

# SSH semantics through SSM (add to ~/.ssh/config, then `ssh ec2-user@i-0abc123`)
cat >> ~/.ssh/config <<'EOF'
Host i-* mi-*
  ProxyCommand sh -c "aws ssm start-session --target %h \
    --document-name AWS-StartSSHSession --parameters portNumber=%p"
EOF
scp -r ./build ec2-user@i-0abc123:/tmp/    # scp/rsync work as normal

# Reach a PRIVATE RDS instance from your laptop - no bastion, no NAT, no public endpoint
aws ssm start-session --target i-0abc123def456 \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["orders.abc123.eu-west-1.rds.amazonaws.com"],
                 "portNumber":["5432"],"localPortNumber":["15432"]}'
psql -h 127.0.0.1 -p 15432 -U app orders

# EC2 Instance Connect Endpoint: short-lived key pushed for you
aws ec2-instance-connect ssh --instance-id i-0abc123 --connection-type eice

# Fleet work without any session at all
aws ssm send-command --document-name AWS-RunPatchBaseline \
  --targets "Key=tag:Environment,Values=prod" \
  --parameters "Operation=Install" --max-concurrency 10% --max-errors 5%
```

```bash
# "The instance is not showing up in Session Manager" - work the list in order
aws ssm describe-instance-information \
  --query 'InstanceInformationList[].[InstanceId,PingStatus,AgentVersion]' --output table
sudo systemctl status amazon-ssm-agent          # 1. agent running?
aws ec2 describe-instances --instance-ids i-0abc \
  --query 'Reservations[0].Instances[0].IamInstanceProfile'   # 2. profile attached?
nslookup ssmmessages.eu-west-1.amazonaws.com    # 3. private IP => endpoint reachable
```

## Interview tips

- Name SSM Session Manager immediately and give the mechanism in one line: the agent connects **outbound**, AWS brokers the session, so there is no inbound port, no public IP, no bastion, and no SSH key.
- Then list the three benefits in the order interviewers care about: IAM-based access control (offboarding is removing a permission), CloudTrail plus optional full session recording, and no key distribution.
- Know the four prerequisites, and specifically the **three** interface endpoints - `ssm`, `ssmmessages`, `ec2messages`. Being able to say `ssmmessages` is the data channel is the detail that proves you have configured it.
- For "reach a database in a private subnet with no NAT, no NAT instance, and no bastion", answer with an SSM **port-forwarding** session to the RDS endpoint. That is exactly what the question is fishing for, and most candidates go straight to "a bastion" and miss it.
- Mention EC2 Instance Connect Endpoint as the SSH-shaped answer with a 60-second ephemeral key, and Session Manager's `ProxyCommand` when the team needs `scp`/`rsync`/VS Code Remote.
- Volunteer tag-based IAM conditions so a role can only open sessions on non-production, plus session recording to S3 with KMS. That turns a convenience answer into a security answer.
- For patching private instances with no internet, answer SSM Patch Manager over VPC endpoints with an internal repository or S3-hosted mirror - not "open the NAT".
- Finish with the design position: no `key_name`, no inbound rules, interactive access as an audited exception, and frequent shell access treated as a signal of missing automation or observability. See [how does a private subnet reach the internet](./how-does-a-private-subnet-reach-the-internet.md), [what are VPC endpoints](./what-are-vpc-endpoints-and-when-do-you-use-a-gateway-versus-an-interface-endpoint.md), [troubleshooting SSH failures on Linux](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md), and [designing least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?]] (`#405`): [How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md)
- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[How do you troubleshoot a Kubernetes node that is NotReady?]] (`#449`): [How do you troubleshoot a Kubernetes node that is NotReady?](../kubernetes/how-do-you-troubleshoot-a-kubernetes-node-that-is-notready.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
