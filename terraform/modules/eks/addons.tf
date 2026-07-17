# =====================================
# EKS Managed Add-ons
# =====================================


# -------------------------------------
# VPC CNI
# -------------------------------------
# Provides AWS VPC networking for pods

resource "aws_eks_addon" "vpc_cni" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "vpc-cni"


  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-vpc-cni"
    }
  )

}



# -------------------------------------
# CoreDNS
# -------------------------------------
# Kubernetes internal DNS service

resource "aws_eks_addon" "coredns" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "coredns"


  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [

    aws_eks_node_group.this

  ]


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-coredns"
    }
  )

}



# -------------------------------------
# kube-proxy
# -------------------------------------
# Kubernetes network rules

resource "aws_eks_addon" "kube_proxy" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "kube-proxy"


  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-kube-proxy"
    }
  )

}



# -------------------------------------
# EBS CSI Driver
# -------------------------------------
# Persistent volume support

resource "aws_eks_addon" "ebs_csi" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "aws-ebs-csi-driver"


  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-ebs-csi"
    }
  )

  depends_on = [
    aws_eks_node_group.this
  ]

}