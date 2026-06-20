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
    Person(ouvidor, "Ouvidor / Auditor", "Responsável por auditoria e LGPD")

    System(guardia, "GuardIA Parto Seguro", "Plataforma multimodal Híbrida (Local + Nuvem)")

    System_Ext(azure_speech, "Azure Speech", "STT e análise de fala")
    System_Ext(azure_lang, "Azure AI Language", "NLP, sentimento e entidades")
    System_Ext(azure_doc, "Azure Document Intelligence", "OCR estruturado")
    System_Ext(azure_blob, "Azure Blob Storage", "Armazenamento seguro de mídias")
    System_Ext(azure_kv, "Azure Key Vault", "Gestão de segredos e chaves")
    System_Ext(azure_monitor, "Azure Monitor", "Auditoria e observabilidade")

    Rel(profissional, guardia, "Visualiza alertas e relatórios", "HTTPS")
    Rel(gestor, guardia, "Monitora IRA e dashboard", "HTTPS")
    Rel(ouvidor, guardia, "Acessa relatórios de auditoria", "HTTPS")
    Rel(guardia, azure_speech, "Transcreve áudios e detecta anomalias", "HTTPS/TLS 1.3")
    Rel(guardia, azure_lang, "Analisa sentimentos e extrai entidades", "HTTPS/TLS 1.3")
    Rel(guardia, azure_doc, "Processa documentos médicos", "HTTPS/TLS 1.3")
    Rel(guardia, azure_blob, "Armazena vídeos, áudios e documentos", "HTTPS/TLS 1.3")
    Rel(guardia, azure_kv, "Recupera credenciais dinâmicas", "HTTPS/TLS 1.3")
    Rel(guardia, azure_monitor, "Registra logs de auditoria (LGPD)", "HTTPS/TLS 1.3")
```

---

## 4. Diagrama de Contêiner (C4 — Nível 2)

```mermaid
C4Container
    title GuardIA Parto Seguro — Diagrama de Contêiner

    Person(user, "Usuário", "Profissional de Saúde / Gestor / Auditor")

    Container(frontend, "Dashboard", "Streamlit", "Interface multimodal de monitoramento")
    Container(gateway, "API Gateway", "FastAPI :8000", "Roteamento e orquestração")
    Container(security_svc, "Security Domain", "FastAPI :8006", "Auth, RBAC, Criptografia, Anonimização LGPD")
    Container(cloud_svc, "Cloud Integration", "FastAPI :8007", "Gateway para serviços Azure, Blob, e Auditoria")
    Container(video_svc, "Video Service", "FastAPI :8001", "OpenCV, MediaPipe, DeepFace, YOLOv8")
    Container(audio_svc, "Audio Service", "FastAPI :8002", "Integra com Cloud Integration para STT/NLP")
    Container(doc_svc, "Document Service", "FastAPI :8003", "Integra com Cloud Integration para OCR")
    Container(risk_svc, "Risk Service", "FastAPI :8004", "Cálculo do IRA")
    Container(report_svc, "Report Service", "FastAPI :8005", "Geração de PDF/Excel")

    ContainerDb(db_core, "Core DB", "PostgreSQL", "Sessões, alertas")
    ContainerDb(db_security, "Security DB", "PostgreSQL", "Usuários, RBAC, AuditLog, Consents")
    ContainerDb(db_cloud, "Cloud DB", "PostgreSQL", "CloudProcessingHistory")
    ContainerDb(db_video, "Video DB", "PostgreSQL", "Análises de vídeo")
    ContainerDb(db_audio, "Audio DB", "PostgreSQL", "Transcrições e análises de áudio")
    ContainerDb(db_doc, "Document DB", "PostgreSQL", "Documentos processados")
    ContainerDb(db_risk, "Risk DB", "PostgreSQL", "Histórico de IRA")
    ContainerDb(db_report, "Report DB", "PostgreSQL", "Relatórios gerados")

    Rel(user, frontend, "Acessa via browser", "HTTPS")
    Rel(frontend, gateway, "Chama APIs", "REST/JSON")
    Rel(gateway, security_svc, "Valida Auth/RBAC/LGPD", "REST")
    Rel(gateway, cloud_svc, "Upload de mídias seguro", "REST")
    Rel(gateway, video_svc, "Delega análise de vídeo (Local)", "REST")
    Rel(gateway, audio_svc, "Delega análise de áudio", "REST")
    Rel(gateway, doc_svc, "Delega análise documental", "REST")
    Rel(gateway, risk_svc, "Solicita cálculo de IRA", "REST")
    Rel(gateway, report_svc, "Solicita geração de relatório", "REST")
    Rel(audio_svc, cloud_svc, "Pede transcrição/sentimento", "REST")
    Rel(doc_svc, cloud_svc, "Pede extração de texto OCR", "REST")
    
    Rel(security_svc, db_security, "Lê/Escreve", "SQL")
    Rel(cloud_svc, db_cloud, "Lê/Escreve", "SQL")
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
    A[Upload Sessão Clínica] --> SEC{Security & LGPD Check}
    SEC -->|Token Inválido / Sem Consentimento| REJ[Rejeita Requisição]
    SEC -->|OK| C_STORE[Cloud Integration: Store in Azure Blob]
    
    C_STORE --> B{Tipo de Mídia}
    B -->|Vídeo| C[Video Service - Local Processing]
    B -->|Áudio| D[Audio Service]
    B -->|Documento| E[Document Service]

    C --> C1[Detecção Facial - DeepFace]
    C --> C2[Pose Estimation - MediaPipe]
    C --> C3[Detecção Objetos - YOLOv8]
    C --> C4[Análise Temporal - OpenCV]

    D --> D_CLOUD[Cloud Integration Domain]
    D_CLOUD --> D1[STT - Azure Speech]
    D_CLOUD --> D2[Análise Sentimento - Azure Language]
    D_CLOUD --> D3[NER Clínico]

    E --> E_CLOUD[Cloud Integration Domain]
    E_CLOUD --> E1[OCR - Azure Doc Intelligence]
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
    
    K & L & M & O --> AUDIT[Security Domain - Registra no Azure Monitor]
