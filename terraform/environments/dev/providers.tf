provider "aws" {

  region = var.aws_region
   
  #remove when using guthub actions
  #profile = var.aws_profile

  default_tags {

    tags = {

      Project     = "ai-analytics-copilot"
      Environment = var.environment
      ManagedBy   = "Terraform"

    }

  }

}