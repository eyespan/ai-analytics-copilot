# =====================================
# EKS OIDC Provider
# =====================================
#
# Enables IAM Roles for Service Accounts
# (IRSA)
#
# Kubernetes Service Accounts
#       |
#       |
#       ▼
# IAM Role
#       |
#       |
#       ▼
# AWS API Access
#
# =====================================


# Get OIDC certificate thumbprint

data "tls_certificate" "eks" {

  url = aws_eks_cluster.this.identity[0].oidc[0].issuer

}



# IAM OIDC Provider

resource "aws_iam_openid_connect_provider" "this" {

  url = aws_eks_cluster.this.identity[0].oidc[0].issuer


  client_id_list = [
    "sts.amazonaws.com"
  ]


  thumbprint_list = [
    data.tls_certificate.eks.certificates[0].sha1_fingerprint
  ]


  depends_on = [
    aws_eks_cluster.this
  ]


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-eks-oidc"
    }
  )

}