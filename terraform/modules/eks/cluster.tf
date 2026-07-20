#Security Group
resource "aws_security_group" "cluster" {

  name = "${var.name}-eks-cluster"

  description = "Security group for the EKS control plane"

  vpc_id = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-eks-cluster"
    }
  )

}

#Security Group Rules
#Inbound - Allow all traffic within the cluster security group
resource "aws_vpc_security_group_ingress_rule" "cluster_self" {

  security_group_id = aws_security_group.cluster.id

  referenced_security_group_id = aws_security_group.cluster.id

  ip_protocol = "-1"

  description = "Cluster internal communication"

}

#Outbound
resource "aws_vpc_security_group_egress_rule" "all" {

  security_group_id = aws_security_group.cluster.id

  cidr_ipv4 = "0.0.0.0/0"

  ip_protocol = "-1"

  description = "Allow outbound traffic"

}


#CloudWatch Log Group
resource "aws_cloudwatch_log_group" "eks" {

  name = "/aws/eks/${var.name}/cluster"

  retention_in_days = var.cloudwatch_log_retention_in_days

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-eks-logs"
    }
  )

}


#EKS Cluster
resource "aws_eks_cluster" "this" {

  name = var.name

  version = var.cluster_version

  role_arn = var.cluster_role_arn

  enabled_cluster_log_types = var.enabled_log_types

  vpc_config {

    subnet_ids = var.private_subnet_ids

    security_group_ids = [
      aws_security_group.cluster.id
    ]

    endpoint_private_access = var.endpoint_private_access

    endpoint_public_access = var.endpoint_public_access

    public_access_cidrs = var.public_access_cidrs

  }

  access_config {

    authentication_mode = "API_AND_CONFIG_MAP"

    bootstrap_cluster_creator_admin_permissions = true

  }

  depends_on = [

    aws_cloudwatch_log_group.eks

  ]

  tags = merge(
    local.common_tags,
    {
      Name = var.name
    }
  )

  timeouts {

    create = "30m"

    update = "60m"

    delete = "30m"

  }

  lifecycle {

    ignore_changes = [

      tags["LastUpdated"]

    ]

  }

}


