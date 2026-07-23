# =====================================
# IRSA Base Trust Policy
# =====================================
#
# Creates reusable IAM trust policies
# for Kubernetes Service Accounts
#
# =====================================



data "aws_iam_policy_document" "irsa" {


  for_each = var.irsa_roles


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

        "system:serviceaccount:${each.value.namespace}:${each.value.service_account}"

      ]

    }

  }

}

#role creation

resource "aws_iam_role" "irsa" {


  for_each = var.irsa_roles


  name = "${var.name}-${each.key}"


  assume_role_policy = data.aws_iam_policy_document.irsa[each.key].json


  tags = merge(

    local.common_tags,

    {

      Name = "${var.name}-${each.key}"

    }

  )

}