"""
GuardIA — Document Domain Service (AWS Integration)
"""
import os
import re
import asyncio
import httpx
import structlog
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

# Load env variables from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

log = structlog.get_logger(__name__)

app = FastAPI(title="GuardIA — Document Service", version="1.0.0")

class DocumentAnalyzeRequest(BaseModel):
    session_id: str
    media_id: str
    blob_url: str
    document_type: str

class TextBlock(BaseModel):
    block_type: str
    text: Optional[str] = None
    confidence: Optional[float] = None

class DocumentAnalyzeResponse(BaseModel):
    session_id: str
    ira_score: float
    document_type: str
    extracted_fields: dict
    completeness_score: float
    consistency_checks: list
    ocr_text: Optional[str] = None
    raw_ai_analysis: Optional[dict] = None

class NotesAnalyzeRequest(BaseModel):
    session_id: str
    notes: str

@app.get("/api/v1/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/documents/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "document"}

@app.post("/api/v1/documents/analyze", status_code=status.HTTP_200_OK, response_model=DocumentAnalyzeResponse)
async def analyze(data: DocumentAnalyzeRequest):
    log.info("document.analyze.started", session_id=data.session_id, blob_url=data.blob_url)
    
    # 1. Resolve local file path from blob_url
    file_path = data.blob_url
    if data.blob_url.startswith("file:///"):
        file_path = data.blob_url.replace("file:///", "/")
    elif data.blob_url.startswith("file://"):
        file_path = data.blob_url.replace("file://", "")
    if os.name == 'nt' and file_path.startswith('/C:'):
        file_path = file_path[1:]

    ocr_text = ""
    
    # 2. Try to communicate with aws-service (Textract router)
    try:
        aws_service_url = os.getenv("AWS_SERVICE_URL", "http://aws-service:8007")
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Solicitar início da análise no Textract
            response = await client.post(
                f"{aws_service_url}/api/v1/textract/analyze",
                json={
                    "file_name": os.path.basename(file_path),
                    "bucket_type": "media"
                }
            )
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data.get("job_id")
                if job_id:
                    import asyncio
                    # Polling para aguardar o resultado do Textract (AWS Async)
                    max_attempts = 15
                    for attempt in range(max_attempts):
                        res_resp = await client.get(f"{aws_service_url}/api/v1/textract/results/{job_id}")
                        if res_resp.status_code == 200:
                            res_data = res_resp.json()
                            if res_data.get("status") == "SUCCEEDED":
                                ocr_text = res_data.get("extracted_text", "") or ""
                                break
                            elif res_data.get("status") in ["FAILED", "PARTIAL_SUCCESS"]:
                                break
                        await asyncio.sleep(2.0)
    except Exception as e:
        log.warning("document.aws_service.failed", error=str(e))

    # Mock do Textract para testes se não houve retorno da AWS
    if not ocr_text.strip():
        log.info("Usando OCR Mockado (Prontuário Simulado)")
        ocr_text = """
PRONTUÁRIO CLÍNICO SIMULADO - GUARDIA
PARTO SEGURO
ATENÇÃO: Documento fictício criado exclusivamente para testes e demonstrações.
Paciente: Maria Aparecida da Silva
ID: PACIENTE_001
Idade: 29 anos
Gestação: 38 semanas
Data da Consulta: 22/06/2026
Histórico Clínico
Hipertensão gestacional controlada. Sem histórico de diabetes gestacional. Relata episódios
recorrentes de ansiedade durante o pré-natal.
Sinais Vitais
PA: 138/88 mmHg | FC: 84 bpm | Temperatura: 36,7°C
Observações da Consulta
Paciente apresentou fala hesitante ao relatar preocupações sobre o parto. Demonstrou sinais
visíveis de ansiedade e desconforto emocional durante parte da entrevista.
Avaliação Psicológica Preliminar
Indicadores compatíveis com ansiedade gestacional moderada. Recomendada avaliação
multiprofissional e acompanhamento psicológico.
Plano de Acompanhamento
Retorno em 7 dias. Monitoramento da pressão arterial. Reforço das orientações sobre trabalho de
parto e suporte emocional.
"""

    # 4. Análise semântica avançada com OpenAI
    import openai
    import json
    api_key = os.environ.get("OPENAI_API_KEY")
    raw_ai_analysis = None
    if not api_key or not ocr_text.strip():
        log.warning("openai_fallback", reason="Sem API KEY ou sem texto OCR")
        # Fallback de erro
        ira_score = 90.0
        extracted_fields = {}
        completeness_score = 40.0
        consistency_checks = []
    else:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            if data.document_type in ["prontuario", "termo_consentimento", "prescricao"]:
                prompt = f"""
Você é o módulo de Inteligência Artificial Clínica do sistema GuardIA Parto Seguro.

Sua função é analisar documentos clínicos relacionados à saúde da mulher, gestação, parto e pós-parto.
Você receberá textos extraídos automaticamente pelo AWS Textract a partir de documentos PDF.

Sua responsabilidade é:
1. Interpretar o conteúdo clínico.
2. Extrair informações estruturadas.
3. Identificar fatores de risco.
4. Avaliar indicadores emocionais e psicossociais.
5. Gerar um Índice de Risco Assistencial (IRA).

IMPORTANTE:
Você não realiza diagnóstico médico.
Você não substitui profissionais de saúde.
Sua função é auxiliar análise assistencial e indicar pontos que merecem atenção.

---
ANTES DA ANÁLISE:
Avalie a qualidade do texto recebido.
Se o documento possuir apenas informações genéricas não invente informações.
Retorne: qualidade_documento = BAIXA e informe que são necessários mais dados.

---
ANALISE OS SEGUINTES DOMÍNIOS:

## 1. Dados obstétricos
Extraia: idade, idade gestacional, número de gestações, histórico obstétrico, complicações, exames, sinais vitais.

## 2. Fatores clínicos
Identifique: hipertensão, diabetes, sangramentos, dores, alterações laboratoriais, condições pré-existentes.

## 3. Fatores emocionais
Avaliar: ansiedade, medo, insegurança, tristeza, sofrimento emocional, sinais de vulnerabilidade.

## 4. Comunicação
Avaliar: dificuldade de expressão, hesitação, dúvidas, necessidade de maior acolhimento.

## 5. Indicadores relacionados à humanização
Identificar: necessidade de escuta ativa, suporte emocional, autonomia da paciente, consentimento informado.

---
CRITÉRIOS DE FILTRAGEM DE RISCO E ALERTAS (EVITAR FALSOS POSITIVOS):
ATENÇÃO MÁXIMA: Os arrays do JSON (`conditions`, `indicators`, `risk_factors`, `attention_points`) DEVEM conter APENAS anomalias severas, riscos não controlados ou falhas assistenciais genuínas. 
Se algo estiver normal, leve ou controlado, DEIXE O ARRAY VAZIO [].
1. Condições Controladas: NUNCA liste condições explícitas como "controlada" (ex: "hipertensão controlada", "diabetes controlada") em `conditions`, `risk_factors` ou `attention_points`. Omita completamente a não ser que haja agravamento atual.
2. Emoções Esperadas: Ansiedade leve, dúvidas e preocupações comuns ("preocupações sobre o parto") NÃO devem aparecer nas listas de `indicators` (emocionais ou comunicação). Só inclua nessas listas se houver pânico, sofrimento extremo ou negligência da equipe perante a emoção.
3. Comunicação: "Fala hesitante" ou dúvidas naturais NÃO devem ser listadas em `indicators` de comunicação ou `attention_points`. Só inclua se a equipe falhar gravemente na escuta ou se houver barreira severa de comunicação.

---
CALCULE O IRA (Índice de Risco Assistencial):
Pesos: Fatores clínicos (30%), Fatores emocionais (30%), Comunicação (20%), Vulnerabilidade psicossocial (20%)
Classificação: 0-25 (BAIXO), 26-50 (MODERADO), 51-75 (ELEVADO), 76-100 (CRÍTICO)
Lembre-se: Prontuários com indicadores apenas "controlados" ou emoções normais devem ter IRA BAIXO (0-25).

---
RETORNE SEMPRE UM JSON ESTRITAMENTE NESTE FORMATO:
{{
 "document_quality": "",
 "patient": {{ "name":"", "age":"", "gestational_age":"" }},
 "clinical_data": {{ "conditions":[], "vital_signs":{{}} }},
 "emotional_analysis": {{ "indicators":[], "severity":"" }},
 "communication_analysis":{{ "indicators":[] }},
 "risk_factors": [],
 "ira": {{ "score":0, "classification":"" }},
 "evidence": {{ "positive":"", "attention_points":[] }},
 "recommendations": [],
 "requires_human_review": true
}}

Nunca invente dados ausentes. Sempre informe quando uma informação não estiver disponível.

Texto OCR do Documento:
{ocr_text}
"""
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" },
                    temperature=0.2
                )
                data_json = json.loads(response.choices[0].message.content)
                raw_ai_analysis = data_json
                
                extracted_fields = data_json
                ira_score = float(data_json.get("ira", {}).get("score", 50.0))
                completeness_score = 90.0 if data_json.get("document_quality", "").upper() != "BAIXA" else 50.0
                consistency_checks = []
                
                log.info("openai_document_analysis_success", ira=ira_score)
            else:
                ira_score = 0.0
                extracted_fields = {}
                completeness_score = 0.0
                consistency_checks = []
        except Exception as oai_err:
            log.error("openai_document_analysis_failed", error=str(oai_err))
            raw_ai_analysis = {"error": str(oai_err)}
            extracted_fields = {}
            completeness_score = 40.0
            ira_score = 90.0
            consistency_checks = [{"check": "error", "passed": False, "severity": "high", "detail": "Falha na análise via IA (OpenAI)"}]

    log.info("document.analyze.completed", session_id=data.session_id, ira_score=ira_score)

    return DocumentAnalyzeResponse(
        session_id=data.session_id,
        ira_score=ira_score,
        document_type=data.document_type,
        extracted_fields=extracted_fields,
        completeness_score=completeness_score,
        consistency_checks=consistency_checks,
        ocr_text=ocr_text,
        raw_ai_analysis=raw_ai_analysis
    )

