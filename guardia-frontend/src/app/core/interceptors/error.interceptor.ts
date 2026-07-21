import {
  HttpInterceptorFn,
  HttpErrorResponse,
  HttpRequest,
  HttpHandlerFn,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import {
  catchError,
  switchMap,
  throwError,
  BehaviorSubject,
  filter,
  take,
  from,
} from 'rxjs';
import { StorageService } from '../services/storage.service';

// Controle de refresh em andamento (evita múltiplas chamadas simultâneas)
let isRefreshing = false;
const refreshTokenSubject = new BehaviorSubject<string | null>(null);

/**
 * errorInterceptor — Trata erros HTTP globalmente:
 * - 401: tenta renovar o token automaticamente; se falhar, faz logout
 * - 403: redireciona para dashboard (sem permissão)
 * - 5xx: pode adicionar logging/toast futuramente
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const storage = inject(StorageService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // 401 — Token expirado ou inválido
      if (error.status === 401 && !req.url.includes('/auth/login')) {
        return handle401(req, next, storage, router);
      }

      // 403 — Sem permissão
      if (error.status === 403) {
        router.navigate(['/dashboard']);
      }

      return throwError(() => error);
    }),
  );
};

function handle401(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
  storage: StorageService,
  router: Router,
) {
  if (isRefreshing) {
    // Aguarda o refresh em andamento completar
    return refreshTokenSubject.pipe(
      filter((token) => token !== null),
      take(1),
      switchMap((token) =>
        next(
          req.clone({
            headers: req.headers.set('Authorization', `Bearer ${token}`),
          }),
        ),
      ),
    );
  }

  isRefreshing = true;
  refreshTokenSubject.next(null);

  const refreshToken = storage.getRefreshToken();
  if (!refreshToken) {
    isRefreshing = false;
    storage.clearAll();
    router.navigate(['/auth/login']);
    return throwError(() => new Error('No refresh token available'));
  }

  // Executa o refresh token isoladamente via fetch e envelopa num Observable com from()
  return from(
    fetch(`${getApiUrl()}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    }).then((res) => {
      if (!res.ok) throw new Error('Refresh failed');
      return res.json();
    })
  ).pipe(
    switchMap((tokens: any) => {
      storage.setAccessToken(tokens.access_token);
      storage.setRefreshToken(tokens.refresh_token);
      isRefreshing = false;
      refreshTokenSubject.next(tokens.access_token);

      return next(
        req.clone({
          headers: req.headers.set(
            'Authorization',
            `Bearer ${tokens.access_token}`,
          ),
        }),
      );
    }),
    catchError(() => {
      isRefreshing = false;
      storage.clearAll();
      router.navigate(['/auth/login']);
      return throwError(() => new Error('Session expired. Please login again.'));
    })
  );
}

function getApiUrl(): string {
  // Fallback para ambiente de desenvolvimento
  return 'http://localhost:8000/api/v1';
}
