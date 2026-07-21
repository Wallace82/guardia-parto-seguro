import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-pipeline-diagram',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="glass-card p-6 overflow-x-auto hover:!transform-none">
      <h3 class="text-lg font-semibold text-white mb-6">Pipeline de análise</h3>
      
      <div class="flex items-start justify-between min-w-[700px] gap-4 relative">
        <!-- Connecting Line -->
        <div class="absolute top-[40px] left-[10%] right-[10%] h-0.5 bg-border -z-10"></div>
        
        <!-- Step 1: Aquisição -->
        <div class="flex-1 flex flex-col items-center text-center">
          <div class="w-20 h-20 rounded-2xl bg-surface flex flex-col items-center justify-center border border-border shadow-card mb-4 relative">
            <mat-icon class="text-primary-400 !text-3xl">upload_file</mat-icon>
            <div class="absolute -right-3 top-1/2 -translate-y-1/2 text-text-muted">
              <mat-icon class="!text-lg">chevron_right</mat-icon>
            </div>
          </div>
          <h4 class="text-sm font-bold text-white mb-2">Aquisição</h4>
          <ul class="text-xs text-text-muted space-y-1">
            <li>Vídeo</li>
            <li>Áudio</li>
            <li>Documentos</li>
            <li>Sinais vitais</li>
          </ul>
        </div>

        <!-- Step 2: Processamento -->
        <div class="flex-1 flex flex-col items-center text-center">
          <div class="w-20 h-20 rounded-2xl bg-surface flex flex-col items-center justify-center border border-primary-500/30 shadow-glow-primary mb-4 relative">
            <mat-icon class="text-primary-400 !text-3xl">memory</mat-icon>
            <div class="absolute -right-3 top-1/2 -translate-y-1/2 text-text-muted">
              <mat-icon class="!text-lg">chevron_right</mat-icon>
            </div>
          </div>
          <h4 class="text-sm font-bold text-white mb-2">Processamento</h4>
          <ul class="text-xs text-text-muted space-y-1">
            <li>DeepFace</li>
            <li>MediaPipe</li>
            <li>YOLOv8</li>
            <li>Whisper (STT)</li>
            <li>Textract</li>
          </ul>
        </div>

        <!-- Step 3: Compreensão -->
        <div class="flex-1 flex flex-col items-center text-center">
          <div class="w-20 h-20 rounded-2xl bg-surface flex flex-col items-center justify-center border border-secondary-500/30 shadow-glow-primary mb-4 relative">
            <mat-icon class="text-secondary-400 !text-3xl">psychology</mat-icon>
            <div class="absolute -right-3 top-1/2 -translate-y-1/2 text-text-muted">
              <mat-icon class="!text-lg">chevron_right</mat-icon>
            </div>
          </div>
          <h4 class="text-sm font-bold text-white mb-2">Compreensão</h4>
          <ul class="text-xs text-text-muted space-y-1">
            <li>Transcribe</li>
            <li>Comprehend</li>
            <li>Análise de Sentimento</li>
            <li>Entidades</li>
          </ul>
        </div>

        <!-- Step 4: Fusão & IA -->
        <div class="flex-1 flex flex-col items-center text-center">
          <div class="w-20 h-20 rounded-2xl bg-surface flex flex-col items-center justify-center border border-success/30 shadow-glow-success mb-4">
            <mat-icon class="text-success !text-3xl">hub</mat-icon>
          </div>
          <h4 class="text-sm font-bold text-white mb-2">Fusão & IA</h4>
          <ul class="text-xs text-text-muted space-y-1">
            <li>Fusão Multimodal</li>
            <li>Score de Risco</li>
            <li>Explicabilidade</li>
            <li>Recomendação</li>
          </ul>
        </div>
      </div>
    </div>
  `
})
export class PipelineDiagramComponent {}
