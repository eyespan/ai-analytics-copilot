# ==============================
# EKS Cluster Name
# ==============================

output "cluster_name" {

  description = "EKS cluster name"

  value = aws_eks_cluster.this.name

}


# ==============================
# EKS Cluster ARN
# ==============================

output "cluster_arn" {

  description = "EKS cluster ARN"

  value = aws_eks_cluster.this.arn

}


# ==============================
# EKS API Endpoint
# ==============================

output "cluster_endpoint" {

  description = "EKS Kubernetes API endpoint"

  value = aws_eks_cluster.this.endpoint

}


# ==============================
# Cluster Certificate Authority
# ==============================

output "cluster_certificate_authority" {

  description = "EKS cluster certificate authority data"

  value = aws_eks_cluster.this.certificate_authority[0].data

}


# ==============================
# OIDC Issuer URL
# ==============================

output "oidc_issuer_url" {

  description = "EKS OIDC issuer URL"

  value = aws_eks_cluster.this.identity[0].oidc[0].issuer

}


# ==============================
# Cluster Security Group ID
# ==============================

output "cluster_security_group_id" {

  description = "EKS cluster security group ID"

  value = aws_security_group.cluster.id

}


output "oidc_provider_arn" {

  description = "IAM OIDC provider ARN for IRSA"

  value = aws_iam_openid_connect_provider.this.arn

}