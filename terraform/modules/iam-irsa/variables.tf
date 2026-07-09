variable "name" {
  description = "Project name"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
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

}


variable "eks_oidc_issuer" {

  description = "EKS OIDC issuer URL without https://"

  type = string

}


variable "irsa_roles" {

  description = "IRSA role definitions"


  type = map(object({

    namespace = string

    service_account = string

  }))

}


variable "create_irsa_roles" {

  description = "Create IRSA workload roles"

  type = bool

  default = false

}

