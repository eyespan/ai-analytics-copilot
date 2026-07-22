output "vpc_id" {
  value = module.vpc.vpc_id
}

output "public_subnet_ids" {
  value = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_arn" {
  value = module.eks.cluster_arn
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  value = module.eks.cluster_security_group_id
}

output "cluster_oidc_issuer" {
  value = module.eks.oidc_issuer_url
}

output "ecr_repository_urls" {
  value = module.ecr.repository_urls
}

#output "github_actions_role_arn" {

#  description = "IAM role ARN assumed by GitHub Actions"

#  value = module.iam_irsa.github_actions_role_arn

#}

output "aws_lb_controller_role_arn" {

  value = module.iam_irsa.aws_lb_controller_role_arn

}