# IAM / IRSA Module

## Purpose

`terraform/modules/iam-irsa` creates IAM roles that Kubernetes workloads can assume through the EKS OIDC provider.

The design is:

```text
Kubernetes ServiceAccount
        │
        ▼
EKS OIDC Provider
        │
        ▼
IAM Role
        │
        ▼
AWS API
```

This avoids placing long-lived AWS access keys inside application containers.

## Current IRSA roles

The module contains dedicated IAM configuration for:

- AWS Load Balancer Controller
- ExternalDNS
- EBS CSI Driver
- CloudWatch Agent
- Bedrock workloads
- generic IRSA roles defined through `irsa_roles`

## AWS Load Balancer Controller

The role is trusted by:

```text
system:serviceaccount:kube-system:aws-load-balancer-controller
```

Its policy is stored in:

```text
terraform/modules/iam-irsa/policies/aws_lb_controller.json
```

The Helm deployment injects this role ARN into the controller ServiceAccount.

## ExternalDNS

ExternalDNS is trusted through IRSA and receives permissions for Route 53 record management, including:

```text
route53:ChangeResourceRecordSets
route53:ListHostedZones
route53:ListResourceRecordSets
route53:ListTagsForResource
```

The intended ServiceAccount is:

```text
system:serviceaccount:kube-system:external-dns
```

## EBS CSI

The EBS CSI role is attached to the AWS-managed:

```text
AmazonEBSCSIDriverPolicy
```

and is supplied to the EKS managed `aws-ebs-csi-driver` add-on.

## CloudWatch Agent

The CloudWatch role is trusted by:

```text
system:serviceaccount:amazon-cloudwatch:cloudwatch-agent
```

It attaches:

```text
CloudWatchAgentServerPolicy
AWSXrayWriteOnlyAccess
```

## Bedrock

The repository contains a dedicated Bedrock IAM role definition for AI workloads.

This is intentionally separate from the EKS node role.

The application currently has Bedrock support in the orchestrator, but actual AWS account permissions still determine whether Bedrock invocation is possible.

For example, in the development AWS account used during Level 7 testing, the Bedrock API call was rejected by an AWS Organizations service-control policy. The presence of the IAM role therefore does not imply that Bedrock is usable in every AWS account.

## Generic IRSA

The `irsa_roles` variable provides reusable ServiceAccount-to-IAM-role mappings.

This allows additional workload roles to be added without changing the base EKS module.

## GitHub Actions OIDC

A commented GitHub Actions OIDC implementation exists in:

```text
github_oidc.tf
```

The active repository bootstrap process currently creates the GitHub OIDC provider and GitHub Actions IAM role through:

```text
.github/workflows/bootstrap.yml
```

The separation should be preserved: GitHub Actions identity and Kubernetes workload identity are different trust relationships.
