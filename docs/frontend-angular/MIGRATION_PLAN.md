# MIGRATION_PLAN.md — GuardIA Parto Seguro Angular

> Plano de migração Streamlit → Angular 21
> Baseado na análise do backend real

---

## Princípios

1. **Não quebrar o backend** — nenhum endpoint existente será alterado sem aprovação
2. **Coexistência** — Streamlit (:8501) e Angular (:4200) rodam simultaneamente durante a migração
3. **Branch por fase** — cada domínio tem sua própria branch
4. **Sem suposições** — só implementar o que está confirmado na API_CONTRACTS.md

---

## FASE 1 — Infraestrutura Angular

**Branch**: `feature/frontend-shell`

### 1.1 Criar Projeto Angular

```bash
# Verificar versão mais recente
npx -y @angular/cli@latest new guardia-frontend \
  --routing \
  --style=scss \
  --standalone \
  --skip-tests=false

# Mover para pasta do projeto
# OU inicializar dentro do monorepo
```

### 1.2 Instalar Dependências

```bash
# Angular Material
ng add @angular/material
# Selecionar: tema customizado, Roboto, animations

# TailwindCSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init

# NgRx Signal Store
npm install @ngrx/signals

# Extras
npm install date-fns
```

### 1.3 Configurar Estrutura Base

- [ ] `tailwind.config.ts` com tokens do design system
- [ ] `styles.scss` com variáveis CSS + imports Material
- [ ] `environments/` com URLs do backend
- [ ] `app.config.ts` com providers globais
- [ ] `app.routes.ts` com roteamento base (lazy)

### 1.4 Implementar Core

- [ ] `AuthInterceptor` (injeta Bearer token)
- [ ] `ErrorInterceptor` (trata 401 auto-refresh, 403, 500)
- [ ] `StorageService` (localStorage para tokens)
- [ ] `ApiService` (base HTTP service)
- [ ] `authGuard` e `roleGuard`

### 1.5 Layout Shell

- [ ] `MainLayoutComponent` (sidebar + header + content)
- [ ] `SidebarComponent` (menu de navegação)
- [ ] `HeaderComponent` (user menu, notifications badge)
- [ ] `AuthLayoutComponent` (layout para login)

**Critério de aceite**: `ng serve` funciona, layout base renderiza.

---

## FASE 2 — Autenticação

**Branch**: `feature/frontend-auth`

### Depende de: FASE 1

### 2.1 Login

- [ ] `LoginPageComponent` (formulário email + senha)
- [ ] `LoginFormComponent` (Reactive Form + validation)
- [ ] `AuthService.login()` → POST /api/v1/auth/login
- [ ] `AuthService.getMe()` → GET /api/v1/auth/me
- [ ] `AuthStore` (Signal Store com user + tokens)
- [ ] Redirecionar para `/dashboard` após login

### 2.2 Refresh Token Automático

- [ ] `ErrorInterceptor` → detecta 401 → chama `refreshToken()` → retry
- [ ] Logout automático se refresh falhar

### 2.3 Logout

- [ ] Botão no header → POST /api/v1/auth/logout
- [ ] Limpa localStorage → redireciona para login

### 2.4 Trocar Senha

- [ ] `ChangePasswordPageComponent`
- [ ] `AuthService.changePassword()`

**Critério de aceite**: Login funciona com backend real; refresh token automático testado.

---

## FASE 3 — Dashboard Principal

**Branch**: `feature/frontend-dashboard`

### Depende de: FASE 2

### 3.1 Dashboard Home

- [ ] `DashboardHomePageComponent` (grid de métricas)
- [ ] `MetricsOverviewComponent` (cards: total sessões, alertas críticos, em processamento)
- [ ] `RecentSessionsComponent` (lista últimas 5 sessões)
- [ ] `CriticalAlertsPanelComponent` (alertas não reconhecidos)

**Dados de dashboard** (combinando endpoints existentes):
```
GET /api/v1/sessions/?limit=5        → sessões recentes
GET /api/v1/alerts/?severity=critical&unacknowledged_only=true → alertas críticos
GET /api/v1/sessions/?status=processing → em processamento
```

**Critério de aceite**: Dashboard exibe dados reais do backend.

---

## FASE 4 — Domínio Sessões

**Branch**: `feature/frontend-sessoes`

### Depende de: FASE 2

### 4.1 Lista de Sessões

- [ ] `SessionListPageComponent`
- [ ] `SessionCardComponent` (título, patient_code, status, IRA)
- [ ] `StatusChipComponent`
- [ ] Paginação (skip/limit)
- [ ] Filtro por status

### 4.2 Criar Sessão

- [ ] `SessionCreatePageComponent`
- [ ] Formulário: title, patient_code, notes
- [ ] Aviso LGPD inline: "Não inserir dados pessoais identificáveis"
- [ ] `SessionsService.createSession()`

### 4.3 Detalhe da Sessão

- [ ] `SessionDetailPageComponent`
- [ ] Exibe: status, IRA score, scores parciais, arquivos de mídia
- [ ] `IraGaugeComponent` (gauge circular do IRA)
- [ ] `RiskCardComponent` x3 (video, audio, document)
- [ ] `MediaFilesListComponent` (lista arquivos com status)

### 4.4 Upload de Mídia

- [ ] `MediaUploaderComponent` (drag & drop)
- [ ] Upload via `FormData` (não JSON!)
- [ ] Indicador de progresso de upload
- [ ] Polling automático após upload (a cada 5s até status != 'processing')

