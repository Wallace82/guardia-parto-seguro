# ARCHITECTURE.md — GuardIA Parto Seguro

> Documento de Arquitetura de Software — Versão 1.0  
> Classificação: Acadêmico — FIAP Tech Challenge

---

## 1. Visão Executiva

### 1.1 Business Case

O Brasil registra altos índices de violência obstétrica e mortalidade materna, muitas vezes associados à ausência de sistemas de vigilância assistencial em tempo real. O **GuardIA Parto Seguro** propõe uma plataforma de IA multimodal capaz de processar simultaneamente vídeo, áudio, documentos e histórico clínico, gerando alertas preventivos e relatórios especializados para equipes de saúde, gestores e ouvidorias.

**Impacto esperado:**
- Redução de 40% nos casos não reportados de violência obstétrica
- Detecção precoce de depressão pós-parto em até 72h após o parto
- Auditoria assistencial automatizada com IRA (Índice de Risco Assistencial)

### 1.2 Problema

- Ausência de vigilância contínua no ambiente obstétrico
- Subnotificação de violência obstétrica e doméstica
- Diagnóstico tardio de depressão pós-parto
- Falta de rastreabilidade em procedimentos clínicos
- Sobrecarga dos profissionais de saúde em registro manual

### 1.3 Objetivos

1. Detectar automaticamente indicadores de violência obstétrica via análise de vídeo e áudio
2. Monitorar sinais de sofrimento psicológico e depressão pós-parto
3. Analisar documentos médicos para detectar inconsistências e riscos
4. Correlacionar múltiplas fontes de dados para calcular o IRA
5. Gerar relatórios e alertas acionáveis para equipes de saúde
6. Fornecer dashboard multimodal em tempo quase real

### 1.4 Escopo

**Dentro do escopo:**
- Análise de vídeo clínico (câmeras de sala de parto e consulta)
- Análise de áudio de consultas (com consentimento)
- Processamento de documentos médicos (prontuários, exames)
- Cálculo do IRA com base em múltiplas fontes
- Dashboard de monitoramento em tempo real
- Sistema de alertas e notificações
- Geração de relatórios especializados

**Fora do escopo:**
- Diagnóstico médico definitivo (sistema é de apoio à decisão)
- Integração com sistemas HIS/RES hospitalares legados (v1.0)
- Aplicativo mobile
- Telemedicina em tempo real

---

## 2. Princípios de Arquitetura

| Princípio | Descrição |
|---|---|
| **Desacoplamento** | Cada domínio é independente; comunicação via API/eventos |
| **Isolamento de dados** | Nenhum domínio acessa o banco de outro diretamente |
| **Contratos versionados** | Toda integração usa contratos com versionamento semântico |
| **Testabilidade** | Cobertura mínima de 80% em testes unitários |
| **Observabilidade** | Logs estruturados, métricas e rastreamento distribuído |
| **Segurança** | Zero-trust, criptografia em repouso e em trânsito |
| **Escalabilidade** | Cada serviço escala independentemente via Docker |

---

## 3. Diagrama de Contexto (C4 — Nível 1)

```mermaid
C4Context
    title GuardIA Parto Seguro — Diagrama de Contexto

    Person(profissional, "Profissional de Saúde", "Médico, enfermeiro, parteiro")
    Person(gestor, "Gestor Hospitalar", "Coordenador de qualidade assistencial")
    Person(ouvidor, "Ouvidor / Compliance", "Responsável por denúncias e auditoria")

    System(guardia, "GuardIA Parto Seguro", "Plataforma multimodal de IA para vigilância obstétrica")

    System_Ext(azure_speech, "Azure Speech", "STT e análise de fala")
    System_Ext(azure_lang, "Azure AI Language", "NLP e análise de sentimento")
    System_Ext(azure_doc, "Azure Document Intelligence", "OCR e extração documental")
    System_Ext(azure_blob, "Azure Blob Storage", "Armazenamento de mídias")
    System_Ext(azure_kv, "Azure Key Vault", "Gerenciamento de segredos")
    System_Ext(azure_monitor, "Azure Monitor", "Observabilidade")

    Rel(profissional, guardia, "Visualiza alertas e relatórios")
    Rel(gestor, guardia, "Monitora IRA e dashboard")
    Rel(ouvidor, guardia, "Acessa relatórios de auditoria")
    Rel(guardia, azure_speech, "Transcreve áudios de consulta")
    Rel(guardia, azure_lang, "Analisa texto para sentimento e risco")
    Rel(guardia, azure_doc, "Processa documentos médicos")
    Rel(guardia, azure_blob, "Armazena vídeos e documentos")
    Rel(guardia, azure_kv, "Recupera credenciais e chaves")
    Rel(guardia, azure_monitor, "Envia logs e métricas")
```

