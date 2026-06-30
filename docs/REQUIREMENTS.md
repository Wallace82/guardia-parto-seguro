# REQUIREMENTS.md — GuardIA Parto Seguro

> Requisitos Funcionais, Não Funcionais e Regras de Negócio — v2.0

---

## Visão Geral do Sistema

### O que é a proposta do sistema?
A proposta do GuardIA Parto Seguro é criar um ambiente obstétrico mais seguro, transparente e monitorado através do uso integrado de Inteligência Artificial multimodal. A solução atua como uma ferramenta de vigilância constante, autônoma e preventiva durante consultas, sessões clínicas e procedimentos de parto.

### O que é o sistema?
Trata-se de uma plataforma tecnológica que processa de forma simultânea múltiplas fontes de dados para monitoramento do ambiente: vídeos (analisando postura, expressões faciais, movimentação e presença de anomalias, como sangramentos), áudio (transcrevendo falas e avaliando sentimentos e tom de voz) e documentos (fazendo leitura de prontuários e termos de consentimento). Com essas informações, o sistema gera de forma automática um Índice de Risco Assistencial (IRA).

### Quais problemas ele resolve?
O GuardIA resolve a carência de auditoria em tempo real e de mecanismos proativos em saúde materna, detectando e alertando sobre:
- Violência obstétrica (física, verbal ou de coerção psicológica).
- Sofrimento e ansiedade gestacional (incluindo riscos de trauma e depressão).
- Desvios ou negligências procedimentais (ex.: ausência de consentimento prévio, sangramentos anômalos não tratados rapidamente e documentação inconsistente).
- Falta de respaldo probatório imparcial em eventuais disputas clínicas ou ouvidorias.

### Qual valor ele agrega à sociedade?
O sistema atua como um verdadeiro guardião da vida e do bem-estar. Ao empoderar gestantes, famílias e instituições de saúde com dados confiáveis, o sistema promove a humanização do parto, inibe práticas abusivas, e garante a proteção materno-infantil contínua. É uma inovação que assegura dignidade, respeito e ética num dos momentos mais críticos e importantes da vida humana, protegendo pacientes e resguardando os bons profissionais e as instituições transparentes.

---

## 📊 Progresso de Implementação

> Acompanhamento dinâmico das entregas com base nos checklists deste documento.

- **Requisitos Funcionais (RF):** 30 / 54 `[█████░░░░░] 55%`
- **Requisitos Não Funcionais (RNF):** 5 / 18 `[███░░░░░░░] 27%`
- **Regras de Negócio (RN):** 4 / 15 `[██░░░░░░░░] 26%`

---

## 1. Requisitos Funcionais

### 1.1 Gerenciamento de Sessões

- [x] **RF-001** O sistema deve permitir o cadastro de sessões clínicas associadas a uma paciente e a um profissional de saúde
- [ ] **RF-002** O sistema deve aceitar upload de arquivo de vídeo (MP4, AVI, MOV) com tamanho máximo de 2 GB
- [ ] **RF-003** O sistema deve aceitar upload de arquivo de áudio (MP3, WAV, OGG) com tamanho máximo de 500 MB
- [x] **RF-004** O sistema deve aceitar upload de documentos (PDF, DOCX, PNG, JPG) com tamanho máximo de 50 MB por arquivo
- [x] **RF-005** O sistema deve associar múltiplas mídias a uma única sessão clínica
- [x] **RF-006** O sistema deve registrar metadados da sessão: data, hora, profissional, tipo de atendimento e unidade de saúde

### 1.2 Análise de Vídeo (Processamento Local)

- [ ] **RF-007** O sistema deve detectar expressões faciais de dor, medo e sofrimento utilizando DeepFace
- [ ] **RF-008** O sistema deve analisar a postura corporal da paciente para detectar sinais de coerção ou desconforto (MediaPipe)
- [ ] **RF-009** O sistema deve detectar objetos de risco no ambiente clínico utilizando YOLOv8
- [ ] **RF-010** O sistema deve realizar análise temporal de vídeo para detectar padrões de comportamento suspeitos (OpenCV)
- [ ] **RF-011** O sistema deve detectar presença e identificação de pessoas no vídeo (face_recognition)
- [ ] **RF-012** O sistema deve analisar sangramento visível classificando-o por localização e intensidade estimada
- [ ] **RF-013** O sistema deve gerar um score de contribuição de vídeo para o IRA (0–100)
- [x] **RF-014** O sistema deve processar vídeos em background sem bloquear a interface do usuário

### 1.3 Análise de Áudio (Processamento via Nuvem - Amazon Web Services)

