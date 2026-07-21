# Arquitetura do GuardIA Parto Seguro

O **GuardIA Parto Seguro** adota uma arquitetura orientada a microsserviços (Microservices), focada em alta escalabilidade, isolamento de domínios (Bounded Contexts) e processamento assíncrono para lidar com grandes volumes de dados de mídia (áudio, vídeo e documentos).

## 1. Visão Geral (High-Level Architecture)

A plataforma é dividida nas seguintes camadas principais:

- **Frontend (Client Layer):** SPA em Angular (Standalone Components) com Server-Side Rendering desativado ou opcional, provendo a interface de telemetria, dashboards e análise multimodal para os profissionais de saúde.
- **API Gateway / Orquestrador:** O `core-api` (Backend FastAPI) atua como o ponto central de entrada (BFF - Backend For Frontend). Ele gerencia sessões, autenticação e orquestra o roteamento para os serviços de Inteligência Artificial.
- **Domínios de IA (Workers):** Microsserviços independentes responsáveis pelo processamento pesado (Vídeo, Áudio, Documentos e Fusão de Risco).
- **Camada de Dados (Persistence):** PostgreSQL para dados relacionais estruturados (Sessões, Análises, Pacientes).
- **Armazenamento de Mídia:** Volume local compartilhado (`/shared_media`) que atua como Storage transiente/persistente (simulando um bucket S3 local). O `aws-domain` abstrai as integrações com serviços gerenciados de nuvem.

### Diagrama de Arquitetura e Modelos de IA

```mermaid
flowchart TD
    %% Frontend
    Client[Frontend Angular\nSPA, TailwindCSS]

    %% Gateway & Core
    Gateway[core-api\nFastAPI / Python\nBFF e Orquestrador]
    
    %% Databases
    DB[(PostgreSQL 16\nDados Clínicos, Sessões)]
    Storage[Volume Local\n/shared_media]

    %% AI Workers
    subgraph AI_Domains [Microsserviços de IA - Processamento Multimodal]
        Video[video-service\nOpenCV, YOLOv8, DeepFace\n(Expressões, Tensão)]
        Audio[audio-service\nWhisper, NLP\n(Tom de voz, Gritos)]
        Doc[document-service\nAWS Textract, OpenAI\n(OCR de Prontuários)]
    end

    %% Fusion
    Risk[risk-service\nMotor de Fusão\nCálculo do IGA]
    AWS[aws-service\nWrapper Integração AWS]
    Outros[report-service / security-service\nPDFs e Autenticação]

    %% Conexões Principais
    Client -- "Upload (MP4, MP3, PDF) / Dashboard" --> Gateway
    Gateway -- "Salva Metadados" --> DB
    Gateway -- "Salva Binário" --> Storage
    
    Gateway -- "HTTP REST (Fan-out)" --> Video
    Gateway -- "HTTP REST (Fan-out)" --> Audio
    Gateway -- "HTTP REST (Fan-out)" --> Doc
    
    Video -- "Lê Mídia" --> Storage
    Audio -- "Lê Mídia" --> Storage
    Doc -- "Lê Mídia" --> Storage

    Doc -. "OCR Externo" .-> AWS
    
    Gateway -- "HTTP REST (Fan-in)" --> Risk
    Risk -- "Consolida Notas e Gera Alerta Crítico" --> DB
    
    Gateway --> Outros
```

## 2. Mapa de Serviços (Docker Compose)

| Serviço | Porta | Tecnologia | Responsabilidade |
|---------|-------|------------|------------------|
| `postgres-core` | 5432 | PostgreSQL 16 | Banco de dados transacional central (`core_db`). |
| `core-api` | 8000 | FastAPI / Python | Orquestrador, CRUD de Sessões, Autenticação, Interface BFF. |
| `video-service` | 8001 | FastAPI / Python | YOLO, MediaPipe, DeepFace. Extração de bounding boxes e emoções de frames. |
| `audio-service` | 8002 | FastAPI / Python | Whisper. Transcrição de áudio, detecção de dor e análise de sentimentos. |
| `document-service` | 8003 | FastAPI / Python | Integração OCR/Textract e extração de dados vitais via NLP (Comprehend/OpenAI). |
| `risk-service` | 8004 | FastAPI / Python | Motor de Fusão. Calcula o IGA (Índice GuardIA de Atenção). |
| `report-service` | 8005 | FastAPI / Python | Geração de PDFs e relatórios formatados da sessão. |
| `security-service` | 8006 | FastAPI / Python | Tratamento de chaves e autorizações. |
| `aws-service` | 8007 | FastAPI / Python | Wrappers para serviços gerenciados (S3, Textract). |

## 3. Fluxo de Processamento Multimodal

A arquitetura do GuardIA resolve o problema de **Fusão Multimodal (Multimodal Sensor Fusion)** da seguinte forma:

1. **Ingestão (Upload):** O cliente envia um arquivo (ex: vídeo MP4) para o `core-api`.
2. **Armazenamento:** O `core-api` salva fisicamente o arquivo no volume `shared_media` e cria um registro `MediaFile` no banco de dados com status `processing`.
3. **Delegação (Fan-out):** O `core-api` realiza uma chamada HTTP para o respectivo microsserviço (ex: `video-service`), passando o caminho do arquivo (`blob_url`).
4. **Processamento Inteligente (AI Worker):** 
   - O serviço lê o arquivo do disco compartilhado.
   - Aplica os modelos neurais em batch/stream (DeepFace para emoções, MediaPipe para postura).
   - Opcionalmente re-encoda o vídeo com *bounding boxes* impressos usando `ffmpeg` (ex: `_annotated.mp4`).
   - Retorna o resultado (`emotion_score`, `key_findings`).
5. **Consolidação (Fan-in / Risk Engine):** O orquestrador salva os metadados no banco (ex: `VideoAnalysis`).
6. **Fusão de Risco:** O orquestrador aciona o `RiskFusionEngine` (`risk-service` ou local fallback) passando as notas de todas as modalidades da sessão. O motor calcula o Score Global Ponderado (IGA - Índice GuardIA de Atenção).
7. **Atualização de Estado:** O `core-api` atualiza a Sessão para o novo status de risco (Baixo, Moderado, Crítico) via WebSocket/Polling, atualizando o *Dashboard* instantaneamente em Angular.

## 4. Topologia de Diretórios e Código

- O monorepo adota a convenção de que **cada pasta raiz corresponde a um serviço/domínio**, garantindo independência e permitindo que as equipes (Squads) trabalhem isoladas.
- O padrão interno dos serviços em Python segue a organização modular:
  - `app/api/` (Routers e Controllers FastAPI)
  - `app/core/` (Configurações, variáveis de ambiente Pydantic BaseSettings)
  - `app/services/` (Lógica de Negócio e IAs - Use Cases)
  - `app/schemas/` (Pydantic Models - DTOs)

## 5. Padrões Adotados (ADRs)

1. **Volume Compartilhado (`/shared_media`) vs. S3 Real:** 
   - Para ambiente de desenvolvimento e latência zero em inferência on-premise, os containers mapeiam o mesmo diretório local.
2. **REST Invocation:**
   - Atualmente a comunicação inter-serviços utiliza chamadas HTTP (REST) síncronas/assíncronas gerenciadas pelo orquestrador. A evolução preverá *Event-Driven* com filas puras (Kafka/RabbitMQ) para tolerância a falhas pesadas.
3. **Injeção de Dependência:**
   - Totalmente gerenciada via `Depends` do FastAPI para sessions de banco de dados (`asyncpg` via `SQLAlchemy`).
