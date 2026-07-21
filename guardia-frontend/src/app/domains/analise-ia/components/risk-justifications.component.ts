import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { RiskDetails } from '../models/analysis.models';

@Component({
  selector: 'app-risk-justifications',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <!-- Video Risk -->
      <div class="glass-card p-5 relative overflow-hidden group">
        <div class="absolute -right-6 -top-6 text-primary-500/5 group-hover:text-primary-500/10 transition-colors">
          <mat-icon style="font-size: 120px; width: 120px; height: 120px;">videocam</mat-icon>
        </div>
        <div class="relative z-10 flex flex-col h-full">
          <h4 class="text-sm font-bold text-text-muted uppercase tracking-wider flex items-center gap-2 mb-4">
            <mat-icon class="text-primary-400 text-sm">visibility</mat-icon> Análise Visual
          </h4>
          @if (details?.video; as video) {
            <p class="text-white text-sm leading-relaxed mb-4 flex-1">{{ video.text }}</p>
            <div class="bg-primary-500/10 border border-primary-500/20 rounded-md p-3">
              <span class="text-xs font-semibold text-primary-300 block mb-1">Recomendação:</span>
              <p class="text-sm text-primary-100">{{ video.recommendation }}</p>
            </div>
          } @else {
            <p class="text-text-subtle text-sm italic flex-1">Nenhum risco visual detectado.</p>
          }
        </div>
      </div>

      <!-- Audio Risk -->
      <div class="glass-card p-5 relative overflow-hidden group">
        <div class="absolute -right-6 -top-6 text-secondary-500/5 group-hover:text-secondary-500/10 transition-colors">
          <mat-icon style="font-size: 120px; width: 120px; height: 120px;">mic</mat-icon>
        </div>
        <div class="relative z-10 flex flex-col h-full">
          <h4 class="text-sm font-bold text-text-muted uppercase tracking-wider flex items-center gap-2 mb-4">
            <mat-icon class="text-secondary-400 text-sm">hearing</mat-icon> Análise de Áudio
          </h4>
          @if (details?.audio; as audio) {
            <p class="text-white text-sm leading-relaxed mb-4 flex-1">{{ audio.text }}</p>
            <div class="bg-secondary-500/10 border border-secondary-500/20 rounded-md p-3">
              <span class="text-xs font-semibold text-secondary-300 block mb-1">Recomendação:</span>
              <p class="text-sm text-secondary-100">{{ audio.recommendation }}</p>
            </div>
          } @else {
            <p class="text-text-subtle text-sm italic flex-1">Nenhum risco vocal detectado.</p>
          }
        </div>
      </div>

      <!-- Document Risk -->
      <div class="glass-card p-5 relative overflow-hidden group">
        <div class="absolute -right-6 -top-6 text-danger-500/5 group-hover:text-danger-500/10 transition-colors">
          <mat-icon style="font-size: 120px; width: 120px; height: 120px;">description</mat-icon>
        </div>
        <div class="relative z-10 flex flex-col h-full">
          <h4 class="text-sm font-bold text-text-muted uppercase tracking-wider flex items-center gap-2 mb-4">
            <mat-icon class="text-danger-400 text-sm">plagiarism</mat-icon> Documentação
          </h4>
          @if (details?.document; as doc) {
            <p class="text-white text-sm leading-relaxed mb-4 flex-1">{{ doc.text }}</p>
            <div class="bg-danger-500/10 border border-danger-500/20 rounded-md p-3">
              <span class="text-xs font-semibold text-danger-300 block mb-1">Recomendação:</span>
              <p class="text-sm text-danger-100">{{ doc.recommendation }}</p>
            </div>
          } @else {
            <p class="text-text-subtle text-sm italic flex-1">Documentação adequada.</p>
          }
        </div>
      </div>

    </div>
  `
})
export class RiskJustificationsComponent {
  @Input() details: RiskDetails | null = null;
}
