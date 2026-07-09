locals {

  common_tags = merge(
    {
      ManagedBy = "Terraform"
      Module    = "EKS"
    },
    var.tags
  )

}