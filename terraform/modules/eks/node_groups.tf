# =====================================
# EKS Managed Node Groups
# =====================================



resource "aws_launch_template" "eks_nodes" {

  name_prefix = "${var.name}-nodes-"

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  tags = local.common_tags
}



resource "aws_eks_node_group" "this" {

  for_each = var.node_groups


  launch_template {
    id      = aws_launch_template.eks_nodes.id
    version = aws_launch_template.eks_nodes.latest_version
  }


  # -----------------------------
  # Cluster
  # -----------------------------

  cluster_name = aws_eks_cluster.this.name


  # -----------------------------
  # Node Group Identity
  # -----------------------------

  node_group_name = each.key

  node_role_arn = var.node_role_arn


  # -----------------------------
  # Networking
  # -----------------------------

  subnet_ids = var.private_subnet_ids


  # -----------------------------
  # Scaling
  # -----------------------------

  scaling_config {

    desired_size = each.value.desired_size

    min_size = each.value.min_size

    max_size = each.value.max_size

  }


  # -----------------------------
  # Instance Configuration
  # -----------------------------

  instance_types = each.value.instance_types

  capacity_type = each.value.capacity_type


  ami_type = each.value.ami_type


  disk_size = each.value.disk_size



  # -----------------------------
  # Kubernetes Configuration
  # -----------------------------

  labels = each.value.labels



  # -----------------------------
  # Update Strategy
  # -----------------------------

  update_config {

    max_unavailable = 1

  }


  # -----------------------------
  # Tags
  # -----------------------------

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-${each.key}"
    }
  )


  depends_on = [

    aws_eks_cluster.this

  ]

}