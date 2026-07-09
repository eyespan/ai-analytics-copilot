# =====================================
# ExternalDNS IAM Policy
# =====================================

resource "aws_iam_policy" "external_dns" {


  name = "${var.name}-external-dns"


  description = "Permissions for ExternalDNS Route53 management"


  policy = jsonencode({

    Version = "2012-10-17"


    Statement = [

      {

        Effect = "Allow"


        Action = [

          "route53:ChangeResourceRecordSets"

        ]


        Resource = [

          "arn:aws:route53:::hostedzone/*"

        ]

      },


      {

        Effect = "Allow"


        Action = [

          "route53:ListHostedZones",

          "route53:ListResourceRecordSets",

          "route53:ListTagsForResource"

        ]


        Resource = "*"

      }

    ]

  })


  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-external-dns-policy"
    }
  )

}


# =====================================
# ExternalDNS IRSA Trust
# =====================================


data "aws_iam_policy_document" "external_dns_assume" {


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

        "system:serviceaccount:kube-system:external-dns"

      ]

    }

  }

}


#ExternalDNS IAM Role

resource "aws_iam_role" "external_dns" {

  name = "${var.name}-external-dns"

  assume_role_policy = data.aws_iam_policy_document.external_dns_assume.json

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name}-external-dns"
    }
  )

}

#Attach Policy
resource "aws_iam_role_policy_attachment" "external_dns" {


  role = aws_iam_role.external_dns.name


  policy_arn = aws_iam_policy.external_dns.arn

}