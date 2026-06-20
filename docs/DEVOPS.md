# DEVOPS.md — GuardIA Parto Seguro

> CI/CD, Docker, GitHub Actions e Infraestrutura — v1.0

---

## 1. Visão Geral da Infraestrutura

```
GitHub (código) → GitHub Actions (CI/CD) → Docker Hub/ACR → Azure Container Apps (produção)
                                         ↓
                                   Testes + Lint + Segurança
```

---

## 2. Docker Compose — Ambiente Local

### `devops/docker-compose.yml`

```yaml
version: "3.9"

services:
  # ============ BANCO DE DADOS ============
  postgres:
    image: postgres:16-alpine
    container_name: guardia-postgres
    environment:
      POSTGRES_USER: ${DB_USER:-guardia}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-guardia_dev_pass}
      POSTGRES_DB: ${DB_NAME:-guardia_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_schemas.sql:/docker-entrypoint-initdb.d/01_init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U guardia"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ============ CORE PLATFORM ============
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: guardia-backend
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      SECRET_KEY: ${SECRET_KEY:-dev_secret_key_change_in_production}
      AZURE_KEY_VAULT_URL: ${AZURE_KEY_VAULT_URL}
      VIDEO_SERVICE_URL: http://video-service:8001
      AUDIO_SERVICE_URL: http://audio-service:8002
      DOCUMENT_SERVICE_URL: http://document-service:8003
      RISK_SERVICE_URL: http://risk-service:8004
      REPORT_SERVICE_URL: http://report-service:8005
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  # ============ SECURITY DOMAIN ============
  security-service:
    build:
      context: ../security-domain
      dockerfile: Dockerfile
    container_name: guardia-security
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AZURE_KEY_VAULT_URL: ${AZURE_KEY_VAULT_URL}
      JWT_SECRET: ${JWT_SECRET:-dev_jwt_secret}
    ports:
      - "8006:8006"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ CLOUD INTEGRATION DOMAIN ============
  cloud-service:
    build:
      context: ../cloud-domain
      dockerfile: Dockerfile
    container_name: guardia-cloud
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AZURE_BLOB_CONNECTION_STRING: ${AZURE_BLOB_CONNECTION_STRING}
      AZURE_SPEECH_KEY: ${AZURE_SPEECH_KEY}
      AZURE_LANGUAGE_KEY: ${AZURE_LANGUAGE_KEY}
      AZURE_DOC_INTELLIGENCE_KEY: ${AZURE_DOC_INTELLIGENCE_KEY}
    ports:
      - "8007:8007"
    depends_on:
      postgres:
        condition: service_healthy
  # ============ VIDEO DOMAIN ============
  video-service:
    build:
      context: ../video-domain
      dockerfile: Dockerfile
    container_name: guardia-video
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AZURE_BLOB_CONNECTION_STRING: ${AZURE_BLOB_CONNECTION_STRING}
    ports:
      - "8001:8001"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - video_tmp:/tmp/video_processing
    deploy:
      resources:
        limits:
          memory: 4G

  # ============ AUDIO DOMAIN ============
  audio-service:
    build:
      context: ../audio-domain
      dockerfile: Dockerfile
    container_name: guardia-audio
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      CLOUD_SERVICE_URL: http://cloud-service:8007
    ports:
      - "8002:8002"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ DOCUMENT DOMAIN ============
  document-service:
    build:
      context: ../document-domain
      dockerfile: Dockerfile
    container_name: guardia-document
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      CLOUD_SERVICE_URL: http://cloud-service:8007
    ports:
      - "8003:8003"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ RISK DOMAIN ============
  risk-service:
    build:
      context: ../risk-domain
      dockerfile: Dockerfile
    container_name: guardia-risk
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
    ports:
      - "8004:8004"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ REPORT DOMAIN ============
  report-service:
    build:
      context: ../report-domain
      dockerfile: Dockerfile
    container_name: guardia-report
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AZURE_BLOB_CONNECTION_STRING: ${AZURE_BLOB_CONNECTION_STRING}
    ports:
      - "8005:8005"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ FRONTEND ============
  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    container_name: guardia-frontend
    environment:
      API_BASE_URL: http://backend:8000
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  postgres_data:
  video_tmp:
```

