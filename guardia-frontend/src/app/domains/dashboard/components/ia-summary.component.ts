import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { IgaLevel } from '../../sessoes/models/sessions.models';

@Component({
  selector: 'app-ia-summary',
  standalone: true,
  imports: [CommonModule, MatIconModule, RouterLink],
  template: `
    <div class="glass-card flex flex-col h-full items-center justify-center text-center p-8 hover:!transform-none">
      <h3 class="text-lg font-semibold text-white mb-6 self-start flex items-center gap-2 w-full">
        <mat-icon class="text-primary-400">smart_toy</mat-icon>
        Resumo da IA
      </h3>

      <div class="flex-1 flex flex-col items-center justify-center gap-4">
        <!-- Large Status Icon -->
        <div class="w-20 h-20 rounded-full flex items-center justify-center"
          [style.background]="iconBg()">
          <mat-icon class="!text-5xl !w-12 !h-12" [style.color]="iconColor()">{{ icon() }}</mat-icon>
        </div>

        <!-- Title -->
        <h4 class="text-lg font-semibold text-white leading-snug">{{ title() }}</h4>

        <!-- Description -->
        <p class="text-sm text-text-muted leading-relaxed max-w-[260px]">{{ description() }}</p>
      </div>

      <!-- Link -->
      <a [routerLink]="sessionId() ? ['/analise/multimodal', sessionId()] : ['/sessoes']"
        class="mt-4 text-sm font-medium text-primary-400 hover:text-primary-300 hover:underline transition-colors flex items-center gap-1">
        Ver detalhes da análise multimodal
        <mat-icon class="!text-base !w-4 !h-4">arrow_forward</mat-icon>
      </a>
    </div>
  `
})
export class IaSummaryComponent {
  iraLevel = input<IgaLevel | null>(null);
  iraScore = input<number | null>(null);
  sessionId = input<number | null>(null);

  icon = computed(() => {
    switch (this.iraLevel()) {
      case 'critico': return 'error';
      case 'moderado': return 'warning';
      default: return 'check_circle';
    }
  });

  iconColor = computed(() => {
    switch (this.iraLevel()) {
      case 'critico': return '#EF4444';
      case 'moderado': return '#F59E0B';
      default: return '#10B981';
    }
  });

  iconBg = computed(() => {
    switch (this.iraLevel()) {
      case 'critico': return 'rgba(239, 68, 68, 0.1)';
      case 'moderado': return 'rgba(245, 158, 11, 0.1)';
      default: return 'rgba(16, 185, 129, 0.1)';
    }
  });

  title = computed(() => {
    switch (this.iraLevel()) {
      case 'critico': return 'Risco crítico identificado';
      case 'moderado': return 'Atenção: indicadores moderados';
      default: return 'Nenhum sinal de risco identificado';
    }
  });

  description = computed(() => {
    const score = this.iraScore();
    const scoreText = score !== null ? ` (IGA: ${score.toFixed(1)})` : '';
    switch (this.iraLevel()) {
      case 'critico':
        return `Indicadores de risco elevados detectados${scoreText}. Ação imediata recomendada.`;
      case 'moderado':
        return `Alguns indicadores requerem atenção${scoreText}. Monitoramento contínuo sugerido.`;
      default:
        return `Todos os indicadores estão dentro dos parâmetros esperados para um parto seguro${scoreText}.`;
    }
  });
}
