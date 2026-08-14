# EKS Terraform Module

## Purpose

`terraform/modules/eks` defines the Amazon EKS platform used by the AI Analytics Copilot.

It owns the Kubernetes control plane, managed node groups, EKS managed add-ons, OIDC provider and default EBS-backed storage class.

## Cluster

The module creates an `aws_eks_cluster`.

Current configuration supports:

- configurable Kubernetes version
- private API endpoint access
- public API endpoint access
- configurable public API CIDRs
- control-plane logging
- EKS API/config-map authentication mode
- cluster security group
- CloudWatch log group

The current environment defaults to Kubernetes `1.36`.

## Control-plane logging

The cluster enables:

```text
api
audit
authenticator
controllerManager
scheduler
```

Logs are written to:

```text
/aws/eks/<cluster-name>/cluster
```

with configurable retention.

## Networking

The cluster is attached to the VPC supplied by:

```text
terraform/modules/vpc
```

and uses the private subnet IDs supplied by the environment.

The cluster security group permits internal communication between members of the cluster security group and unrestricted outbound traffic.

## Managed node groups

Node groups are created from a configurable map.

Each node group supports:

- desired size
- minimum size
- maximum size
- instance types
- capacity type
- AMI type
- labels

The module uses an EC2 launch template with:

- IMDSv2 required
- 50 GiB encrypted `gp3` root volume
- automatic volume deletion
- update strategy with `max_unavailable = 1`

Nodes are deployed into private subnets.

## EKS managed add-ons

The module currently creates four AWS-managed add-ons:

```text
vpc-cni
coredns
kube-proxy
aws-ebs-csi-driver
```

The EBS CSI driver receives the IRSA role supplied by the environment.

## OIDC / IRSA

The module creates an IAM OIDC provider from the EKS cluster's OIDC issuer.

This is the trust foundation for Kubernetes workloads that need AWS API access without storing long-lived AWS credentials in pods.

## Storage

The module creates a Kubernetes `gp3` StorageClass:

```text
gp3
```

It is the default StorageClass and uses:

```text
ebs.csi.aws.com
```

with:

- encrypted `gp3`
- `WaitForFirstConsumer`
- volume expansion enabled

## What this module does not install

The following are **not** implemented as EKS managed add-ons here:

- AWS Load Balancer Controller
- ExternalDNS
- cert-manager
- Prometheus
- Grafana
- Metrics Server
- NGINX Ingress Controller

Those platform components are deployed by the GitHub Actions bootstrap workflow using Helm.

This distinction is important: an EKS managed add-on and a Helm-installed Kubernetes platform component are separate mechanisms in this repository.
