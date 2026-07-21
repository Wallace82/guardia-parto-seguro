import { Routes } from '@angular/router';

export const ANALYSIS_ROUTES: Routes = [
  {
    path: 'video/:id',
    loadComponent: () => import('../pages/video-analysis/video-analysis-page.component').then(c => c.VideoAnalysisPageComponent)
  },
  {
    path: 'multimodal/:id',
    loadComponent: () => import('../pages/multimodal-analysis/multimodal-analysis-page.component').then(c => c.MultimodalAnalysisPageComponent)
  },
  {
    path: ':id',
    loadComponent: () => import('../pages/analysis-detail/analysis-detail.component').then(c => c.AnalysisDetailPageComponent)
  }
];
