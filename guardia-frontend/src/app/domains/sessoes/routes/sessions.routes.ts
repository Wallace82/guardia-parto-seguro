import { Routes } from '@angular/router';

export const SESSIONS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('../pages/session-list-page/session-list-page.component').then(c => c.SessionListPageComponent)
  },
  {
    path: 'nova',
    loadComponent: () => import('../pages/session-create-page/session-create-page.component').then(c => c.SessionCreatePageComponent)
  },
  {
    path: ':id',
    loadComponent: () => import('../pages/session-detail-page/session-detail-page.component').then(c => c.SessionDetailPageComponent)
  }
];
