#output "github_actions_role_arn" {


#  description = "IAM role assumed by GitHub Actions"


#  value = aws_iam_role.github_actions.arn


#}

output "irsa_role_arns" {

  description = "IRSA role ARNs"

  value = {

    for k, v in aws_iam_role.irsa :

    k => v.arn

  }

}


output "aws_lb_controller_role_arn" {

  description = "IAM role ARN for AWS Load Balancer Controller"

  value = aws_iam_role.aws_lb_controller.arn

}

output "external_dns_role_arn" {

  description = "IAM role ARN for ExternalDNS"

  value = aws_iam_role.external_dns.arn

}


output "ebs_csi_role_arn" {

  description = "IAM role ARN for EBS CSI Driver"

  value = aws_iam_role.ebs_csi.arn

}

output "cloudwatch_role_arn" {

  description = "IAM role ARN for CloudWatch Agent"

  value = aws_iam_role.cloudwatch.arn

}


output "bedrock_role_arn" {

  description = "IAM role ARN for Bedrock AI workloads"

  value = aws_iam_role.bedrock.arn

}



