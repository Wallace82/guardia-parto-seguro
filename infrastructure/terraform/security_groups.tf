resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_prefix}-ecs-tasks-sg-${var.environment}"
  description = "Controle de trafego de entrada/saida para as tasks ECS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    protocol    = "tcp"
    from_port   = 8000
    to_port     = 8000
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 8007
    to_port     = 8007
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_prefix}-ecs-tasks-sg-${var.environment}"
  }
}

resource "aws_security_group" "rds" {
  name        = "${var.project_prefix}-rds-sg-${var.environment}"
  description = "Permitir trafego de entrada para o RDS a partir das tasks ECS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = 5432
    to_port         = 5432
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_prefix}-rds-sg-${var.environment}"
  }
}
