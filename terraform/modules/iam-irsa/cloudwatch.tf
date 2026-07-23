# =====================================
# CloudWatch Observability IRSA Role
# =====================================
#
# Used by:
#
# namespace:
# amazon-cloudwatch
#
# service account:
# cloudwatch-agent
#
# Purpose:
# Send:
# - Container logs
# - Kubernetes metrics
# - Application telemetry
#
# =====================================



# -------------------------------------
# Trust Policy
# -------------------------------------

data "aws_iam_policy_document" "cloudwatch_assume" {


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

        "system:serviceaccount:amazon-cloudwatch:cloudwatch-agent"

      ]

    }

  }

}



# -------------------------------------
# IAM Role
# -------------------------------------

resource "aws_iam_role" "cloudwatch" {

  name = "${var.name}-cloudwatch-agent"

  assume_role_policy = data.aws_iam_policy_document.cloudwatch_assume.json

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-cloudwatch-agent"
    }
  )

}



# -------------------------------------
# CloudWatch Agent Permissions
# -------------------------------------

resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {


  role = aws_iam_role.cloudwatch.name


  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"

}



# -------------------------------------
# X-Ray Trace Permissions
# -------------------------------------
#
# Required for distributed tracing
# integration
#
# -------------------------------------

resource "aws_iam_role_policy_attachment" "xray" {


  role = aws_iam_role.cloudwatch.name


  policy_arn = "arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"

}