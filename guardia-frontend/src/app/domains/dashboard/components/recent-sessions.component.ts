import { Component, Input } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { SessionOut } from '../../sessoes/models/sessions.models';

@Component({
  selector: 'app-recent-sessions',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatIconModule, MatButtonModule, MatTooltipModule, RouterLink],
  providers: [DatePipe],
  template: `
    <div class="glass-card flex flex-col h-full animate-slide-up" style="animation-delay: 0.2s">
      <div class="p-5 border-b border-border flex items-center justify-between">
        <h3 class="text-lg font-bold text-white flex items-center gap-2">
          <mat-icon class="text-primary-400">history</mat-icon>
          Sessões Recentes
        </h3>
        <a mat-button color="primary" routerLink="/sessoes">Ver Todas</a>
      </div>
      
      <div class="flex-1 overflow-auto p-0">
        @if (loading) {
          <div class="p-8 flex justify-center">
            <mat-icon class="animate-spin text-primary-500">autorenew</mat-icon>
          </div>
        } @else if (sessions.length === 0) {
          <div class="p-8 text-center text-text-muted flex flex-col items-center gap-2">
            <mat-icon class="text-4xl opacity-50">inbox</mat-icon>
            <p>Nenhuma sessão recente encontrada.</p>
          </div>
        } @else {
          <table mat-table [dataSource]="sessions" class="w-full bg-transparent">
            
            <!-- Patient Code Column -->
            <ng-container matColumnDef="patient_code">
              <th mat-header-cell *matHeaderCellDef class="text-text-muted font-semibold text-xs tracking-wider uppercase border-b border-border"> Paciente </th>
              <td mat-cell *matCellDef="let element" class="border-b border-border/50 py-3">
                <div class="font-medium text-white">{{ element.patient_code }}</div>
                <div class="text-xs text-text-muted">{{ element.created_at | date:'dd/MM/yyyy HH:mm' }}</div>
              </td>
            </ng-container>

            <!-- Status Column -->
            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef class="text-text-muted font-semibold text-xs tracking-wider uppercase border-b border-border"> Status </th>
              <td mat-cell *matCellDef="let element" class="border-b border-border/50">
                <span class="status-chip" [ngClass]="'status-chip--' + element.status">
                  <span class="dot"></span>
                  {{ getStatusLabel(element.status) }}
                </span>
              </td>
            </ng-container>

            <!-- IGA Column -->
            <ng-container matColumnDef="ira">
              <th mat-header-cell *matHeaderCellDef class="text-text-muted font-semibold text-xs tracking-wider uppercase border-b border-border"> IGA </th>
              <td mat-cell *matCellDef="let element" class="border-b border-border/50">
                @if (element.ira_score !== null) {
                  <span class="ira-badge" [ngClass]="'ira-badge--' + element.ira_level">
                    {{ element.ira_score | number:'1.1-1' }}
                  </span>
                } @else {
                  <span class="text-text-subtle text-sm">-</span>
                }
              </td>
            </ng-container>

            <!-- Actions Column -->
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef class="text-text-muted font-semibold text-xs tracking-wider uppercase border-b border-border text-right"> </th>
              <td mat-cell *matCellDef="let element" class="border-b border-border/50 text-right">
                <a mat-icon-button color="primary" [routerLink]="['/sessoes', element.id]" matTooltip="Ver Detalhes">
                  <mat-icon>chevron_right</mat-icon>
                </a>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;" class="hover:bg-surface2/50 transition-colors"></tr>
          </table>
        }
      </div>
    </div>
  `,
  styles: [`
    .mat-mdc-table {
      background: transparent !important;
    }
    .mat-mdc-header-cell, .mat-mdc-cell {
      color: inherit;
    }
  `]
})
export class RecentSessionsComponent {
  @Input() sessions: SessionOut[] = [];
  @Input() loading = false;
  
  displayedColumns: string[] = ['patient_code', 'status', 'ira', 'actions'];

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      pending: 'Pendente',
      processing: 'Processando IA',
      completed: 'Concluído',
      error: 'Erro'
    };
    return labels[status] || status;
  }
}
