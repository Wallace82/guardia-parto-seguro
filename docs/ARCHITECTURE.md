# ARCHITECTURE.md — GuardIA Parto Seguro

> Documento de Arquitetura de Software — Versão 2.0  
> Classificação: Acadêmico — FIAP Tech Challenge

---

## 1. Visão Executiva

### 1.1 Business Case

O Brasil registra altos índices de violência obstétrica e mortalidade materna, muitas vezes associados à ausência de sistemas de vigilância assistencial em tempo real. O **GuardIA Parto Seguro** propõe uma plataforma de IA multimodal capaz de processar simultaneamente vídeo, áudio, documentos e histórico clínico, gerando alertas preventivos e relatórios especializados para equipes de saúde, gestores e ouvidorias.

**Impacto esperado:**
- Redução de 40% nos casos não reportados de violência obstétrica
- Detecção precoce de depressão pós-parto em até 72h após o parto
- Auditoria assistencial automatizada com IGA (Índice GuardIA de Atenção)

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
4. Correlacionar múltiplas fontes de dados para calcular o IGA
5. Gerar relatórios e alertas acionáveis para equipes de saúde
6. Fornecer dashboard multimodal em tempo quase real

### 1.4 Escopo

**Dentro do escopo:**
- Análise de vídeo clínico (câmeras de sala de parto e consulta)
- Análise de áudio de consultas (com consentimento)
- Processamento de documentos médicos (prontuários, exames)
- Cálculo do IGA com base em múltiplas fontes
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
| **Testabilidade** | Cobertura mínima de 80% em testes unitários **(Atingido no core-api com pytest)** |
| **Observabilidade** | Logs estruturados **(Implementado com structlog)**, métricas e rastreamento distribuído (Amazon CloudWatch) |
| **Segurança** | Zero-trust, criptografia em repouso (S3 Encryption) e em trânsito (HTTPS/TLS) |
| **Escalabilidade** | Cada serviço escala independentemente via Docker e futuramente ECS Fargate |

---

## 3. Diagrama de Contexto (C4 — Nível 1)

```mermaid
C4Context
    title GuardIA Parto Seguro — Diagrama de Contexto

    Person(profissional, "Profissional de Saúde", "Médico, enfermeiro, parteiro")
    Person(gestor, "Gestor Hospitalar", "Coordenador de qualidade assistencial")
    Person(ouvidor, "Ouvidor / Auditor", "Responsável por auditoria e LGPD")

    System(guardia, "GuardIA Parto Seguro", "Plataforma multimodal Híbrida (Local + Nuvem)")

    System_Ext(aws_transcribe, "Amazon Transcribe", "STT e análise de fala")
    System_Ext(aws_comprehend, "Amazon Comprehend", "NLP, sentimento e entidades")
    System_Ext(aws_textract, "Amazon Textract", "OCR estruturado")
    System_Ext(aws_s3, "Amazon S3", "Armazenamento seguro de mídias")
    System_Ext(aws_sm, "AWS Secrets Manager", "Gestão de segredos e credenciais")
    System_Ext(aws_cw, "Amazon CloudWatch", "Auditoria e observabilidade")

    Rel(profissional, guardia, "Visualiza alertas e relatórios", "HTTPS")
    Rel(gestor, guardia, "Monitora IGA e dashboard", "HTTPS")
    Rel(ouvidor, guardia, "Acessa relatórios de auditoria", "HTTPS")
    Rel(guardia, aws_transcribe, "Transcreve áudios e detecta anomalias", "HTTPS/TLS 1.3")
    Rel(guardia, aws_comprehend, "Analisa sentimentos e extrai entidades", "HTTPS/TLS 1.3")
    Rel(guardia, aws_textract, "Processa documentos médicos", "HTTPS/TLS 1.3")
    Rel(guardia, aws_s3, "Armazena vídeos, áudios e documentos", "HTTPS/TLS 1.3")
    Rel(guardia, aws_sm, "Recupera credenciais dinâmicas", "HTTPS/TLS 1.3")
    Rel(guardia, aws_cw, "Registra logs de auditoria (LGPD)", "HTTPS/TLS 1.3")
```

---

## 4. Diagrama de Contêiner (C4 — Nível 2)

