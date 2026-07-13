# FRONTEND_ARCHITECTURE.md — GuardIA Parto Seguro Angular

> Arquitetura Angular 21 para o GuardIA Parto Seguro
> Baseada na análise do backend existente (ver BACKEND_ANALYSIS.md)

---

## 1. Stack Tecnológica

| Item | Tecnologia | Versão |
|---|---|---|
| Framework | Angular | 21+ |
| Linguagem | TypeScript | 5.5+ |
| Estilos | Angular Material + TailwindCSS | Material 21 / Tailwind 3 |
| State Management | NgRx Signal Store | 21+ |
| HTTP | Angular HttpClient | built-in |
| Reatividade | Signals + RxJS | Angular Signals + RxJS 7 |
| Testes | Jasmine + Karma / Jest | - |
| i18n | Angular i18n | built-in |
| Formulários | Reactive Forms | built-in |
| Roteamento | Angular Router (Lazy Loading) | built-in |

---

## 2. Padrão de Componentes

**Standalone Components** — sem NgModules tradicionais.

```typescript
@Component({
  selector: 'app-example',
  standalone: true,
  imports: [CommonModule, RouterLink, ...],
  template: `...`,
})
export class ExampleComponent {}
```

---

## 3. Estrutura de Diretórios

```
src/
├── app/
│   ├── core/                          # Singleton — providers globais
│   │   ├── guards/
│   │   │   ├── auth.guard.ts
│   │   │   └── role.guard.ts
│   │   ├── interceptors/
│   │   │   ├── auth.interceptor.ts    # Injeta Bearer token
│   │   │   ├── error.interceptor.ts   # Trata 401, 403, 500
│   │   │   └── logging.interceptor.ts
│   │   ├── services/
│   │   │   └── storage.service.ts     # localStorage wrapper
│   │   └── core.providers.ts
│   │
│   ├── shared/                        # Componentes e utilitários reutilizáveis
│   │   ├── components/
│   │   │   ├── risk-card/
│   │   │   ├── emotion-card/
│   │   │   ├── patient-card/
│   │   │   ├── ai-timeline/
│   │   │   ├── video-player/
│   │   │   ├── alert-badge/
│   │   │   ├── confidence-meter/
│   │   │   ├── ira-gauge/
│   │   │   └── status-chip/
│   │   ├── models/
│   │   │   ├── paginated-response.model.ts
│   │   │   └── api-error.model.ts
│   │   ├── constants/
│   │   │   └── ira.constants.ts
│   │   ├── pipes/
│   │   │   ├── ira-level.pipe.ts
│   │   │   ├── media-size.pipe.ts
│   │   │   └── date-br.pipe.ts
│   │   └── utils/
│   │       └── form.utils.ts
│   │
│   ├── layout/                        # Shell da aplicação
│   │   ├── sidebar/
│   │   ├── header/
│   │   ├── main-layout/
│   │   └── auth-layout/
│   │
│   ├── domains/                       # Feature modules por domínio
│   │   ├── auth/
│   │   │   ├── pages/
│   │   │   │   ├── login/
│   │   │   │   └── change-password/
│   │   │   ├── components/
│   │   │   │   └── login-form/
│   │   │   ├── services/
│   │   │   │   └── auth.service.ts
│   │   │   ├── models/
│   │   │   │   ├── login-credentials.model.ts
│   │   │   │   ├── auth-tokens.model.ts
│   │   │   │   └── user-profile.model.ts
│   │   │   ├── store/
│   │   │   │   └── auth.store.ts
│   │   │   └── routes/
│   │   │       └── auth.routes.ts
│   │   │
│   │   ├── dashboard/
│   │   │   ├── pages/
│   │   │   │   └── dashboard-home/
│   │   │   ├── components/
│   │   │   │   ├── metrics-overview/
│   │   │   │   ├── recent-sessions/
│   │   │   │   └── critical-alerts-panel/
│   │   │   └── routes/
│   │   │       └── dashboard.routes.ts
│   │   │
│   │   ├── sessoes/                   # Sessões Clínicas
│   │   │   ├── pages/
│   │   │   │   ├── session-list/
│   │   │   │   ├── session-detail/
│   │   │   │   └── session-create/
│   │   │   ├── components/
│   │   │   │   ├── session-card/
│   │   │   │   ├── media-uploader/
│   │   │   │   ├── session-status-badge/
│   │   │   │   └── media-files-list/
│   │   │   ├── services/
│   │   │   │   └── sessions.service.ts
│   │   │   ├── models/
│   │   │   │   ├── clinical-session.model.ts
│   │   │   │   ├── media-file.model.ts
│   │   │   │   └── create-session-request.model.ts
│   │   │   ├── store/
│   │   │   │   └── sessions.store.ts
│   │   │   └── routes/
│   │   │       └── sessions.routes.ts
│   │   │
│   │   ├── analise-ia/                # Análise IA (vídeo, áudio, risco)
│   │   │   ├── pages/
│   │   │   │   ├── analysis-dashboard/
│   │   │   │   └── analysis-detail/
│   │   │   ├── components/
│   │   │   │   ├── ira-score-panel/
│   │   │   │   ├── transcription-viewer/
│   │   │   │   ├── video-findings-timeline/
│   │   │   │   ├── risk-justifications/
│   │   │   │   ├── emotion-chart/
│   │   │   │   └── analysis-loading/
│   │   │   ├── services/
│   │   │   │   └── analysis.service.ts
│   │   │   ├── models/
│   │   │   │   └── session-analysis.model.ts
│   │   │   ├── store/
│   │   │   │   └── analysis.store.ts
│   │   │   └── routes/
│   │   │       └── analysis.routes.ts
│   │   │
│   │   ├── alertas/                   # Central de Alertas
│   │   │   ├── pages/
│   │   │   │   └── alerts-center/
│   │   │   ├── components/
│   │   │   │   ├── alert-list/
│   │   │   │   └── alert-acknowledge-dialog/
│   │   │   ├── services/
│   │   │   │   └── alerts.service.ts
│   │   │   ├── models/
│   │   │   │   └── alert.model.ts
│   │   │   ├── store/
│   │   │   │   └── alerts.store.ts
│   │   │   └── routes/
│   │   │       └── alerts.routes.ts
│   │   │
│   │   ├── relatorios/                # Relatórios (report-service :8005)
│   │   │   ├── pages/
│   │   │   │   └── reports-list/
│   │   │   ├── services/
│   │   │   │   └── reports.service.ts
│   │   │   └── routes/
│   │   │       └── reports.routes.ts
│   │   │
│   │   └── admin/                     # Gestão de usuários (admin/gestor)
│   │       ├── pages/
│   │       │   ├── users-list/
│   │       │   └── user-create/
│   │       ├── services/
│   │       │   └── admin.service.ts
│   │       └── routes/
│   │           └── admin.routes.ts
│   │
│   ├── app.config.ts                  # provideRouter, provideHttpClient, etc.
│   ├── app.routes.ts                  # Rotas raiz (lazy loading)
│   └── app.component.ts
│
├── environments/
│   ├── environment.ts                 # dev: localhost:8000
│   └── environment.prod.ts            # prod: URL AWS
├── assets/
│   └── icons/
├── styles.scss                        # Global styles + Tailwind imports
└── index.html
```

