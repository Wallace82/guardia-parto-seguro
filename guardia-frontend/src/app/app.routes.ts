import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    loadChildren: () =>
      import('./domains/auth/routes/auth.routes').then((r) => r.AUTH_ROUTES),
  },
  {
    path: '',
    loadComponent: () =>
      import('./layout/main-layout/main-layout.component').then(
        (m) => m.MainLayoutComponent,
      ),
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadChildren: () =>
          import('./domains/dashboard/routes/dashboard.routes').then(
            (r) => r.DASHBOARD_ROUTES,
          ),
      },
      {
        path: 'sessoes',
        loadChildren: () =>
          import('./domains/sessoes/routes/sessions.routes').then(
            (r) => r.SESSIONS_ROUTES,
          ),
      },
      {
        path: 'analise',
        loadChildren: () =>
          import('./domains/analise-ia/routes/analysis.routes').then(
            (r) => r.ANALYSIS_ROUTES,
          ),
      },
      {
        path: 'alertas',
        loadChildren: () =>
          import('./domains/alertas/routes/alerts.routes').then(
            (r) => r.ALERTS_ROUTES,
          ),
      },
      {
        path: 'relatorios',
        loadChildren: () => import('./domains/relatorios/routes/reports.routes').then((r) => r.REPORTS_ROUTES),
        // Force recompile
      },
      {
        path: 'admin',
        canActivate: [roleGuard(['admin', 'gestor'])],
        loadChildren: () => import('./domains/admin/routes/admin.routes').then((r) => r.ADMIN_ROUTES),
      },
    ],
  },
  {
    path: '**',
    redirectTo: '/dashboard',
  },
];
