provider "aws" {

  region = var.aws_region

  #profile = var.aws_profile

  default_tags {

    tags = {

      Project     = "ai-analytics-copilot"
      Environment = var.environment
      ManagedBy   = "Terraform"

    }

  }

}