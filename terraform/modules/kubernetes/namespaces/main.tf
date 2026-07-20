resource "kubernetes_namespace" "namespaces" {

  for_each = toset(var.namespaces)

  metadata {

    name = each.value

    labels = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = "ai-analytics-copilot"
    }

  }

}