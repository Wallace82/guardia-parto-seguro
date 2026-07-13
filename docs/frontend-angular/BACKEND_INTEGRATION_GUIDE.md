# BACKEND_INTEGRATION_GUIDE.md — GuardIA Parto Seguro Angular

> Guia de integração Angular → Backend FastAPI
> Baseado na análise real do código-fonte

---

## 1. HTTP Client Setup

```typescript
// src/app/app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([
        authInterceptor,
        errorInterceptor,
        loggingInterceptor,
      ])
    ),
    // ...
  ],
};
```

---

## 2. Auth Interceptor (injeta Bearer token)

```typescript
// src/app/core/interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { StorageService } from '../services/storage.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const storage = inject(StorageService);
  const token = storage.getAccessToken();

  if (token) {
    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`),
    });
    return next(authReq);
  }

  return next(req);
};
```

---

## 3. Error Interceptor (401 auto-refresh + tratamento global)

```typescript
// src/app/core/interceptors/error.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../../domains/auth/services/auth.service';
import { Router } from '@angular/router';

let isRefreshing = false;

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !req.url.includes('/auth/login')) {
        // Token expirado — tentar refresh
        if (!isRefreshing) {
          isRefreshing = true;
          return authService.refreshToken().pipe(
            switchMap((tokens) => {
              isRefreshing = false;
              const retryReq = req.clone({
                headers: req.headers.set('Authorization', `Bearer ${tokens.access_token}`),
              });
              return next(retryReq);
            }),
            catchError((refreshError) => {
              isRefreshing = false;
              authService.logout();
              router.navigate(['/auth/login']);
              return throwError(() => refreshError);
            })
          );
        }
      }

      if (error.status === 403) {
        router.navigate(['/dashboard']); // Sem permissão
      }

      return throwError(() => error);
    })
  );
};
```

---

## 4. Storage Service (tokens JWT)

```typescript
// src/app/core/services/storage.service.ts
import { Injectable } from '@angular/core';

const KEYS = {
  ACCESS_TOKEN: 'guardia_access_token',
  REFRESH_TOKEN: 'guardia_refresh_token',
  USER: 'guardia_user',
} as const;

@Injectable({ providedIn: 'root' })
export class StorageService {
  // Access Token
  getAccessToken(): string | null {
    return localStorage.getItem(KEYS.ACCESS_TOKEN);
  }

  setAccessToken(token: string): void {
    localStorage.setItem(KEYS.ACCESS_TOKEN, token);
  }

  // Refresh Token
  getRefreshToken(): string | null {
    return localStorage.getItem(KEYS.REFRESH_TOKEN);
  }

  setRefreshToken(token: string): void {
    localStorage.setItem(KEYS.REFRESH_TOKEN, token);
  }

  // User Profile
  getUser(): UserProfile | null {
    const raw = localStorage.getItem(KEYS.USER);
    return raw ? JSON.parse(raw) : null;
  }

  setUser(user: UserProfile): void {
    localStorage.setItem(KEYS.USER, JSON.stringify(user));
  }

  // Clear all
  clearAll(): void {
    Object.values(KEYS).forEach(key => localStorage.removeItem(key));
  }
}
```

---

## 5. Base API Service

```typescript
// src/app/core/services/api.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  protected readonly http = inject(HttpClient);
  protected readonly baseUrl = environment.apiUrl;

  protected get<T>(path: string, params?: Record<string, unknown>): Observable<T> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, String(value));
        }
      });
    }
    return this.http.get<T>(`${this.baseUrl}${path}`, { params: httpParams });
  }

  protected post<T>(path: string, body: unknown): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${path}`, body);
  }

  protected patch<T>(path: string, body: unknown): Observable<T> {
    return this.http.patch<T>(`${this.baseUrl}${path}`, body);
  }

  protected delete<T>(path: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}${path}`);
  }

  protected postFormData<T>(path: string, formData: FormData): Observable<T> {
    // NÃO definir Content-Type — o browser define automaticamente com boundary
    return this.http.post<T>(`${this.baseUrl}${path}`, formData);
  }
}
```

---

## 6. Auth Service

```typescript
// src/app/domains/auth/services/auth.service.ts
@Injectable({ providedIn: 'root' })
export class AuthService extends ApiService {
  private readonly storage = inject(StorageService);

  login(credentials: LoginCredentials): Observable<AuthTokens> {
    return this.post<AuthTokens>('/auth/login', credentials).pipe(
      tap(tokens => {
        this.storage.setAccessToken(tokens.access_token);
        this.storage.setRefreshToken(tokens.refresh_token);
      })
    );
  }

  getMe(): Observable<UserProfile> {
    return this.get<UserProfile>('/auth/me');
  }

  refreshToken(): Observable<AuthTokens> {
    const refreshToken = this.storage.getRefreshToken();
    return this.post<AuthTokens>('/auth/refresh', { refresh_token: refreshToken }).pipe(
      tap(tokens => {
        this.storage.setAccessToken(tokens.access_token);
        this.storage.setRefreshToken(tokens.refresh_token);
      })
    );
  }

  logout(): Observable<void> {
    const refreshToken = this.storage.getRefreshToken();
    return this.post<void>('/auth/logout', { refresh_token: refreshToken }).pipe(
      finalize(() => this.storage.clearAll())
    );
  }

  changePassword(data: ChangePasswordRequest): Observable<void> {
    return this.post<void>('/auth/password/change', data);
  }

  createUser(data: CreateUserRequest): Observable<CreateUserResponse> {
    return this.post<CreateUserResponse>('/auth/users', data);
  }
}
```

---

## 7. Sessions Service

```typescript
// src/app/domains/sessoes/services/sessions.service.ts
@Injectable({ providedIn: 'root' })
export class SessionsService extends ApiService {