**Critério de aceite**: Fluxo completo de criação → upload → polling funciona com backend.

---

## FASE 5 — Domínio Análise IA

**Branch**: `feature/frontend-ia`

### Depende de: FASE 4

### 5.1 Painel de Análise

- [ ] `AnalysisDashboardPageComponent`
- [ ] Chama GET /api/v1/sessions/{id}/analysis
- [ ] Loading state enquanto status = processing

### 5.2 Transcrição

- [ ] `TranscriptionViewerComponent`
- [ ] Exibe `full_text`
- [ ] Lista `segments` com speaker, role, sentiment
- [ ] Color code por sentiment (negative=vermelho, positive=verde, neutral=cinza)

### 5.3 Timeline de Vídeo

- [ ] `VideoFindingsTimelineComponent`
- [ ] `AITimelineComponent` com `VideoFinding[]`
- [ ] Timestamp formatado (HH:MM:SS)
- [ ] `ConfidenceMeterComponent` por finding

### 5.4 Justificativas de Risco

- [ ] `RiskJustificationsComponent`
- [ ] 3 cards: video, audio, document
- [ ] Key indicators como chips/tags
- [ ] Recomendações como alertas informacionais

### 5.5 Score de Risco Explicável

- [ ] `IraExplainabilityComponent`
- [ ] Gráfico de contribuição por componente (Chart.js ou ngx-charts)
- [ ] Fórmula: video×0.4 + audio×0.35 + document×0.25

**Critério de aceite**: Análise completa exibida para sessões `completed`.

---

## FASE 6 — Central de Alertas

**Branch**: `feature/frontend-alertas`

### Depende de: FASE 2

### 6.1 Lista de Alertas

- [ ] `AlertsCenterPageComponent`
- [ ] `AlertListComponent` (tabela + cards)
- [ ] `AlertBadgeComponent` (severity: moderate/critical)
- [ ] Filtros: severity, unacknowledged_only, session_id

### 6.2 Reconhecer Alerta

- [ ] `AlertAcknowledgeDialogComponent` (MatDialog)
- [ ] PATCH /api/v1/alerts/{id}/acknowledge
- [ ] Atualiza lista após confirmação

### 6.3 Notificações em Tempo Real

- [ ] Badge de alertas não reconhecidos no header
- [ ] Polling a cada 30s para contagem de alertas críticos

**Critério de aceite**: Alertas exibidos e reconhecimento funcional.

---

## FASE 7 — Relatórios

**Branch**: `feature/frontend-relatorios`

### Depende de: FASE 4

### Observação

O report-service (porta 8005) não está integrado ao core-api via endpoints públicos ainda. O frontend precisará:
1. Chamar diretamente report-service:8005 (se CORS permitir) OU
2. Aguardar endpoint no core-api

- [ ] `ReportsListPageComponent`
- [ ] Integração com report-service (verificar disponibilidade)
- [ ] `ReportsService.generateReport(sessionId)`
- [ ] Download de PDF via URL pré-assinada S3

---

## FASE 8 — Administração (Gestão de Usuários)

**Branch**: `feature/frontend-admin`

### Depende de: FASE 2 | Role: admin, gestor

### Observação

O core-api não tem endpoint `GET /api/v1/users` implementado ainda. Coordenar com Dev 1.

- [ ] `UsersListPageComponent` (aguardar implementação backend)
- [ ] `UserCreatePageComponent` → POST /api/v1/auth/users

---

## Cronograma Sugerido

| Fase | Branch | Semanas |
|---|---|---|
| FASE 1 — Infraestrutura | `feature/frontend-shell` | 1 |
| FASE 2 — Autenticação | `feature/frontend-auth` | 1 |
| FASE 3 — Dashboard | `feature/frontend-dashboard` | 1 |
| FASE 4 — Sessões | `feature/frontend-sessoes` | 2 |
| FASE 5 — Análise IA | `feature/frontend-ia` | 2 |
| FASE 6 — Alertas | `feature/frontend-alertas` | 1 |
| FASE 7 — Relatórios | `feature/frontend-relatorios` | 1 |
| FASE 8 — Admin | `feature/frontend-admin` | 1 |

---

## Estratégia de Branches e Commits

### Branches

```
main
├── feature/frontend-shell
├── feature/frontend-auth
├── feature/frontend-dashboard
├── feature/frontend-sessoes
├── feature/frontend-ia
├── feature/frontend-alertas
├── feature/frontend-relatorios
└── feature/frontend-admin
```

### Padrão de Commits

```
feat(auth): implement login page with JWT integration
feat(sessoes): add session list with pagination
feat(ia): create IRA gauge component
fix(interceptor): handle 401 refresh token rotation
refactor(shared): extract risk-card to shared components
docs(sessoes): add LGPD warning to session create form
test(auth): add unit tests for auth.service
```

---

## Pré-condições Antes de Iniciar

- [ ] Dev 1 adicionar `http://localhost:4200` ao CORS no main.py
- [ ] Node.js 20+ instalado
- [ ] Angular CLI 21+ instalado globalmente
- [ ] Acesso ao backend rodando local (docker-compose up)
- [ ] Credenciais de teste disponíveis (seed.py executado)

---

*Plano baseado na análise completa do backend real (BACKEND_ANALYSIS.md + API_CONTRACTS.md).*
