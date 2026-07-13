import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs';

import { AnalysisService } from '../../services/analysis.service';
import { SessionsService } from '../../../sessoes/services/sessions.service';
import { SessionAnalysisOut } from '../../models/analysis.models';
import { SessionOut } from '../../../sessoes/models/sessions.models';
import { EmotionMeterComponent } from '../../../../shared/components/emotion-meter.component';
import { PersonCardComponent } from '../../components/person-card.component';

@Component({
  selector: 'app-video-analysis-page',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatIconModule, MatButtonModule,
    MatTabsModule, MatProgressSpinnerModule,
    EmotionMeterComponent, PersonCardComponent
  ],
  template: `
    <div class="p-6 lg:p-8 max-w-[1600px] mx-auto min-h-screen">

      <!-- Header -->
      <div class="mb-6 flex items-center justify-between animate-fade-in">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <a mat-icon-button routerLink="/dashboard" class="!text-text-muted">
              <mat-icon>arrow_back</mat-icon>
            </a>
            <span class="text-text-muted text-sm">Voltar</span>
          </div>
          <h1 class="text-2xl lg:text-3xl font-bold text-white ml-1">Análise de Vídeo</h1>
          <p class="text-text-muted text-sm ml-1">Análise inteligente de comportamentos e expressões</p>
        </div>
      </div>

      @if (loading()) {
        <div class="flex flex-col items-center justify-center h-[50vh] gap-4">
          <mat-spinner diameter="48"></mat-spinner>
          <p class="text-text-muted">Carregando análise de vídeo...</p>
        </div>
      } @else {

      <!-- Video Player + Pessoas -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8 animate-fade-in" style="animation-delay: 0.1s">
        <!-- Video Player -->
        <div class="lg:col-span-3">
          <div class="glass-card overflow-hidden hover:!transform-none">
            <div class="relative bg-black aspect-video flex items-center justify-center">
              <!-- Placeholder video -->
              <div class="absolute inset-0 bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center">
                <img src="https://images.unsplash.com/photo-1631815589968-fdb09a223b1e?w=800&q=80"
                  alt="Sala de parto"
                  class="w-full h-full object-cover opacity-60" />
              </div>

              <!-- Overlay badges -->
              <div class="absolute top-4 left-4 flex items-center gap-2">
                <span class="bg-danger-500 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1 animate-pulse">
                  <span class="w-2 h-2 bg-white rounded-full"></span> AO VIVO
                </span>
                <span class="bg-black/60 text-white text-xs px-3 py-1 rounded-full font-mono">00:12:45</span>
              </div>

              <!-- Play button -->
              <div class="relative z-10 w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center cursor-pointer hover:bg-white/30 transition-colors">
                <mat-icon class="!text-4xl text-white">play_arrow</mat-icon>
              </div>

              <!-- Bottom controls -->
              <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                <div class="flex items-center gap-3">
                  <button class="text-white"><mat-icon>play_arrow</mat-icon></button>
                  <button class="text-white"><mat-icon>skip_previous</mat-icon></button>
                  <button class="text-white"><mat-icon>skip_next</mat-icon></button>
                  <div class="flex-1 h-1 bg-white/20 rounded-full mx-3">
                    <div class="h-full bg-primary-500 rounded-full w-1/3"></div>
                  </div>
                  <span class="text-white text-xs font-mono">1:09s</span>
                  <button class="text-white"><mat-icon>volume_up</mat-icon></button>
                  <button class="text-white"><mat-icon>fullscreen</mat-icon></button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pessoas identificadas -->
        <div class="lg:col-span-1">
          <div class="glass-card p-5 h-full hover:!transform-none">
            <h3 class="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <mat-icon class="text-primary-400 !text-lg">people</mat-icon>
              Pessoas identificadas
            </h3>
            <div class="flex flex-col divide-y divide-border">
              @for (person of people; track person.name) {
                <app-person-card [name]="person.name" [role]="person.role" />
              }
              @if (people.length === 0) {
                <p class="text-sm text-text-muted p-2">Nenhuma pessoa identificada.</p>
              }
            </div>
          </div>
        </div>
      </div>

      <!-- Análise da IA em tempo real -->
      <div class="mb-8 animate-fade-in" style="animation-delay: 0.2s">
        <h3 class="text-lg font-semibold text-white mb-4">Análise da IA em tempo real</h3>

        <!-- Tabs -->
        <div class="flex flex-wrap gap-2 mb-6">
          @for (tab of tabs; track tab) {
            <button
              (click)="activeTab.set(tab)"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              [class]="activeTab() === tab ? 'bg-primary-500 text-white' : 'bg-surface2/50 text-text-muted hover:bg-surface2 hover:text-white'">
              {{ tab }}
            </button>
          }
        </div>

        <!-- Tab content: Expressões faciais -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Face analysis card -->
          <div class="glass-card p-6 hover:!transform-none">
            <div class="flex items-center gap-4 mb-4">
              <div class="w-20 h-20 rounded-xl bg-surface2 overflow-hidden border-2 border-primary-500/30">
                <div class="w-full h-full bg-gradient-to-br from-primary-500/20 to-surface2 flex items-center justify-center">
                  <mat-icon class="!text-3xl text-primary-400">face</mat-icon>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-text-muted">Confiança da análise</span>
              <div class="flex-1 h-1.5 bg-surface2 rounded-full overflow-hidden">
                <div class="h-full bg-primary-500 rounded-full" [style.width]="confidence + '%'"></div>
              </div>
              <span class="text-xs font-semibold text-primary-400">{{ confidence }}%</span>
            </div>
          </div>

          <!-- Emoções detectadas -->
          <div class="glass-card p-6 hover:!transform-none">
            <h4 class="text-sm font-bold text-white mb-4">Emoções detectadas</h4>
            <div class="flex flex-col gap-3">
              @for (emotion of emotions; track emotion.label) {
                <app-emotion-meter [label]="emotion.label" [value]="emotion.value" [color]="emotion.color" />
              }
              @if (emotions.length === 0) {
                <p class="text-sm text-text-muted">Aguardando dados...</p>
              }
            </div>
          </div>

          <!-- Resumo da análise -->
          <div class="glass-card p-6 hover:!transform-none">
            <h4 class="text-sm font-bold text-white mb-4">Resumo da análise</h4>
            <div class="flex flex-col gap-3 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-text-muted">Estado emocional:</span>
                <span class="font-semibold text-success">Positivo</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-text-muted">Nível de conforto:</span>
                <span class="font-semibold text-success">Alto</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-text-muted">Interações positivas:</span>
                <span class="font-semibold text-primary-400">{{ positiveInteractions }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-text-muted">Sinais de preocupação:</span>
                <span class="font-semibold text-text-muted">{{ concernSigns }}</span>
              </div>
              <div class="flex items-center justify-between pt-2 border-t border-border">
                <span class="text-text-muted">Risco atual:</span>
                <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold"
                  [class]="riskBadgeClass">
                  <mat-icon class="!text-sm !w-3.5 !h-3.5">{{ riskIcon }}</mat-icon>
                  {{ riskLabel }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Eventos detectados -->
      <div class="mb-8 animate-fade-in" style="animation-delay: 0.3s">
        <h3 class="text-lg font-semibold text-white mb-4">Eventos detectados</h3>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          @if (analysis()?.video_findings?.length) {
            @for (event of analysis()?.video_findings; track event.description) {
              <div class="glass-card p-4 text-center hover:border-primary-500/30">
                <div class="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-2"
                     [ngClass]="getEventIconClass(event.type)">
                  <mat-icon class="!text-lg">{{ getEventIcon(event.type) }}</mat-icon>
                </div>
                <p class="text-xs font-medium text-white mb-1">{{ event.description }}</p>
                <p class="text-[10px] text-text-subtle font-mono">{{ formatTimestamp(event.timestamp_seconds) }}</p>
              </div>
            }
          } @else {
            <p class="text-sm text-text-muted col-span-5">Nenhum evento processado ainda.</p>
          }
        </div>
        <div class="mt-3 text-right">
          <a class="text-xs text-primary-400 hover:underline cursor-pointer">Ver todos os eventos →</a>
        </div>
      </div>

      <!-- Linha do tempo -->
      <div class="glass-card p-6 hover:!transform-none animate-fade-in" style="animation-delay: 0.4s">
        <h3 class="text-sm font-bold text-white mb-4">Linha do tempo da análise</h3>
        <div class="relative">
          <!-- Timeline bar -->
          <div class="h-2 bg-surface2 rounded-full relative overflow-hidden">
            <div class="absolute inset-y-0 left-0 w-[85%] bg-gradient-to-r from-success via-primary-500 to-warning rounded-full"></div>
          </div>
          <!-- Time labels -->
          <div class="flex justify-between mt-2 text-[10px] text-text-subtle font-mono">
            <span>10:00</span><span>10:12</span><span>10:24</span><span>10:36</span><span>10:48</span><span>11:00</span>
          </div>
          <!-- Legend -->
          <div class="flex items-center gap-4 mt-3 text-xs text-text-muted">
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-success"></span> Emoções positivas</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-primary-500"></span> Interações</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-warning"></span> Sinais de atenção</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-danger-500"></span> Eventos</span>
          </div>
        </div>
      </div>

      }
    </div>
  `
})
export class VideoAnalysisPageComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly analysisService = inject(AnalysisService);
  private readonly sessionsService = inject(SessionsService);
  private readonly snackBar = inject(MatSnackBar);

  sessionId: number | null = null;
  loading = signal(true);
  analysis = signal<SessionAnalysisOut | null>(null);
  session = signal<SessionOut | null>(null);
  activeTab = signal('Expressões faciais');

  tabs = ['Expressões faciais', 'Emoções', 'Linguagem corporal', 'Interações', 'Ambiente'];

  people: { name: string; role: 'paciente' | 'medico' | 'enfermeiro' | 'acompanhante' }[] = [];

  emotions: { label: string; value: number; color: string }[] = [];

  confidence = 0;

  getEventIcon(type: string): string {
    if (type === 'interaction') return 'forum';
    if (type === 'concern' || type === 'pain' || type === 'risk') return 'warning';
    return 'visibility';
  }

  getEventIconClass(type: string): string {
    if (type === 'interaction') return 'bg-primary-500/10 text-primary-400';
    if (type === 'concern' || type === 'pain' || type === 'risk') return 'bg-warning/10 text-warning';
    return 'bg-success/10 text-success';
  }

  formatTimestamp(seconds: number): string {
    if (!seconds) return '00:00';
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  }

  positiveInteractions = 0;
  concernSigns = 0;
  riskLabel = 'Baixo';
  riskIcon = 'check_circle';
  riskBadgeClass = 'bg-success/15 text-success';

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
        this.updateFromSession(session);
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
        this.updateFromAnalysis(analysis);
      }
    });
  }

  private updateFromSession(session: SessionOut) {
    if (session.ira_level === 'critico') {
      this.riskLabel = 'Crítico';
      this.riskIcon = 'error';
      this.riskBadgeClass = 'bg-danger-500/15 text-danger-500';
    } else if (session.ira_level === 'moderado') {
      this.riskLabel = 'Moderado';
      this.riskIcon = 'warning';
      this.riskBadgeClass = 'bg-warning/15 text-warning';
    }
  }

  private updateFromAnalysis(analysis: SessionAnalysisOut) {
    // Update emotions from transcription sentiment if available
    if (analysis.transcription?.segments) {
      const segs = analysis.transcription.segments;
      const pos = segs.filter(s => s.sentiment === 'positive').length;
      const neg = segs.filter(s => s.sentiment === 'negative').length;
      this.positiveInteractions = pos;
      this.concernSigns = neg;
    }

    // Attempt to extract video metrics
    if (analysis.video_analyses) {
      const keys = Object.keys(analysis.video_analyses);
      if (keys.length > 0) {
        const vidRes = analysis.video_analyses[keys[0]];
        if (vidRes && vidRes.components) {
          this.confidence = Math.round(vidRes.ira_score || 0);
          this.emotions = [
            { label: 'Score Emocional', value: vidRes.components.emotion_score || 0, color: '#16A34A' },
            { label: 'Risco de Objetos', value: vidRes.components.object_risk_score || 0, color: '#EAB308' },
            { label: 'Postura', value: vidRes.components.pose_score || 0, color: '#3B82F6' },
          ];
        }
      }
    }
  }
}
