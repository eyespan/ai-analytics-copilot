locals {

  common_tags = {
    Project     = "ai-analytics-copilot"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  cluster_name = "${var.project_name}-${var.environment}-eks"


}
