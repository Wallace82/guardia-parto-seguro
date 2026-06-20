"""
GuardIA — Document Domain Service (Azure Integration)
"""
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env variables from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

app = FastAPI(title="GuardIA — Document Service", version="1.0.0")

class DocumentAnalyzeRequest(BaseModel):
    file_path: str

class DocumentAnalyzeResponse(BaseModel):
    diagnosticos: list[str]

def analyze_document_with_azure(file_path: str):
    endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")

    if not all([endpoint, key]):
        raise HTTPException(status_code=500, detail="Azure credentials missing in .env")

    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    with open(file_path, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-document", analyze_request=f, content_type="application/octet-stream"
        )
    result = poller.result()

    diagnosticos = []
    
    # Busca por pares chave-valor que remetam a um diagnóstico
    if result.key_value_pairs:
        for kv_pair in result.key_value_pairs:
            if kv_pair.key and kv_pair.value:
                key_text = kv_pair.key.content.lower()
                if "diagnóstico" in key_text or "diagnostico" in key_text or "cid" in key_text:
                    diagnosticos.append(kv_pair.value.content)
                    
    # Se não encontrar nada estruturado, adicionamos uma mensagem padrão
    if not diagnosticos:
        diagnosticos = ["Nenhum diagnóstico explicitamente mapeado pelas chaves do documento."]

    return {"diagnosticos": diagnosticos}

@app.get("/api/v1/documents/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "document"}

@app.post("/api/v1/documents/analyze", status_code=status.HTTP_200_OK, response_model=DocumentAnalyzeResponse)
async def analyze(data: DocumentAnalyzeRequest):
    result = analyze_document_with_azure(data.file_path)
    return DocumentAnalyzeResponse(
        diagnosticos=result["diagnosticos"]
    )
