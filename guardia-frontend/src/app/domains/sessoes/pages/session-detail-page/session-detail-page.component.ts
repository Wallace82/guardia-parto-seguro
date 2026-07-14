import { Component, inject, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { finalize } from 'rxjs';

import { SessionsService } from '../../services/sessions.service';
import { SessionOut, MediaFile } from '../../models/sessions.models';
import { MediaUploaderComponent } from '../../components/media-uploader.component';
import { ConfirmDialogComponent } from '../../../../shared/components/confirm-dialog.component';

@Component({
  selector: 'app-session-detail-page',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule, RouterLink, MediaUploaderComponent, MatDialogModule],
  providers: [DatePipe],
  template: `
    <div class="p-8 max-w-[1200px] mx-auto min-h-screen">
      
      <!-- Header -->
      <div class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <a mat-icon-button color="primary" routerLink="/sessoes">
              <mat-icon>arrow_back</mat-icon>
            </a>
            <h1 class="text-3xl font-bold text-white m-0">{{ session()?.title || 'Detalhes da Sessão' }}</h1>
          </div>
          <div class="ml-12 flex flex-wrap items-center gap-4 text-sm font-medium">
            <span class="text-text-muted font-mono bg-surface2/50 px-2 py-1 rounded border border-border">
              Paciente: {{ session()?.patient_code || '---' }}
            </span>
            <span class="text-text-muted flex items-center gap-1">
              <mat-icon class="text-[16px] w-[16px] h-[16px]">schedule</mat-icon>
              {{ session()?.created_at | date:'dd/MM/yyyy HH:mm' }}
            </span>
            <span class="status-chip" [ngClass]="'status-chip--' + (session()?.status || 'pending')">
              <span class="dot"></span> {{ getStatusLabel(session()?.status || 'pending') }}
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          @if (session()?.status === 'completed') {
            <a mat-flat-button color="accent" [routerLink]="['/analise-ia', session()?.id]">
              <mat-icon>psychology</mat-icon> Ver Análise de IA
            </a>
          } @else if (session()?.status === 'processing') {
            <button mat-flat-button disabled class="bg-surface2 text-text-muted">
              <mat-icon class="animate-spin">autorenew</mat-icon> IA Processando...
            </button>
          }
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Upload Area (Left 2 cols) -->
        <div class="lg:col-span-2 flex flex-col gap-6 animate-slide-up" style="animation-delay: 0.1s">
          
          @if (session()?.notes) {
            <div class="glass-card p-6">
              <h3 class="font-bold text-white flex items-center gap-2 mb-2">
                <mat-icon class="text-primary-400">notes</mat-icon> Notas Clínicas Iniciais
              </h3>
              <p class="text-text-muted text-sm leading-relaxed whitespace-pre-line">{{ session()?.notes }}</p>
            </div>
          }

          <div class="glass-card p-6">
            <h3 class="font-bold text-white flex items-center gap-2 mb-4">
              <mat-icon class="text-secondary-400">add_photo_alternate</mat-icon> Adicionar Arquivos
            </h3>
            <app-media-uploader 
              [uploading]="uploading" 
              (fileDropped)="onFileUpload($event)">
            </app-media-uploader>
          </div>
        </div>

        <!-- Files List (Right 1 col) -->
        <div class="glass-card p-0 flex flex-col h-[600px] animate-slide-up" style="animation-delay: 0.2s">
          <div class="p-5 border-b border-border">
            <h3 class="font-bold text-white flex items-center gap-2 m-0">
              <mat-icon class="text-primary-400">folder</mat-icon> Arquivos da Sessão
            </h3>
          </div>
          
          <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
            @if (session()?.media_files?.length === 0) {
              <div class="flex flex-col items-center justify-center h-full text-text-muted text-center opacity-70">
                <mat-icon class="text-4xl mb-2">file_present</mat-icon>
                <p>Nenhum arquivo enviado ainda.</p>
              </div>
            } @else {
              @for (file of session()?.media_files; track file.id) {
                <div class="bg-surface2/50 border border-border rounded-lg p-3 flex gap-3 hover:bg-surface2/80 transition-colors">
                  <div class="w-10 h-10 rounded bg-primary-500/10 flex flex-shrink-0 items-center justify-center text-primary-400">
                    <mat-icon>{{ getFileIcon(file.media_type) }}</mat-icon>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-white text-sm font-bold truncate mb-0.5" [title]="file.filename">{{ file.filename }}</p>
                    <p class="text-text-muted text-[11px] mb-1.5 leading-tight">{{ getFileDescription(file.media_type) }}</p>
                    <div class="flex items-center justify-between text-xs text-text-subtle">
                      <span>{{ (file.file_size_bytes / 1024 / 1024) | number:'1.1-2' }} MB</span>
                      
                      @if (file.status === 'analyzed') {
                        <span class="text-success flex items-center gap-0.5"><mat-icon class="text-[12px] w-[12px] h-[12px]">check_circle</mat-icon> Analisado</span>
                      } @else if (file.status === 'processing') {
                        <span class="text-warning-400 flex items-center gap-0.5"><mat-icon class="text-[12px] w-[12px] h-[12px] animate-spin">autorenew</mat-icon> Processando</span>
                      } @else {
                        <span class="text-primary-300">Enviado</span>
                      }
                    </div>
                  </div>
                  <button mat-icon-button color="warn" class="scale-75 text-text-subtle hover:text-warn-500 transition-colors" title="Excluir arquivo" (click)="deleteFile(file.id)">
                    <mat-icon>delete</mat-icon>
                  </button>
                </div>
              }
            }
          </div>
        </div>

      </div>
    </div>
  `
})
export class SessionDetailPageComponent implements OnInit, OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly sessionsService = inject(SessionsService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly dialog = inject(MatDialog);

  sessionId: number | null = null;
  session = signal<SessionOut | null>(null);
  loading = signal(true);
  uploading = signal(false);
  private pollingTimer: any = null;

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.sessionId = +id;
        this.loadSession();
      }
    });
  }

  ngOnDestroy() {
    this.stopPolling();
  }

  startPolling() {
    if (!this.pollingTimer) {
      this.pollingTimer = setInterval(() => {
        this.loadSession(true);
      }, 5000);
    }
  }

  stopPolling() {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = null;
    }
  }

  loadSession(isPolling = false) {
    if (!this.sessionId) return;
    if (!isPolling) this.loading.set(true);
    this.sessionsService.getSession(this.sessionId).subscribe({
      next: (res) => {
        this.session.set(res);
        if (!isPolling) this.loading.set(false);
        
        const needsPolling = res.status === 'processing' || res.media_files?.some(f => f.status === 'processing');
        if (needsPolling) {
          this.startPolling();
        } else {
          this.stopPolling();
        }
      },
      error: () => {
        if (!isPolling) {
          this.snackBar.open('Sessão não encontrada.', 'Fechar', { duration: 3000 });
          this.loading.set(false);
        }
        this.stopPolling();
      }
    });
  }

  onFileUpload(data: { file: File; type: 'video' | 'audio' | 'document' }) {
    if (!this.sessionId) return;
    
    this.uploading.set(true);
    this.sessionsService.uploadMedia(this.sessionId, data.file, data.type).pipe(
      finalize(() => this.uploading.set(false))
    ).subscribe({
      next: () => {
        this.snackBar.open('Arquivo enviado com sucesso. Análise iniciada.', 'OK', { duration: 4000 });
        this.loadSession(); // Recarrega para ver o arquivo na lista
      },
      error: (err) => {
        let msg = 'Erro ao fazer upload do arquivo.';
        if (err.status === 413) msg = 'Arquivo muito grande (Excedeu o limite).';
        this.snackBar.open(msg, 'Fechar', { duration: 4000 });
      }
    });
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      pending: 'Pendente',
      processing: 'Em Análise',
      completed: 'Análise Concluída',
      error: 'Falha'
    };
    return labels[status] || status;
  }

  getFileIcon(type: string): string {
    switch (type) {
      case 'video': return 'videocam';
      case 'audio': return 'mic';
      default: return 'description';
    }
  }

  getFileDescription(type: string): string {
    switch (type) {
      case 'video': return 'Extrai postura corporal e expressões faciais.';
      case 'audio': return 'Avalia ansiedade vocal e comunicação humanizada.';
      case 'document': return 'Extrai indicadores de risco do prontuário.';
      default: return 'Arquivo em processamento de IA.';
    }
  }

  deleteFile(mediaId: number) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Excluir arquivo',
        message: 'Tem certeza que deseja excluir este arquivo? Essa ação não pode ser desfeita e os dados da análise serão perdidos.',
        confirmText: 'Excluir',
        cancelText: 'Cancelar',
        isDestructive: true
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.sessionsService.deleteMediaFile(mediaId).subscribe({
          next: () => {
            this.snackBar.open('Arquivo excluído com sucesso!', 'OK', { duration: 3000 });
            this.loadSession();
          },
          error: () => {
            this.snackBar.open('Erro ao excluir o arquivo.', 'Fechar', { duration: 3000 });
          }
        });
      }
    });
  }
}
