/*variable "name" {
  description = "Project name"
  type        = string
}*/

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

variable "tags" {
  type    = map(string)
  default = {}
}

variable "max_image_count" {
  description = "Maximum number of images to retain per repository"
  type        = number
  default     = 20
}