variable "name" {
  description = "Project name"
  type        = string
}

variable "cluster_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.36"
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs"
  type        = list(string)
}

variable "cluster_role_arn" {
  description = "IAM Role ARN for the EKS control plane"
  type        = string
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

variable "tags" {
  type    = map(string)
  default = {}
}


variable "public_access_cidrs" {

  description = "CIDRs allowed to access the EKS API endpoint"

  type = list(string)

  default = [
    "0.0.0.0/0"
  ]

}

variable "cloudwatch_log_retention_in_days" {

  description = "CloudWatch log retention"

  type = number

  default = 30

}

/*variable "cluster_admin_role_arn" {

  description = "IAM role ARN used for EKS cluster administration"

  type = string

}*/

variable "node_role_arn" {

  description = "IAM role ARN for EKS worker nodes"

  type = string

}

#node group definition
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