```

---

## 8. Domain Map

```mermaid
graph LR
    subgraph "Security Domain"
        SEC_AUTH[Auth & Identity]
        SEC_RBAC[RBAC Control]
        SEC_LGPD[Anonymization & LGPD]
        SEC_AUDIT[Audit Logger]
    end

    subgraph "Core Platform"
        SESSION[Session Manager]
        ALERT[Alert Engine]
    end
    
    subgraph "Cloud Integration Domain"
        CLOUD_STORE[Azure Blob Gateway]
        CLOUD_AI[Azure AI Services Gateway]
        CLOUD_MON[Azure Monitor Gateway]
    end

    subgraph "Video Domain (Local)"
        VID_INGEST[Video Ingestion]
        VID_FACE[Facial Analysis]
        VID_POSE[Pose Analysis]
        VID_OBJ[Object Detection]
    end

    subgraph "Audio Domain"
        AUD_INGEST[Audio Ingestion]
        AUD_SENT[Sentiment Processing]
        AUD_NER[NER Processing]
    end

    subgraph "Document Domain"
        DOC_INGEST[Document Ingestion]
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
    end

    subgraph "Dashboard Domain"
        DASH_RT[Real-time View]
        DASH_HIST[Historical View]
    end

    SEC_AUTH --> SESSION
    SESSION --> CLOUD_STORE
    CLOUD_STORE --> VID_INGEST & AUD_INGEST & DOC_INGEST
    
    VID_INGEST --> VID_FACE & VID_POSE & VID_OBJ
    AUD_INGEST --> CLOUD_AI
    DOC_INGEST --> CLOUD_AI
    
    CLOUD_AI --> AUD_SENT & AUD_NER & DOC_EXTRACT
    DOC_EXTRACT --> DOC_VALID

    VID_OBJ & AUD_NER & DOC_VALID --> RISK_CORR --> IRA_CALC
    IRA_CALC --> ALERT --> DASH_RT
    IRA_CALC --> RPT_GEN --> DASH_HIST
    
    ALERT & RPT_GEN --> SEC_AUDIT --> CLOUD_MON
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
| Containerização | Docker + Compose | — | Execução e testes estritamente locais |

---

## 10. Decisões Arquiteturais (ADRs)

### ADR-001: Arquitetura de Microsserviços por Domínio
**Decisão:** Cada domínio é um serviço FastAPI independente com seu próprio banco PostgreSQL.  
**Justificativa:** Permite desenvolvimento paralelo sem conflitos, deploy independente e isolamento de falhas.  
**Consequências:** Overhead de infraestrutura, mas ganho em autonomia da equipe.

### ADR-002: Arquitetura Híbrida (Local + Cloud)
**Decisão:** O processamento de Visão Computacional (Vídeo) será executado integralmente de forma local (Opção A) utilizando OpenCV, DeepFace, MediaPipe, e YOLOv8. Já os processamentos de Áudio, Linguagem Natural e OCR de Documentos serão delegados aos serviços gerenciados na nuvem (Azure Speech, Azure AI Language, Azure Document Intelligence). O projeto será executado exclusivamente de forma local via Docker, sem CI/CD no GitHub.
**Justificativa:** O projeto deve cumprir o requisito de integrar serviços em nuvem gerenciados com segurança. Usaremos a Azure para os serviços cognitivos complexos de linguagem e documentos, enquanto a visão computacional (que exige latência muito baixa e alta vazão de dados) rodará localmente. A execução apenas local é suficiente para fins de demonstração do Tech Challenge.
**Consequências:** O setup inicial requer a injeção manual das chaves da Azure no `.env` e a infraestrutura não necessitará de pipelines de esteira automatizados.

### ADR-003: Segurança por Design e Conformidade LGPD
**Decisão:** Centralizar segurança no `Security Domain`, implementando mascaramento de dados pessoais (anonimização) em bancos e logs, AES-256 para dados em repouso e TLS 1.3 em trânsito. Nenhuma credencial será exposta; o `Cloud Domain` integrará com o Azure Key Vault.
**Justificativa:** Vídeos, áudios e prontuários são classificados como dados pessoais sensíveis pela LGPD, requerendo proteção máxima.
**Consequências:** Complexidade adicional na gestão de acesso, exigindo criptografia antes da persistência e decriptação para exibição baseada em RBAC (Role-Based Access Control).

### ADR-004: Comunicação Síncrona via REST
**Decisão:** Comunicação entre serviços via REST HTTPS (v1.0), com possibilidade de migrar para mensageria assíncrona (RabbitMQ/Azure Service Bus) na v2.0.  
**Justificativa:** Simplicidade de implementação para o escopo acadêmico.

### ADR-005: Banco por Domínio
**Decisão:** Cada serviço tem seu próprio banco de dados PostgreSQL (schemas separados na mesma instância para o ambiente de dev).  
**Justificativa:** Isolamento de dados, evita acoplamento via banco compartilhado.

### ADR-006: IRA como Score Composto
**Decisão:** O IRA é calculado pelo Risk Service com base em pesos ponderados das contribuições de vídeo (40%), áudio (35%) e documentos (25%).  
**Justificativa:** Pesos baseados na literatura de detecção de violência obstétrica.