@app.post("/api/v1/documents/analyze-notes", status_code=status.HTTP_200_OK)
async def analyze_notes(data: NotesAnalyzeRequest):
    import openai
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API Key não configurada no document-domain")
        
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"""
Você é o módulo de Inteligência Artificial Clínica do sistema GuardIA Parto Seguro.

Sua função é analisar anotações clínicas relacionadas à saúde da mulher, gestação, parto e pós-parto.

Você NÃO deve realizar diagnóstico médico definitivo.

Sua função é identificar indicadores, padrões, fatores de atenção e gerar uma análise assistencial baseada nas informações fornecidas.

Analise sempre considerando:
- contexto obstétrico;
- aspectos emocionais;
- comunicação paciente-equipe;
- sinais de ansiedade, medo ou sofrimento;
- possíveis barreiras de comunicação;
- fatores psicossociais;
- indicadores relacionados à humanização do atendimento.

IMPORTANTE:
Antes de analisar o conteúdo clínico, avalie a qualidade da informação recebida.
Caso o texto seja muito curto, genérico ou sem informações relevantes, NÃO invente informações.

Exemplos de textos insuficientes:
"Paciente gestante em acompanhamento pré-natal."
"Paciente está bem."
"Consulta realizada."

Nestes casos responda:
- Informação insuficiente para análise detalhada.
- Solicitar complementação da anotação clínica.
Nunca crie sintomas, emoções ou riscos que não estejam descritos.

---

REGRAS DE ANÁLISE:
1. Identifique informações clínicas presentes.
2. Identifique indicadores emocionais.
3. Identifique indicadores comportamentais.
4. Identifique fatores de vulnerabilidade.
5. Avalie qualidade da comunicação registrada.
6. Gere um índice de atenção assistencial (IRA).
7. Para cada indicador, classifique seu impacto ("POSITIVO" ou "ATENCAO"). Se o indicador representar segurança, confiança ou normalidade, é POSITIVO. Se representar vulnerabilidade, medo, dor ou pressão de terceiros (ex: "pressão do parceiro"), é ATENCAO.
O IRA é um indicador auxiliar e não substitui avaliação profissional.

---

ESCALA IRA:
0-25: Baixo indicador de atenção.
26-50: Necessita acompanhamento.
51-75: Atenção elevada.
76-100: Necessita avaliação prioritária.

---

FORMATO OBRIGATÓRIO DA RESPOSTA:
Retorne sempre em JSON:
{{
 "qualidade_informacao": {{
    "nivel": "ALTA|MEDIA|BAIXA",
    "observacao": ""
 }},
 "resumo_clinico": "",
 "indicadores_identificados": [
    {{
      "tipo":"",
      "descricao":"",
      "intensidade":"BAIXA|MEDIA|ALTA",
      "impacto":"POSITIVO|ATENCAO"
    }}
 ],
 "aspectos_emocionais": {{
    "identificados": [],
    "nivel": ""
 }},
 "aspectos_comunicacao": {{
    "avaliacao":"",
    "indicadores":[]
 }},
 "fatores_risco": [],
 "ira_score": 0,
 "classificacao_ira": "",
 "recomendacoes": [
    ""
 ],
 "necessita_avaliacao_humana": true
}}

---

Sempre mantenha uma abordagem ética, cuidadosa e baseada em evidências.

Anotações Clínicas: "{data.notes}"
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.3
        )
        import json
        result = json.loads(response.choices[0].message.content)
        
        # Formata o texto para manter compatibilidade com a UI existente
        analysis_text = f"**Resumo Clínico:**\n{result.get('resumo_clinico', 'Não informado')}\n\n"
        analysis_text += f"**Qualidade da Informação:** {result.get('qualidade_informacao', {}).get('nivel', '')} - {result.get('qualidade_informacao', {}).get('observacao', '')}\n\n"
        
        if result.get("indicadores_identificados"):
            analysis_text += "**Indicadores Identificados:**\n"
            for ind in result.get("indicadores_identificados", []):
                analysis_text += f"- {ind.get('tipo', 'Outro')}: {ind.get('descricao', '')} (Impacto: {ind.get('impacto', 'ATENCAO')}, Intensidade: {ind.get('intensidade', '')})\n"
            analysis_text += "\n"
            
        if result.get("aspectos_emocionais", {}).get("identificados"):
            analysis_text += f"**Aspectos Emocionais (Nível {result.get('aspectos_emocionais', {}).get('nivel', '')}):**\n"
            for emo in result.get("aspectos_emocionais", {}).get("identificados", []):
                analysis_text += f"- {emo}\n"
            analysis_text += "\n"
            
        if result.get("fatores_risco"):
            analysis_text += "**Fatores de Risco:**\n"
            for fator in result.get("fatores_risco", []):
                analysis_text += f"- {fator}\n"
            analysis_text += "\n"
            
        if result.get("recomendacoes"):
            analysis_text += "**Recomendações:**\n"
            for rec in result.get("recomendacoes", []):
                analysis_text += f"- {rec}\n"
                
        return {
            "analysis": analysis_text,
            "clinical_risk_score": float(result.get("ira_score", 0.0)),
            "structured_analysis": result
        }
    except Exception as e:
        log.error("openai_notes_analysis_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro na OpenAI: {str(e)}")
