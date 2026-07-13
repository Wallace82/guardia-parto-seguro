import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs';

import { SessionsService } from '../../../sessoes/services/sessions.service';
import { AnalysisService } from '../../services/analysis.service';
import { SessionOut } from '../../../sessoes/models/sessions.models';
import { SessionAnalysisOut } from '../../models/analysis.models';
import { PatientInfoBarComponent } from '../../../dashboard/components/patient-info-bar.component';
import { PipelineDiagramComponent } from '../../components/pipeline-diagram.component';
import { FusionResultComponent } from '../../components/fusion-result.component';
import { FactorsPanelComponent } from '../../components/factors-panel.component';

@Component({
  selector: 'app-multimodal-analysis-page',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatIconModule, MatButtonModule, MatProgressSpinnerModule,
    PatientInfoBarComponent, PipelineDiagramComponent,
    FusionResultComponent, FactorsPanelComponent
  ],
  template: `
    <div class="p-6 lg:p-8 max-w-[1600px] mx-auto min-h-screen">
      
      <!-- Header -->
      <div class="mb-6 flex items-center justify-between animate-fade-in">
        <div>
          <h1 class="text-2xl lg:text-3xl font-bold text-white mb-1">Análise Multimodal</h1>
          <p class="text-text-muted text-sm">Fusão inteligente de dados para avaliação de risco</p>
        </div>
        <a mat-stroked-button routerLink="/dashboard" class="!rounded-full">
          <mat-icon>arrow_back</mat-icon>
          Voltar ao Centro de Controle
        </a>
      </div>

      @if (loading()) {
        <div class="flex flex-col items-center justify-center h-[50vh] gap-4">
          <mat-spinner diameter="48"></mat-spinner>
          <p class="text-text-muted">Carregando análise multimodal...</p>
        </div>
      } @else if (session()) {

        <!-- Patient Info Bar -->
        <div class="mb-8 animate-fade-in" style="animation-delay: 0.1s">
          <app-patient-info-bar [session]="session()" />
        </div>

        <!-- Fontes de dados analisadas -->
        <div class="mb-8 animate-fade-in" style="animation-delay: 0.15s">
          <h3 class="text-lg font-semibold text-white mb-4">Fontes de dados analisadas</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            
            <div class="glass-card p-5 flex flex-col items-center text-center hover:!transform-none">
              <mat-icon class="text-primary-400 !text-3xl mb-2">videocam</mat-icon>
              <h4 class="text-sm font-bold text-white">Vídeo</h4>
              <p class="text-xs text-text-muted mb-4 font-mono">15 min 32s</p>
              <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-success/15 text-success text-xs font-semibold rounded-full w-full justify-center">
                <mat-icon class="!text-[14px] !w-[14px] !h-[14px]">check_circle</mat-icon>
                Processado
              </span>
            </div>

            <div class="glass-card p-5 flex flex-col items-center text-center hover:!transform-none">
              <mat-icon class="text-secondary-400 !text-3xl mb-2">graphic_eq</mat-icon>
              <h4 class="text-sm font-bold text-white">Áudio</h4>
              <p class="text-xs text-text-muted mb-4 font-mono">08 min 47s</p>
              <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-success/15 text-success text-xs font-semibold rounded-full w-full justify-center">
                <mat-icon class="!text-[14px] !w-[14px] !h-[14px]">check_circle</mat-icon>
                Transcrito
              </span>
            </div>

            <div class="glass-card p-5 flex flex-col items-center text-center hover:!transform-none">
              <mat-icon class="text-primary-300 !text-3xl mb-2">description</mat-icon>
              <h4 class="text-sm font-bold text-white">Documentos</h4>
              <p class="text-xs text-text-muted mb-4 font-mono">3 arquivos</p>
              <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-success/15 text-success text-xs font-semibold rounded-full w-full justify-center">
                <mat-icon class="!text-[14px] !w-[14px] !h-[14px]">check_circle</mat-icon>
                Extraído
              </span>
            </div>

            <div class="glass-card p-5 flex flex-col items-center text-center hover:!transform-none">
              <mat-icon class="text-danger-400 !text-3xl mb-2">monitor_heart</mat-icon>
              <h4 class="text-sm font-bold text-white">Sinais vitais</h4>
              <p class="text-xs text-text-muted mb-4 font-mono">Tempo real</p>
              <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-success/15 text-success text-xs font-semibold rounded-full w-full justify-center">
                <mat-icon class="!text-[14px] !w-[14px] !h-[14px]">check_circle</mat-icon>
                Monitorado
              </span>
            </div>

          </div>
        </div>

        <!-- Pipeline Diagram -->
        <div class="mb-8 animate-fade-in" style="animation-delay: 0.2s">
          <app-pipeline-diagram />
        </div>

        <!-- Fusion Result & Factors -->
        <div class="mb-12 animate-fade-in" style="animation-delay: 0.25s">
          <div class="grid grid-cols-1 gap-8">
            <app-fusion-result [score]="session()?.ira_score || 0" />
            <app-factors-panel [factors]="analysis()?.factors" />
          </div>
        </div>

      }
    </div>
  `
})
export class MultimodalAnalysisPageComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly sessionsService = inject(SessionsService);
  private readonly analysisService = inject(AnalysisService);
  private readonly snackBar = inject(MatSnackBar);

  sessionId: number | null = null;
  loading = signal(true);
  session = signal<SessionOut | null>(null);
  analysis = signal<SessionAnalysisOut | null>(null);

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.sessionId = +id;
        this.loadData();
      } else {
        this.loading.set(false);
      }
    });
  }

  loadData() {
    this.loading.set(true);
    this.sessionsService.getSession(this.sessionId!).pipe(
      finalize(() => this.loading.set(false))
    ).subscribe({
      next: (session) => {
        this.session.set(session);
        if (session.status === 'completed') {
          this.loadAnalysis();
        }
      },
      error: () => {
        this.snackBar.open('Erro ao carregar sessão.', 'Fechar', { duration: 3000 });
      }
    });
  }

  loadAnalysis() {
    this.analysisService.getAnalysis(this.sessionId!).subscribe({
      next: (analysis) => {
        this.analysis.set(analysis);
      }
    });
  }
}