---

## 4. Diagrama de Contêiner (C4 — Nível 2)

```mermaid
C4Container
    title GuardIA Parto Seguro — Diagrama de Contêiner

    Person(user, "Usuário", "Profissional de Saúde / Gestor")

    Container(frontend, "Dashboard", "Streamlit", "Interface multimodal de monitoramento")
    Container(gateway, "API Gateway", "FastAPI :8000", "Roteamento, autenticação, orquestração")
    Container(video_svc, "Video Service", "FastAPI :8001", "OpenCV, MediaPipe, DeepFace, YOLOv8")
    Container(audio_svc, "Audio Service", "FastAPI :8002", "Azure Speech, Azure AI Language")
    Container(doc_svc, "Document Service", "FastAPI :8003", "Azure Document Intelligence")
    Container(risk_svc, "Risk Service", "FastAPI :8004", "Cálculo do IRA")
    Container(report_svc, "Report Service", "FastAPI :8005", "Geração de PDF/Excel")

    ContainerDb(db_core, "Core DB", "PostgreSQL", "Usuários, sessões, alertas")
    ContainerDb(db_video, "Video DB", "PostgreSQL", "Análises de vídeo")
    ContainerDb(db_audio, "Audio DB", "PostgreSQL", "Transcrições e análises de áudio")
    ContainerDb(db_doc, "Document DB", "PostgreSQL", "Documentos processados")
    ContainerDb(db_risk, "Risk DB", "PostgreSQL", "Histórico de IRA")
    ContainerDb(db_report, "Report DB", "PostgreSQL", "Relatórios gerados")

    Rel(user, frontend, "Acessa via browser", "HTTP")
    Rel(frontend, gateway, "Chama APIs", "REST/JSON")
    Rel(gateway, video_svc, "Delega análise de vídeo", "REST")
    Rel(gateway, audio_svc, "Delega análise de áudio", "REST")
    Rel(gateway, doc_svc, "Delega análise documental", "REST")
    Rel(gateway, risk_svc, "Solicita cálculo de IRA", "REST")
    Rel(gateway, report_svc, "Solicita geração de relatório", "REST")
    Rel(gateway, db_core, "Lê/Escreve", "SQL")
    Rel(video_svc, db_video, "Lê/Escreve", "SQL")
    Rel(audio_svc, db_audio, "Lê/Escreve", "SQL")
    Rel(doc_svc, db_doc, "Lê/Escreve", "SQL")
    Rel(risk_svc, db_risk, "Lê/Escreve", "SQL")
    Rel(report_svc, db_report, "Lê/Escreve", "SQL")
```

---

## 5. Diagrama de Componentes — API Gateway (C4 — Nível 3)

```mermaid
C4Component
    title API Gateway — Componentes Internos

    Container_Boundary(gateway, "API Gateway — FastAPI") {
        Component(auth, "Auth Module", "JWT + Azure AD", "Autenticação e autorização")
        Component(router, "Domain Router", "FastAPI Router", "Roteia requisições para os domínios")
        Component(orchestrator, "Orchestrator", "Python", "Coordena fluxos multimodais")
        Component(alert_engine, "Alert Engine", "Python", "Dispara alertas com base em thresholds")
        Component(audit_log, "Audit Logger", "Python + Azure Monitor", "Log imutável de auditoria")
    }
```