---

## 4. Roteamento Principal (Lazy Loading)

```typescript
// src/app/app.routes.ts
export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    loadChildren: () => import('./domains/auth/routes/auth.routes').then(r => r.AUTH_ROUTES),
  },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadChildren: () => import('./domains/dashboard/routes/dashboard.routes').then(r => r.DASHBOARD_ROUTES),
      },
      {
        path: 'sessoes',
        loadChildren: () => import('./domains/sessoes/routes/sessions.routes').then(r => r.SESSIONS_ROUTES),
      },
      {
        path: 'analise',
        loadChildren: () => import('./domains/analise-ia/routes/analysis.routes').then(r => r.ANALYSIS_ROUTES),
      },
      {
        path: 'alertas',
        loadChildren: () => import('./domains/alertas/routes/alerts.routes').then(r => r.ALERTS_ROUTES),
      },
      {
        path: 'relatorios',
        loadChildren: () => import('./domains/relatorios/routes/reports.routes').then(r => r.REPORTS_ROUTES),
      },
      {
        path: 'admin',
        canActivate: [roleGuard(['admin', 'gestor'])],
        loadChildren: () => import('./domains/admin/routes/admin.routes').then(r => r.ADMIN_ROUTES),
      },
    ],
  },
];
```

---

## 5. Configuração da Aplicação (app.config.ts)