  createSession(data: CreateSessionRequest): Observable<CreateSessionResponse> {
    return this.post<CreateSessionResponse>('/sessions/', data);
  }

  listSessions(params: {
    skip?: number;
    limit?: number;
    status?: SessionStatus;
  } = {}): Observable<SessionListResponse> {
    return this.get<SessionListResponse>('/sessions/', params);
  }

  getSession(id: number): Observable<ClinicalSession> {
    return this.get<ClinicalSession>(`/sessions/${id}`);
  }

  updateSession(id: number, data: UpdateSessionRequest): Observable<ClinicalSession> {
    return this.patch<ClinicalSession>(`/sessions/${id}`, data);
  }

  deleteSession(id: number): Observable<void> {
    return this.delete<void>(`/sessions/${id}`);
  }

  uploadMedia(sessionId: number, file: File, mediaType: MediaType): Observable<MediaFile> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('media_type', mediaType);
    // CRÍTICO: usar postFormData, não post (não serializar como JSON)
    return this.postFormData<MediaFile>(`/sessions/${sessionId}/media`, formData);
  }

  deleteMedia(mediaId: number): Observable<void> {
    return this.delete<void>(`/sessions/media/${mediaId}`);
  }

  getSessionAnalysis(sessionId: number): Observable<SessionAnalysis> {
    return this.get<SessionAnalysis>(`/sessions/${sessionId}/analysis`);
  }
}
```

---

## 8. Alerts Service

```typescript
// src/app/domains/alertas/services/alerts.service.ts
@Injectable({ providedIn: 'root' })
export class AlertsService extends ApiService {

  listAlerts(filter: AlertsFilter = {}): Observable<AlertListResponse> {
    return this.get<AlertListResponse>('/alerts/', filter);
  }

  getAlert(id: number): Observable<Alert> {
    return this.get<Alert>(`/alerts/${id}`);
  }

  acknowledgeAlert(id: number): Observable<Alert> {
    return this.patch<Alert>(`/alerts/${id}/acknowledge`, {});
  }
}
```

---

## 9. Tratamento de Erros na UI

```typescript
// src/app/shared/utils/error.utils.ts
import { HttpErrorResponse } from '@angular/common/http';

export function extractErrorMessage(error: HttpErrorResponse): string {
  if (!error.error) return 'Erro desconhecido';

  const detail = error.error?.detail;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    // Erros de validação Pydantic
    return detail.map(e => e.msg).join('; ');
  }

  return `Erro ${error.status}: ${error.statusText}`;
}
```

---

## 10. Polling para Status de Sessão

```typescript
// src/app/domains/sessoes/pages/session-detail/session-detail.component.ts
export class SessionDetailComponent implements OnDestroy {
  private readonly destroy$ = new Subject<void>();
  private pollingActive = signal(false);

  startPolling(sessionId: number): void {
    this.pollingActive.set(true);

    interval(5000).pipe(
      takeUntil(this.destroy$),
      takeWhile(() => this.pollingActive()),
      switchMap(() => this.sessionsService.getSession(sessionId)),
    ).subscribe({
      next: (session) => {
        this.session.set(session);
        // Para quando sair de 'processing'
        if (session.status !== 'processing') {
          this.pollingActive.set(false);
        }
      },
      error: () => this.pollingActive.set(false),
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

---

## 11. CORS — Ação Requerida no Backend

Para que o Angular (`http://localhost:4200`) funcione, o Dev 1 deve adicionar ao `backend/app/main.py`:

```python
# backend/app/main.py — linha CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://frontend:8501",
        "http://localhost:4200",  # ← ADICIONAR ESTA LINHA
        "http://localhost:4300",  # ← Porta alternativa Angular
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Branch sugerida**: `fix/cors-angular-frontend`
**Commit**: `fix(core): add Angular dev server origin to CORS config`

---

## 12. Timeout e Retry

```typescript
// Para operações de upload (arquivos grandes)
const UPLOAD_TIMEOUT = 300_000;  // 5 minutos

// Para análise (pode demorar)
const ANALYSIS_TIMEOUT = 60_000; // 1 minuto

// Retry automático para erros de rede (não para 4xx)
import { retry } from 'rxjs/operators';

this.sessionsService.listSessions().pipe(
  retry({
    count: 3,
    delay: (error, retryCount) => {
      if (error instanceof HttpErrorResponse && error.status >= 400) {
        return throwError(() => error); // Não retenta erros do cliente
      }
      return timer(1000 * retryCount); // Backoff exponencial
    },
  })
);
```

---

## 13. Upload Progress (opcional)

```typescript
// Para feedback visual de upload
uploadWithProgress(sessionId: number, file: File, mediaType: MediaType): Observable<HttpEvent<MediaFile>> {
  const formData = new FormData();
  formData.append('file', file, file.name);
  formData.append('media_type', mediaType);

  return this.http.post<MediaFile>(
    `${this.baseUrl}/sessions/${sessionId}/media`,
    formData,
    {
      reportProgress: true,
      observe: 'events',
      headers: { Authorization: `Bearer ${this.storage.getAccessToken()}` }
    }
  );
}

// No componente:
this.sessionsService.uploadWithProgress(id, file, type).subscribe(event => {
  if (event.type === HttpEventType.UploadProgress && event.total) {
    this.uploadProgress.set(Math.round(100 * event.loaded / event.total));
  }
  if (event.type === HttpEventType.Response) {
    this.mediaFile.set(event.body);
  }
});
```

---

*Guia baseado no código real do backend e nas melhores práticas Angular 21.*
