# PRESENTATION_PLAN.md — GuardIA Parto Seguro

> Roteiro de Apresentação Final — Vídeo de 15 Minutos — v1.0

---

## Estrutura Geral

| Bloco | Tema | Duração | Responsável |
|---|---|---|---|
| 1 | Abertura e Contexto | 2 min | Presenter A |
| 2 | Problema e Solução | 1,5 min | Presenter B |
| 3 | Arquitetura | 2 min | Presenter A |
| 4 | Demonstração ao Vivo | 5 min | Presenter C |
| 5 | IA e Resultados | 2 min | Presenter D |
| 6 | Conclusão e Impacto | 1,5 min | Todos |
| 7 | Q&A | 1 min | Todos |

**Total: 15 minutos**

---

## Bloco 1 — Abertura e Contexto (2 min)

### Roteiro
> *"Todos os anos, milhares de mulheres brasileiras enfrentam situações de violência obstétrica — muitas vezes em silêncio, sem que nenhum sistema de vigilância esteja presente para identificar e alertar os responsáveis."*

**Dados de impacto:**
- 1 em cada 4 mulheres relata alguma forma de violência obstétrica no Brasil (OMS, 2019)
- Subnotificação estimada em 70% dos casos
- Depressão pós-parto afeta até 20% das puérperas, com diagnóstico tardio frequente

**Transição:** *"Para responder a esse desafio, desenvolvemos o GuardIA Parto Seguro."*

### Slide Sugerido
- Background: imagem de sala de parto (respeitosa)
- Dados em destaque visual
- Logo do projeto

---

## Bloco 2 — Problema e Solução (1,5 min)

### Problema (30s)
- Ausência de vigilância sistematizada
- Dependência de relatos subjetivos
- Profissionais sobrecarregados sem ferramentas de apoio

### Solução (1 min)

> *"O GuardIA é uma plataforma multimodal de Inteligência Artificial que processa simultaneamente vídeo clínico, áudio de consultas e documentos médicos — calculando em tempo quase real o Índice de Risco Assistencial (IRA) e gerando alertas automáticos para equipes de saúde."*

**Diagrama:** Fluxo visual (Vídeo + Áudio + Documento → IA → IRA → Alertas)

---

## Bloco 3 — Arquitetura (2 min)

### Arquitetura de Microsserviços (45s)
- Mostrar diagrama de contêiner (C4 Level 2)
- Explicar os 8 domínios desacoplados
- Destacar: cada domínio com seu próprio banco

### Stack Tecnológica (45s)

| Camada | Tech |
|---|---|
| Backend | FastAPI (Python 3.11) |
| Visão | OpenCV + DeepFace + MediaPipe + YOLOv8 |
| Voz/NLP | Azure Speech + Azure AI Language |
| Docs | Azure Document Intelligence |
| Frontend | Streamlit |
| Cloud | Azure (Blob, Key Vault, Monitor) |
| Banco | PostgreSQL |

### Destaque de Decisões Arquiteturais (30s)
- Microsserviços por domínio → desenvolvimento paralelo sem conflitos
- Banco isolado por domínio → zero acoplamento de dados
- IRA composto ponderado (vídeo 40% + áudio 35% + documento 25%)

---

## Bloco 4 — Demonstração ao Vivo (5 min)

### Cena 1 — Login e Dashboard (30s)
- Abrir browser em `http://localhost:8501`
- Fazer login com `admin@guardia.health`
- Mostrar dashboard vazio (sem sessões)

### Cena 2 — Criação de Sessão (30s)
- Clicar em "Nova Sessão"
- Preencher: paciente de demonstração, tipo "Consulta Pré-Natal", data atual
- Mostrar sessão criada com status "Aguardando Mídias"

### Cena 3 — Upload de Mídias (1 min)
- Upload de **vídeo de demonstração** (~2 min de vídeo pré-preparado)
- Upload de **áudio de demonstração** (transcrição com keywords de risco)
- Upload de **prontuário PDF de demonstração** (com campos incompletos)
- Mostrar status "Processando..." em tempo real

### Cena 4 — Resultados da Análise (2 min)
- Aguardar ou mostrar sessão pré-processada com IRA já calculado
- **IRA Score:** mostrar gauge em 72.5 (CRÍTICO, vermelho)
- Expandir cada componente:
  - 🎥 Vídeo: 75/100 — "Expressões de dor detectadas em 3 momentos"
  - 🎙️ Áudio: 68/100 — "2 verbalizações de sofrimento, sentimento negativo dominante"
  - 📄 Documento: 40/100 — "Consentimento ausente, 3 campos obrigatórios faltando"
- Mostrar transcrição sincronizada com timestamp de risco destacado
- Mostrar mapa de calor temporal do IRA ao longo do vídeo

### Cena 5 — Alertas e Relatório (1 min)
- Mostrar alerta CRÍTICO gerado automaticamente
- Reconhecer alerta com justificativa
- Gerar PDF do relatório
- Mostrar primeira página do PDF com IRA e justificativas

