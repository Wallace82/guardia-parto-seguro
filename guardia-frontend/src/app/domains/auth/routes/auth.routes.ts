import { Routes } from '@angular/router';

export const AUTH_ROUTES: Routes = [
  {
    path: 'login',
    loadComponent: () => import('../pages/login/login.page').then(c => c.LoginPageComponent)
  },
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  }
];