---

## 3. Dockerfiles Padrão

### Backend / Serviços FastAPI

```dockerfile
# ============ STAGE 1: Builder ============
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============ STAGE 2: Runtime ============
FROM python:3.11-slim AS runtime

# Usuário não-root para segurança
RUN groupadd -r guardia && useradd -r -g guardia guardia

WORKDIR /app

# Copiar dependências do builder
COPY --from=builder /root/.local /home/guardia/.local
COPY --chown=guardia:guardia . .

USER guardia

ENV PATH=/home/guardia/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Streamlit

```dockerfile
FROM python:3.11-slim AS runtime

RUN groupadd -r guardia && useradd -r -g guardia guardia
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=guardia:guardia . .
USER guardia

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

---

## 4. GitHub Actions — Pipeline CI/CD

### `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"

jobs:
  # ============================================================
  # JOB 1: LINT
  # ============================================================
  lint:
    name: "🔍 Lint & Format Check"
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [backend, security-domain, cloud-domain, video-domain, audio-domain, document-domain, risk-domain, report-domain, frontend]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: "pip"
          cache-dependency-path: ${{ matrix.service }}/requirements.txt

      - name: Install lint tools
        run: pip install ruff black

      - name: Run ruff (linting)
        run: ruff check ${{ matrix.service }}/

      - name: Run black (formatting)
        run: black --check ${{ matrix.service }}/

  # ============================================================
  # JOB 2: TESTES UNITÁRIOS
  # ============================================================
  test:
    name: "🧪 Unit Tests"
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        service: [backend, video-domain, audio-domain, document-domain, risk-domain, report-domain]
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: guardia_test
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: guardia_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: "pip"
          cache-dependency-path: ${{ matrix.service }}/requirements.txt

      - name: Install dependencies
        run: |
          cd ${{ matrix.service }}
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql+asyncpg://guardia_test:test_pass@localhost:5432/guardia_test
          SECRET_KEY: test_secret_key
          TESTING: "true"
        run: |
          cd ${{ matrix.service }}
          pytest tests/ \
            --cov=app \
            --cov-report=xml \
            --cov-fail-under=80 \
            -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ${{ matrix.service }}/coverage.xml
          flags: ${{ matrix.service }}

  # ============================================================
  # JOB 3: SEGURANÇA (SAST)
  # ============================================================
  security:
    name: "🔒 Security Scan"
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install security tools
        run: pip install bandit safety

      - name: Run Bandit (SAST)
        run: |
          bandit -r backend/ video-domain/ audio-domain/ document-domain/ risk-domain/ report-domain/ frontend/ \
            -ll \
            --format json \
            --output bandit-report.json || true
          cat bandit-report.json

      - name: Check dependencies for known vulnerabilities
        run: |
          for service in backend security-domain cloud-domain video-domain audio-domain document-domain risk-domain report-domain frontend; do
            echo "Checking $service..."
            safety check -r $service/requirements.txt || true
          done

      - name: Run TruffleHog (Secret Scanning)
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --debug --only-verified

      - name: Upload Bandit report
        uses: actions/upload-artifact@v4
        with:
          name: bandit-report
          path: bandit-report.json

  # ============================================================
  # JOB 4: BUILD DOCKER
  # ============================================================
  build:
    name: "🐳 Docker Build"
    runs-on: ubuntu-latest
    needs: [test, security]
    strategy:
      matrix:
        service:
          - name: backend
            port: 8000
          - name: video-domain
            port: 8001
          - name: audio-domain
            port: 8002
          - name: document-domain
            port: 8003
          - name: risk-domain
            port: 8004
          - name: report-domain
            port: 8005
          - name: frontend
            port: 8501

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./${{ matrix.service.name }}
          push: false
          tags: guardia/${{ matrix.service.name }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ============================================================
  # JOB 5: INTEGRATION TEST (apenas PR → main)
  # ============================================================
  integration:
    name: "🔗 Integration Test"
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - name: Start services with Docker Compose
        run: |
          cp .env.example .env
          docker compose -f devops/docker-compose.yml up -d --build
          sleep 30  # aguardar serviços iniciarem

      - name: Run integration tests
        run: |
          pip install pytest httpx
          pytest tests/integration/ -v

      - name: Stop services
        if: always()
        run: docker compose -f devops/docker-compose.yml down
```

---

### `.github/workflows/deploy.yml`

```yaml
name: Deploy to Azure

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  deploy:
    name: "🚀 Deploy Production"
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Login to Azure Container Registry
        run: |
          az acr login --name ${{ secrets.ACR_NAME }}

      - name: Build and push images
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          for service in backend video-domain audio-domain document-domain risk-domain report-domain frontend; do
            docker build -t ${{ secrets.ACR_NAME }}.azurecr.io/guardia/$service:$TAG ./$service/
            docker push ${{ secrets.ACR_NAME }}.azurecr.io/guardia/$service:$TAG
          done

      - name: Deploy to Azure Container Apps
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          az containerapp update \
            --name guardia-backend \
            --resource-group ${{ secrets.AZURE_RG }} \
            --image ${{ secrets.ACR_NAME }}.azurecr.io/guardia/backend:$TAG
```

---

## 5. Variáveis de Ambiente

### `.env.example`

```bash
# ============ BANCO DE DADOS ============
DB_USER=guardia
DB_PASSWORD=guardia_dev_pass
DB_NAME=guardia_db
DB_HOST=localhost
DB_PORT=5432

# ============ CORE API ============
SECRET_KEY=your_secret_key_here_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ============ AZURE SERVICES ============
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
AZURE_BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_BLOB_CONTAINER_MEDIA=guardia-media
AZURE_BLOB_CONTAINER_REPORTS=guardia-reports

# Azure Speech
AZURE_SPEECH_KEY=your_speech_key
AZURE_SPEECH_REGION=brazilsouth

# Azure AI Language
AZURE_LANGUAGE_ENDPOINT=https://your-language.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=your_language_key

# Azure Document Intelligence
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-doc-intelligence.cognitiveservices.azure.com/
AZURE_DOC_INTELLIGENCE_KEY=your_doc_key

# ============ NOTIFICAÇÕES ============
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@guardia.health
SMTP_PASSWORD=your_smtp_password
ALERT_EMAIL_GESTOR=gestor@hospital.com

# ============ AMBIENTE ============
ENVIRONMENT=development  # development | staging | production
LOG_LEVEL=INFO
```

---

## 6. CODEOWNERS

### `.github/CODEOWNERS`

```
# Responsáveis por domínio
/backend/              @dev1
/devops/               @dev1
/.github/              @dev1

/video-domain/         @dev2
/audio-domain/         @dev2

/document-domain/      @dev3
/risk-domain/          @dev3

/frontend/             @dev4
/report-domain/        @dev4

/docs/                 @dev1 @dev2 @dev3 @dev4
```

---

## 7. Pull Request Template

### `.github/pull_request_template.md`

```markdown
## 📋 Descrição
Descreva brevemente o que este PR faz.

## 🔗 Issue relacionada
Fecha #(número)

## 🧪 Tipo de mudança
- [ ] Nova funcionalidade
- [ ] Correção de bug
- [ ] Refactoring
- [ ] Documentação
- [ ] CI/CD / Infraestrutura

## ✅ Checklist
- [ ] Código segue os padrões do projeto (ruff + black)
- [x] Testes adicionados/atualizados (cobertura ≥ 80%)
- [ ] Documentação atualizada (se necessário)
- [ ] Nenhum segredo ou credencial no código
- [ ] Dockerfile atualizado (se necessário)
- [ ] API_SPEC.md atualizado (se nova API)

## 🧪 Como testar
Descreva os passos para testar manualmente.

## 📸 Screenshots (se houver mudança de UI)
```
