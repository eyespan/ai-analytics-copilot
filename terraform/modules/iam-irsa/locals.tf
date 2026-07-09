locals {

  common_tags = merge(
    {
      ManagedBy = "Terraform"
      Module    = "IAM-IRSA"
    },
    var.tags
  )

}