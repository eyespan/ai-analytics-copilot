#################################################
# AI Analytics Copilot
# Level 7 - Development Environment
#################################################

#################################################
# VPC
#################################################

module "vpc" {

  source = "../../modules/vpc"

  name = var.project_name

  cluster_name = local.cluster_name

  vpc_cidr = var.vpc_cidr

  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets


  single_nat_gateway = var.single_nat_gateway

  tags = local.common_tags

}

#################################################
# ECR
#################################################

module "ecr" {

  source = "../../modules/ecr"

  repositories         = var.repositories
  image_tag_mutability = var.image_tag_mutability
  scan_on_push         = var.scan_on_push


  tags = local.common_tags

}

#################################################
# IAM
#################################################

module "iam" {

  source = "../../modules/iam"

  name = var.project_name
  tags = local.common_tags

}

#################################################
# EKS
#################################################

module "eks" {

  source = "../../modules/eks"

  name = var.project_name

  cluster_version = var.cluster_version

  cluster_role_arn = module.iam.eks_cluster_role_arn
  node_role_arn    = module.iam.eks_node_role_arn
  node_groups      = var.node_groups

  ebs_csi_role_arn = module.iam_irsa.ebs_csi_role_arn

  vpc_id = module.vpc.vpc_id

  private_subnet_ids = module.vpc.private_subnet_ids

  endpoint_private_access = var.endpoint_private_access
  endpoint_public_access  = var.endpoint_public_access

  public_access_cidrs = var.public_access_cidrs

  enabled_log_types = var.enabled_log_types

  tags = local.common_tags

  depends_on = [
    module.vpc,
    module.iam
  ]

}


module "iam_irsa" {

  source = "../../modules/iam-irsa"


  name = var.project_name


  eks_oidc_issuer = module.eks.oidc_issuer_url


  eks_oidc_provider_arn = module.eks.oidc_provider_arn


  #github_org = var.github_org

  #github_repo = var.github_repo


  irsa_roles = var.irsa_roles


  tags = local.common_tags

}

module "kubernetes_namespaces" {

  source = "../../modules/kubernetes/namespaces"


  environment = "dev"


  namespaces = [

    "ai-analytics",

    "monitoring",

    "ingress-nginx",
    
    "data"

  ]

  depends_on = [

    module.eks

  ]

}