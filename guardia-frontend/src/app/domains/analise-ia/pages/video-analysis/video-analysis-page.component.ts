import { Component, inject, OnInit, OnDestroy, signal, computed, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs';

import { AnalysisService } from '../../services/analysis.service';
import { SessionsService } from '../../../sessoes/services/sessions.service';
import { SessionAnalysisOut } from '../../models/analysis.models';
import { SessionOut, MediaFile } from '../../../sessoes/models/sessions.models';
import { EmotionMeterComponent } from '../../../../shared/components/emotion-meter.component';
import { PersonCardComponent } from '../../components/person-card.component';
import { environment } from '../../../../../environments/environment';
import { StorageService } from '../../../../core/services/storage.service';

interface VideoFileData {
  mediaFile: MediaFile;
  videoAnalysis: any;
  blobUrl: string;
}

interface TimelineEvent {
  time: number;
  description: string;
  type: string;
  confidence: number;
  videoName: string;
  riskLevel: 'low' | 'medium' | 'high';
}

@Component({
  selector: 'app-video-analysis-page',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatIconModule, MatButtonModule,
    MatProgressSpinnerModule,
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
          <h1 class="text-2xl lg:text-3xl font-bold text-white ml-1">Análise de Vídeo — Visão Computacional</h1>
          <p class="text-text-muted text-sm ml-1">
            Sessão #{{ sessionId }} · {{ session()?.title || 'Carregando...' }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold"
            [class]="globalRiskBadgeClass()">
            <mat-icon class="!text-sm !w-3.5 !h-3.5">{{ globalRiskIcon() }}</mat-icon>
            IGA: {{ session()?.ira_score?.toFixed(1) || 'N/A' }}
          </span>
        </div>
      </div>

      @if (loading()) {
        <div class="flex flex-col items-center justify-center h-[50vh] gap-4">
          <mat-spinner diameter="48"></mat-spinner>
          <p class="text-text-muted">Carregando análise de vídeo...</p>
        </div>
      } @else {

      <!-- Video player + Sidebar -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8 animate-fade-in" style="animation-delay: 0.1s">
        <!-- Video Player -->
        <div class="lg:col-span-3">
          <div class="glass-card overflow-hidden hover:!transform-none">
            <div class="relative bg-black aspect-video flex items-center justify-center">
              @if (currentVideoUrl()) {
                <video #videoPlayer
                  class="w-full h-full object-contain"
                  [src]="currentVideoUrl()"
                  (timeupdate)="onTimeUpdate()"
                  (loadedmetadata)="onMetadataLoaded()"
                  (play)="isPlaying.set(true)"
                  (pause)="isPlaying.set(false)"
                  (ended)="isPlaying.set(false)"
                  crossorigin="anonymous">
                </video>
              } @else {
                <div class="flex flex-col items-center justify-center gap-3">
                  <mat-icon class="!text-5xl text-text-subtle">videocam_off</mat-icon>
                  <p class="text-text-muted text-sm">Nenhum vídeo disponível</p>
                </div>
              }

              <!-- Overlay: análise badge -->
              <div class="absolute top-4 left-4 flex items-center gap-2 pointer-events-none">
                <span class="bg-primary-500/80 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                  <mat-icon class="!text-sm !w-3.5 !h-3.5">smart_display</mat-icon>
                  Análise IA
                </span>
                @if (currentVideoFile()) {
                  <span class="bg-black/60 text-white text-xs px-3 py-1 rounded-full font-mono">
                    {{ currentVideoFile()!.mediaFile.filename }}
                  </span>
                }
              </div>

              <!-- Score overlay right -->
              @if (currentVideoFile()?.videoAnalysis) {
                <div class="absolute top-4 right-4 flex flex-col gap-1.5 pointer-events-none">
                  <span class="text-xs font-bold px-3 py-1 rounded-full"
                    [class]="getScoreBadgeClass(currentVideoFile()!.mediaFile.analysis_score)">
                    Score: {{ currentVideoFile()!.mediaFile.analysis_score?.toFixed(1) || 'N/A' }}
                  </span>
                </div>
              }

              <!-- Play button center overlay -->
              @if (!isPlaying()) {
                <div class="absolute inset-0 flex items-center justify-center cursor-pointer z-10"
                  (click)="togglePlay()">
                  <div class="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors">
                    <mat-icon class="!text-4xl text-white">play_arrow</mat-icon>
                  </div>
                </div>
              }

              <!-- Bottom controls -->
              <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 z-20">
                <div class="flex items-center gap-3">
                  <button class="text-white hover:text-primary-400 transition-colors" (click)="togglePlay()">
                    <mat-icon>{{ isPlaying() ? 'pause' : 'play_arrow' }}</mat-icon>
                  </button>
                  <!-- Progress bar -->
                  <div class="flex-1 h-1.5 bg-white/20 rounded-full cursor-pointer relative group"
                    (click)="seekVideo($event)">
                    <div class="h-full bg-primary-500 rounded-full transition-all duration-150"
                      [style.width.%]="videoProgress()"></div>
                    <div class="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                      [style.left.%]="videoProgress()"></div>
                  </div>
                  <span class="text-white text-xs font-mono min-w-[80px] text-right">
                    {{ formatTime(currentTime()) }} / {{ formatTime(duration()) }}
                  </span>
                  <button class="text-white hover:text-primary-400 transition-colors" (click)="toggleMute()">
                    <mat-icon>{{ isMuted() ? 'volume_off' : 'volume_up' }}</mat-icon>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Video selector tabs -->
          @if (videoFiles().length > 1) {
            <div class="flex flex-wrap gap-2 mt-3">
              @for (vf of videoFiles(); track vf.mediaFile.id; let i = $index) {
                <button (click)="selectVideo(i)"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2"
                  [class]="selectedVideoIndex() === i
                    ? 'bg-primary-500 text-white'
                    : 'bg-surface2/50 text-text-muted hover:bg-surface2 hover:text-white'">
                  <mat-icon class="!text-base">videocam</mat-icon>
                  {{ vf.mediaFile.filename }}
                  <span class="text-[10px] px-1.5 py-0.5 rounded-full"
                    [class]="getScoreBadgeClass(vf.mediaFile.analysis_score)">
                    {{ vf.mediaFile.analysis_score?.toFixed(0) || '?' }}
                  </span>
                </button>
              }
            </div>
          }
        </div>

        <!-- Sidebar: Resumo do vídeo selecionado -->
        <div class="lg:col-span-1 flex flex-col gap-4">
          <!-- Score do vídeo atual -->
          <div class="glass-card p-5 hover:!transform-none">
            <h3 class="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <mat-icon class="text-primary-400 !text-lg">analytics</mat-icon>
              Score do Vídeo
            </h3>
            @if (currentVideoFile()?.videoAnalysis) {
              <div class="flex items-center justify-center mb-4">
                <div class="relative w-28 h-28">
                  <svg class="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <path class="text-surface2"
                      stroke="currentColor" stroke-width="3" fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <path
                      [attr.stroke]="getScoreColor(currentVideoFile()!.mediaFile.analysis_score)"
                      stroke-width="3" fill="none" stroke-linecap="round"
                      [attr.stroke-dasharray]="(currentVideoFile()!.mediaFile.analysis_score || 0) + ', 100'"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  </svg>
                  <div class="absolute inset-0 flex flex-col items-center justify-center">
                    <span class="text-2xl font-bold text-white">{{ currentVideoFile()!.mediaFile.analysis_score?.toFixed(0) || 0 }}</span>
                    <span class="text-[10px] text-text-muted">/ 100</span>
                  </div>
                </div>
              </div>
            } @else {
              <p class="text-sm text-text-muted text-center py-4">Dados indisponíveis</p>
            }
          </div>

          <!-- Pessoas na cena -->
          <div class="glass-card p-5 hover:!transform-none">
            <h3 class="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <mat-icon class="text-primary-400 !text-lg">people</mat-icon>
              Pessoas na cena
            </h3>
            <div class="flex flex-col divide-y divide-border">
              @for (person of people; track person.name) {
                <app-person-card [name]="person.name" [role]="person.role" />
              }
              @if (people.length === 0) {
                <p class="text-sm text-text-muted p-2">Detecção automática indisponível.</p>
              }
            </div>
          </div>
        </div>
      </div>

      <!-- Métricas de Visão Computacional -->
      <div class="mb-8 animate-fade-in" style="animation-delay: 0.2s">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <mat-icon class="text-primary-400">visibility</mat-icon>
          Métricas de Visão Computacional
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Emoções Faciais -->
          <div class="glass-card p-5 hover:border-primary-500/30 transition-colors">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <mat-icon class="text-blue-400 !text-xl">face</mat-icon>
              </div>
              <div>
                <p class="text-xs text-text-muted">Emoções Faciais</p>
                <p class="text-lg font-bold text-white">{{ currentEmotionScore().toFixed(1) }}</p>
              </div>
            </div>
            <div class="h-1.5 bg-surface2 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-700"
                [style.width.%]="currentEmotionScore()"
                [style.background]="getScoreColor(currentEmotionScore())"></div>
            </div>
            <p class="text-[10px] text-text-subtle mt-2">DeepFace · Análise de expressões</p>
          </div>

          <!-- Linguagem Corporal -->
          <div class="glass-card p-5 hover:border-primary-500/30 transition-colors">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <mat-icon class="text-purple-400 !text-xl">accessibility_new</mat-icon>
              </div>
              <div>
                <p class="text-xs text-text-muted">Linguagem Corporal</p>
                <p class="text-lg font-bold text-white">{{ currentBodyScore().toFixed(1) }}</p>
              </div>
            </div>
            <div class="h-1.5 bg-surface2 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-700"
                [style.width.%]="currentBodyScore()"
                [style.background]="getScoreColor(currentBodyScore())"></div>
            </div>
            <p class="text-[10px] text-text-subtle mt-2">MediaPipe · Postura e movimentos</p>
          </div>

          <!-- Interações -->
          <div class="glass-card p-5 hover:border-primary-500/30 transition-colors">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <mat-icon class="text-green-400 !text-xl">forum</mat-icon>
              </div>
              <div>
                <p class="text-xs text-text-muted">Interações</p>
                <p class="text-lg font-bold text-white">{{ currentInteractionScore().toFixed(1) }}</p>
              </div>
            </div>
            <div class="h-1.5 bg-surface2 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-700"
                [style.width.%]="currentInteractionScore()"
                [style.background]="getScoreColor(currentInteractionScore())"></div>
            </div>
            <p class="text-[10px] text-text-subtle mt-2">Proximidade e contato visual</p>
          </div>

          <!-- Indicadores de Violência -->
          <div class="glass-card p-5 hover:border-primary-500/30 transition-colors">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                <mat-icon class="text-red-400 !text-xl">gpp_maybe</mat-icon>
              </div>
              <div>
                <p class="text-xs text-text-muted">Indicadores Risco</p>
                <p class="text-lg font-bold text-white">{{ currentViolenceScore().toFixed(1) }}</p>
              </div>
            </div>
            <div class="h-1.5 bg-surface2 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-700"
                [style.width.%]="currentViolenceScore()"
                [style.background]="getScoreColor(currentViolenceScore())"></div>
            </div>
            <p class="text-[10px] text-text-subtle mt-2">YOLOv8 · Objetos e sangramento</p>
          </div>
        </div>
      </div>

      <!-- Eventos detectados -->
      <div class="mb-8 animate-fade-in" style="animation-delay: 0.3s">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <mat-icon class="text-warning">event_note</mat-icon>
          Eventos Detectados ({{ timelineEvents().length }})
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          @for (event of timelineEvents(); track $index) {
            <div class="glass-card p-4 hover:border-primary-500/30 transition-colors cursor-pointer"
              (click)="jumpToEvent(event)">
              <div class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                  [ngClass]="getEventIconClass(event.type)">
                  <mat-icon class="!text-lg">{{ getEventIcon(event.type) }}</mat-icon>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-white leading-snug">{{ event.description }}</p>
                  <div class="flex items-center gap-2 mt-1.5">
                    <span class="text-[10px] text-text-subtle font-mono bg-surface2 px-1.5 py-0.5 rounded">
                      {{ formatTime(event.time) }}
                    </span>
                    <span class="text-[10px] text-text-subtle">{{ event.videoName }}</span>
                    <span class="text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                      [class]="event.riskLevel === 'high' ? 'bg-danger-500/15 text-danger-500' :
                               event.riskLevel === 'medium' ? 'bg-warning/15 text-warning' :
                               'bg-success/15 text-success'">
                      {{ (event.confidence * 100).toFixed(0) }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          }
          @if (timelineEvents().length === 0) {
            <p class="text-sm text-text-muted col-span-3">Nenhum evento detectado pela visão computacional.</p>
          }
        </div>
      </div>

      <!-- Resumo Geral da Análise de Vídeo -->
      <div class="glass-card p-6 hover:!transform-none animate-fade-in" style="animation-delay: 0.4s">
        <h3 class="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <mat-icon class="text-primary-400 !text-lg">summarize</mat-icon>
          Resumo Geral — Todos os Vídeos
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="flex flex-col gap-1 p-3 rounded-lg bg-surface2/30">
            <span class="text-xs text-text-muted">Total de vídeos</span>
            <span class="text-xl font-bold text-white">{{ videoFiles().length }}</span>
          </div>
          <div class="flex flex-col gap-1 p-3 rounded-lg bg-surface2/30">
            <span class="text-xs text-text-muted">Score máximo</span>
            <span class="text-xl font-bold" [style.color]="getScoreColor(maxVideoScore())">
              {{ maxVideoScore().toFixed(1) }}
            </span>
          </div>
          <div class="flex flex-col gap-1 p-3 rounded-lg bg-surface2/30">
            <span class="text-xs text-text-muted">Score médio</span>
            <span class="text-xl font-bold text-white">{{ avgVideoScore().toFixed(1) }}</span>
          </div>
          <div class="flex flex-col gap-1 p-3 rounded-lg bg-surface2/30">
            <span class="text-xs text-text-muted">Eventos totais</span>
            <span class="text-xl font-bold text-warning">{{ timelineEvents().length }}</span>
          </div>
        </div>

        <!-- Per-video breakdown -->
        @if (videoFiles().length > 0) {
          <div class="mt-6">
            <h4 class="text-xs font-bold text-text-muted uppercase tracking-wider mb-3">Detalhamento por arquivo</h4>
            <div class="flex flex-col gap-2">
              @for (vf of videoFiles(); track vf.mediaFile.id) {
                <div class="flex items-center gap-3 p-2 rounded-lg bg-surface2/20 hover:bg-surface2/40 transition-colors">
                  <mat-icon class="text-text-subtle !text-lg">videocam</mat-icon>
                  <span class="text-sm text-white flex-1 truncate">{{ vf.mediaFile.filename }}</span>
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-text-muted">Emoção: {{ getVaScore(vf.videoAnalysis, 'emotion_score').toFixed(0) }}</span>
                    <span class="text-xs text-text-muted">Corpo: {{ getVaScore(vf.videoAnalysis, 'body_language_score').toFixed(0) }}</span>
                    <span class="text-xs font-bold px-2 py-0.5 rounded-full"
                      [class]="getScoreBadgeClass(vf.mediaFile.analysis_score)">
                      {{ vf.mediaFile.analysis_score?.toFixed(0) || 'N/A' }}
                    </span>
                  </div>
                </div>
              }
            </div>
          </div>
        }
      </div>

      }
    </div>
  `
})
export class VideoAnalysisPageComponent implements OnInit, OnDestroy {
  @ViewChild('videoPlayer') videoPlayerRef!: ElementRef<HTMLVideoElement>;

  private readonly route = inject(ActivatedRoute);
  private readonly analysisService = inject(AnalysisService);
  private readonly sessionsService = inject(SessionsService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly storage = inject(StorageService);

  sessionId: number | null = null;
  loading = signal(true);
  analysis = signal<SessionAnalysisOut | null>(null);
  session = signal<SessionOut | null>(null);

  videoFiles = signal<VideoFileData[]>([]);
  selectedVideoIndex = signal(0);
  isPlaying = signal(false);
  isMuted = signal(false);
  currentTime = signal(0);
  duration = signal(0);
  videoProgress = signal(0);

  timelineEvents = signal<TimelineEvent[]>([]);

  people: { name: string; role: 'paciente' | 'medico' | 'enfermeiro' | 'acompanhante' }[] = [
    { name: 'Paciente (Anônima)', role: 'paciente' },
    { name: 'Profissional de Saúde', role: 'medico' },
  ];

  currentVideoFile = computed(() => {
    const files = this.videoFiles();
    const idx = this.selectedVideoIndex();
    return files[idx] || null;
  });

  currentVideoUrl = computed(() => {
    const vf = this.currentVideoFile();
    if (!vf) return '';
    // Convert internal blob_url to the proxied URL via core-api
    const token = this.storage.getAccessToken();
    return `${environment.apiUrl}/sessions/${this.sessionId}/media/${vf.mediaFile.id}/download?token=${token}`;
  });

  currentEmotionScore = computed(() => this.getVaScore(this.currentVideoFile()?.videoAnalysis, 'emotion_score'));
  currentBodyScore = computed(() => this.getVaScore(this.currentVideoFile()?.videoAnalysis, 'body_language_score'));
  currentInteractionScore = computed(() => this.getVaScore(this.currentVideoFile()?.videoAnalysis, 'interaction_score'));
  currentViolenceScore = computed(() => this.getVaScore(this.currentVideoFile()?.videoAnalysis, 'violence_indicator_score'));

  globalRiskBadgeClass = computed(() => {
    const level = this.session()?.ira_level;
    if (level === 'critico') return 'bg-danger-500/15 text-danger-500';
    if (level === 'moderado') return 'bg-warning/15 text-warning';
    return 'bg-success/15 text-success';
  });

  globalRiskIcon = computed(() => {
    const level = this.session()?.ira_level;
    if (level === 'critico') return 'error';
    if (level === 'moderado') return 'warning';
    return 'check_circle';
  });

  maxVideoScore = computed(() => {
    const scores = this.videoFiles()
      .map(v => v.mediaFile.analysis_score)
      .filter((s): s is number => s !== null);
    return scores.length > 0 ? Math.max(...scores) : 0;
  });

  avgVideoScore = computed(() => {
    const scores = this.videoFiles()
      .map(v => v.mediaFile.analysis_score)
      .filter((s): s is number => s !== null);
    return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
  });

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

  ngOnDestroy() {
    // Pause video when leaving
    const player = this.videoPlayerRef?.nativeElement;
    if (player) player.pause();
  }

  loadData() {
    this.loading.set(true);
    this.sessionsService.getSession(this.sessionId!).pipe(
      finalize(() => this.loading.set(false))
    ).subscribe({
      next: (session) => {
        this.session.set(session);
        this.buildVideoFiles(session);
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
        this.enrichVideoFilesWithAnalysis(analysis);
        this.buildTimelineEvents(analysis);
      }
    });
  }

  private buildVideoFiles(session: SessionOut) {
    const vFiles = session.media_files
      .filter(f => f.media_type === 'video')
      .map(f => ({
        mediaFile: f,
        videoAnalysis: null as any,
        blobUrl: f.blob_url || ''
      }));
    this.videoFiles.set(vFiles);
  }

  private enrichVideoFilesWithAnalysis(analysis: SessionAnalysisOut) {
    if (!analysis.video_analyses) return;

    const current = this.videoFiles();
    const updated = current.map(vf => {
      // Try to find video analysis by media_id key
      const va = analysis.video_analyses[String(vf.mediaFile.id)];
      return va ? { ...vf, videoAnalysis: va } : vf;
    });
    this.videoFiles.set(updated);
  }

  private buildTimelineEvents(analysis: SessionAnalysisOut) {
    const events: TimelineEvent[] = [];

    // From video_findings (first video's key_findings from the API)
    if (analysis.video_findings?.length) {
      for (const f of analysis.video_findings) {
        events.push({
          time: f.timestamp_seconds,
          description: f.description,
          type: f.type,
          confidence: f.confidence,
          videoName: this.videoFiles()[0]?.mediaFile.filename || 'Vídeo',
          riskLevel: f.confidence >= 0.8 ? 'high' : f.confidence >= 0.5 ? 'medium' : 'low'
        });
      }
    }

    // From per-video analyses
    if (analysis.video_analyses) {
      for (const [mediaId, va] of Object.entries(analysis.video_analyses)) {
        if (va?.key_findings) {
          const vf = this.videoFiles().find(v => String(v.mediaFile.id) === mediaId);
          const videoName = vf?.mediaFile.filename || `Vídeo #${mediaId}`;
          for (const f of va.key_findings) {
            // Avoid duplicating if already added from video_findings
            const isDupe = events.some(e =>
              e.description === f.description && Math.abs(e.time - f.timestamp_seconds) < 1
            );
            if (!isDupe) {
              events.push({
                time: f.timestamp_seconds,
                description: f.description,
                type: f.type,
                confidence: f.confidence,
                videoName,
                riskLevel: f.confidence >= 0.8 ? 'high' : f.confidence >= 0.5 ? 'medium' : 'low'
              });
            }
          }
        }
      }
    }

    events.sort((a, b) => a.time - b.time);
    this.timelineEvents.set(events);
  }

  // ──── Video controls ────

  selectVideo(index: number) {
    const player = this.videoPlayerRef?.nativeElement;
    if (player) player.pause();
    this.isPlaying.set(false);
    this.currentTime.set(0);
    this.videoProgress.set(0);
    this.selectedVideoIndex.set(index);
  }

  togglePlay() {
    const player = this.videoPlayerRef?.nativeElement;
    if (!player) return;
    if (player.paused) {
      player.play();
    } else {
      player.pause();
    }
  }

  toggleMute() {
    const player = this.videoPlayerRef?.nativeElement;
    if (!player) return;
    player.muted = !player.muted;
    this.isMuted.set(player.muted);
  }

  onTimeUpdate() {
    const player = this.videoPlayerRef?.nativeElement;
    if (!player) return;
    this.currentTime.set(player.currentTime);
    this.videoProgress.set(player.duration ? (player.currentTime / player.duration) * 100 : 0);
  }

  onMetadataLoaded() {
    const player = this.videoPlayerRef?.nativeElement;
    if (!player) return;
    this.duration.set(player.duration);
  }

  seekVideo(event: MouseEvent) {
    const player = this.videoPlayerRef?.nativeElement;
    if (!player || !player.duration) return;
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    const pct = (event.clientX - rect.left) / rect.width;
    player.currentTime = pct * player.duration;
  }

  jumpToEvent(event: TimelineEvent) {
    // Find the right video for this event
    const idx = this.videoFiles().findIndex(v => v.mediaFile.filename === event.videoName);
    if (idx >= 0 && idx !== this.selectedVideoIndex()) {
      this.selectVideo(idx);
      // Small delay to let the video element load
      setTimeout(() => {
        const player = this.videoPlayerRef?.nativeElement;
        if (player) {
          player.currentTime = event.time;
          player.play();
        }
      }, 300);
    } else {
      const player = this.videoPlayerRef?.nativeElement;
      if (player) {
        player.currentTime = event.time;
        player.play();
      }
    }
  }

  // ──── Helpers ────

  getVaScore(va: any, field: string): number {
    if (!va) return 0;
    // From video-domain response (components object)
    if (va.components && va.components[field] !== undefined) {
      return va.components[field] || 0;
    }
    // Direct fields (from DB query)
    return va[field] || 0;
  }

  formatTime(seconds: number): string {
    if (!seconds || isNaN(seconds)) return '00:00';
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  }

  getScoreColor(score: number | null | undefined): string {
    if (score === null || score === undefined) return '#64748B';
    if (score >= 70) return '#EF4444';
    if (score >= 40) return '#EAB308';
    return '#16A34A';
  }

  getScoreBadgeClass(score: number | null | undefined): string {
    if (score === null || score === undefined) return 'bg-surface2 text-text-muted';
    if (score >= 70) return 'bg-danger-500/15 text-danger-500';
    if (score >= 40) return 'bg-warning/15 text-warning';
    return 'bg-success/15 text-success';
  }

  getEventIcon(type: string): string {
    if (type === 'emotion' || type === 'face') return 'face';
    if (type === 'pose') return 'accessibility_new';
    if (type === 'object') return 'gpp_maybe';
    if (type === 'bleeding') return 'water_drop';
    if (type === 'interaction') return 'forum';
    if (type === 'concern' || type === 'pain' || type === 'risk') return 'warning';
    return 'visibility';
  }

  getEventIconClass(type: string): string {
    if (type === 'emotion' || type === 'face') return 'bg-blue-500/10 text-blue-400';
    if (type === 'pose') return 'bg-purple-500/10 text-purple-400';
    if (type === 'object' || type === 'bleeding') return 'bg-red-500/10 text-red-400';
    if (type === 'interaction') return 'bg-primary-500/10 text-primary-400';
    if (type === 'concern' || type === 'pain' || type === 'risk') return 'bg-warning/10 text-warning';
    return 'bg-success/10 text-success';
  }
}
