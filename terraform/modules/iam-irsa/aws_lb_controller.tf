# =====================================
# AWS Load Balancer Controller
# IAM Policy
# =====================================


resource "aws_iam_policy" "aws_lb_controller" {


  name = "${var.name}-aws-load-balancer-controller"


  description = "Permissions for AWS Load Balancer Controller"


  policy = file("${path.module}/policies/aws_lb_controller.json")


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-aws-lb-controller-policy"
    }
  )

}


# =====================================
# AWS Load Balancer Controller
# IRSA Trust
# =====================================


data "aws_iam_policy_document" "aws_lb_controller_assume" {


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

        "system:serviceaccount:kube-system:aws-load-balancer-controller"

      ]

    }

  }

}


#IAM Role
resource "aws_iam_role" "aws_lb_controller" {

  name = "${var.name}-aws-lb-controller"

  assume_role_policy = data.aws_iam_policy_document.aws_lb_controller_assume.json

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-aws-lb-controller"
    }
  )

}

#Attach Policy

resource "aws_iam_role_policy_attachment" "aws_lb_controller" {


  role = aws_iam_role.aws_lb_controller.name


  policy_arn = aws_iam_policy.aws_lb_controller.arn

}