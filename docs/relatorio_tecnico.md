# Relatório Técnico: Plataforma GuardIA Parto Seguro

Este relatório descreve a arquitetura de processamento, os modelos de Inteligência Artificial empregados e os resultados obtidos na plataforma GuardIA Parto Seguro, em cumprimento aos requisitos do desafio técnico da pós-graduação.

---

## 1. Descrição do Fluxo Multimodal

A plataforma utiliza um fluxo de processamento **multimodal assíncrono** orquestrado por uma arquitetura de microserviços. O objetivo é cruzar dados de diferentes naturezas (visuais, auditivas e textuais) para compor o **Índice de Gravidade Assistencial (IGA)**, garantindo a segurança e o bem-estar da paciente durante os procedimentos obstétricos e ginecológicos.

O fluxo ocorre nas seguintes etapas:
1. **Ingestão de Dados:** O frontend envia mídias (vídeos, áudios e prontuários PDF) para o `core-api`.
2. **Distribuição (Fan-out):** O `core-api` despacha as mídias em paralelo para seus respectivos domínios especializados (`video-service`, `audio-service`, `document-service`).
3. **Análise por Inferência Neural:** Cada serviço processa o dado de forma independente utilizando algoritmos de Visão Computacional (CV) e Processamento de Linguagem Natural (NLP).
4. **Agregação e Triagem de Risco:** O orquestrador central consolida os achados (`key_findings`), calcula scores penalizadores para cada anomalia e utiliza o `risk-service` para computar o Score IGA consolidado da sessão.
5. **Apresentação:** O resultado é entregue em uma linha do tempo (Timeline) interativa no frontend, apontando os *timestamps* exatos das anomalias.

---

## 2. Modelos Aplicados em Cada Tipo de Dado

A solução emprega um conjunto de modelos state-of-the-art adaptados para o contexto clínico de saúde da mulher:

### A. Domínio de Vídeo (Visão Computacional)
* **YOLOv8 Nano (Ultralytics):** Treinado/mapeado no dataset COCO para detecção de objetos de risco. É utilizado na triagem de automutilação ou exposição inadequada de instrumentos, identificando cirúrgicos (tesouras, bisturis).
* **DeepFace (RetinaFace):** Análise de microexpressões faciais quadro a quadro. Consegue inferir estados de tensão, medo, tristeza e picos de dor (mapeados a partir da classe "angry" em contexto obstétrico).
* **MediaPipe Pose (Google):** Estimação de marcos corporais (Landmarks) para avaliar a postura da paciente. Identifica movimentos bruscos ou a perda de enquadramento da paciente por longos períodos.

### B. Domínio de Áudio (Análise Semântica)
* **LLM (OpenAI GPT-4o-mini / Whisper):** Realiza a avaliação semântica aprofundada da transcrição do diálogo. O modelo atua como um juiz técnico, identificando tom de voz agressivo, queixas de dor ignoradas e inadequação na analgesia por meio de *prompt engineering* focado em violência obstétrica.

### C. Domínio de Prontuários e Documentos (NLP)
* **PyPDF & OCR fallback:** Extração de texto bruto de PDFs clínicos.
* **LLM (OpenAI GPT-4o-mini):** Processamento do texto livre do prontuário pré-natal para extrair **Fatores Clínicos** (ex: DHEG, diabetes), **Fatores Emocionais** (ex: ansiedade) e **Fatores de Atenção**. Ele pondera o risco pré-existente da paciente, injetando esse peso no IGA inicial antes mesmo do procedimento começar.

---

## 3. Serviços de Cloud e Infraestrutura

A plataforma opera em um modelo híbrido e faz uso extensivo de serviços em nuvem (Cloud Computing) para viabilizar o processamento assíncrono e a análise inteligente dos dados. 

### Amazon Web Services (AWS)
O microserviço exclusivo `guardia-aws-service` abstrai e gerencia a comunicação com a AWS, provendo os seguintes serviços estruturais e cognitivos:
* **Amazon S3 (Simple Storage Service):** Utilizado como *Blob Storage* para armazenamento seguro e persistência temporária/permanente das mídias originais (vídeos, áudios e PDFs). 
* **Amazon Transcribe Medical / Transcribe:** Responsável pela conversão *Speech-to-Text* de alta precisão dos áudios captados nas consultas e procedimentos obstétricos.
* **Amazon Textract:** Atua na extração de texto (OCR avançado) de prontuários digitalizados, formulários médicos e PDFs escaneados, preservando a estrutura clínica para posterior inferência.
* **Amazon Comprehend Medical:** Complementa a análise semântica extraindo entidades médicas (medicamentos, condições de saúde, anatomia) diretamente dos textos e transcrições geradas.

### Inteligência Artificial como Serviço (OpenAI)
Para as camadas de raciocínio lógico (LLM) que exigem interpretação de contexto e identificação de violência obstétrica ou risco iminente, integramos a API da OpenAI:
* **GPT-4o / GPT-4o-mini:** Empregado no `document-service` e `audio-service`. Funciona como um juiz técnico que processa o texto limpo (saído do AWS Textract/Transcribe ou PyPDF) utilizando *Prompt Engineering* refinado. Ele categoriza as falas ou textos do prontuário, identificando alertas como "tom de voz agressivo" ou "risco gestacional oculto", compondo o IGA.

---

## 4. Resultados Obtidos e Exemplos de Anomalias Detectadas

Durante a validação e integração do fluxo multimodal, o sistema conseguiu identificar e alertar com sucesso diversas anomalias simuladas.

### Exemplos de Anomalias Detectadas na Prática:

1. **Detecção Visual de Risco (Automutilação/Cirúrgico):**
   * *Resultado:* O modelo YOLOv8 identificou lâminas/tesouras expostas em frames chave (ex: `cena_9.mp4`), plotando Bounding Boxes alaranjadas na interface.
   * *Ação:* O achado `"Alerta de Objeto: Tesoura Cirurgica detectado na cena clínica"` elevou o `object_risk_score` e impactou o IGA dinâmico da sessão imediatamente.

2. **Desconforto Emocional e Dor:**
   * *Resultado:* O DeepFace capturou picos de mais de 60% de confiança nas emoções *fear* (medo) e *angry* (dor/esforço) durante a gravação visual.
   * *Ação:* O sistema marcou o timestamp exato do evento, sinalizando à auditoria o momento em que a paciente demonstrou desconforto extremo não verbalizado.

3. **Inconsistências no Prontuário:**
   * *Resultado:* O processamento de um PDF contendo "Hipertensão gestacional controlada" e "Fala hesitante ao relatar preocupações" foi classificado pelo LLM como fator de risco latente.
   * *Ação:* A sessão de parto iniciou com um IGA de base inflado, orientando a equipe a ter maior cautela devido ao histórico de ansiedade e pressão arterial limítrofe da paciente.

### Conclusão
A integração dos modelos provou a viabilidade técnica da orquestração multimodal. A plataforma consegue isolar eventos (áudio, vídeo e texto), mas os unifica em um único painel holístico de risco, cumprindo com excelência a proposta de auditoria para prevenção de abusos e garantia do parto seguro.
