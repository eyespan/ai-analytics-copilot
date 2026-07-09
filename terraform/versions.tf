terraform {

  required_version = ">= 1.8"

  required_providers {

    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.35"
    }

    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.16"
    }

  }

}