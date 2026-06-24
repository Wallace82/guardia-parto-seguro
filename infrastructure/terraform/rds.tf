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
  
  vpc_security_group_ids = [] # To be associated with VPC module output
  db_subnet_group_name   = "" # To be associated with VPC private subnets
  
  skip_final_snapshot    = true
  publicly_accessible    = false
}
