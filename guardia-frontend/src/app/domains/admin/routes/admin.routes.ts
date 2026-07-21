import { Routes } from '@angular/router';

export const ADMIN_ROUTES: Routes = [
  {
    path: 'usuarios',
    loadComponent: () => import('../pages/users-page/users-page.component').then(c => c.AdminUsersPageComponent)
  },
  {
    path: 'auditoria',
    loadComponent: () => import('../pages/audit-page/audit-page.component').then(c => c.AdminAuditPageComponent)
  },
  {
    path: 'configuracoes',
    loadComponent: () => import('../pages/settings-page/settings-page.component').then(c => c.AdminSettingsPageComponent)
  },
  {
    path: '',
    redirectTo: 'usuarios',
    pathMatch: 'full'
  }
];