```typescript
// src/app/app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withPreloading(PreloadAllModules)),
    provideHttpClient(
      withInterceptors([authInterceptor, errorInterceptor])
    ),
    provideAnimations(),
    provideNgRxSignalStore({ /* config */ }),
    {
      provide: MAT_FORM_FIELD_DEFAULT_OPTIONS,
      useValue: { appearance: 'outline' },
    },
  ],
};
```

---

## 6. Environments

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  awsApiUrl: 'http://localhost:8007/api/v1',
};

// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://api.guardia.health/api/v1',
  awsApiUrl: 'https://aws.guardia.health/api/v1',
};
```

---

## 7. Signal Store — Padrão Adotado

```typescript
// src/app/domains/auth/store/auth.store.ts
import { signalStore, withState, withMethods, withComputed } from '@ngrx/signals';

type AuthState = {
  user: UserProfile | null;
  tokens: AuthTokens | null;
  loading: boolean;
  error: string | null;
};

const initialState: AuthState = {
  user: null,
  tokens: null,
  loading: false,
  error: null,
};

export const AuthStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed(({ user, tokens }) => ({
    isAuthenticated: computed(() => !!tokens()),
    userRole: computed(() => user()?.role ?? null),
  })),
  withMethods((store, authService = inject(AuthService)) => ({
    async login(credentials: LoginCredentials) {
      patchState(store, { loading: true, error: null });
      // ...
    },
    logout() {
      patchState(store, initialState);
    },
  }))
);
```

---

## 8. Auth Guard e Role Guard

```typescript
// src/app/core/guards/auth.guard.ts
export const authGuard: CanActivateFn = () => {
  const authStore = inject(AuthStore);
  const router = inject(Router);
  if (authStore.isAuthenticated()) return true;
  return router.createUrlTree(['/auth/login']);
};

// src/app/core/guards/role.guard.ts
export function roleGuard(allowedRoles: UserRole[]): CanActivateFn {
  return () => {
    const authStore = inject(AuthStore);
    const role = authStore.userRole();
    if (role && allowedRoles.includes(role)) return true;
    return inject(Router).createUrlTree(['/dashboard']);
  };
}
```

---

## 9. Estratégia de Polling para Status de Sessão

Como a análise é assíncrona (background), o Angular deve fazer polling:

```typescript
// Polling a cada 5 segundos enquanto status for 'processing'
this.pollingSubscription = interval(5000).pipe(
  switchMap(() => this.sessionsService.getSession(sessionId)),
  takeUntil(this.destroy$),
  filter(session => session.status !== 'processing')
).subscribe(session => {
  this.session.set(session);
  // Para quando completar ou der erro
});
```

---

## 10. Estratégia LGPD na UI

- Nunca exibir `patient_code` como "nome do paciente"
- Exibir label: "Código do Paciente" ou "ID Anonimizado"
- Formulários nunca devem solicitar CPF, nome, endereço
- Upload de documentos: mostrar aviso sobre processamento seguro
- Logs de auditoria: acessíveis apenas para `admin` e `auditor`

---

*Documento baseado na análise do backend real (BACKEND_ANALYSIS.md).*
