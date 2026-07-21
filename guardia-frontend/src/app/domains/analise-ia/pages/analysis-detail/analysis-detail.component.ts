import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs';

import { AnalysisService } from '../../services/analysis.service';
import { SessionAnalysisOut } from '../../models/analysis.models';
import { TranscriptionViewerComponent } from '../../components/transcription-viewer.component';
import { AITimelineComponent } from '../../components/ai-timeline.component';
import { RiskJustificationsComponent } from '../../components/risk-justifications.component';

@Component({
  selector: 'app-analysis-detail',
  standalone: true,
  imports: [
    CommonModule, 
    MatIconModule, 
    MatButtonModule, 
    MatProgressSpinnerModule,
    RouterLink,
    TranscriptionViewerComponent,
    AITimelineComponent,
    RiskJustificationsComponent
  ],
  template: `
    <div class="p-8 max-w-[1600px] mx-auto min-h-screen">
      <!-- Header -->
      <div class="mb-8 flex items-center justify-between animate-fade-in">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <a mat-icon-button color="primary" routerLink="/dashboard">
              <mat-icon>arrow_back</mat-icon>
            </a>
            <h1 class="text-3xl font-bold text-white m-0">Análise de IA</h1>
          </div>
          <p class="text-text-muted ml-12">Detalhamento dos achados, transcrições e métricas de risco assistencial da Sessão #{{ sessionId }}</p>
        </div>
        
        @if (analysis()?.status === 'completed') {
          <div class="flex items-center gap-2 px-4 py-2 bg-success/10 border border-success/30 text-success rounded-full font-medium text-sm">
            <mat-icon class="text-[18px] w-[18px] h-[18px]">check_circle</mat-icon>
            Análise Concluída
          </div>
        }
      </div>

      <!-- Loading State -->
      @if (loading()) {
        <div class="flex flex-col items-center justify-center h-[50vh] gap-4">
          <mat-spinner diameter="48" class="text-primary-500"></mat-spinner>
          <p class="text-text-muted">Carregando processamento de inteligência artificial...</p>
        </div>
      } 
      <!-- Error / Empty State -->
      @else if (!analysis()) {
        <div class="glass-card p-12 flex flex-col items-center text-center">
          <div class="w-20 h-20 rounded-full bg-surface2 flex items-center justify-center text-text-muted mb-4">
            <mat-icon class="text-4xl">search_off</mat-icon>
          </div>
          <h3 class="text-xl font-bold text-white mb-2">Análise não encontrada</h3>
          <p class="text-text-subtle max-w-md">Não foi possível carregar os dados desta sessão ou ela ainda não possui arquivos processados.</p>
          <button mat-flat-button color="primary" class="mt-6" routerLink="/dashboard">Voltar ao Dashboard</button>
        </div>
      }
      <!-- Processing State -->
      @else if (analysis()?.status === 'processing' || analysis()?.status === 'pending') {
        <div class="glass-card p-12 flex flex-col items-center text-center animate-pulse">
          <div class="w-24 h-24 rounded-full bg-secondary-500/10 flex items-center justify-center text-secondary-500 mb-6 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary-400 opacity-20"></span>
            <mat-icon class="text-5xl animate-spin">memory</mat-icon>
          </div>
          <h3 class="text-2xl font-bold text-white mb-3">IA Processando Sessão</h3>
          <p class="text-text-muted max-w-lg mb-6">Nossos algoritmos estão analisando os vídeos, áudios e documentos desta sessão. Isso pode levar alguns minutos.</p>
          <div class="w-64 h-2 bg-surface2 rounded-full overflow-hidden">
            <div class="h-full bg-secondary-500 rounded-full w-1/2 animate-[progress_2s_ease-in-out_infinite]"></div>
          </div>
        </div>
      }
      <!-- Content State -->
      @else {
        <!-- Risk Cards -->
        <div class="mb-6 animate-slide-up" style="animation-delay: 0.1s">
          <app-risk-justifications [details]="analysis()!.risk_details"></app-risk-justifications>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[700px] mb-8">
          <!-- Transcription (Takes 2 columns) -->
          <div class="lg:col-span-2 h-full animate-slide-up" style="animation-delay: 0.2s">
            <app-transcription-viewer 
              [segments]="analysis()!.transcription?.segments || []">
            </app-transcription-viewer>
          </div>
          
          <!-- Timeline (Takes 1 column) -->
          <div class="h-full animate-slide-up" style="animation-delay: 0.3s">
            <app-ai-timeline
              [findings]="analysis()!.video_findings || []">
            </app-ai-timeline>
          </div>
        </div>
      }
    </div>
  `
})
export class AnalysisDetailPageComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly analysisService = inject(AnalysisService);
  private readonly snackBar = inject(MatSnackBar);

  sessionId: number | null = null;
  loading = signal(true);
  analysis = signal<SessionAnalysisOut | null>(null);

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.sessionId = +id;
        this.loadAnalysis();
      }
    });
  }

  loadAnalysis() {
    if (!this.sessionId) return;
    
    this.loading.set(true);
    this.analysisService.getAnalysis(this.sessionId)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (res) => {
          this.analysis.set(res);
        },
        error: (err) => {
          console.error(err);
          this.snackBar.open('Falha ao carregar análise. A sessão pode não existir ou a IA falhou.', 'Fechar', { duration: 4000 });
        }
      });
  }
}
