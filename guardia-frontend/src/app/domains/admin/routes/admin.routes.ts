import { Routes } from '@angular/router';

export const ADMIN_ROUTES: Routes = [
  {
    path: 'usuarios',
    loadComponent: () => import('../pages/users-page/users-page.component').then(c => c.AdminUsersPageComponent)
  },
  {
    path: '',
    redirectTo: 'usuarios',
    pathMatch: 'full'
  }
];
