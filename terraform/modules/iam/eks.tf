#EKS Cluster Trust Policy
data "aws_iam_policy_document" "eks_cluster_assume_role" {

  statement {

    actions = [
      "sts:AssumeRole"
    ]

    principals {

      type = "Service"

      identifiers = [
        "eks.amazonaws.com"
      ]

    }

  }

}

#Cluster Role
resource "aws_iam_role" "eks_cluster" {

  name = "${var.name}-eks-cluster"

  assume_role_policy = data.aws_iam_policy_document.eks_cluster_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-eks-cluster"
    }
  )

}

#Attach Required AWS Policies

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {

  role = aws_iam_role.eks_cluster.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"

}


#Node Group Trust Policy
data "aws_iam_policy_document" "eks_node_assume_role" {

  statement {

    actions = [
      "sts:AssumeRole"
    ]

    principals {

      type = "Service"

      identifiers = [
        "ec2.amazonaws.com"
      ]

    }

  }

}

#Node Role
resource "aws_iam_role" "eks_node_group" {

  name = "${var.name}-eks-node-group"

  assume_role_policy = data.aws_iam_policy_document.eks_node_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-eks-node-group"
    }
  )

}

#Required Managed Policies
resource "aws_iam_role_policy_attachment" "worker_node" {

  role = aws_iam_role.eks_node_group.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"

}

resource "aws_iam_role_policy_attachment" "cni" {

  role = aws_iam_role.eks_node_group.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"

}

resource "aws_iam_role_policy_attachment" "ecr" {

  role = aws_iam_role.eks_node_group.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"

}


