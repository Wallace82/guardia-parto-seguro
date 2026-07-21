import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-metrics-overview',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Total Sessions -->
      <div class="metric-card animate-fade-in" style="animation-delay: 0.1s">
        <div class="flex items-center justify-between mb-2">
          <span class="text-text-muted text-xs font-bold uppercase tracking-wider">Total de Sessões</span>
          <div class="w-8 h-8 rounded-full bg-primary-500/10 flex items-center justify-center text-primary-400">
            <mat-icon class="text-sm">analytics</mat-icon>
          </div>
        </div>
        <span class="text-3xl font-bold text-white">{{ totalSessions }}</span>
      </div>

      <!-- Processing -->
      <div class="metric-card animate-fade-in" style="animation-delay: 0.2s">
        <div class="flex items-center justify-between mb-2">
          <span class="text-text-muted text-xs font-bold uppercase tracking-wider">Em Análise (IA)</span>
          <div class="w-8 h-8 rounded-full bg-secondary-500/10 flex items-center justify-center text-secondary-500">
            <mat-icon class="text-sm">psychology</mat-icon>
          </div>
        </div>
        <div class="flex items-end gap-3">
          <span class="text-3xl font-bold text-white">{{ processingSessions }}</span>
          @if (processingSessions > 0) {
            <span class="flex h-3 w-3 relative mb-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-secondary-500"></span>
            </span>
          }
        </div>
      </div>

      <!-- Critical Alerts -->
      <div class="metric-card animate-fade-in glow-border" style="animation-delay: 0.3s">
        <div class="flex items-center justify-between mb-2">
          <span class="text-text-muted text-xs font-bold uppercase tracking-wider">Alertas Críticos</span>
          <div class="w-8 h-8 rounded-full bg-danger-500/10 flex items-center justify-center text-danger-500">
            <mat-icon class="text-sm">warning</mat-icon>
          </div>
        </div>
        <span class="text-3xl font-bold text-danger-500">{{ criticalAlerts }}</span>
      </div>

      <!-- Average IGA -->
      <div class="metric-card animate-fade-in" style="animation-delay: 0.4s">
        <div class="flex items-center justify-between mb-2">
          <span class="text-text-muted text-xs font-bold uppercase tracking-wider">IGA Médio</span>
          <div class="w-8 h-8 rounded-full bg-success/10 flex items-center justify-center text-success">
            <mat-icon class="text-sm">trending_up</mat-icon>
          </div>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-bold text-white">{{ averageIra | number:'1.1-1' }}</span>
          <span class="text-text-muted text-sm">/ 100</span>
        </div>
      </div>
    </div>
  `
})
export class MetricsOverviewComponent {
  @Input() totalSessions = 0;
  @Input() processingSessions = 0;
  @Input() criticalAlerts = 0;
  @Input() averageIra = 0;
}