---

## 6. Diagrama de Sequência — Fluxo Principal de Análise

```mermaid
sequenceDiagram
    actor Prof as Profissional
    participant FE as Dashboard (Streamlit)
    participant GW as API Gateway
    participant VS as Video Service
    participant AS as Audio Service
    participant DS as Document Service
    participant RS as Risk Service
    participant RP as Report Service

    Prof->>FE: Upload de sessão clínica (vídeo + áudio + doc)
    FE->>GW: POST /api/v1/sessions
    GW->>GW: Autentica JWT e cria sessão

    par Análise Paralela
        GW->>VS: POST /analyze (vídeo)
        GW->>AS: POST /analyze (áudio)
        GW->>DS: POST /analyze (documentos)
    end

    VS-->>GW: VideoAnalysisResult {ira_contribuicao, alertas}
    AS-->>GW: AudioAnalysisResult {ira_contribuicao, alertas}
    DS-->>GW: DocumentAnalysisResult {ira_contribuicao, alertas}

    GW->>RS: POST /correlate (resultados multimodais)
    RS-->>GW: IRAResult {score, nivel_risco, justificativas}

    GW->>RP: POST /generate (IRA + resultados)
    RP-->>GW: ReportURL

    GW-->>FE: SessionResult {ira, alertas, report_url}
    FE-->>Prof: Dashboard atualizado com IRA e alertas
```

---

## 7. Fluxo de Eventos

```mermaid
flowchart TD
    A[Upload Sessão Clínica] --> B{Tipo de Mídia}
    B -->|Vídeo| C[Video Service]
    B -->|Áudio| D[Audio Service]
    B -->|Documento| E[Document Service]

    C --> C1[Detecção Facial - DeepFace]
    C --> C2[Pose Estimation - MediaPipe]
    C --> C3[Detecção Objetos - YOLOv8]
    C --> C4[Análise Temporal - OpenCV]

    D --> D1[STT - Azure Speech]
    D --> D2[Análise Sentimento - Azure Language]
    D --> D3[NER Clínico]

    E --> E1[OCR - Azure Doc Intelligence]
    E --> E2[Extração Estruturada]
    E --> E3[Validação de Inconsistências]

    C1 & C2 & C3 & C4 --> F[VideoAnalysisResult]
    D1 & D2 & D3 --> G[AudioAnalysisResult]
    E1 & E2 & E3 --> H[DocumentAnalysisResult]

    F & G & H --> I[Risk Service - Correlação IRA]
    I --> J{IRA Score}
    J -->|>= 70| K[🚨 ALERTA CRÍTICO]
    J -->|40-69| L[⚠️ ALERTA MODERADO]
    J -->|< 40| M[✅ BAIXO RISCO]

    I --> N[Report Service]
    N --> O[PDF/Excel Report]
    K & L & M --> P[Dashboard Streamlit]
    O --> P
```

---

## 8. Domain Map

