import { Routes } from '@angular/router';

export const REPORTS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('../pages/reports-page/reports-page.component').then(c => c.ReportsPageComponent)
  }
];
