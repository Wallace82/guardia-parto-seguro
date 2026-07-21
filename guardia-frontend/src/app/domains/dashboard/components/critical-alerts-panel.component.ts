import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';
import { AlertOut } from '../../alertas/models/alerts.models';

@Component({
  selector: 'app-critical-alerts-panel',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule, RouterLink],
  providers: [DatePipe],
  template: `
    <div class="glass-card flex flex-col h-full animate-slide-up" style="animation-delay: 0.3s">
      <div class="p-5 border-b border-border flex items-center justify-between">
        <h3 class="text-lg font-bold text-white flex items-center gap-2">
          <mat-icon class="text-danger-500">notification_important</mat-icon>
          Atenção Imediata
        </h3>
        <a mat-button color="warn" routerLink="/alertas">Central de Alertas</a>
      </div>
      
      <div class="flex-1 overflow-auto p-5">
        @if (loading) {
          <div class="flex justify-center p-4">
            <mat-icon class="animate-spin text-danger-500">autorenew</mat-icon>
          </div>
        } @else if (alerts.length === 0) {
          <div class="flex flex-col items-center justify-center text-text-muted h-full py-8 gap-3">
            <div class="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center text-success mb-2">
              <mat-icon class="text-3xl">check_circle</mat-icon>
            </div>
            <p class="font-medium text-white">Nenhum alerta crítico</p>
            <p class="text-sm text-center">Tudo sob controle no momento.</p>
          </div>
        } @else {
          <div class="flex flex-col gap-4">
            @for (alert of alerts; track alert.id) {
              <div class="bg-danger-500/10 border border-danger-500/30 rounded-lg p-4 flex gap-4 transition-all hover:bg-danger-500/20">
                <div class="mt-1 flex-shrink-0 text-danger-500">
                  <mat-icon>warning</mat-icon>
                </div>
                <div class="flex-1">
                  <div class="flex items-start justify-between mb-1 gap-2">
                    <h4 class="font-bold text-white text-sm">{{ alert.title }}</h4>
                    <span class="text-xs font-semibold text-danger-400 bg-danger-500/20 px-2 py-0.5 rounded flex-shrink-0">
                      Sessão #{{ alert.session_id }}
                    </span>
                  </div>
                  <p class="text-sm text-text-muted mb-3">{{ alert.description }}</p>
                  
                  <div class="flex items-center justify-between">
                    <span class="text-xs text-text-subtle flex items-center gap-1">
                      <mat-icon class="text-[14px] w-[14px] h-[14px]">schedule</mat-icon>
                      {{ alert.created_at | date:'dd/MM HH:mm' }}
                    </span>
                    <div class="flex gap-2">
                      <a mat-button color="primary" class="!px-3 !h-8 !min-w-0" [routerLink]="['/sessoes', alert.session_id]">
                        Ver Sessão
                      </a>
                      <button mat-flat-button color="warn" class="!px-3 !h-8 !min-w-0" (click)="onAcknowledge.emit(alert.id)">
                        Reconhecer
                      </button>
                    </div>
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
export class CriticalAlertsPanelComponent {
  @Input() alerts: AlertOut[] = [];
  @Input() loading = false;
  @Output() onAcknowledge = new EventEmitter<number>();
}