---

## Bloco 5 — IA e Resultados (2 min)

### Tecnologias de IA em Destaque (1 min)

**Visão Computacional:**
```python
# DeepFace — Detecção de emoções
result = DeepFace.analyze(frame, actions=['emotion'])
dominant_emotion = result[0]['dominant_emotion']  # 'fear', 'sad', 'angry'
confidence = result[0]['emotion'][dominant_emotion]  # 0.89
```

```python
# MediaPipe — Pose estimation
with mp_holistic.Holistic() as holistic:
    results = holistic.process(rgb_frame)
    pose_score = classify_posture(results.pose_landmarks)
```

**NLP com Azure:**
```python
# Azure Speech — Speaker Diarization
result = speech_recognizer.recognize_once_async().get()
# Output: "Speaker_1: 'Tá doendo muito, para por favor'"

# Azure Language — Análise de sentimento
sentiment = text_analytics_client.analyze_sentiment([text])
# Output: {'sentiment': 'negative', 'confidence': 0.94}
```

### Resultados Obtidos (1 min)
| Métrica | Resultado |
|---|---|
| Precisão DeepFace (emoções) | 73% em vídeos de demonstração |
| WER Azure Speech (pt-BR) | < 18% em áudio limpo |
| Acurácia OCR (prontuários) | > 87% em documentos bem digitalizados |
| Tempo de processamento (30 min de vídeo) | ~ 12 minutos |
| Latência da API Gateway | < 350ms (p95) |

---

## Bloco 6 — Conclusão e Impacto (1,5 min)

### O que foi entregue (45s)
- ✅ Plataforma multimodal completa (vídeo + áudio + documento)
- ✅ IRA calculado com 3 componentes e justificativas
- ✅ Dashboard em tempo real com alertas
- ✅ Relatórios PDF/Excel gerados automaticamente
- ✅ Arquitetura desacoplada para 4 devs em paralelo
- ✅ CI/CD com GitHub Actions
- ✅ Conformidade com LGPD

### Impacto Potencial (30s)
> *"O GuardIA não substitui o julgamento clínico — ele amplifica a capacidade de vigilância, tornando visível o que antes era invisível. Com um sistema como este, gestores hospitalares teriam uma ferramenta concreta para identificar padrões de risco assistencial e agir preventivamente."*

### Trabalhos Futuros (15s)
- Integração com sistemas HIS/RES
- Aplicativo mobile para alertas em tempo real
- Fine-tuning de modelos com dados clínicos reais
- Expansão para outras línguas (espanhol para comunidades imigrantes)

---

## Bloco 7 — Q&A e Encerramento (1 min)

### Perguntas Frequentes Antecipadas

**"Como vocês garantem a privacidade da paciente?"**
> Nomes são armazenados apenas como hash SHA-256. Nunca exibimos dados identificáveis sem autenticação e permissão. Consentimento é verificado antes de qualquer processamento. Compliant com LGPD.

**"O IRA é suficientemente preciso para uso real?"**
> Na versão atual, o IRA é uma ferramenta de apoio à decisão, não um diagnóstico. Toda análise apresenta confidence scores e o sistema é explícito sobre suas limitações. O próximo passo seria validação com especialistas clínicos.

**"Como o sistema escala para múltiplos hospitais?"**
> A arquitetura de microsserviços permite que cada serviço escale independentemente. Para múltiplos hospitais, cada instituição poderia ter sua instância ou compartilhar a plataforma com isolamento de dados por tenant.

---

## Dicas para a Gravação

1. **Ambiente de demo:** Usar sessão pré-processada para a parte do IRA (não esperar processamento ao vivo)
2. **Dados de demo:** Preparar 3 sessões com IRA Baixo, Moderado e Crítico
3. **Vídeo demo:** Usar arquivo de vídeo curto (2 min) para não esperar muito
4. **Qualidade visual:** Dashboard em tela cheia, fonte grande, modo escuro
5. **Narração:** Cada desenvolvedor narra sua área de responsabilidade
6. **Backup:** Ter screenshots de todos os estados importantes caso algo falhe ao vivo

---

## Checklist de Preparação para Apresentação

- [ ] Dataset de demonstração pronto (3 sessões com diferentes IRAs)
- [ ] Vídeo de demo pré-processado carregado no sistema
- [ ] Áudio de demo pré-transcrito carregado
- [ ] Prontuário PDF de demo carregado
- [ ] Sistema rodando estável em ambiente de demonstração
- [ ] URL pública ou acesso local funcionando
- [ ] Slides preparados com dados e diagramas
- [ ] Roteiro ensaiado (ao menos 1 vez completo)
- [ ] Backup: screenshots de todos os estados críticos
- [ ] Backup: vídeo pré-gravado do fluxo completo (caso falha ao vivo)
