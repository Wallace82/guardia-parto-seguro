# Criação da chave KMS para S3 Encryption (Obrigatório por LGPD/Security)
resource "aws_kms_key" "s3_key" {
  description             = "Chave KMS para encriptação dos buckets S3 do GuardIA"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

resource "aws_kms_alias" "s3_key_alias" {
  name          = "alias/${var.project_prefix}-s3-key-${var.environment}"
  target_key_id = aws_kms_key.s3_key.key_id
}

# Bucket para armazenamento de mídias (vídeos, áudios, documentos sensíveis)
resource "aws_s3_bucket" "media_bucket" {
  bucket = "${var.project_prefix}-media-${var.environment}"
}

# Habilitar versionamento no bucket de mídia
resource "aws_s3_bucket_versioning" "media_bucket_versioning" {
  bucket = aws_s3_bucket.media_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Habilitar criptografia server-side via KMS
resource "aws_s3_bucket_server_side_encryption_configuration" "media_bucket_encryption" {
  bucket = aws_s3_bucket.media_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Bucket para armazenamento de relatórios e exportações (PDF/Excel)
resource "aws_s3_bucket" "reports_bucket" {
  bucket = "${var.project_prefix}-reports-${var.environment}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "reports_bucket_encryption" {
  bucket = aws_s3_bucket.reports_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}
