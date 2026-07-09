locals {

  common_tags = merge(
    {
      ManagedBy = "Terraform"
      Module    = "ECR"
    },
    var.tags
  )

}