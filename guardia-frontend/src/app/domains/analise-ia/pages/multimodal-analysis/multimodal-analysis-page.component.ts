import { Component, inject, OnInit, OnDestroy, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink, Router } from '@angular/router';
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
import { NotesAnalysisDialogComponent } from '../../components/notes-analysis-dialog.component';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

@Component({
  selector: 'app-multimodal-analysis-page',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatIconModule, MatButtonModule, MatProgressSpinnerModule,
    PatientInfoBarComponent, PipelineDiagramComponent,
    FusionResultComponent, FactorsPanelComponent, MatDialogModule
  ],
  template: `
    <div class="p-6 lg:p-8 max-w-[1600px] mx-auto min-h-screen">
      
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        <!-- Sidebar de Navegação de Pacientes -->
        <div class="lg:col-span-1 flex flex-col gap-4 animate-fade-in">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-bold text-primary-300 uppercase tracking-wider px-2">Em atendimento</h3>
          </div>
          
          <div class="flex flex-col gap-3">
            @for (s of allSessions(); track s.id) {
              <a [routerLink]="['/analise/multimodal', s.id]" 
                 class="glass-card p-4 transition-all border-l-4 hover:bg-surface2/50 flex flex-col gap-2 relative overflow-hidden"
                 [ngClass]="{
                   'border-l-primary-500 bg-primary-500/10 shadow-glow-primary': sessionId === s.id,
                   'border-l-transparent': sessionId !== s.id
                 }">
                
                @if (sessionId === s.id) {
                  <div class="absolute right-0 top-0 bottom-0 w-1 bg-primary-500"></div>
                }

                <div class="flex justify-between items-start">
                  <h4 class="font-bold text-white text-sm m-0 leading-tight pr-4">{{ s.title || 'Paciente Não Identificado' }}</h4>
                  <span class="text-[10px] font-mono text-text-muted mt-0.5">#{{ s.id }}</span>
                </div>
                
                <div class="flex flex-col gap-1 text-xs text-text-muted">
                  <span class="flex items-center gap-1.5"><mat-icon class="!text-[14px] !w-[14px] !h-[14px]">meeting_room</mat-icon> {{ s.patient_code || 'Não Informado' }}</span>
                  <span class="flex items-center gap-1.5">
                    <mat-icon class="!text-[14px] !w-[14px] !h-[14px]" 
                      [ngClass]="{
                        'text-danger-500': s.ira_level === 'critico',
                        'text-warning': s.ira_level === 'moderado',
                        'text-success': s.ira_level === 'baixo' || !s.ira_level
                      }">
                      {{ s.ira_level === 'critico' ? 'emergency' : s.ira_level === 'moderado' ? 'warning' : 'favorite' }}
                    </mat-icon> 
                    Risco: {{ s.ira_level === 'critico' ? 'Crítico' : s.ira_level === 'moderado' ? 'Atenção' : 'Baixo' }}
                  </span>
                </div>
              </a>
            }
          </div>
        </div>

        <!-- Conteúdo Principal -->
        <div class="lg:col-span-3 flex flex-col gap-6">
          
          <!-- Header do Conteúdo -->
          <div class="mb-2 flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
            <div>
              <h1 class="text-2xl lg:text-3xl font-bold text-white mb-1">Análise Multimodal</h1>
              <p class="text-text-muted text-sm">Fusão inteligente de dados para avaliação de risco</p>
            </div>
            
            <a mat-stroked-button routerLink="/dashboard" class="!rounded-full">
              <mat-icon>arrow_back</mat-icon>
              Voltar
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

        <!-- Anotações Clínicas Iniciais -->
        @if (session()?.notes) {
          <div class="mb-8 animate-fade-in" style="animation-delay: 0.12s">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-white m-0">Anotações Clínicas</h3>
              
              <button mat-stroked-button color="accent" class="!rounded-full border-accent-500/50 hover:bg-accent-500/10 transition-colors" (click)="openNotesAnalysis()">
                <mat-icon>psychology</mat-icon> Ver Avaliação com IA
              </button>
            </div>

            <div class="glass-card p-5">
              <p class="text-sm text-text-muted whitespace-pre-line leading-relaxed">{{ session()?.notes }}</p>
            </div>
          </div>
        }

        <!-- Fontes de dados analisadas -->
        <div class="mb-8 animate-fade-in" style="animation-delay: 0.15s">
          <h3 class="text-lg font-semibold text-white mb-4">Fontes de dados analisadas</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
            
            <!-- Video -->
            <div class="glass-card p-5 flex flex-col items-center text-center hover:!transform-none" [class.opacity-50]="videoFiles().length === 0">
              <mat-icon class="text-primary-400 !text-3xl mb-2">videocam</mat-icon>
              <h4 class="text-sm font-bold text-white">Vídeo</h4>
              <p class="text-xs text-text-muted mb-4 font-mono">{{ videoFiles().length }} arquivo(s)</p>
              @if (videoFiles().length > 0) {
                <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-success/15 text-success text-xs font-semibold rounded-full w-full justify-center mb-3">
                  <mat-icon class="!text-[14px] !w-[14px] !h-[14px]">check_circle</mat-icon> Processado
                </span>
                <a mat-stroked-button color="primary" class="w-full !rounded-full text-xs" [routerLink]="['/analise/video', sessionId]">
                  Ver Vídeo
                </a>
              } @else {
                <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-surface2 text-text-muted text-xs font-semibold rounded-full w-full justify-center">
                  Não enviado
                </span>
              }
            </div>

            <!-- Audio -->
            <div class="glass-card p-5 flex flex-col items-center text-center hover:!transform-none" [class.opacity-50]="audioFiles().length === 0">
              <mat-icon class="text-secondary-400 !text-3xl mb-2">graphic_eq</mat-icon>
              <h4 class="text-sm font-bold text-white">Áudio</h4>
              <p class="text-xs text-text-muted mb-4 font-mono">{{ audioFiles().length }} arquivo(s)</p>
              @if (audioFiles().length > 0) {
                <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-success/15 text-success text-xs font-semibold rounded-full w-full justify-center">
                  <mat-icon class="!text-[14px] !w-[14px] !h-[14px]">check_circle</mat-icon> Transcrito
                </span>
              } @else {
                <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-surface2 text-text-muted text-xs font-semibold rounded-full w-full justify-center">
                  Não enviado
                </span>
              }
            </div>

            <!-- Documentos -->
            <div class="glass-card p-5 flex flex-col items-center text-center hover:!transform-none" [class.opacity-50]="docFiles().length === 0">
              <mat-icon class="text-primary-300 !text-3xl mb-2">description</mat-icon>
              <h4 class="text-sm font-bold text-white">Documentos</h4>
              <p class="text-xs text-text-muted mb-4 font-mono">{{ docFiles().length }} arquivo(s)</p>
              @if (docFiles().length > 0) {
                <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-success/15 text-success text-xs font-semibold rounded-full w-full justify-center">
                  <mat-icon class="!text-[14px] !w-[14px] !h-[14px]">check_circle</mat-icon> Extraído
                </span>
              } @else {
                <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-surface2 text-text-muted text-xs font-semibold rounded-full w-full justify-center">
                  Não enviado
                </span>
              }
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
            <app-fusion-result 
              [score]="session()?.ira_score || 0"
              [scoreVideo]="session()?.score_video"
              [scoreAudio]="session()?.score_audio"
              [scoreDocument]="session()?.score_document"
              [scoreNotes]="session()?.score_notes"
            />
            <app-factors-panel [factors]="analysis()?.factors" />
          </div>
        </div>

      }
        </div> <!-- Fim Conteúdo Principal -->
      </div> <!-- Fim Grid -->
    </div>
  `
})
export class MultimodalAnalysisPageComponent implements OnInit, OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly sessionsService = inject(SessionsService);
  private readonly analysisService = inject(AnalysisService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly dialog = inject(MatDialog);

  sessionId: number | null = null;
  loading = signal(true);
  session = signal<SessionOut | null>(null);
  analysis = signal<SessionAnalysisOut | null>(null);
  private pollingTimer: any = null;
  
  allSessions = signal<SessionOut[]>([]);

  videoFiles = computed(() => this.session()?.media_files?.filter(f => f.media_type === 'video') || []);
  audioFiles = computed(() => this.session()?.media_files?.filter(f => f.media_type === 'audio') || []);
  docFiles = computed(() => this.session()?.media_files?.filter(f => f.media_type === 'document') || []);

  loadingNotesAnalysis = signal(false);
  notesAnalysisResult = signal<string | null>(null);

  prevSessionId = computed(() => {
    const list = this.allSessions();
    if (list.length === 0 || !this.sessionId) return null;
    const idx = list.findIndex(s => s.id === this.sessionId);
    if (idx > 0) return list[idx - 1].id;
    return null;
  });

  nextSessionId = computed(() => {
    const list = this.allSessions();
    if (list.length === 0 || !this.sessionId) return null;
    const idx = list.findIndex(s => s.id === this.sessionId);
    if (idx !== -1 && idx < list.length - 1) return list[idx + 1].id;
    return null;
  });

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.sessionId = +id;
        this.notesAnalysisResult.set(null); // Reseta a analise ao trocar paciente
        this.loadData();
      } else {
        this.loading.set(false);
      }
    });

    // Carregar sessões para habilitar a navegação Anterior/Próximo
    this.sessionsService.getSessions(0, 50).subscribe({
      next: (res) => {
        this.allSessions.set(res.items);
      }
    });
  }

  ngOnDestroy() {
    this.stopPolling();
  }

  startPolling() {
    if (!this.pollingTimer) {
      this.pollingTimer = setInterval(() => {
        this.loadData(true);
      }, 5000);
    }
  }

  stopPolling() {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = null;
    }
  }

  loadData(isPolling = false) {
    if (!isPolling) this.loading.set(true);
    this.sessionsService.getSession(this.sessionId!).subscribe({
      next: (session) => {
        this.session.set(session);
        if (!isPolling) this.loading.set(false);
        
        const needsPolling = 
          session.status === 'processing' || 
          session.media_files?.some(f => f.status === 'processing') || 
          (!!session.notes && session.score_notes === null);
          
        if (needsPolling) {
          this.startPolling();
        } else {
          this.stopPolling();
        }

        if (session.status === 'completed' || session.score_notes !== null || session.ira_score !== null) {
          this.loadAnalysis();
        }
      },
      error: () => {
        if (!isPolling) {
          this.snackBar.open('Erro ao carregar sessão.', 'Fechar', { duration: 3000 });
          this.loading.set(false);
        }
        this.stopPolling();
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

  openNotesAnalysis() {
    if (!this.analysis()?.notes_analysis_text) {
      this.snackBar.open('Análise textual ainda não está disponível ou está sendo processada.', 'Fechar', { duration: 3000 });
      return;
    }
    
    this.dialog.open(NotesAnalysisDialogComponent, {
      data: { text: this.analysis()?.notes_analysis_text },
      panelClass: 'custom-dialog-container',
      backdropClass: 'custom-backdrop',
      width: '600px'
    });
  }
}
