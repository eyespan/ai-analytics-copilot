
# =====================================
# Bedrock Runtime IRSA Role
# =====================================
#
# Used by:
#
# namespace:
# ai-platform
#
# service account:
# ai-copilot-bedrock
#
# Purpose:
# Allow AI workloads running in EKS
# to invoke Amazon Bedrock models
#
# =====================================



# -------------------------------------
# Trust Policy
# -------------------------------------

data "aws_iam_policy_document" "bedrock_assume" {


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

        "system:serviceaccount:ai-platform:ai-copilot-bedrock"

      ]

    }

  }

}




# -------------------------------------
# IAM Role
# -------------------------------------

resource "aws_iam_role" "bedrock" {

  name = "${var.name}-bedrock-runtime"

  assume_role_policy = data.aws_iam_policy_document.bedrock_assume.json

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-bedrock-runtime"
    }
  )

}


# -------------------------------------
# Bedrock Runtime Policy
# -------------------------------------

resource "aws_iam_policy" "bedrock" {


  name = "${var.name}-bedrock-runtime"


  description = "Permissions for AI workloads to invoke Bedrock models"


  policy = jsonencode({

    Version = "2012-10-17"


    Statement = [

      {

        Sid = "BedrockInvoke"


        Effect = "Allow"


        Action = [

          "bedrock:InvokeModel",

          "bedrock:InvokeModelWithResponseStream"

        ]


        Resource = "*"

      }

    ]

  })


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-bedrock-policy"
    }
  )

}


#Attach policy
resource "aws_iam_role_policy_attachment" "bedrock" {


  role = aws_iam_role.bedrock.name


  policy_arn = aws_iam_policy.bedrock.arn

}