- [x] **RF-015** O sistema deve transcrever o áudio da consulta para texto utilizando Amazon Transcribe
- [ ] **RF-016** O sistema deve detectar o idioma predominante no áudio automaticamente
- [x] **RF-017** O sistema deve identificar múltiplos falantes na transcrição (speaker diarization)
- [x] **RF-018** O sistema deve analisar o sentimento do texto transcrito (positivo/negativo/neutro) utilizando Amazon Comprehend
- [ ] **RF-019** O sistema deve identificar entidades clínicas relevantes no texto (NER): diagnósticos, medicamentos, procedimentos via Amazon Comprehend
- [ ] **RF-020** O sistema deve detectar verbalizações de dor, medo, ameaça ou constrangimento
- [ ] **RF-021** O sistema deve analisar o tom de voz e indicadores prosódicos de sofrimento
- [x] **RF-022** O sistema deve gerar um score de contribuição de áudio para o IRA (0–100)

### 1.4 Análise de Documentos (Processamento via Nuvem - Amazon Web Services)

- [x] **RF-023** O sistema deve extrair texto de documentos médicos via OCR Inteligente (Amazon Textract)
- [x] **RF-024** O sistema deve identificar campos-chave em prontuários: diagnóstico, medicamentos, procedimentos, datas
- [ ] **RF-025** O sistema deve detectar inconsistências entre o prontuário e os dados da consulta (áudio/vídeo)
- [x] **RF-026** O sistema deve identificar ausência de consentimento informado documentado
- [x] **RF-027** O sistema deve validar completude do prontuário conforme checklist obstétrico
- [x] **RF-028** O sistema deve gerar um score de contribuição documental para o IRA (0–100)

### 1.5 Cálculo do IRA (Índice de Risco Assistencial)

- [x] **RF-029** O sistema deve calcular o IRA como score composto ponderado: vídeo (40%) + áudio (35%) + documento (25%)
- [x] **RF-030** O sistema deve classificar o IRA em três níveis: Baixo (0–39), Moderado (40–69), Crítico (70–100)
- [x] **RF-031** O sistema deve gerar justificativas textuais para cada componente do IRA
- [x] **RF-032** O sistema deve armazenar o histórico de IRA por paciente e por sessão
- [ ] **RF-033** O sistema deve calcular tendências do IRA ao longo do tempo para uma mesma paciente

### 1.6 Alertas e Notificações

- [x] **RF-034** O sistema deve disparar alertas automáticos quando o IRA atingir nível Moderado ou Crítico
- [x] **RF-035** O sistema deve enviar notificações por e-mail para o gestor responsável em casos de IRA Crítico
- [ ] **RF-036** O sistema deve exibir alertas em tempo real no dashboard durante o processamento
- [ ] **RF-037** O sistema deve registrar todos os alertas com timestamp, responsável e ação tomada
- [x] **RF-038** O sistema deve permitir que profissionais reconheçam e comentem os alertas

### 1.7 Relatórios

- [x] **RF-039** O sistema deve gerar relatório completo de sessão em formato PDF
- [x] **RF-040** O sistema deve gerar relatório executivo de IRA em formato Excel
- [x] **RF-041** O sistema deve gerar relatório de auditoria para ouvidoria
- [ ] **RF-042** O sistema deve suportar filtros de período, profissional, unidade e nível de risco nos relatórios
- [ ] **RF-043** O sistema deve incluir imagens-chave do vídeo e trechos da transcrição nos relatórios

### 1.8 Dashboard

- [x] **RF-044** O sistema deve exibir dashboard multimodal com visão consolidada da sessão
- [ ] **RF-045** O sistema deve exibir mapa de calor temporal do IRA durante o vídeo
- [ ] **RF-046** O sistema deve exibir gráfico de tendência histórica do IRA por paciente
- [x] **RF-047** O sistema deve exibir lista de alertas ativos com filtros por severidade
- [ ] **RF-048** O sistema deve exibir transcrição sincronizada com o vídeo

### 1.9 Autenticação e Controle de Acesso

- [x] **RF-049** O sistema deve suportar login com usuário e senha com autenticação JWT
- [x] **RF-050** O sistema deve implementar controle de acesso baseado em papéis (RBAC - IAM Role mappings): Admin, Médico, Enfermeiro, Auditor
- [x] **RF-051** O sistema deve registrar log de auditoria detalhado (usuário/data/recurso/operação) em todos os acessos e ações via Amazon CloudWatch
- [x] **RF-052** O sistema deve encerrar sessões inativas após 30 minutos
- [ ] **RF-053** O sistema deve mascarar dados sensíveis de pacientes (anonimização: ex. Maria Silva → PACIENTE_001) com base no perfil de acesso
- [ ] **RF-054** O sistema deve rotear toda comunicação de mídia com a nuvem pelo AWS Integration Domain para garantir conformidade

---

## 2. Requisitos Não Funcionais

