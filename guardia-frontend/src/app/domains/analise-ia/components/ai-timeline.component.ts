import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { VideoFinding } from '../models/analysis.models';
import { FormatTimePipe } from './transcription-viewer.component';

@Component({
  selector: 'app-ai-timeline',
  standalone: true,
  imports: [CommonModule, MatIconModule, FormatTimePipe],
  template: `
    <div class="glass-card flex flex-col h-full">
      <div class="p-4 border-b border-border flex items-center justify-between">
        <h3 class="font-bold text-white flex items-center gap-2">
          <mat-icon class="text-secondary-400">timeline</mat-icon>
          Eventos Clínicos (Visão IA)
        </h3>
      </div>
      
      <div class="p-4 flex-1 overflow-y-auto">
        @if (findings.length === 0) {
          <div class="h-full flex flex-col items-center justify-center text-text-muted opacity-50">
            <mat-icon class="text-4xl mb-2">videocam_off</mat-icon>
            <p>Nenhum achado visual detectado.</p>
          </div>
        } @else {
          <div class="relative pl-6 border-l-2 border-border/50 ml-4 py-2 flex flex-col gap-6">
            @for (finding of findings; track finding.timestamp_seconds) {
              <div class="relative animate-slide-up">
                <!-- Timeline Dot -->
                <div class="absolute -left-[31px] top-1 w-4 h-4 rounded-full border-4 border-bg shadow-glow-danger bg-danger-500"></div>
                
                <div class="bg-surface2/50 border border-border rounded-lg p-3 hover:bg-surface2/80 transition-colors">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs font-bold text-danger-400 bg-danger-500/10 px-2 py-0.5 rounded uppercase tracking-wider">
                      {{ finding.type }}
                    </span>
                    <span class="text-xs font-mono text-text-muted font-medium bg-bg/50 px-2 py-0.5 rounded">
                      {{ finding.timestamp_seconds | formatTime }}
                    </span>
                  </div>
                  <p class="text-sm text-white leading-snug">{{ finding.description }}</p>
                  <div class="mt-2 flex items-center gap-2 text-xs text-text-subtle">
                    <div class="flex-1 h-1 bg-surface rounded-full overflow-hidden">
                      <div class="h-full bg-primary-500 rounded-full" [style.width.%]="finding.confidence * 100"></div>
                    </div>
                    <span>Confiança: {{ finding.confidence | percent }}</span>
                  </div>
                </div>
              </div>
            }
          </div>
        }
      </div>
    </div>
  `
})
export class AITimelineComponent {
  @Input() findings: VideoFinding[] = [];
}
