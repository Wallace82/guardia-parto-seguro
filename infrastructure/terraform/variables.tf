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