```mermaid
C4Container
    title GuardIA Parto Seguro — Diagrama de Contêiner (MVP Local + AWS)

    Person(user, "Usuário", "Profissional de Saúde / Gestor / Auditor")

    Container(frontend, "Dashboard", "Streamlit", "Interface multimodal de monitoramento")
    Container(gateway, "API Gateway", "FastAPI :8000", "Roteamento e orquestração")
    Container(security_svc, "Security Domain", "FastAPI :8006", "Auth, IAM, Criptografia, Anonimização LGPD")
    Container(aws_svc, "AWS Integration Domain", "FastAPI :8007", "Gateway para serviços AWS (S3, IA, Auditoria)")
    Container(video_svc, "Video Service", "FastAPI :8001", "OpenCV, MediaPipe, DeepFace, YOLOv8")
    Container(audio_svc, "Audio Service", "FastAPI :8002", "Integra com AWS Integration para STT/NLP")
    Container(doc_svc, "Document Service", "FastAPI :8003", "Integra com AWS Integration para OCR")
    Container(risk_svc, "Risk Service", "FastAPI :8004", "Cálculo do IGA")
    Container(report_svc, "Report Service", "FastAPI :8005", "Geração de PDF/Excel")

    ContainerDb(db_core, "Core DB", "PostgreSQL Local / RDS", "Sessões, alertas")
    ContainerDb(db_security, "Security DB", "PostgreSQL Local / RDS", "Usuários, RBAC, AuditLog, Consents")
    ContainerDb(db_cloud, "AWS Domain DB", "PostgreSQL Local / RDS", "AWSProcessingHistory")
    ContainerDb(db_video, "Video DB", "PostgreSQL Local / RDS", "Análises de vídeo")
    ContainerDb(db_audio, "Audio DB", "PostgreSQL Local / RDS", "Transcrições e análises de áudio")
    ContainerDb(db_doc, "Document DB", "PostgreSQL Local / RDS", "Documentos processados")
    ContainerDb(db_risk, "Risk DB", "PostgreSQL Local / RDS", "Histórico de IGA")
    ContainerDb(db_report, "Report DB", "PostgreSQL Local / RDS", "Relatórios gerados")

    Rel(user, frontend, "Acessa via browser", "HTTPS")
    Rel(frontend, gateway, "Chama APIs", "REST/JSON")
    Rel(gateway, security_svc, "Valida Auth/IAM/LGPD", "REST")
    Rel(gateway, aws_svc, "Upload de mídias seguro", "REST")
    Rel(gateway, video_svc, "Delega análise de vídeo (Local)", "REST")
    Rel(gateway, audio_svc, "Delega análise de áudio", "REST")
    Rel(gateway, doc_svc, "Delega análise documental", "REST")
    Rel(gateway, risk_svc, "Solicita cálculo de IGA", "REST")
    Rel(gateway, report_svc, "Solicita geração de relatório", "REST")
    Rel(audio_svc, aws_svc, "Pede transcrição/sentimento", "REST")
    Rel(doc_svc, aws_svc, "Pede extração de texto OCR", "REST")
    
    Rel(security_svc, db_security, "Lê/Escreve", "SQL")
    Rel(aws_svc, db_cloud, "Lê/Escreve", "SQL")
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
        Component(auth, "Auth Module", "JWT", "Autenticação e autorização")
        Component(router, "Domain Router", "FastAPI Router", "Roteia requisições para os domínios")
        Component(orchestrator, "Orchestrator", "Python", "Coordena fluxos multimodais")
        Component(alert_engine, "Alert Engine", "Python", "Dispara alertas com base em thresholds")
        Component(audit_log, "Audit Logger", "Python + Amazon CloudWatch", "Log imutável de auditoria")
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

    GW->>RP: POST /generate (IGA + resultados)
    RP-->>GW: ReportURL

    GW-->>FE: SessionResult {ira, alertas, report_url}
    FE-->>Prof: Dashboard atualizado com IGA e alertas
```

---

## 7. Fluxo de Eventos

