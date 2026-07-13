import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { StorageService } from '../services/storage.service';

/**
 * authGuard — Protege rotas que requerem autenticação.
 * Redireciona para /auth/login se não houver token válido.
 */
export const authGuard: CanActivateFn = () => {
  const storage = inject(StorageService);
  const router = inject(Router);

  if (storage.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree(['/auth/login']);
};
