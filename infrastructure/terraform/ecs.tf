resource "aws_ecs_cluster" "main" {
  name = "guardia-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# Placeholder for Task Definitions and Services (e.g., aws-domain, core-api)
# These will be expanded later with actual ECR image URIs and port mappings.
