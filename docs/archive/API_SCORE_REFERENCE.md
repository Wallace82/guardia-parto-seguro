# Referência da API de Scores e Análises

As rotas base `api/v1/sessions` agora interagem em conjunto com o `analysis_router`.

## POST /api/video-analysis
Recebe métricas visuais extraídas pelo RetinaFace e OpenPose. Cria registro granular vinculado à sessão.

## POST /api/audio-analysis
Recebe os `sentiment_scores` processados pelo Audio Service. 

## POST /api/document-analysis
Recebe as saídas do Textract formatadas.

## GET /api/session/{id}/risk-summary
Endpoint de fusão sob demanda.
**Retorno Exemplo:**
```json
{
 "sessionId": 123,
 "globalScore": 42.5,
 "riskLevel": "MEDIUM",
 "sources": {
   "video": 35.0,
   "audio": 50.0,
   "document": 40.0
 }
}
```
