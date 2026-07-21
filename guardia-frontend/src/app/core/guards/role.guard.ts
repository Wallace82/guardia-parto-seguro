import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthStore } from '../../domains/auth/store/auth.store';
import { MatSnackBar } from '@angular/material/snack-bar';

export const roleGuard = (allowedRoles: string[]): CanActivateFn => {
  return () => {
    const authStore = inject(AuthStore);
    const router = inject(Router);
    const snackBar = inject(MatSnackBar);
    
    const user = authStore.user();
    
    if (user && allowedRoles.includes(user.role)) {
      return true;
    }
    
    snackBar.open('Acesso negado: Você não tem permissão para acessar esta área.', 'OK', { duration: 4000 });
    return router.createUrlTree(['/dashboard']);
  };
};
