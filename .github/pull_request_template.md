## 📋 Descrição
<!-- Descreva brevemente o que este PR faz e por quê -->

## 🔗 Issue/Task relacionada
<!-- Fecha #(número da issue) ou referencia a tarefa do ROADMAP.md -->
Fecha #

## 🧩 Domínio afetado
<!-- Marque o(s) domínio(s) modificado(s) -->
- [ ] `backend/` — Core Platform (Dev 1)
- [ ] `devops/` — Infraestrutura (Dev 1)
- [ ] `video-domain/` — Video AI (Dev 2)
- [ ] `audio-domain/` — Audio AI (Dev 2)
- [ ] `document-domain/` — Document AI (Dev 3)
- [ ] `risk-domain/` — Risk Correlation (Dev 3)
- [ ] `frontend/` — Dashboard (Dev 4)
- [ ] `report-domain/` — Reports (Dev 4)
- [ ] `docs/` — Documentação

## 🧪 Tipo de mudança
- [ ] ✨ Nova funcionalidade (feat)
- [ ] 🐛 Correção de bug (fix)
- [ ] ♻️ Refactoring (sem mudança de comportamento)
- [ ] 📝 Documentação
- [ ] 🔧 CI/CD / Infraestrutura (chore)
- [ ] 🧪 Apenas testes

## ✅ Checklist Obrigatório
- [ ] Código segue padrão do projeto (`ruff check` e `black --check` passam)
- [ ] Testes adicionados/atualizados para as mudanças
- [ ] Cobertura de testes mantida ≥ 80% (`pytest --cov`)
- [ ] Nenhum segredo, senha ou chave no código
- [ ] Variáveis sensíveis usando `.env` (dev) ou Azure Key Vault (produção)
- [ ] `Dockerfile` atualizado se necessário
- [ ] `API_SPEC.md` atualizado se nova API adicionada/modificada
- [ ] `REQUIREMENTS.md` atualizado se novo RF/RNF
- [ ] Domínios vizinhos NÃO foram modificados (sem acoplamento)

## 🧪 Como testar manualmente
<!-- Descreva os passos para reproduzir e verificar a mudança -->
1. 
2. 
3. 

## ⚡ Impacto em outros domínios
<!-- Este PR quebra algum contrato de API? Afeta algum outro serviço? -->
- [ ] Nenhum impacto nos outros domínios
- [ ] Mudança de breaking change de API (descrever abaixo)

<!-- Se sim, descreva: -->

## 📸 Screenshots / Logs (se aplicável)
<!-- Cole screenshots do dashboard, logs de testes ou output relevante -->

---
*Lembre-se: mantenha o PR pequeno (< 300 linhas de diff). PRs grandes são difíceis de revisar!*
