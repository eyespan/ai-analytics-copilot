variable "aws_region" {

  type = string

}

variable "aws_profile" {

  type = string

}

variable "environment" {

  type = string

}

variable "project_name" {

  type = string

}


#vpc

/*variable "name" {
  type        = string
  description = "Name prefix for all resources"
}*/

variable "vpc_cidr" {
  type = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Invalid CIDR block."
  }
}


variable "public_subnets" {
  description = "Map of public subnets keyed by name"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "private_subnets" {
  description = "Map of private subnets keyed by name"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "enable_nat_gateway" {
  type    = bool
  default = true
}

variable "single_nat_gateway" {
  type    = bool
  default = true
}

variable "tags" {
  type    = map(string)
  default = {}
}

/*variable "cluster_name" {
  type = string
}*/


#ecs

variable "repositories" {
  description = "List of ECR repositories"
  type        = list(string)
}

variable "image_tag_mutability" {
  type    = string
  default = "IMMUTABLE"
}

variable "scan_on_push" {
  type    = bool
  default = true
}

/*variable "tags" {
  type    = map(string)
  default = {}
}*/

variable "max_image_count" {
  description = "Maximum number of images to retain per repository"
  type        = number
  default     = 20
}



#

variable "node_groups" {

  description = "EKS managed node groups configuration"


  type = map(object({

    desired_size = number

    min_size = number

    max_size = number


    instance_types = list(string)


    capacity_type = string


    ami_type = string


    disk_size = number


    labels = map(string)


  }))


}

variable "github_org" {

  description = "GitHub organisation"

  type = string

}


variable "github_repo" {

  description = "GitHub repository"

  type = string

}

variable "eks_oidc_provider_arn" {

  description = "EKS IAM OIDC Provider ARN"

  type = string

  default = null

}


variable "eks_oidc_issuer" {

  description = "EKS OIDC issuer URL without https://"

  type = string

  default = null

}


variable "irsa_roles" {

  description = "IRSA role definitions"


  type = map(object({

    namespace = string

    service_account = string

  }))

   default = {}

}


variable "create_irsa_roles" {

  description = "Create IRSA workload roles"

  type        = bool

  default     = false

}


variable "cluster_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.36"
}

variable "public_access_cidrs" {

  description = "CIDRs allowed to access the EKS API endpoint"

  type = list(string)

  default = [
    "0.0.0.0/0"
  ]

}

variable "endpoint_private_access" {
  description = "Enable private API endpoint"
  type        = bool
  default     = true
}

variable "endpoint_public_access" {
  description = "Enable public API endpoint"
  type        = bool
  default     = true
}

variable "enabled_log_types" {
  description = "Control plane logs"

  type = list(string)

  default = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]
}
