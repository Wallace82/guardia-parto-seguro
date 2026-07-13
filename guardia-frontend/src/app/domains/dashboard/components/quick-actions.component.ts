import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

interface QuickAction {
  icon: string;
  label: string;
  id: string;
}

@Component({
  selector: 'app-quick-actions',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="animate-fade-in" style="animation-delay: 0.35s">
      <h3 class="text-xl font-semibold text-white mb-5 flex items-center gap-2">
        <mat-icon class="text-primary-400">bolt</mat-icon>
        Ações rápidas
      </h3>

      <div class="flex flex-wrap gap-4">
        @for (action of actions; track action.id) {
          <button
            (click)="actionClick.emit(action.id)"
            class="quick-action-btn group">
            <mat-icon class="!text-xl text-text-muted group-hover:text-primary-400 transition-colors">{{ action.icon }}</mat-icon>
            <span class="text-sm font-medium text-text-muted group-hover:text-white transition-colors">{{ action.label }}</span>
          </button>
        }
      </div>
    </div>
  `,
  styles: [`
    .quick-action-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.875rem 1.5rem;
      background: rgba(30, 41, 59, 0.6);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        border-color: rgba(139, 92, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
      }

      &:active {
        transform: translateY(0);
      }
    }
  `]
})
export class QuickActionsComponent {
  sessionId = input<number | null>(null);
  actionClick = output<string>();

  actions: QuickAction[] = [
    { icon: 'videocam', label: 'Ver vídeo ao vivo', id: 'video' },
    { icon: 'description', label: 'Gerar relatório', id: 'report' },
    { icon: 'rate_review', label: 'Avaliar caso', id: 'evaluate' },
    { icon: 'edit_note', label: 'Observação', id: 'note' },
    { icon: 'history', label: 'Histórico do paciente', id: 'history' },
  ];
}
