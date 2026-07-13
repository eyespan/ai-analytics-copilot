# =====================================
# GitHub Actions OIDC Provider
# =====================================

/*resource "aws_iam_openid_connect_provider" "github" {

  url = "https://token.actions.githubusercontent.com"


  client_id_list = [

    "sts.amazonaws.com"

  ]


  thumbprint_list = [

    "6938fd4d98bab03faadb97b34396831e3780aea1"

  ]


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-github-actions-oidc"
    }
  )

}



#GitHub Actions Assume Role Policy
data "aws_iam_policy_document" "github_actions_assume" {


  statement {


    effect = "Allow"


    actions = [

      "sts:AssumeRoleWithWebIdentity"

    ]


    principals {

      type = "Federated"

      identifiers = [

        aws_iam_openid_connect_provider.github.arn

      ]

    }


    condition {


      test = "StringEquals"


      variable = "token.actions.githubusercontent.com:aud"


      values = [

        "sts.amazonaws.com"

      ]

    }


    condition {


      test = "StringLike"


      variable = "token.actions.githubusercontent.com:sub"


      values = [

        "repo:${var.github_org}/${var.github_repo}:*"

      ]

    }

  }

}

#GitHub Actions Deployment Role
resource "aws_iam_role" "github_actions" {

  name = "${var.name}-github-actions"

  assume_role_policy = data.aws_iam_policy_document.github_actions_assume.json


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-github-actions"
    }
  )

}


#Permissions for Terraform + EKS Deployment
resource "aws_iam_role_policy_attachment" "github_admin" {

  role = aws_iam_role.github_actions.name

  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"


}

*/