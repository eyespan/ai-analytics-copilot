variable "name" {
  description = "Project name"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}

/*variable "eks_oidc_provider_arn" {

  description = "EKS IAM OIDC Provider ARN"

  type = string

}


variable "eks_oidc_issuer" {

  description = "EKS OIDC issuer URL without https://"

  type = string

}*/