```mermaid
flowchart TD
    A[Upload Sessão Clínica] --> SEC{Security & LGPD Check}
    SEC -->|Token Inválido / Sem Consentimento| REJ[Rejeita Requisição]
    SEC -->|OK| C_STORE[AWS Integration: Store in Amazon S3]
    
    C_STORE --> B{Tipo de Mídia}
    B -->|Vídeo| C[Video Service - Local Processing]
    B -->|Áudio| D[Audio Service]
    B -->|Documento| E[Document Service]

    C --> C1[Detecção Facial - DeepFace]
    C --> C2[Pose Estimation - MediaPipe]
    C --> C3[Detecção Objetos - YOLOv8]
    C --> C4[Análise Temporal - OpenCV]

    D --> D_CLOUD[AWS Integration Domain]
    D_CLOUD --> D1[STT - Amazon Transcribe]
    D_CLOUD --> D2[Análise Sentimento - Amazon Comprehend]
    D_CLOUD --> D3[NER Clínico]

    E --> E_CLOUD[AWS Integration Domain]
    E_CLOUD --> E1[OCR - Amazon Textract]
    E --> E2[Extração Estruturada]
    E --> E3[Validação de Inconsistências]

    C1 & C2 & C3 & C4 --> F[VideoAnalysisResult]
    D1 & D2 & D3 --> G[AudioAnalysisResult]
    E1 & E2 & E3 --> H[DocumentAnalysisResult]

    F & G & H --> I[Risk Service - Correlação IGA]
    I --> J{IGA Score}
    J -->|>= 70| K[🚨 ALERTA CRÍTICO]
    J -->|40-69| L[⚠️ ALERTA MODERADO]
    J -->|< 40| M[✅ BAIXO RISCO]

    I --> N[Report Service]
    N --> O[PDF/Excel Report]
    K & L & M --> P[Dashboard Streamlit]
    O --> P
    
    K & L & M & O --> AUDIT[Security Domain - Registra no Amazon CloudWatch]
```

---

## 8. Domain Map

