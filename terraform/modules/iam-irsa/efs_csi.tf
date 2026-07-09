# =====================================
# EFS CSI Driver IRSA Role
# =====================================
#
# Used by:
# kube-system/efs-csi-controller-sa
#
# Purpose:
# Allow Kubernetes EFS CSI Driver
# to manage Amazon EFS resources
#
# =====================================


# -------------------------------------
# Trust Policy
# -------------------------------------

data "aws_iam_policy_document" "efs_csi_assume" {


  statement {


    effect = "Allow"


    actions = [

      "sts:AssumeRoleWithWebIdentity"

    ]


    principals {


      type = "Federated"


      identifiers = [

        var.eks_oidc_provider_arn

      ]

    }


    condition {


      test = "StringEquals"


      variable = "${var.eks_oidc_issuer}:aud"


      values = [

        "sts.amazonaws.com"

      ]

    }


    condition {


      test = "StringEquals"


      variable = "${var.eks_oidc_issuer}:sub"


      values = [

        "system:serviceaccount:kube-system:efs-csi-controller-sa"

      ]

    }

  }

}



# -------------------------------------
# IAM Role
# -------------------------------------

resource "aws_iam_role" "efs_csi" {

  name = "${var.name}-efs-csi-driver"


  assume_role_policy = data.aws_iam_policy_document.efs_csi_assume.json



  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-efs-csi-driver"
    }
  )

}



# -------------------------------------
# Attach AWS Managed Policy
# -------------------------------------

resource "aws_iam_role_policy_attachment" "efs_csi" {


  role = aws_iam_role.efs_csi.name


  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEFSCSIDriverPolicy"


}