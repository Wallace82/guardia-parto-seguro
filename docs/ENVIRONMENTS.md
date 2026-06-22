# ENVIRONMENTS.md — GuardIA Parto Seguro

> Estratégia de Ambientes e Deploy — v1.0

---

## 1. Visão Geral da Estratégia de Ambientes

O GuardIA Parto Seguro adota uma arquitetura em 4 camadas (Tiers) para garantir a evolução gradual do projeto desde a demonstração acadêmica (MVP Local) até a implantação na nuvem (Produção).

Os ambientes são:
1. **LOCAL (Localhost)**: Desenvolvimento e testes individuais.
2. **DEV (Development)**: Integração contínua e validação da equipe.
3. **HML (Homologação / Staging)**: Validação com usuários finais (médicos, gestores) na AWS.
4. **PRD (Produção)**: Ambiente isolado e seguro na AWS, com SLA e monitoramento crítico.

> **NOTA ARQUITETURAL OFICIAL**: O GuardIA Parto Seguro **NÃO será hospedado inicialmente na nuvem**. A aplicação será executada **localmente (LOCAL/DEV)** durante o desenvolvimento e demonstração acadêmica. Entretanto, ela consumirá serviços gerenciados de Inteligência Artificial da AWS através de APIs.

---

## 2. Detalhamento dos Ambientes

### 2.1 Ambiente LOCAL (MVP / Demonstração)

- **Objetivo**: Desenvolvimento ágil, depuração e a demonstração principal do MVP acadêmico.
- **Hospedagem da Aplicação**: Máquina local do desenvolvedor ou da banca avaliadora.
- **Orquestração**: Docker Compose (`environments/local/docker-compose.yml`).
- **Banco de Dados**: Container PostgreSQL rodando localmente, isolado por schemas.
- **Armazenamento de Mídias (S3)**: Mock local ou S3 bucket de sandbox.
- **Serviços de IA (Visão)**: Executados 100% localmente (OpenCV, YOLOv8, MediaPipe, DeepFace) no container do `video-domain`.
- **Integração AWS**: O `aws-domain` fará requisições para Amazon Transcribe, Textract e Comprehend.
- **Custos**: Apenas o consumo de APIs SaaS AWS.

### 2.2 Ambiente DEV (Integração)

- **Objetivo**: Garantir que as implementações dos múltiplos desenvolvedores funcionam juntas.
- **Hospedagem da Aplicação**: Servidor de testes local (on-premise) ou máquina virtual dedicada.
- **Orquestração**: Docker Compose.
- **CI/CD**: Pipelines de PR disparam testes unitários e lint neste ambiente.
- **Integração AWS**: Idêntico ao LOCAL, mas utilizando keys restritas ao ambiente `DEV`.

### 2.3 Ambiente HML (Homologação na AWS)

- **Objetivo**: Validação com dados "simulados mas realistas" por key-users, pré-produção.
- **Hospedagem da Aplicação**: Nuvem AWS (Amazon ECS Fargate).
- **Banco de Dados**: Amazon RDS para PostgreSQL (Single-AZ para contenção de custos).
- **Armazenamento de Mídias**: Amazon S3 (bucket `hml-guardia-media`).
- **Secret Management**: AWS Secrets Manager.
- **CI/CD**: Deploy automático via GitHub Actions após aprovação do PR para a branch `release`.
- **Custos**: Infraestrutura provisionada na AWS.

### 2.4 Ambiente PRD (Produção na AWS)

- **Objetivo**: Operação real no hospital, processando dados sensíveis de pacientes com rigorosa conformidade LGPD.
- **Hospedagem da Aplicação**: Nuvem AWS (Amazon ECS Fargate com Auto Scaling).
- **Banco de Dados**: Amazon RDS para PostgreSQL (Multi-AZ para alta disponibilidade) e KMS Encryption.
- **Armazenamento de Mídias**: Amazon S3 (bucket `prd-guardia-media` com encriptação AES-256 rotacionada).
- **Observabilidade**: Amazon CloudWatch Logs integrado ao `security-domain` para manter log de auditoria irrefutável.
- **CI/CD**: Deploy rigorosamente manual após aprovação técnica de CISO e Tech Lead, a partir de Git Tags (ex: `v1.0.0`).

---

## 3. Gestão de Variáveis e Segredos

A transição entre ambientes é governada pela injeção de variáveis de ambiente.

- **LOCAL / DEV**: As variáveis residem no arquivo `.env` carregado pelo Docker Compose.
- **HML / PRD**: Arquivos `.env` não são permitidos. Os containers no ECS recebem as variáveis dinamicamente através do **AWS Secrets Manager** ou do parâmetro de task do ECS, provendo uma camada de *Zero Trust*.

---

## 4. Diretórios de Configuração

A estrutura do projeto reflete esta separação:

```text
guardia-parto-seguro/
├── environments/
│   ├── local/          # docker-compose.yml e .env.example
│   ├── dev/            # docker-compose.dev.yml e scripts de mock
│   ├── hml/            # Scripts IaC (Terraform) para ambiente de Homologação AWS
│   └── prd/            # Scripts IaC (Terraform) para ambiente de Produção AWS (Multi-AZ)
```
