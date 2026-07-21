# Registros de Decisões Arquiteturais (ADRs)

Este documento registra as decisões de engenharia mais vitais adotadas ao longo do ciclo de vida do projeto **GuardIA Parto Seguro**. Ele documenta o *Porquê* de ferramentas específicas terem sido selecionadas, garantindo o alinhamento das futuras equipes (Tribes/Squads).

## ADR-001: Adoção do Padrão Monorepo de Microsserviços
- **Contexto**: A complexidade do GuardIA exige orquestração, leitura de banco relacional e processamento extremamente custoso de Visão (OpenCV) e Áudio.
- **Decisão**: Foi adotado um padrão de Microsserviços via Docker Compose localizados em um único Monorepo (Git).
- **Razão**: Isso garante que o motor de Inteligência Artificial de Vídeo não congele/starve o Backend de APIs (`core-api`). Manter em Monorepo simplifica drasticamente o Setup para ambientes de testes e homologação local usando o `start.sh`.

## ADR-002: Por que FastAPI e Python?
- **Contexto**: Escolha da linguagem de back-end.
- **Decisão**: Python 3 com FastAPI foi eleito como padrão para 100% do backend (Core + Domains).
- **Razão**: Python possui o ecossistema insuperável para Machine Learning. O FastAPI foi escolhido especificamente pelo seu roteamento **assíncrono** nativo, essencial para escalar chamadas de I/O bloqueantes (como aguardar transcrições do Textract) sem bloquear a esteira principal de requisições web.

## ADR-003: Por que OpenCV + DeepFace + MediaPipe?
- **Contexto**: Processamento computacional pesado de imagens médicas / parto.
- **Decisão**:
  - `MediaPipe` adotado para inferência de cinemática (movimentação e articulações da paciente) com altíssima taxa de FPS mesmo em CPU local.
  - `DeepFace` adotado por possuir modelos pré-treinados focados no escopo de micro-expressões de dor e medo (`angry`, `fear`, `sad`).
  - `OpenCV` como manipulador base (I/O de frames) por ser o standard de mercado da engenharia C++.

## ADR-004: Por que usar AWS Textract via Wrapper?
- **Contexto**: Leitura de exames escritos à mão livre, receituários borrados e PDFs médicos.
- **Decisão**: Ao invés de treinar um modelo de OCR local (como Tesseract), adotou-se o AWS Textract através do wrapper `aws-service`.
- **Razão**: O índice de assertividade do Tesseract em formulários desestruturados era baixo. O Textract extrai dados médicos já em formato de chaves-valores sem a necessidade de modelagem pesada interna.

## ADR-005: Por que Angular + Signals no Frontend?
- **Contexto**: Interface de Telemetria Médica de alta criticidade.
- **Decisão**: Angular v17+ com Signals.
- **Razão**: Uma tela de monitoramento em UTI (Dashboards que acendem de verde para vermelho baseados em Polling de Websockets/HTTP) não pode sofrer renderizações custosas na árvore do DOM. O uso de Signals do Angular moderno provê a detecção de mudanças granular sem a necessidade de disparar *Zone.js* exaustivamente.

## ADR-006: Por que OpenAI GPT-4o-mini para Interpretação?
- **Contexto**: Uma vez que os textos são gerados (Áudios ou Receitas), o sistema precisa julgar friamente se a linguagem médica utilizada configurou violência ou descaso.
- **Decisão**: Utilização da API de Completions da OpenAI (GPT-4o-mini).
- **Razão**: Modelos NLP locais clássicos (como SpaCy ou NLTK) não atingem precisão de "tom irônico" ou "linguagem opressiva" não explícita. O LLM foi essencial para interpretar a *nuance* de comunicação humanizada versus fria.
