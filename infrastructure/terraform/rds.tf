resource "aws_db_subnet_group" "postgres" {
  name       = "${var.project_prefix}-db-subnet-group-${var.environment}"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "${var.project_prefix}-db-subnet-group-${var.environment}"
  }
}

resource "aws_db_instance" "postgres" {
  identifier           = "guardia-db-${var.environment}"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_type         = "gp2"
  
  db_name              = "guardia_db"
  username             = "postgres"
  # In a real environment, the password should be fetched from AWS Secrets Manager
  password             = "guardia_temporary_pass"
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  
  skip_final_snapshot    = true
  publicly_accessible    = false
}

