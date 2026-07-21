# Modelos de Inteligência Artificial (GuardIA Parto Seguro)

O projeto GuardIA utiliza uma combinação de visão computacional, processamento de linguagem natural (NLP) e aprendizado de máquina para analisar o estado clínico, emocional e postural de pacientes em trabalho de parto.

## 1. Visão Computacional (Video Domain)

O microsserviço `video-domain` processa frames dos vídeos carregados para gerar os scores. 
O processamento é feito usando **OpenCV** para leitura e manipulação de frames e salva um vídeo resultante (anotado) via `ffmpeg`.

### 1.1 DeepFace (Análise Facial e Emocional)
- **Finalidade:** Detectar faces nos frames do vídeo e inferir a emoção dominante.
- **Entrada:** Frames de vídeo extraídos (RGB Array).
- **Saída:** Região da face (`x, y, w, h`) e o espectro de emoções, extraindo a dominante (`angry`, `fear`, `sad`, `happy`, etc).
- **Fluxo:** O `processor.py` utiliza o modelo em intervalos amostrados (ex: 1 frame/segundo) para evitar sobrecarga. Quando picos de dor/medo (`fear`, `sad`, `angry`) com alta confiança são detectados, um alerta (Key Finding) é gerado para a timeline. O score de emoção final foca na **média do top 10% dos frames mais negativos** para não diluir picos críticos.
- **Limitações:** A detecção falha caso o rosto da paciente esteja oculto ou em ângulos extremos.

### 1.2 MediaPipe Pose (Linguagem Corporal)
- **Finalidade:** Identificar a postura e presença corporal do paciente.
- **Entrada:** Frames de vídeo.
- **Saída:** Coordenadas (landmarks) ósseas/posturais.
- **Fluxo:** É utilizado para avaliar a mobilidade. Uma proporção baixa de visibilidade (paciente imóvel ou oculta) gera um score mais alto de risco (imobilidade pode indicar gravidade).

*Nota sobre o YOLO:* Embora o `docker-compose.yml` mencione a variável `YOLO_CONFIDENCE_THRESHOLD`, a implementação atual em `processor.py` baseia-se no DeepFace e MediaPipe. A integração com YOLO (para detecção de objetos de risco como sangue ou instrumentos cirúrgicos soltos) está prevista no Roadmap.

## 2. Processamento de Áudio (Audio Domain)

O `audio-domain` extrai diálogos e sinais acústicos.

### 2.1 SpeechRecognition (Reconhecimento de Voz)
- **Finalidade:** Transcrever o áudio bruto da sessão.
- **Entrada:** Arquivo `.mp4` / `.wav`.
- **Saída:** Texto transcrito.
- **Fluxo:** O arquivo é convertido para WAV usando `pydub`, lido em memória, e transcrito (por padrão utiliza a API do Google via pacote `speech_recognition`).

### 2.2 OpenAI GPT-4o-mini (Análise Semântica de Áudio)
- **Finalidade:** Interpretar a transcrição para buscar sinais de dor, violência obstétrica, desrespeito, ou falta de humanização (frieza, linguagem invasiva).
- **Entrada:** Texto transcrito e prompt altamente instruído.
- **Saída:** JSON com `ira_score` (Índice de Risco Acústico/Assistencial), `sentiment_score` e achados chave.
- **Limitações:** Se não houver transcrição clara (áudio ruim) ou falta de API Key, um *fallback* usando regex simples ("socorro", "ajuda", "dor") é acionado.

## 3. Processamento de Documentos e Notas (Document Domain)

O `document-domain` foca em textos: documentos clínicos em PDF (receitas, prontuários escaneados) e anotações digitadas.

### 3.1 AWS Textract (OCR Multimodal)
- **Finalidade:** Extrair texto bruto de PDFs e imagens enviadas pelos médicos.
- **Entrada:** PDF/Imagem (via bucket simulado ou S3).
- **Saída:** Texto bruto (`ocr_text`).
- **Fluxo:** O `document-service` envia uma requisição para o `aws-service`, que gerencia a fila assíncrona da AWS (ou devolve um documento mockado para testes).

### 3.2 OpenAI GPT-4o-mini (Extração de Dados e NLP)
- **Finalidade:** Ler o texto cru (do OCR ou notas clínicas) e extrair metadados vitais, sinais vitais, histórico médico e indicadores de risco (Ansiedade, Pressão Alta).
- **Entrada:** `ocr_text` ou `notes` + Prompt Estruturado (focado em saúde da mulher/gestação).
- **Saída:** JSON com score de risco documental, sinais vitais classificados, indicadores emocionais e recomendações geradas sinteticamente.

## Considerações de Performance
Atualmente, as inferências neurais (DeepFace/MediaPipe) ocorrem na mesma máquina/container (CPU-bound) do microserviço FastAPI, o que pode bloquear a thread principal em vídeos muito longos. Para implantação em produção, recomenda-se que os *Workers* assíncronos (Celery/Redis) gerenciem filas separadas do roteador HTTP.
