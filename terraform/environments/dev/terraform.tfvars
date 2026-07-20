aws_region = "us-east-1"

aws_profile = "default"

environment = "dev"

project_name = "ai-analytics-copilot"



#################################################
# VPC
#################################################

vpc_cidr = "10.20.0.0/16"

public_subnets = {

  public-a = {
    cidr = "10.20.1.0/24"
    az   = "us-east-1a"
  }

  public-b = {
    cidr = "10.20.2.0/24"
    az   = "us-east-1b"
  }

}


private_subnets = {

  private-a = {
    cidr = "10.20.11.0/24"
    az   = "us-east-1a"
  }

  private-b = {
    cidr = "10.20.12.0/24"
    az   = "us-east-1b"
  }

}


#################################################
# ECR
#################################################

repositories = [
  
  "ml-base",
  "api-gateway",
  "embedding-service",
  "indexer-service",
  "rag-service",
  "orchestrator-service",
  "frontend"

]


node_groups = {

  general = {

    desired_size = 2

    min_size = 2

    max_size = 4


    instance_types = [
      "t3.medium"
    ]


    capacity_type = "ON_DEMAND"


    ami_type = "AL2023_x86_64_STANDARD"


    disk_size = 50


    labels = {

      role = "general"

    }

  }

}


#github_org = "eyespan"

#github_repo = "ai-analytics-copilot"


irsa_roles = {


  aws_lb_controller = {

    namespace = "kube-system"

    service_account = "aws-load-balancer-controller"

  }


  external_dns = {

    namespace = "kube-system"

    service_account = "external-dns"

  }


  efs_csi = {

    namespace = "kube-system"

    service_account = "efs-csi-controller-sa"

  }


  cloudwatch = {

    namespace = "amazon-cloudwatch"

    service_account = "cloudwatch-agent"

  }


}