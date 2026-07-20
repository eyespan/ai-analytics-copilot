locals {
  common_tags = merge(var.tags, {
    Project = var.name
  })
  #azs = var.azs
}