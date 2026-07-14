# Modelo de Dados (Evidências Hierárquicas)

O sistema mudou da abordagem achatada (colunas `score_video`, `ira_score` em `sessions`) para uma abordagem relacional 1:N.

## Entidades Principais
1. **Session**: Retém apenas metadados do atendimento (status, datas, paciente, profissional).
2. **VideoAnalysis**: Guarda a análise facial profunda (emotion_score) e postural, mais eventos descritivos JSON.
3. **AudioAnalysis**: Guarda transcrições verbais, análise tonal (anxiety_score) e detecção de hesitações.
4. **DocumentAnalysis**: Guarda entidades extraídas por OCR, presença de CRM/assinatura e extração de CIDs.
5. **RiskHistory**: Funciona como um event sourcing das pontuações gerais do paciente a cada nova análise.
