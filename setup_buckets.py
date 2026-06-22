import os
import boto3
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do .env local
load_dotenv()

def create_buckets():
    region = os.getenv("AWS_REGION", "us-east-1")
    media_bucket = os.getenv("MEDIA_BUCKET_NAME")
    reports_bucket = os.getenv("REPORTS_BUCKET_NAME")

    if not media_bucket or not reports_bucket:
        print("ERRO: MEDIA_BUCKET_NAME e REPORTS_BUCKET_NAME precisam estar definidos no .env")
        return

    print(f"Tentando conectar na AWS região: {region}...")
    
    try:
        s3 = boto3.client('s3', region_name=region)
        
        # Parâmetros de criação de bucket (us-east-1 não precisa de LocationConstraint)
        create_kwargs = {}
        if region != 'us-east-1':
            create_kwargs = {'CreateBucketConfiguration': {'LocationConstraint': region}}

        # Criação do Media Bucket
        print(f"Criando bucket de mídia: {media_bucket}...")
        s3.create_bucket(Bucket=media_bucket, **create_kwargs)
        print("✅ Bucket de mídias criado com sucesso!")

        # Criação do Reports Bucket
        print(f"Criando bucket de relatórios: {reports_bucket}...")
        s3.create_bucket(Bucket=reports_bucket, **create_kwargs)
        print("✅ Bucket de relatórios criado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao criar buckets: {e}")

if __name__ == "__main__":
    create_buckets()
