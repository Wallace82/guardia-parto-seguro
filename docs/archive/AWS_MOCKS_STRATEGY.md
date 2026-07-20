# Estratégia de Mocks para Integração AWS (AWS Domain)

## 1. Contexto Atual
Para não bloquear o desenvolvimento das equipes dependentes (Dev 2 - Áudio/Vídeo, Dev 3 - Documentos, e Frontend), os serviços gerenciados da AWS no módulo `aws-domain` foram **mockados**.

Isso significa que as APIs do `aws-domain` aceitam requisições normalmente e respondem com dados estruturados (no formato esperado pela AWS), mas sem realizar as chamadas reais para a nuvem usando o `boto3`.

## 2. Como os Mocks Estão Configurados
O controle dos mocks é feito através de uma variável (flag) no arquivo de configuração do domínio:
**Arquivo:** `aws-domain/app/core/config.py`
**Flag:** `MOCK_AWS: bool = True`

Quando `MOCK_AWS` está como `True`, os seguintes serviços retornam dados estáticos fictícios, injetando logs descritivos para informar que o mock está ativo.

### 2.1. Amazon Textract (OCR de Prontuários)
- **Arquivo:** `app/services/textract_service.py`
- **Comportamento Real:** Lê um PDF/Imagem do S3 e inicia um Job assíncrono de OCR.
- **Comportamento Mockado:** Retorna um `job_id` fictício (ex: `mock-job-id-textract-12345`). Ao consultar o resultado, retorna um status `SUCCEEDED` instantâneo e um bloco de texto contendo `"RELATÓRIO MÉDICO SIMULADO (MOCK)"` com confiança de 99.9%.

### 2.2. Amazon Transcribe (Transcrição de Áudio)
- **Arquivo:** `app/services/transcribe_service.py`
- **Comportamento Real:** Lê um áudio do S3, processa diarização e retorna uma URI do S3 com o JSON do texto extraído.
- **Comportamento Mockado:** Retorna um `job_name` baseado no nome do arquivo. A consulta de resultado devolve status `COMPLETED` com a URI estática `https://mock-s3-url.com/transcript.json`.

### 2.3. Amazon Comprehend (NLP Médico e Sentimentos)
- **Arquivo:** `app/services/comprehend_service.py`
- **Comportamento Real:** Analisa a string de texto para detectar sentimento (Positivo, Negativo, etc.) e extrai entidades médicas (Comprehend Medical).
- **Comportamento Mockado:**
  - Sentimento: Sempre retorna `"NEUTRAL"`.
  - Entidades Médicas: Retorna uma lista contendo entidades hardcoded (Ex: Hipertensão, Aspirina).

## 3. Guia de Transição para o Ambiente Real

Quando a conta da AWS estiver 100% configurada, com as Roles IAM e Permissions Boundaries ajustadas (especialmente os bloqueios de `s3:PutObject`, `textract:*`, etc.), siga este passo a passo para habilitar a integração real:

### Passo 1: Configurar Credenciais
Garanta que as credenciais da AWS estejam devidamente injetadas via `.env` (no ambiente local) ou através de IAM Task Roles (quando feito o deploy via ECS Fargate).

### Passo 2: Desativar a Flag
No arquivo `aws-domain/app/core/config.py`, altere:
```python
# De:
MOCK_AWS: bool = True

# Para:
MOCK_AWS: bool = False
```
*(Alternativamente, essa flag deve ser mapeada para ler do `.env`, ex: `MOCK_AWS: bool = Field(default=False, env="MOCK_AWS")` no pydantic_settings).*

### Passo 3: Validação das IAM Policies
Certifique-se de que o IAM Role utilizado pelo serviço possua as seguintes permissões básicas para que os serviços não retornem `AccessDenied`:
- `s3:GetObject` e `s3:PutObject` nos buckets de mídia e relatórios.
- `textract:StartDocumentTextDetection` e `textract:GetDocumentTextDetection`.
- `transcribe:StartTranscriptionJob` e `transcribe:GetTranscriptionJob`.
- `comprehend:DetectSentiment` e `comprehendmedical:DetectEntitiesV2`.
