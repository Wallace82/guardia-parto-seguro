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

resource "aws_cloudwatch_log_group" "core_api" {
  name              = "/ecs/guardia-core-api-${var.environment}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "aws_service" {
  name              = "/ecs/guardia-aws-service-${var.environment}"
  retention_in_days = 30
}

resource "aws_ecs_task_definition" "core_api" {
  family                   = "guardia-core-api-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.app_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "core-api"
      image     = var.core_api_image
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.core_api.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        { name = "ENVIRONMENT", value = var.environment }
      ]
    }
  ])
}

resource "aws_ecs_task_definition" "aws_service" {
  family                   = "guardia-aws-service-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.app_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "aws-service"
      image     = var.aws_service_image
      essential = true
      portMappings = [
        {
          containerPort = 8007
          hostPort      = 8007
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.aws_service.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        { name = "ENVIRONMENT", value = var.environment }
      ]
    }
  ])
}

resource "aws_ecs_service" "core_api" {
  name            = "guardia-core-api-service-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.core_api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
}

resource "aws_ecs_service" "aws_service" {
  name            = "guardia-aws-service-service-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.aws_service.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
}

