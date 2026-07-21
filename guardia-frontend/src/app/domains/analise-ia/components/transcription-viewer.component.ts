import { Component, Input, Pipe, PipeTransform } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { TranscriptionSegment } from '../models/analysis.models';

@Pipe({ name: 'formatTime', standalone: true })
export class FormatTimePipe implements PipeTransform {
  transform(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  }
}

@Component({
  selector: 'app-transcription-viewer',
  standalone: true,
  imports: [CommonModule, MatIconModule, FormatTimePipe],
  template: `
    <div class="flex flex-col h-full bg-surface2/30 rounded-xl border border-border overflow-hidden">
      <div class="p-4 border-b border-border bg-surface2/50 flex items-center justify-between">
        <h3 class="font-bold text-white flex items-center gap-2">
          <mat-icon class="text-primary-400">record_voice_over</mat-icon>
          Transcrição da Sessão
        </h3>
        <div class="flex gap-3 text-xs font-medium">
          <span class="flex items-center gap-1 text-primary-300"><div class="w-2 h-2 rounded-full bg-primary-400"></div> Profissional</span>
          <span class="flex items-center gap-1 text-secondary-300"><div class="w-2 h-2 rounded-full bg-secondary-400"></div> Paciente</span>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        @for (segment of segments; track segment.start) {
          <div class="flex gap-4 animate-fade-in" 
               [ngClass]="segment.role === 'paciente' ? 'flex-row-reverse' : 'flex-row'">
            
            <!-- Avatar -->
            <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 shadow-md"
                 [ngClass]="{
                   'bg-primary-500 text-white': segment.role === 'profissional',
                   'bg-secondary-500 text-white': segment.role === 'paciente',
                   'bg-surface text-text-muted': segment.role === 'desconhecido'
                 }">
              <mat-icon class="text-[18px] w-[18px] h-[18px]">
                {{ segment.role === 'profissional' ? 'medical_services' : (segment.role === 'paciente' ? 'person' : 'help_outline') }}
              </mat-icon>
            </div>

            <!-- Bubble -->
            <div class="flex flex-col max-w-[80%]"
                 [ngClass]="segment.role === 'paciente' ? 'items-end' : 'items-start'">
              <div class="flex items-center gap-2 mb-1 text-xs text-text-muted">
                <span class="font-semibold">{{ segment.speaker }}</span>
                <span>{{ segment.start | formatTime }}</span>
              </div>
              
              <div class="px-4 py-2.5 rounded-2xl relative"
                   [ngClass]="{
                     'bg-primary-500/20 text-white border border-primary-500/30 rounded-tl-sm': segment.role === 'profissional',
                     'bg-secondary-500/20 text-white border border-secondary-500/30 rounded-tr-sm': segment.role === 'paciente',
                     'bg-surface text-text-muted border border-border': segment.role === 'desconhecido'
                   }">
                <p class="text-sm leading-relaxed">{{ segment.text }}</p>
                
                <!-- Sentiment indicator -->
                @if (segment.sentiment === 'negative' && segment.sentiment_confidence > 0.7) {
                  <div class="absolute -bottom-2 -right-2 bg-danger-500 text-white rounded-full w-5 h-5 flex items-center justify-center shadow-glow-danger"
                       title="Sentimento Negativo Detectado">
                    <mat-icon class="text-[12px] w-[12px] h-[12px]">warning</mat-icon>
                  </div>
                }
              </div>
            </div>
          </div>
        }
        
        @if (segments.length === 0) {
          <div class="h-full flex flex-col items-center justify-center text-text-muted opacity-50">
            <mat-icon class="text-4xl mb-2">speaker_notes_off</mat-icon>
            <p>Nenhuma transcrição disponível.</p>
          </div>
        }
      </div>
    </div>
  `
})
export class TranscriptionViewerComponent {
  @Input() segments: TranscriptionSegment[] = [];
}
