# Roadmap do Projeto (GuardIA Parto Seguro)

Este documento centraliza as evoluções estratégicas do produto e refinamentos técnicos, priorizados de acordo com impacto direto na confiabilidade da plataforma e viabilidade de implementação.

---

## 1. Curto Prazo (Próxima Sprint - 1 a 2 Meses)
*Foco em Estabilidade, Finalização de Refatoração e Segurança de Dados*

- [x] **Migração do DTO de IGA:** Finalizar a remoção completa dos campos legados (`score_video`, `iga_score`) estáticos da entidade principal de `Session`, assegurando que 100% da leitura seja feita através das tabelas filhas dinâmicas (`VideoAnalysis`, `AudioAnalysis`).
- [x] **Substituição de Fallbacks Inseguros:** Remover o mock de "Prontuário Simulado" estático no `document-service`, substituindo-o por tratativas adequadas de indisponibilidade da AWS (re-tentativas automáticas).
- [x] **Aprimoramento de Exceções Baseado em Logger:** Converter todo e qualquer "silent try/catch pass" (`except Exception: pass`) em chamadas controladas ao `structlog` com níveis de Warning, para facilitar o debug de IA nos frames de vídeo.
- [x] **Implementação Rigorosa de Testes (Unitários e E2E):** Elevar a cobertura de código dos Domains Python para mais de 80% usando PyTest, garantindo contratos íntegros de comunicação HTTP.

---

## 2. Médio Prazo (3 a 6 Meses)
*Foco em Performance Assíncrona e Ampliação do Core de IA*

- [ ] **Mensageria Assíncrona Nativa (Kafka / RabbitMQ):** Substituir as invocações REST Síncronas (HTTP via Domain Client) do orquestrador por um padrão orientado a eventos (Event-Driven). A análise de vídeos de 2h exigirá processamento fragmentado via Workers, insustentável no formato de polling HTTP atual.
- [x] **Integração Real do Modelo YOLO (Object Detection):** Ativar o Ultralytics YOLOv8 no fluxo de processamento de vídeo para identificar fisicamente a presença de sangue severo ou retenção inadequada de ferramentas cirúrgicas próximas à paciente.
- [x] **Adoção do Whisper On-Premise:** Substituir a dependência externa (Google Speech Recognition) do módulo de áudio por um modelo **Whisper** rodando localmente (CPU/GPU-bound), fundamental para certificar conformidade com a LGPD impedindo a saída de dados médicos via nuvens públicas não certificadas.
- [x] **Streaming Progressivo do Frontend:** Suportar streaming real-time de alertas para o dashboard Angular via WebSockets/Server-Sent Events (SSE), em vez de exigir refresh automático.

---

## 3. Longo Prazo (Além de 6 Meses)
*Foco em Hardware, Edge Computing e Telemedicina Distribuída*

- [ ] **Edge Computing (In-Room Processing):** Portar os microsserviços pesados de Visão (`video-domain`) para C++ (e.g. TensorRT) e embarcá-los em dispositivos Edge (NVIDIA Jetson) alocados dentro da própria sala de cirurgia, reduzindo drásticamente a transferência pesada de arquivos locais para datacenters.
- [ ] **Federated Learning:** Habilitar modelos neurais de LLM adaptáveis que se retroalimentam localmente, aprendendo sotaques hospitalares e especificidades culturais, sem centralizar as gravações na matriz.
- [ ] **Auditoria Blockchain:** Gravar a linha do tempo imutável (Audit Trail) de um parto (quem registrou ações, quem minimizou alertas críticos) em cadeias de blocos para resguardo incontestável em investigações jurídicas médicas.
