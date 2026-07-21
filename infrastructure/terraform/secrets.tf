# ==============================================================================
# ATENÇÃO: AWS Secrets Manager desativado para o MVP/Ambiente Local
# ==============================================================================
# Motivo: O Secrets Manager gera cobranças rápidas (por secret/mês + chamadas API).
# Como este é um projeto acadêmico (MVP), estamos priorizando a contenção de custos.
# 
# Estratégia Adotada:
# - LOCAL/DEV: Utilizaremos variáveis de ambiente gerenciadas por arquivos `.env`.
# - HML/PRD: Utilizaremos o AWS Secrets Manager (código abaixo será ativado).
# ==============================================================================

# resource "aws_secretsmanager_secret" "app_secrets" {
#   name        = "${var.project_prefix}-secrets-${var.environment}"
#   description = "Segredos do aplicativo GuardIA Parto Seguro (DB, API Keys)"
# }

# resource "aws_secretsmanager_secret_version" "app_secrets_version" {
#   secret_id = aws_secretsmanager_secret.app_secrets.id
#   secret_string = jsonencode({
#     DB_USER     = "guardia_user"
#     DB_PASSWORD = "CHANGE_ME"
#     JWT_SECRET  = "CHANGE_ME"
#   })
# 
#   lifecycle {
#     ignore_changes = [secret_string]
#   }
# }
