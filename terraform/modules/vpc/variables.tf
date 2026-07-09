variable "name" {
  type        = string
  description = "Name prefix for all resources"
}

variable "vpc_cidr" {
  type = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Invalid CIDR block."
  }
}

/*variable "azs" {
  type        = list(string)
  description = "Availability zones"
}*/

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

variable "cluster_name" {
  type = string
}