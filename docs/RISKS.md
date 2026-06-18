# RISKS.md — GuardIA Parto Seguro

> Matriz de Riscos e Plano de Mitigação — v1.0

---

## Matriz de Riscos

A probabilidade e o impacto são classificados em: **Baixo (1) / Médio (2) / Alto (3)**  
**Criticidade = Probabilidade × Impacto**  
Criticidade ≥ 6: 🔴 Crítico | 4–5: 🟡 Moderado | ≤ 3: 🟢 Baixo

---

## Riscos Técnicos

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RT-001** | Latência alta no processamento de vídeo (> 15 min para 30 min de vídeo) | 3 | 3 | 🔴 9 | Usar amostragem de frames (1 FPS) em vez de todos os frames; processar em background assíncrono; usar GPU se disponível (OpenCV CUDA) | Dev 2 |
| **RT-002** | Limite de quota do Azure Speech excedido durante testes | 3 | 2 | 🟡 6 | Criar mocks para Azure Speech nos testes; usar tier gratuito com controle de uso; criar fallback com Whisper local | Dev 2 |
| **RT-003** | Acurácia do STT < 80% para sotaques regionais em pt-BR | 2 | 3 | 🔴 6 | Testar com múltiplos sotaques; ajustar linguagem personalizada no Azure Speech; documentar limitações claramente | Dev 2 |
| **RT-004** | DeepFace com falsos positivos em condições de iluminação ruim | 3 | 2 | 🟡 6 | Pré-processar frames (equalização de histograma); incluir confidence score e threshold ajustável; documentar limitações | Dev 2 |
| **RT-005** | Conflitos de merge entre desenvolvedores | 2 | 2 | 🟡 4 | Estrutura de pastas totalmente separada por domínio; CODEOWNERS; PRs pequenos (< 300 linhas); branch de curta duração | Dev 1 |
| **RT-006** | Docker Compose com conflito de portas no ambiente local | 2 | 1 | 🟢 2 | Documentar portas usadas; criar script de verificação de portas livres; usar `.env` para configurar portas | Dev 1 |
| **RT-007** | Azure Document Intelligence com baixa acurácia em documentos escaneados com qualidade ruim | 2 | 2 | 🟡 4 | Pré-processar imagem (deskew, binarização OpenCV); aceitar threshold mínimo de qualidade no upload; documentar requisitos de qualidade | Dev 3 |
| **RT-008** | Migrations de banco inconsistentes entre serviços | 2 | 3 | 🔴 6 | Cada serviço tem suas próprias migrations Alembic; CI verifica migrations antes do deploy; scripts de rollback documentados | Dev 1 |
| **RT-009** | YOLOv8 detectando falsos positivos (objetos de risco inexistentes) | 2 | 2 | 🟡 4 | Fine-tuning com dataset obstétrico; threshold de confiança ≥ 0.7; validação humana para alertas de objetos | Dev 2 |

---

## Riscos de Projeto

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RP-001** | Prazo de 8 semanas insuficiente para todos os domínios | 2 | 3 | 🔴 6 | Priorizar o fluxo core (vídeo + IRA + dashboard); ter MVP funcional na semana 4; features secundárias na lista de backlog | Todos |
| **RP-002** | Desenvolvedor indisponível por doença ou compromisso | 2 | 3 | 🔴 6 | Documentação completa de cada domínio; pair programming chave para compartilhar conhecimento; Dev 1 conhece todos os serviços | Dev 1 |
| **RP-003** | Escopo inflando durante o desenvolvimento (scope creep) | 3 | 2 | 🟡 6 | Requisitos congelados após semana 1; toda mudança passa pelo PO Agent; backlog documentado para v2.0 | Todos |
| **RP-004** | Falta de dados reais para testar o sistema | 3 | 2 | 🟡 6 | Criar dataset sintético de demonstração (vídeos, áudios e documentos fictícios mas realistas) na semana 1 | Dev 2 + Dev 3 |
| **RP-005** | Integração entre domínios mais complexa que previsto | 2 | 2 | 🟡 4 | Definir contratos de API no início (semana 1); usar schemas Pydantic compartilhados; testes de contrato | Dev 1 |