```mermaid
graph LR
    subgraph "Core Platform"
        AUTH[Auth & Identity]
        SESSION[Session Manager]
        ALERT[Alert Engine]
    end

    subgraph "Video Domain"
        VID_INGEST[Video Ingestion]
        VID_FACE[Facial Analysis]
        VID_POSE[Pose Analysis]
        VID_OBJ[Object Detection]
    end

    subgraph "Audio Domain"
        AUD_INGEST[Audio Ingestion]
        AUD_STT[Speech-to-Text]
        AUD_SENT[Sentiment Analysis]
        AUD_NER[Clinical NER]
    end

    subgraph "Document Domain"
        DOC_INGEST[Document Ingestion]
        DOC_OCR[OCR Processing]
        DOC_EXTRACT[Data Extraction]
        DOC_VALID[Validation]
    end

    subgraph "Risk Domain"
        RISK_CORR[Correlation Engine]
        IRA_CALC[IRA Calculator]
        RISK_HIST[Risk History]
    end

    subgraph "Report Domain"
        RPT_GEN[Report Generator]
        RPT_TMPL[Template Engine]
        RPT_STORE[Report Storage]
    end

    subgraph "Dashboard Domain"
        DASH_RT[Real-time View]
        DASH_HIST[Historical View]
        DASH_ALERT[Alert Center]
    end

    AUTH --> SESSION
    SESSION --> VID_INGEST & AUD_INGEST & DOC_INGEST
    VID_INGEST --> VID_FACE & VID_POSE & VID_OBJ
    AUD_INGEST --> AUD_STT --> AUD_SENT & AUD_NER
    DOC_INGEST --> DOC_OCR --> DOC_EXTRACT --> DOC_VALID

    VID_OBJ & AUD_NER & DOC_VALID --> RISK_CORR --> IRA_CALC
    IRA_CALC --> ALERT --> DASH_ALERT
    IRA_CALC --> RPT_GEN --> RPT_STORE --> DASH_HIST
```

---

## 9. Stack Tecnológica

| Camada | Tecnologia | Versão | Propósito |
|---|---|---|---|
| Backend API | FastAPI | 0.110+ | API Gateway e serviços de domínio |
| Frontend | Streamlit | 1.35+ | Dashboard interativo |
| Visão Computacional | OpenCV | 4.9+ | Processamento de frames de vídeo |
| Análise Facial | DeepFace | 0.0.91+ | Detecção de emoções faciais |
| Pose Estimation | MediaPipe | 0.10+ | Análise de postura corporal |
| Detecção Objetos | YOLOv8 | ultralytics 8.x | Detecção de objetos/instrumentos |
| Face Recognition | face_recognition | 1.3+ | Identificação de indivíduos |
| STT | Azure Speech | SDK 1.37+ | Transcrição de fala |
| NLP | Azure AI Language | SDK 1.0+ | Sentimento, NER, key phrases |
| OCR | Azure Doc Intelligence | SDK 1.0+ | Extração documental |
| Storage | Azure Blob Storage | — | Armazenamento de mídias |
| Secrets | Azure Key Vault | — | Gerenciamento de segredos |
| Observabilidade | Azure Monitor | — | Logs, métricas, traces |
| Banco de Dados | PostgreSQL | 16+ | Persistência relacional |
| ORM | SQLAlchemy | 2.0+ | Mapeamento objeto-relacional |
| Migrations | Alembic | 1.13+ | Controle de schema |
| Auth | PyJWT + OAuth2 | — | Autenticação e autorização |
| Containerização | Docker + Compose | — | Deploy local e cloud |
| CI/CD | GitHub Actions | — | Pipeline automatizado |

---

## 10. Decisões Arquiteturais (ADRs)

### ADR-001: Arquitetura de Microsserviços por Domínio
**Decisão:** Cada domínio é um serviço FastAPI independente com seu próprio banco PostgreSQL.  
**Justificativa:** Permite desenvolvimento paralelo sem conflitos, deploy independente e isolamento de falhas.  
**Consequências:** Overhead de infraestrutura, mas ganho em autonomia da equipe.

### ADR-002: Comunicação Síncrona via REST
**Decisão:** Comunicação entre serviços via REST HTTP (v1.0), com possibilidade de migrar para mensageria assíncrona (RabbitMQ/Azure Service Bus) na v2.0.  
**Justificativa:** Simplicidade de implementação para o escopo acadêmico.

### ADR-003: Banco por Domínio
**Decisão:** Cada serviço tem seu próprio banco de dados PostgreSQL (schemas separados na mesma instância para o ambiente de dev).  
**Justificativa:** Isolamento de dados, evita acoplamento via banco compartilhado.

### ADR-004: IRA como Score Composto
**Decisão:** O IRA é calculado pelo Risk Service com base em pesos ponderados das contribuições de vídeo (40%), áudio (35%) e documentos (25%).  
**Justificativa:** Pesos baseados na literatura de detecção de violência obstétrica.
