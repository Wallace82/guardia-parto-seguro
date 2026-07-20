# Guia de Migração (Hierarquia de Evidências)

Durante a adoção da nova arquitetura (v1.0 -> v2.0 do motor de riscos), modificamos a estrutura da tabela `sessions`.

## Migração de Dados (Alembic)
O script `3a343aa1ac1b_add_analysis_models.py` não apenas recria as tabelas `video_analysis`, `audio_analysis` e `document_analysis`, mas insere nativamente um "mockup" nessas tabelas para preservar o histórico visual do frontend.

Se a `Session` ID 100 possuía `score_video=80`, criamos retroativamente um registro em `video_analysis` com esse mesmo ID de sessão e `emotion_score=80`. A tabela `risk_history` guarda os níveis da época em que a consulta ocorreu.

**Atenção:** Em versões futuras (v3.0), as colunas legadas `iga_score`, `score_video`, etc., serão deletadas via `op.drop_column('sessions', 'iga_score')`. Não crie novas regras de negócio lendo dessas colunas, consuma a rota `/api/session/{id}/risk-summary`.
