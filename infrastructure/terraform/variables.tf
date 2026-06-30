variable "aws_region" {
  description = "Região da AWS onde os recursos serão criados"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente de deployment (local, dev, hml, prd)"
  type        = string
  default     = "dev"
}

variable "project_prefix" {
  description = "Prefixo para nomear recursos de forma consistente"
  type        = string
  default     = "guardia-parto-seguro"
}

variable "core_api_image" {
  description = "URI da imagem Docker para o Core API"
  type        = string
  default     = "568137441171.dkr.ecr.us-east-1.amazonaws.com/guardia-core-api:latest"
}

variable "aws_service_image" {
  description = "URI da imagem Docker para o AWS Domain Service"
  type        = string
  default     = "568137441171.dkr.ecr.us-east-1.amazonaws.com/guardia-aws-service:latest"
}

