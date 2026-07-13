import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { StorageService } from '../services/storage.service';

/**
 * authInterceptor — Injeta o Bearer token em todas as requisições HTTP autenticadas.
 * URLs de login/refresh/logout não recebem o token pois não requerem autenticação.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const storage = inject(StorageService);

  // Endpoints que NÃO devem receber o token
  const publicPaths = ['/auth/login', '/auth/refresh', '/auth/logout', '/health'];
  const isPublic = publicPaths.some((path) => req.url.includes(path));

  if (isPublic) {
    return next(req);
  }

  const token = storage.getAccessToken();
  if (!token) {
    return next(req);
  }

  const authReq = req.clone({
    headers: req.headers.set('Authorization', `Bearer ${token}`),
  });

  return next(authReq);
};