```mermaid
graph LR
    subgraph "Security Domain"
    direction TB
        SEC_AUTH[Auth & IAM]
        SEC_RBAC[RBAC Control]
        SEC_LGPD[Anonymization & LGPD]
        SEC_AUDIT[Audit Logger]
    end

    subgraph "Core Platform"
    direction TB
        SESSION[Session Manager]
        ALERT[Alert Engine]
    end
    
    subgraph "AWS Integration Domain"
    direction TB
        CLOUD_STORE[Amazon S3 Gateway]
        CLOUD_AI[AWS AI Services Gateway]
        CLOUD_MON[Amazon CloudWatch Gateway]
        CLOUD_SEC[AWS Secrets Manager]
    end

    subgraph "Video Domain (Local)"
    direction TB
        VID_INGEST[Video Ingestion]
        VID_FACE[Facial Analysis]
        VID_POSE[Pose Analysis]
        VID_OBJ[Object Detection]
    end

    subgraph "Audio Domain"
    direction TB
        AUD_INGEST[Audio Ingestion]
        AUD_SENT[Sentiment Processing]
        AUD_NER[NER Processing]
    end

    subgraph "Document Domain"
    direction TB
        DOC_INGEST[Document Ingestion]
        DOC_EXTRACT[Data Extraction]
        DOC_VALID[Validation]
    end

    subgraph "Risk Domain"
    direction TB
        RISK_CORR[Correlation Engine]
        IRA_CALC[IGA Calculator]
        RISK_HIST[Risk History]
    end

    subgraph "Report Domain"
    direction TB
        RPT_GEN[Report Generator]
        RPT_TMPL[Template Engine]
    end

    subgraph "Dashboard Domain"
    direction TB
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
| STT | Amazon Transcribe | SDK boto3 | Transcrição de fala |
| NLP | Amazon Comprehend | SDK boto3 | Sentimento, NER, key phrases |
| OCR | Amazon Textract | SDK boto3 | Extração documental |
| Storage | Amazon S3 | SDK boto3 | Armazenamento de mídias |
| Secrets | AWS Secrets Manager | SDK boto3 | Gerenciamento de segredos e credenciais |
| Observabilidade | Amazon CloudWatch | SDK boto3 | Logs, métricas, traces para auditoria |
| Banco de Dados | PostgreSQL | 16+ | Persistência relacional |
| ORM | SQLAlchemy | 2.0+ | Mapeamento objeto-relacional |
| Migrations | Alembic | 1.13+ | Controle de schema |
| Auth | PyJWT + IAM | — | Autenticação e controle de acesso |
| Containerização | Docker + Compose | — | Execução local |
| Deploy (HML/PRD) | ECS Fargate | — | Orquestração Serverless na nuvem |

---

## 10. Decisões Arquiteturais (ADRs)

### ADR-001: Arquitetura de Microsserviços por Domínio
**Decisão:** Cada domínio é um serviço FastAPI independente com seu próprio banco PostgreSQL.  
**Justificativa:** Permite desenvolvimento paralelo sem conflitos, deploy independente e isolamento de falhas.  
**Consequências:** Overhead de infraestrutura, mas ganho em autonomia da equipe.

### ADR-002: Estratégia de Ambientes (LOCAL, DEV, HML, PRD) e MVP Local + AWS
**Decisão:** O projeto adota uma estratégia evolutiva de 4 ambientes:
- **LOCAL**: Execução 100% local (FastAPI, Postgres, IA Visual) consumindo serviços reais da AWS (Transcribe, Comprehend, Textract) via API, sem deploy na nuvem.
- **DEV**: Similar ao LOCAL, mas focada na integração da equipe (banco compartilhado opcional e testes integrados).
- **HML (Homologação)**: Primeiro deploy na nuvem (EC2/ECS, RDS PostgreSQL, CloudWatch).
- **PRD (Produção)**: Arquitetura alvo totalmente nuvem (ECS Fargate, Amazon RDS, S3).
O MVP será desenvolvido com foco nos ambientes LOCAL e DEV para agilidade e controle de custos no contexto acadêmico.
**Justificativa:** Essa progressão permite foco no MVP funcional e IA avançada antes da sobrecarga de infraestrutura complexa na nuvem.
**Consequências:** Inicialmente a execução será local, utilizando credenciais da AWS via `~/.aws/credentials` ou `.env`.

### ADR-003: Segurança por Design e Conformidade LGPD
**Decisão:** Centralizar segurança no `Security Domain`, implementando mascaramento de dados pessoais (anonimização) em bancos e logs, S3 Encryption (AES-256) para dados em repouso e HTTPS/TLS 1.3 em trânsito. Nenhuma credencial será exposta; o `AWS Integration Domain` fará uso do AWS Secrets Manager e as políticas seguirão o IAM.
**Justificativa:** Vídeos, áudios e prontuários são classificados como dados pessoais sensíveis pela LGPD, requerendo proteção máxima.
**Consequências:** Complexidade adicional na gestão de acesso, exigindo criptografia antes da persistência e decriptação para exibição baseada em RBAC.

### ADR-004: Comunicação Síncrona via REST
**Decisão:** Comunicação entre serviços via REST HTTPS (v1.0), com possibilidade de migrar para mensageria assíncrona (RabbitMQ/Amazon SQS) na v2.0.  
**Justificativa:** Simplicidade de implementação para o escopo inicial.

### ADR-005: Banco por Domínio
**Decisão:** Cada serviço tem seu próprio banco de dados PostgreSQL (schemas separados na mesma instância para o ambiente de dev local, instâncias RDS dedicadas no alvo).  
**Justificativa:** Isolamento de dados, evita acoplamento via banco compartilhado.

### ADR-006: IGA como Score Composto
**Decisão:** O IGA é calculado pelo Risk Service com base em pesos ponderados das contribuições de vídeo (40%), áudio (35%) e documentos (25%).  
**Justificativa:** Pesos baseados na literatura de detecção de violência obstétrica.

### ADR-007: Gerenciamento de Segredos (AWS Secrets Manager vs .env)
**Decisão:** O MVP e ambiente de desenvolvimento local (LOCAL/DEV) farão a injeção de segredos estritamente utilizando arquivos `.env`. O uso do AWS Secrets Manager será prorrogado e exigido apenas para ambientes gerenciados (HML e PRD).
**Justificativa:** Reduzir os custos recorrentes na AWS. O Secrets Manager cobra por segredo persistido mensalmente além de custo por requisições na API. Para um projeto acadêmico o balanço custo vs benefício não justifica usá-lo ativamente em Dev.
**Consequências:** O código IaC (Terraform) para os segredos existe mas está comentado ("documentado") na base até o momento do deploy em HML. Os desenvolvedores devem garantir que o `.env` jamais seja "commitado" no Git.
