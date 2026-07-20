locals {

  common_tags = merge(
    {
      ManagedBy = "Terraform"
      Module    = "IAM"
    },
    var.tags
  )

}