- [ ] **RNF-001** Performance: O sistema deve processar um vídeo de 30 minutos em no máximo 15 minutos
- [ ] **RNF-002** Performance: A API Gateway deve responder em menos de 500ms para requisições síncronas
- [ ] **RNF-003** Performance: O dashboard deve carregar em menos de 3 segundos
- [ ] **RNF-004** Disponibilidade: O sistema deve ter disponibilidade mínima de 99% em ambiente de produção na nuvem (PRD)
- [ ] **RNF-005** Escalabilidade: Cada serviço de domínio deve escalar horizontalmente de forma independente no ECS Fargate (em HML/PRD)
- [ ] **RNF-006** Segurança (Trânsito): Todos os dados em trânsito devem ser criptografados via HTTPS/TLS 1.3
- [ ] **RNF-007** Segurança (Repouso): Dados de pacientes e mídias devem ser criptografados em repouso com algoritmo AES-256 (via Amazon S3 Encryption e DB Encryption)
- [ ] **RNF-008** Segurança (Identidade): A Gestão de Segredos e credenciais deve ser feita exclusivamente via AWS Secrets Manager e IAM policies
- [ ] **RNF-009** Segurança (LGPD): O sistema deve estar em estrita conformidade com a LGPD (Lei 13.709/2018), garantindo minimização, anonimização e privacidade por design
- [x] **RNF-010** Qualidade: A cobertura de testes unitários deve ser ≥ 80% por serviço
- [ ] **RNF-011** Qualidade: O código deve passar no linting (ruff/flake8) sem erros
- [x] **RNF-012** Observabilidade: Todos os serviços devem emitir logs estruturados em JSON para envio ao Amazon CloudWatch Logs
- [x] **RNF-013** Observabilidade: O sistema deve expor métricas de saúde via `/health` endpoint
- [ ] **RNF-014** Manutenibilidade: Toda API deve ter documentação OpenAPI/Swagger atualizada
- [x] **RNF-015** Flexibilidade e Deploy: O sistema deve suportar uma evolução de 4 ambientes (LOCAL, DEV, HML, PRD). O MVP executará 100% via Docker Compose local, com os demais ambientes suportando CI/CD na infraestrutura AWS
- [x] **RNF-016** Interoperabilidade: As APIs devem seguir padrão REST com retorno JSON
- [ ] **RNF-017** Usabilidade: O dashboard deve ser responsivo e funcionar em resolução mínima de 1280x720
- [ ] **RNF-018** Auditabilidade: Todo acesso a dados de pacientes deve ser registrado em log imutável no CloudWatch Logs

---

## 3. Regras de Negócio

- [x] **RN-001** IRA: O IRA deve ser calculado somente quando ao menos um tipo de análise (vídeo, áudio ou documento) for concluído
- [x] **RN-002** IRA: Os pesos do IRA são: vídeo=0.40, áudio=0.35, documento=0.25. A soma sempre deve ser 1.0
- [x] **RN-003** IRA: Se apenas um tipo de análise estiver disponível, o IRA deve ser normalizado para 100% daquele tipo
- [x] **RN-004** Alertas: Alertas de nível Crítico (IRA ≥ 70) devem ser enviados obrigatoriamente ao gestor responsável
- [ ] **RN-005** Alertas: Um alerta não pode ser descartado sem que o responsável registre uma justificativa
- [ ] **RN-006** Sessões: Uma sessão clínica não pode ter mais de 3 arquivos de vídeo, 3 de áudio e 10 de documentos
- [ ] **RN-007** LGPD: Nenhum dado de paciente pode ser exibido sem que o profissional esteja autenticado e tenha permissão explícita (mecanismo de consentimento dinâmico e IAM)
- [ ] **RN-008** LGPD: Dados de pacientes devem ser completamente anonimizados/pseudo-anonimizados nas bases analíticas e mantidos em segredo de acordo com o CFM
- [ ] **RN-009** Documentos: O consentimento informado deve ser verificado antes do processamento de qualquer mídia
- [ ] **RN-010** Vídeo: A análise de vídeo deve ser realizada apenas em arquivos previamente autorizados pelo consentimento verificado
- [ ] **RN-011** Áudio: A gravação de consultas requer consentimento explícito documentado e registrado no sistema
- [ ] **RN-012** Papéis: Médicos e Enfermeiros podem criar sessões e visualizar seus pacientes; Auditores e Admins podem acessar logs e relatórios anonimizados
- [x] **RN-013** Relatórios: Relatórios de auditoria são imutáveis após geração e devem ter hash SHA-256 registrado
- [ ] **RN-014** Processamento: O processamento de vídeo e áudio deve ser realizado em background sem bloquear a submissão de novas sessões
- [ ] **RN-015** Retenção: Logs de sistema e dados de auditoria devem ser retidos no CloudWatch Logs/S3 por no mínimo 1 ano
