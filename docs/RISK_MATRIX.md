# RISK_MATRIX.md — GuardIA Parto Seguro

> Matriz de Riscos e Plano de Mitigação — v1.0

---

## Matriz de Riscos

A probabilidade e o impacto são classificados em: **Baixo (1) / Médio (2) / Alto (3)**  
**Criticidade = Probabilidade × Impacto**  
Criticidade ≥ 6: 🔴 Crítico | 4–5: 🟡 Moderado | ## Riscos Técnicos

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RT-001** | Latência alta no processamento de vídeo (> 15 min para 30 min de vídeo) | 3 | 3 | 🔴 9 | Usar amostragem de frames (1 FPS) em vez de todos os frames; processar em background assíncrono; usar GPU se disponível (OpenCV CUDA) | Paulo Roberto Gonçalves |
| **RT-002** | Limite de quota do Azure Speech excedido durante testes | 3 | 2 | 🟡 6 | Criar mocks para Azure Speech nos testes; usar tier gratuito com controle de uso; criar fallback com Whisper local | Paulo Roberto Gonçalves |
| **RT-003** | Acurácia do STT < 80% para sotaques regionais em pt-BR | 2 | 3 | 🔴 6 | Testar com múltiplos sotaques; ajustar linguagem personalizada no Azure Speech; documentar limitações claramente | Paulo Roberto Gonçalves |
| **RT-004** | DeepFace com falsos positivos em condições de iluminação ruim | 3 | 2 | 🟡 6 | Pré-processar frames (equalização de histograma); incluir confidence score e threshold ajustável; documentar limitações | Paulo Roberto Gonçalves |
| **RT-005** | Conflitos de merge entre desenvolvedores | 2 | 2 | 🟡 4 | Estrutura de pastas totalmente separada por domínio; CODEOWNERS; PRs pequenos (< 300 linhas); branch de curta duração | Wallace Gomes |
| **RT-006** | Docker Compose com conflito de portas no ambiente local | 2 | 1 | 🟢 2 | Documentar portas usadas; criar script de verificação de portas livres; usar `.env` para configurar portas | Wallace Gomes |
| **RT-007** | Azure Document Intelligence com baixa acurácia em documentos escaneados com qualidade ruim | 2 | 2 | 🟡 4 | Pré-processar imagem (deskew, binarização OpenCV); aceitar threshold mínimo de qualidade no upload; documentar requisitos de qualidade | Evandro Rosa Sampaio |
| **RT-008** | Migrations de banco inconsistentes entre serviços | 2 | 3 | 🔴 6 | Cada serviço tem suas próprias migrations Alembic; CI verifica migrations antes do deploy; scripts de rollback documentados | Wallace Gomes |
| **RT-009** | YOLOv8 detectando falsos positivos (objetos de risco inexistentes) | 2 | 2 | 🟡 4 | Fine-tuning com dataset obstétrico; threshold de confiança ≥ 0.7; validação humana para alertas de objetos | Paulo Roberto Gonçalves |
| **RT-010** | Gargalo no Cloud Integration Domain centralizando as requisições | 2 | 3 | 🔴 6 | Implementar circuit breaker, rate limiting, e escalar horizontalmente os containers do Cloud Domain | Wallace Gomes |

---

## Riscos de Projeto

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RP-001** | Prazo de 8 semanas insuficiente para todos os domínios | 2 | 3 | 🔴 6 | Priorizar o fluxo core (vídeo + IRA + dashboard); ter MVP funcional na semana 4; features secundárias na lista de backlog | Todos |
| **RP-002** | Desenvolvedor indisponível por doença ou compromisso | 2 | 3 | 🔴 6 | Documentação completa de cada domínio; pair programming chave para compartilhar conhecimento; Dev 1 conhece todos os serviços | Wallace Gomes |
| **RP-003** | Escopo inflando durante o desenvolvimento (scope creep) | 3 | 2 | 🟡 6 | Requisitos congelados após semana 1; toda mudança passa pelo PO Agent; backlog documentado para v2.0 | Todos |
| **RP-004** | Falta de dados reais para testar o sistema | 3 | 2 | 🟡 6 | Criar dataset sintético de demonstração (vídeos, áudios e documentos fictícios mas realistas) na semana 1 | Paulo Roberto Gonçalves + Evandro Rosa Sampaio |
| **RP-005** | Integração entre domínios mais complexa que previsto | 2 | 2 | 🟡 4 | Definir contratos de API no início (semana 1); usar schemas Pydantic compartilhados; testes de contrato | Wallace Gomes |

