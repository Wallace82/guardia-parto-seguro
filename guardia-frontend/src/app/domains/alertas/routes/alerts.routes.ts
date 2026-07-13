import { Routes } from '@angular/router';

export const ALERTS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('../pages/alerts-center/alerts-center.component').then(c => c.AlertsCenterPageComponent)
  }
];
