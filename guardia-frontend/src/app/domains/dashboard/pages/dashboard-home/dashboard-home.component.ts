import { Component, inject, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { AuthStore } from '../../../auth/store/auth.store';
import { PatientInfoBarComponent } from '../../components/patient-info-bar.component';
import { RealtimeIndicatorsComponent } from '../../components/realtime-indicators.component';
import { DashboardTimelineComponent, TimelineEvent } from '../../components/dashboard-timeline.component';
import { IaSummaryComponent } from '../../components/ia-summary.component';
import { QuickActionsComponent } from '../../components/quick-actions.component';
import { SessionsService } from '../../../sessoes/services/sessions.service';
import { AnalysisService } from '../../../analise-ia/services/analysis.service';
import { SessionOut } from '../../../sessoes/models/sessions.models';
import { SessionAnalysisOut } from '../../../analise-ia/models/analysis.models';
import { finalize, Subject, takeUntil } from 'rxjs';
import { ExportPdfService } from '../../../relatorios/services/export-pdf.service';

@Component({
  selector: 'app-dashboard-home',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatSnackBarModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    PatientInfoBarComponent,
    RealtimeIndicatorsComponent,
    DashboardTimelineComponent,
    IaSummaryComponent,
    QuickActionsComponent,
  ],
  template: `
    <div class="p-6 lg:p-8 pb-12 max-w-[1600px] mx-auto">

      <!-- Header -->
      <div class="mb-6 animate-fade-in flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl lg:text-3xl font-bold text-white mb-1">Centro de Controle</h1>
          <p class="text-text-muted text-sm">Monitoramento em tempo real com IA</p>
        </div>
        
        <div class="flex items-center gap-2">
          <span class="flex items-center gap-2 text-sm text-text-subtle bg-surface2/50 px-3 py-1.5 rounded-full border border-border">
            <div class="w-2 h-2 rounded-full bg-success animate-pulse"></div>
            Sistema Online
          </span>
          <a routerLink="/sessoes/nova" mat-flat-button color="primary" class="!rounded-full">
            <mat-icon>add</mat-icon> Novo Atendimento
          </a>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        <!-- Sidebar Esquerda: Pacientes Recentes -->
        <div class="lg:col-span-1 flex flex-col gap-4 animate-fade-in" style="animation-delay: 0.1s">
          <h3 class="text-sm font-bold text-text-muted uppercase tracking-wider px-2">Em atendimento</h3>
          
          @if (loading() && recentSessions().length === 0) {
            <div class="glass-card p-6 flex justify-center">
              <mat-spinner diameter="30"></mat-spinner>
            </div>
          } @else if (recentSessions().length > 0) {
            <div class="flex flex-col gap-3">
              @for (session of recentSessions(); track session.id) {
                <div 
                  (click)="selectSession(session)"
                  class="glass-card p-4 cursor-pointer transition-all border-l-4 hover:bg-surface2/50"
                  [ngClass]="{
                    'border-l-primary-500 bg-primary-500/5 shadow-glow-primary': activeSession()?.id === session.id,
                    'border-l-transparent': activeSession()?.id !== session.id
                  }">
                  <div class="flex justify-between items-start mb-2">
                    <h4 class="font-bold text-white text-sm m-0">{{ session.title || 'Paciente Não Identificado' }}</h4>
                    <span class="text-[10px] font-mono text-text-muted">#{{ session.id }}</span>
                  </div>
                  <div class="flex flex-col gap-1 text-xs text-text-muted">
                    <span class="flex items-center gap-1"><mat-icon class="!text-[14px] !w-[14px] !h-[14px]">meeting_room</mat-icon> {{ session.patient_code || 'Sala Não Informada' }}</span>
                    <span class="flex items-center gap-1">
                      <mat-icon class="!text-[14px] !w-[14px] !h-[14px]" [ngClass]="getIraColor(session.ira_level)">{{ getIraIcon(session.ira_level) }}</mat-icon> 
                      Risco: {{ session.ira_level === 'critico' ? 'Crítico' : session.ira_level === 'moderado' ? 'Atenção' : 'Baixo' }}
                    </span>
                  </div>
                </div>
              }
            </div>
          } @else {
            <div class="glass-card p-6 text-center text-text-muted text-sm border-dashed">
              Nenhuma sessão ativa encontrada.
            </div>
          }
        </div>

        <!-- Conteúdo Principal do Dashboard -->
        <div class="lg:col-span-3 flex flex-col gap-6 animate-fade-in" style="animation-delay: 0.2s">
          
          @if (loadingSessionDetails()) {
            <div class="glass-card p-12 flex flex-col items-center justify-center gap-4 animate-processing h-[400px]">
              <mat-spinner diameter="40"></mat-spinner>
              <span class="text-text-muted font-medium">Carregando dados do atendimento...</span>
            </div>
          } @else if (activeSession()) {
            
            <!-- Patient Info Bar -->
            <div>
              <app-patient-info-bar [session]="activeSession()" />
            </div>

            <!-- Realtime Indicators -->
            <app-realtime-indicators
              [scoreVideo]="activeSession()!.score_video"
              [scoreAudio]="activeSession()!.score_audio"
              [scoreDocument]="activeSession()!.score_document"
              [iraScore]="activeSession()!.ira_score"
            />

            <!-- Timeline + IA Summary -->
            <div class="grid grid-cols-1 xl:grid-cols-5 gap-6">
              <div class="xl:col-span-3 min-h-[360px]">
                <app-dashboard-timeline
                  [sessionId]="activeSession()!.id"
                  [rawEvents]="timelineEvents()"
                />
              </div>
              <div class="xl:col-span-2 min-h-[360px]">
                <app-ia-summary
                  [iraLevel]="activeSession()!.ira_level"
                  [iraScore]="activeSession()!.ira_score"
                  [sessionId]="activeSession()!.id"
                />
              </div>
            </div>

            <!-- Quick Actions -->
            <app-quick-actions
              [sessionId]="activeSession()!.id"
              (actionClick)="handleQuickAction($event)"
            />
            
          } @else {
            <!-- Empty state (se nenhuma sessão for selecionada ou não houver) -->
            <div class="glass-card p-12 flex flex-col items-center justify-center text-center gap-4 h-[400px]">
              <div class="w-20 h-20 rounded-full bg-primary-500/10 flex items-center justify-center">
                <mat-icon class="!text-4xl text-primary-400">monitor_heart</mat-icon>
              </div>
              <h3 class="text-xl font-semibold text-white">Nenhum atendimento selecionado</h3>
              <p class="text-sm text-text-muted max-w-md">
                Selecione um paciente na lista à esquerda ou inicie um novo atendimento.
              </p>
            </div>
          }
          
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-12 pt-6 border-t border-border text-center">
        <p class="text-xs text-text-subtle">GuardIA Parto Seguro © 2025 • Todos os direitos reservados</p>
      </div>
    </div>
  `
})
export class DashboardHomePageComponent implements OnInit, OnDestroy {
  public readonly authStore = inject(AuthStore);
  private readonly sessionsService = inject(SessionsService);
  private readonly analysisService = inject(AnalysisService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly exportPdf = inject(ExportPdfService);
  private readonly destroy$ = new Subject<void>();

  recentSessions = signal<SessionOut[]>([]);
  activeSession = signal<SessionOut | null>(null);
  analysis = signal<SessionAnalysisOut | null>(null);
  timelineEvents = signal<TimelineEvent[]>([]);
  loading = signal(false);
  loadingSessionDetails = signal(false);

  ngOnInit() {
    this.loadRecentSessions();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadRecentSessions() {
    this.loading.set(true);

    // Buscar as 5 últimas sessões
    this.sessionsService.getSessions(0, 5).pipe(
      takeUntil(this.destroy$),
      finalize(() => this.loading.set(false))
    ).subscribe({
      next: (res) => {
        this.recentSessions.set(res.items);
        if (res.items.length > 0) {
          // Selecionar automaticamente a primeira sessão da lista
          this.selectSession(res.items[0]);
        }
      },
      error: () => {
        this.snackBar.open('Erro ao carregar lista de atendimentos.', 'Fechar', { duration: 3000 });
      }
    });
  }

  selectSession(session: SessionOut) {
    if (this.activeSession()?.id === session.id) {
      return; // Já selecionada
    }
    
    this.activeSession.set(session);
    this.timelineEvents.set([]);
    
    if (session.status === 'completed') {
      this.loadAnalysis(session.id);
    }
  }

  loadAnalysis(sessionId: number) {
    this.loadingSessionDetails.set(true);
    this.analysisService.getAnalysis(sessionId).pipe(
      takeUntil(this.destroy$),
      finalize(() => this.loadingSessionDetails.set(false))
    ).subscribe({
      next: (analysis) => {
        this.analysis.set(analysis);
        this.buildTimelineFromAnalysis(analysis);
      },
      error: () => {
        // Mock data
      }
    });
  }

  getIraColor(level: string | null | undefined): string {
    if (level === 'critico') return 'text-danger-500';
    if (level === 'moderado') return 'text-warning';
    return 'text-success';
  }

  getIraIcon(level: string | null | undefined): string {
    if (level === 'critico') return 'error';
    if (level === 'moderado') return 'warning';
    return 'check_circle';
  }

  private buildTimelineFromAnalysis(analysis: SessionAnalysisOut) {
    const events: TimelineEvent[] = [];

    // Build from video findings
    if (analysis.video_findings && analysis.video_findings.length > 0) {
      for (const finding of analysis.video_findings.slice(0, 6)) {
        const mins = Math.floor(finding.timestamp_seconds / 60);
        const secs = Math.floor(finding.timestamp_seconds % 60);
        const time = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        events.push({
          time,
          description: finding.description,
          classification: finding.type,
          type: finding.confidence > 0.8 ? 'warning' : finding.confidence > 0.5 ? 'neutral' : 'positive',
        });
      }
    }

    // Build from transcription segments
    if (analysis.transcription?.segments && analysis.transcription.segments.length > 0) {
      for (const seg of analysis.transcription.segments.slice(0, 4)) {
        const mins = Math.floor(seg.start / 60);
        const secs = Math.floor(seg.start % 60);
        const time = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        const shortText = seg.text.length > 60 ? seg.text.substring(0, 57) + '...' : seg.text;

        events.push({
          time,
          description: shortText,
          classification: seg.sentiment === 'positive' ? 'Interação positiva' :
                          seg.sentiment === 'negative' ? 'Atenção necessária' : 'Condição estável',
          type: seg.sentiment === 'positive' ? 'positive' :
                seg.sentiment === 'negative' ? 'warning' : 'neutral',
        });
      }
    }

    // Sort by time
    events.sort((a, b) => a.time.localeCompare(b.time));

    if (events.length > 0) {
      this.timelineEvents.set(events.slice(0, 6));
    }
  }

  handleQuickAction(actionId: string) {
    const session = this.activeSession();
    switch (actionId) {
      case 'report':
        if (session) {
          this.exportPdf.exportDashboardReport();
          this.snackBar.open('Gerando relatório...', 'OK', { duration: 2000 });
        }
        break;
      case 'video':
        if (session) {
          window.location.href = `/analise/video/${session.id}`;
        }
        break;
      case 'evaluate':
        if (session) {
          window.location.href = `/analise/multimodal/${session.id}`;
        }
        break;
      case 'note':
        this.snackBar.open('Observações em desenvolvimento.', 'OK', { duration: 2000 });
        break;
      case 'history':
        this.snackBar.open('Histórico do paciente em desenvolvimento.', 'OK', { duration: 2000 });
        break;
    }
  }
}
