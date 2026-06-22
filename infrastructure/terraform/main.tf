terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Configure backend after initial setup if needed
  # backend "s3" {}
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "GuardIA Parto Seguro"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