---

## Riscos de Segurança e Conformidade

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RS-001** | Exposição de dados de pacientes em logs | 3 | 3 | 🔴 9 | Nunca logar nome, CPF ou dados identificáveis; usar IDs opacos nos logs; filtro de PII em todos os serviços; revisão de código com foco em privacidade | Dev 1 + Dev 3 |
| **RS-002** | Credenciais Azure hardcoded no código | 2 | 3 | 🔴 6 | CODEOWNERS + Bandit verifica hardcoded strings; Azure Key Vault para produção; `.env` para dev (gitignored) | Dev 1 |
| **RS-003** | Token JWT com expiração longa comprometido | 2 | 3 | 🔴 6 | Expiração de 1h com refresh token de 7 dias; blacklist de tokens revogados; HTTPS obrigatório | Dev 1 |
| **RS-004** | Arquivo malicioso no upload (path traversal, zip bomb) | 2 | 3 | 🔴 6 | Validar extensão e MIME type; limite de tamanho rígido; análise do arquivo em sandbox; nunca executar arquivo recebido | Dev 1 + Dev 2 |
| **RS-005** | Não conformidade com LGPD para dados de pacientes | 2 | 3 | 🔴 6 | Anonimização de dados pessoais (hash de nome); consentimento verificado antes do processamento; log de auditoria imutável; política de retenção documentada | Dev 3 |

---

## Riscos de Infraestrutura

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RI-001** | Serviços Azure indisponíveis durante demonstração | 1 | 3 | 🟢 3 | Criar mocks de fallback para todos os serviços Azure; ter demo com dados pré-processados gravados; ambiente local como backup | Dev 1 |
| **RI-002** | Custo Azure excedendo orçamento acadêmico | 2 | 2 | 🟡 4 | Usar tiers gratuitos sempre que possível; implementar mocks nos testes para não consumir quota; monitorar custos diariamente via Azure Cost Management | Dev 1 |
| **RI-003** | PostgreSQL sem backup causando perda de dados | 1 | 3 | 🟢 3 | Docker volume para persistência; script de backup diário; dados de demo com script de seed para recriar | Dev 1 |

---

## Riscos de Qualidade da IA

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RQ-001** | IRA gera score errado por pesos incorretos | 2 | 3 | 🔴 6 | Testes unitários extensivos para o calculador de IRA; casos de teste documentados com valores esperados; revisão da fórmula por todos | Dev 3 |
| **RQ-002** | Sistema detecta violência onde não há (falso positivo) causando problema na demonstração | 2 | 3 | 🔴 6 | Sempre apresentar confidence scores; dashboards mostram "indicativo de risco", não "diagnóstico"; disclaimers claros no sistema | Dev 4 |
| **RQ-003** | Sistema não detecta violência real (falso negativo) | 2 | 3 | 🔴 6 | Thresholds conservadores (prefere falso positivo a negativo); sistema é de apoio, não substitui avaliação humana | Dev 2 + Dev 3 |

---

## Plano de Contingência Geral

### Semana 4 — Ponto de Decisão GO/NO-GO

Na semana 4, avaliar:
1. O fluxo ponta a ponta funciona (vídeo → IRA → alerta)?
2. Os principais domínios estão integrados?
3. A equipe está dentro do cronograma?

**Se NO-GO:** Reduzir escopo para MVP mínimo:
- Manter: Video Domain + Core + Dashboard + IRA
- Adiar para v2.0: Audio Domain completo, Document Domain, Report avançado

### Semana 6 — Ponto de Decisão DEMO QUALITY

Na semana 6, verificar:
1. O sistema funciona com dados de demonstração?
2. A performance está aceitável?
3. Os bugs críticos foram resolvidos?

**Se NÃO:** Priorizar estabilidade sobre novas features. Congelar desenvolvimento de features e focar em correções.

---

## Registro de Riscos Materializados

| Data | ID do Risco | O que ocorreu | Impacto real | Resolução |
|---|---|---|---|---|
| — | — | Nenhum risco materializado até o momento | — | — |

*Atualizar esta tabela ao longo do desenvolvimento.*
