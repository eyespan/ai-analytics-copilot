variable "namespaces" {

  description = "Kubernetes namespaces to create"

  type = list(string)

}


variable "environment" {

  description = "Environment name"

  type = string

}