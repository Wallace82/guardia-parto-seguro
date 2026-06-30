import os
from app.config import settings
import structlog

log = structlog.get_logger(__name__)

def upload_report_to_storage(filename: str, file_bytes: bytes) -> str:
    """
    Realiza o upload do relatório para o Azure Blob Storage.
    Caso a Connection String não esteja configurada, salva localmente em uma pasta static.
    """
    # 1. Tentar upload para o Azure Blob Storage
    if settings.AZURE_BLOB_CONNECTION_STRING:
        try:
            from azure.storage.blob import BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_BLOB_CONNECTION_STRING)
            
            # Garante que o container existe
            container_client = blob_service_client.get_container_client(settings.AZURE_BLOB_CONTAINER_REPORTS)
            try:
                container_client.create_container()
            except Exception:
                pass # Container já existe
                
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(file_bytes, overwrite=True)
            
            # Retorna a URL pública / assinada (mockado para demo de SAS)
            return f"https://storageaccount.blob.core.windows.net/{settings.AZURE_BLOB_CONTAINER_REPORTS}/{filename}?sas=mocked_sas_token"
        except Exception as e:
            log.warning("storage.azure_upload.failed", error=str(e))
            
    # 2. Fallback: Armazenamento Local
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    local_file_path = os.path.join(settings.LOCAL_STORAGE_PATH, filename)
    with open(local_file_path, "wb") as f:
        f.write(file_bytes)
        
    # Retorna uma URL estática servida pelo próprio microsserviço
    return f"http://localhost:8005/static/{filename}"
