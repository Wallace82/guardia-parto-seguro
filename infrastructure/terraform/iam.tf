# IAM Role base para a API que consumirá os serviços AWS
resource "aws_iam_role" "app_execution_role" {
  name = "${var.project_prefix}-app-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          # Pode ser assumido por usuário IAM (local/dev) ou ECS (hml/prd)
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Política de Acesso aos Buckets S3
resource "aws_iam_policy" "s3_access_policy" {
  name        = "${var.project_prefix}-s3-access-${var.environment}"
  description = "Acesso de leitura/escrita aos buckets do GuardIA"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.media_bucket.arn,
          "${aws_s3_bucket.media_bucket.arn}/*",
          aws_s3_bucket.reports_bucket.arn,
          "${aws_s3_bucket.reports_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = [aws_kms_key.s3_key.arn]
      }
    ]
  })
}

# Política para AWS AI Services
resource "aws_iam_policy" "ai_services_policy" {
  name        = "${var.project_prefix}-ai-services-${var.environment}"
  description = "Acesso aos serviços de Inteligência Artificial da AWS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob",
          "comprehend:DetectSentiment",
          "comprehend:DetectEntities",
          "textract:StartDocumentAnalysis",
          "textract:GetDocumentAnalysis",
          "textract:AnalyzeDocument"
        ]
        Resource = "*"
      }
    ]
  })
}

# ==============================================================================
# NOTA: O Secrets Manager está desativado para LOCAL/DEV devido a custos (ver secrets.tf).
# As policies abaixo só devem ser ativadas nos ambientes HML/PRD.
# ==============================================================================

# Política de Acesso ao Secrets Manager (Desativada no MVP)
# resource "aws_iam_policy" "secrets_access_policy" {
#   name        = "${var.project_prefix}-secrets-access-${var.environment}"
#   description = "Acesso para leitura do Secrets Manager"
# 
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "secretsmanager:GetSecretValue"
#         ]
#         Resource = [aws_secretsmanager_secret.app_secrets.arn]
#       }
#     ]
#   })
# }

# Attach policies
resource "aws_iam_role_policy_attachment" "attach_s3" {
  role       = aws_iam_role.app_execution_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_ai" {
  role       = aws_iam_role.app_execution_role.name
  policy_arn = aws_iam_policy.ai_services_policy.arn
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_prefix}-ecs-task-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


# resource "aws_iam_role_policy_attachment" "attach_secrets" {
#   role       = aws_iam_role.app_execution_role.name
#   policy_arn = aws_iam_policy.secrets_access_policy.arn
# }
