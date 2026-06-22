"""
GuardIA — Document Domain Service (AWS Integration)
"""
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load env variables from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

app = FastAPI(title="GuardIA — Document Service", version="1.0.0")

class DocumentAnalyzeRequest(BaseModel):
    file_path: str

class DocumentAnalyzeResponse(BaseModel):
    diagnosticos: list[str]

def analyze_document_with_aws(file_path: str):
    # TODO: Initialize boto3 textract client
    # textract = boto3.client('textract')
    
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
    result = analyze_document_with_aws(data.file_path)
    return DocumentAnalyzeResponse(
        diagnosticos=result["diagnosticos"]
    )
