# =====================================================
# GuardIA — Core API (backend)
# Multi-stage Dockerfile: builder + development + production
# =====================================================

# ----------- STAGE: builder -----------
FROM python:3.11-slim AS builder

WORKDIR /build

# Instala dependências de sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python em isolamento
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ----------- STAGE: development -----------
FROM python:3.11-slim AS development

WORKDIR /app

# Instala apenas runtime deps do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia pacotes já instalados do builder
COPY --from=builder /install /usr/local

# Copia código fonte (em dev, o volume override isso — Dockerfile é fallback)
COPY . .

EXPOSE 8000

# Executa as migrações Alembic e inicia o uvicorn com hot-reload em dev
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

# ----------- STAGE: production -----------
FROM python:3.11-slim AS production

# Usuário não-root para segurança
RUN groupadd -r guardia && useradd -r -g guardia guardia

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY --chown=guardia:guardia . .

USER guardia

EXPOSE 8000

# Executa as migrações Alembic e inicia o uvicorn com workers em produção
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
