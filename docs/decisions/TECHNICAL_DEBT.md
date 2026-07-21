# Relatório de Débito Técnico e Oportunidades de Melhoria (GuardIA)

Durante a auditoria arquitetural completa do projeto GuardIA Parto Seguro, foram identificadas diversas instâncias de débitos técnicos (Technical Debt), *dead-code* (código órfão) e *workarounds* (gambiarras temporárias). 

Este documento visa mapear essas ocorrências para que possam ser priorizadas e resolvidas nas próximas Sprints, sem impactar o funcionamento atual.

## 1. Divergências entre Modelos de IA Declarados e Implementados

### 1.1 Modelo YOLO (Vídeo)
- **Problema**: O arquivo `docker-compose.yml` declara a variável `YOLO_CONFIDENCE_THRESHOLD`, indicando a intenção de usar o YOLO para detecção de objetos de risco (ex: instrumentos cirúrgicos soltos). Contudo, o arquivo `video-domain/app/services/processor.py` apenas utiliza **DeepFace** (Emoções) e **MediaPipe** (Postura).
- **Ação Recomendada**: Implementar efetivamente a inferência com `ultralytics YOLOv8` no frame de análise de vídeo, ou remover a variável de ambiente se a feature for despriorizada.

### 1.2 Whisper (Áudio)
- **Problema**: Algumas menções no escopo do projeto apontavam o uso do modelo OpenAI Whisper para transcrição. Entretanto, o arquivo `audio-domain/app/services/processor.py` utiliza a biblioteca padrão `speech_recognition` e chama o motor **Google Web Speech API** para converter áudio em texto.
- **Ação Recomendada**: Migrar o reconhecedor (Recognizer) para o modelo Whisper local (usando `openai-whisper` ou `faster-whisper`) para transcrições *on-premise* seguras (essencial para dados sensíveis médicos de LGPD), eliminando a dependência do Google.

## 2. Hardcoded Mocks (Simulações Forçadas)

### 2.1 AWS Textract (Document Domain)
- **Problema**: Em `document-domain/app/main.py`, se a comunicação com o serviço AWS Textract falhar ou se o retorno for vazio, o sistema faz *fallback* para um longo texto em *hardcode* ("PRONTUÁRIO CLÍNICO SIMULADO - GUARDIA... Maria Aparecida da Silva").
- **Impacto**: Se houver instabilidade momentânea na conexão de internet do hospital, um prontuário real sofrerá uma análise sobre dados falsos.
- **Ação Recomendada**: Substituir o Mock estático por um lançamento de erro `503 Service Unavailable`, ou enfileirar o documento para re-tentativas (Retry com *Exponential Backoff*).

## 3. Débitos Arquiteturais (Backend Core)

### 3.1 Transição de Schema no Banco de Dados
- **Problema**: No arquivo `backend/app/sessions/models.py`, os campos agregados na tabela `Session` (`iga_score`, `iga_level`, `score_video`, `score_audio`, `score_document`) possuem comentários marcando-os como **DEPRECATED**. O sistema está em uma fase de transição (Etapa 2) para utilizar as novas tabelas de relações analíticas granulares (`video_analysis`, `audio_analysis`).
- **Ação Recomendada**: Finalizar a transição lógica nas queries. Executar uma migração via Alembic para transferir os dados antigos (se existirem) e realizar o `DROP COLUMN` destes campos da tabela `sessions`, centralizando todas as consultas nas tabelas satélites de análise.

### 3.2 Comunicação HTTP vs Filas Assíncronas
- **Problema**: Atualmente o orquestrador despacha mensagens para os serviços de visão/áudio/documento por chamadas HTTP e Polling.
- **Ação Recomendada**: Em vídeos/áudios muito longos de parto (ex: 2 horas de duração), as conexões HTTP estourarão por Timeout. É fundamental migrar a orquestração para eventos gerenciados (RabbitMQ, Kafka ou Redis Pub/Sub + Celery Workers).

## 4. Frontend Angular

### 4.1 Campos Mistos de Notação
- **Problema**: O backend estava exportando os dados analíticos como `iga_level` (Índice GuardIA), e partes do frontend estavam buscando como `ira_level` (Índice de Risco Assistencial).
- **Status**: Esta divergência foi resolvida recentemente, mas o código deve ser escaneado constantemente para não reintroduzir a confusão de termos (recomenda-se unificar o glossário em torno do termo **IGA** - Índice GuardIA de Atenção).
- **Ação Recomendada**: Configurar testes unitários estritos com validação de interfaces TypeScripts (Strict Mode).

## 5. Limpeza de Código Órfão e TODOs
- Vários arquivos Python contêm blocos isolados do tipo `except Exception as e: pass`. Ignorar exceções em laços for silenciosamente mascara falhas graves de IA em frames específicos. Sugere-se registrar todas as anomalias via `structlog.warning()`.
