# =====================================================
# GuardIA — Video Domain Service
# Nota: modelos de visão computacional (DeepFace, YOLOv8,
# MediaPipe) aumentam significativamente o tamanho da imagem.
# =====================================================

FROM python:3.11-slim AS builder

WORKDIR /build

# Dependências de sistema para OpenCV, dlib e face_recognition
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libpq-dev \
    libopencv-dev \
    libboost-python-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ----------- development -----------
FROM python:3.11-slim AS development

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# ----------- production -----------
FROM python:3.11-slim AS production

RUN groupadd -r guardia && useradd -r -g guardia guardia

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY --chown=guardia:guardia . .

USER guardia

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