---

## Riscos de Segurança e Conformidade

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RS-001** | Exposição de dados de pacientes em logs | 3 | 3 | 🔴 9 | Nunca logar nome, CPF ou dados identificáveis; usar IDs opacos nos logs; filtro de PII em todos os serviços; revisão de código com foco em privacidade | Wallace Gomes + Evandro Rosa Sampaio |
| **RS-002** | Credenciais Azure hardcoded no código | 2 | 3 | 🔴 6 | CODEOWNERS + Bandit verifica hardcoded strings; Azure Key Vault para produção; `.env` para dev (gitignored) | Wallace Gomes |
| **RS-003** | Token JWT com expiração longa comprometido | 2 | 3 | 🔴 6 | Expiração de 1h com refresh token de 7 dias; blacklist de tokens revogados; HTTPS obrigatório | Wallace Gomes |
| **RS-004** | Arquivo malicioso no upload (path traversal, zip bomb) | 2 | 3 | 🔴 6 | Validar extensão e MIME type; limite de tamanho rígido; análise do arquivo em sandbox; nunca executar arquivo recebido | Wallace Gomes + Paulo Roberto Gonçalves |
| **RS-005** | Não conformidade com LGPD para dados de pacientes | 2 | 3 | 🔴 6 | Anonimização de dados pessoais; log de auditoria imutável **(Implementado)**; política de retenção | Evandro Rosa Sampaio |
| **RS-006** | Vazamento da Chave Mestra do Key Vault | 1 | 3 | 🟢 3 | Rotação automática de chaves, acesso condicional, e uso exclusivo via Managed Identity em produção | Wallace Gomes |
| **RS-007** | Falha na pseudo-anonimização enviando PII para nuvem | 2 | 3 | 🔴 6 | Testes estritos na camada de integração do Security Domain; varredura de regex local antes do envio ao Azure AI | Wallace Gomes + Evandro R. |

---

## Riscos de Infraestrutura

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RI-001** | Serviços Azure indisponíveis durante demonstração | 1 | 3 | 🟢 3 | Criar mocks de fallback para todos os serviços Azure; ter demo com dados pré-processados gravados; ambiente local como backup | Wallace Gomes |
| **RI-002** | Custo Azure excedendo orçamento acadêmico | 2 | 2 | 🟡 4 | Usar tiers gratuitos sempre que possível; implementar mocks nos testes para não consumir quota; monitorar custos diariamente via Azure Cost Management | Wallace Gomes |
| **RI-003** | PostgreSQL sem backup causando perda de dados | 1 | 3 | 🟢 3 | Docker volume para persistência; script de backup diário; dados de demo com script de seed para recriar | Wallace Gomes |

---

## Riscos de Qualidade da IA

| ID | Risco | Prob. | Impacto | Criticidade | Mitigação | Responsável |
|---|---|---|---|---|---|---|
| **RQ-001** | IRA gera score errado por pesos incorretos | 2 | 3 | 🔴 6 | Testes unitários extensivos **(Cobertura implementada no backend)**; revisão da fórmula por todos | Evandro Rosa Sampaio |
| **RQ-002** | Sistema detecta violência onde não há (falso positivo) causando problema na demonstração | 2 | 3 | 🔴 6 | Sempre apresentar confidence scores; dashboards mostram "indicativo de risco", não "diagnóstico"; disclaimers claros no sistema | Gustavo Octaviano |
| **RQ-003** | Sistema não detecta violência real (falso negativo) | 2 | 3 | 🔴 6 | Thresholds conservadores (prefere falso positivo a negativo); sistema é de apoio, não substitui avaliação humana | Paulo Roberto Gonçalves + Evandro Rosa Sampaio |

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
