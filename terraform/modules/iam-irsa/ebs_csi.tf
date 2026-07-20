# =====================================
# EFS CSI Driver IRSA Role
# =====================================
#
# Used by:
# kube-system/ebs-csi-controller-sa
#
# Purpose:
# Allow Kubernetes EFS CSI Driver
# to manage Amazon EFS resources
#
# =====================================


# -------------------------------------
# Trust Policy
# -------------------------------------

data "aws_iam_policy_document" "ebs_csi_assume" {


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


      #variable = "${var.eks_oidc_issuer}:aud"
      variable = "${replace(var.eks_oidc_issuer, "https://", "")}:aud"


      values = [

        "sts.amazonaws.com"

      ]

    }


    condition {


      test = "StringEquals"


      #variable = "${var.eks_oidc_issuer}:sub"
      variable = "${replace(var.eks_oidc_issuer, "https://", "")}:sub"


      values = [

        "system:serviceaccount:kube-system:ebs-csi-controller-sa"

      ]

    }

  }

}



# -------------------------------------
# IAM Role
# -------------------------------------

resource "aws_iam_role" "ebs_csi" {

  name = "${var.name}-ebs-csi-driver"


  assume_role_policy = data.aws_iam_policy_document.ebs_csi_assume.json



  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-ebs-csi-driver"
    }
  )

}



# -------------------------------------
# Attach AWS Managed Policy
# -------------------------------------

resource "aws_iam_role_policy_attachment" "ebs_csi" {


  role = aws_iam_role.ebs_csi.name


  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"


}