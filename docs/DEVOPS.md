# DEVOPS.md — GuardIA Parto Seguro

> CI/CD, Docker, GitHub Actions e Infraestrutura — v2.0

---

## 1. Visão Geral da Infraestrutura

```
GitHub (código) → GitHub Actions (CI/CD) → Amazon ECR → AWS ECS Fargate (HML/PRD)
                                         ↓
                                   Testes + Lint + Segurança
```

A execução no ambiente `LOCAL` e `DEV` se dá integralmente via `docker-compose`.

---

## 2. Docker Compose — Ambiente Local

### `environments/local/docker-compose.yml`

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
      - ../../infra/postgres/init-domains.sql:/docker-entrypoint-initdb.d/01_init.sql
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
      context: ../../backend
      dockerfile: Dockerfile
    container_name: guardia-backend
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      SECRET_KEY: ${SECRET_KEY:-dev_secret_key_change_in_production}
      AWS_REGION: ${AWS_REGION:-us-east-1}
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
      context: ../../security-domain
      dockerfile: Dockerfile
    container_name: guardia-security
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AWS_REGION: ${AWS_REGION:-us-east-1}
      JWT_SECRET: ${JWT_SECRET:-dev_jwt_secret}
    ports:
      - "8006:8006"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ AWS INTEGRATION DOMAIN ============
  aws-service:
    build:
      context: ../../aws-domain
      dockerfile: Dockerfile
    container_name: guardia-aws
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      AWS_REGION: ${AWS_REGION:-us-east-1}
      AWS_S3_BUCKET: ${AWS_S3_BUCKET}
    ports:
      - "8007:8007"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ VIDEO DOMAIN ============
  video-service:
    build:
      context: ../../video-domain
      dockerfile: Dockerfile
    container_name: guardia-video
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AWS_SERVICE_URL: http://aws-service:8007
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
      context: ../../audio-domain
      dockerfile: Dockerfile
    container_name: guardia-audio
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AWS_SERVICE_URL: http://aws-service:8007
    ports:
      - "8002:8002"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ DOCUMENT DOMAIN ============
  document-service:
    build:
      context: ../../document-domain
      dockerfile: Dockerfile
    container_name: guardia-document
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AWS_SERVICE_URL: http://aws-service:8007
    ports:
      - "8003:8003"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ RISK DOMAIN ============
  risk-service:
    build:
      context: ../../risk-domain
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
      context: ../../report-domain
      dockerfile: Dockerfile
    container_name: guardia-report
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-guardia}:${DB_PASSWORD:-guardia_dev_pass}@postgres:5432/${DB_NAME:-guardia_db}
      AWS_SERVICE_URL: http://aws-service:8007
    ports:
      - "8005:8005"
    depends_on:
      postgres:
        condition: service_healthy

  # ============ FRONTEND ============
  frontend:
    build:
      context: ../../frontend
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
        service: [backend, security-domain, aws-domain, video-domain, audio-domain, document-domain, risk-domain, report-domain, frontend]
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
          for service in backend security-domain aws-domain video-domain audio-domain document-domain risk-domain report-domain frontend; do
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
          - name: aws-domain
          - name: security-domain
          - name: video-domain
          - name: audio-domain
          - name: document-domain
          - name: risk-domain
          - name: report-domain
          - name: frontend

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
          docker compose -f environments/local/docker-compose.yml up -d --build
          sleep 30  # aguardar serviços iniciarem

      - name: Run integration tests
        run: |
          pip install pytest httpx
          pytest tests/integration/ -v

      - name: Stop services
        if: always()
        run: docker compose -f environments/local/docker-compose.yml down
```

---

### `.github/workflows/deploy.yml`

```yaml
name: Deploy to AWS ECS

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

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push images
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          for service in backend aws-domain security-domain video-domain audio-domain document-domain risk-domain report-domain frontend; do
            docker build -t $ECR_REGISTRY/guardia-$service:$TAG ./$service/
            docker push $ECR_REGISTRY/guardia-$service:$TAG
          done

      - name: Deploy to Amazon ECS
        run: |
          # Exemplo de update do serviço core backend
          aws ecs update-service --cluster guardia-cluster --service guardia-backend-service --force-new-deployment
```

---

## 5. Variáveis de Ambiente

### `.env.example`

```bash
# ============ BANCO DE DADOS ============
DB_USER=guardia
DB_PASSWORD=guardia_dev_pass
DB_NAME=guardia_db
DB_HOST=postgres
DB_PORT=5432

# ============ CORE API ============
SECRET_KEY=your_secret_key_here_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ============ AWS SERVICES ============
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=guardia-parto-seguro

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
/infrastructure/       @dev1 @cloud-dev
/.github/              @dev1 @cloud-dev

/video-domain/         @dev2
/audio-domain/         @dev2

/document-domain/      @dev3
/risk-domain/          @dev3

/frontend/             @dev4
/report-domain/        @dev4

/aws-domain/           @cloud-dev
/security-domain/      @cloud-dev

/docs/                 @dev1 @dev2 @dev3 @dev4 @cloud-dev
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
