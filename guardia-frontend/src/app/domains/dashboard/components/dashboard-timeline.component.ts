import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';

export interface TimelineEvent {
  time: string;
  description: string;
  classification: string;
  type: 'positive' | 'neutral' | 'warning' | 'critical';
  technology?: string;
  participantId?: string;
}

@Component({
  selector: 'app-dashboard-timeline',
  standalone: true,
  imports: [CommonModule, MatIconModule, RouterLink],
  template: `
    <div class="glass-card flex flex-col h-full hover:!transform-none">
      <div class="p-5 border-b border-border">
        <h3 class="text-lg font-semibold text-white flex items-center gap-2">
          <mat-icon class="text-primary-400">timeline</mat-icon>
          Timeline da análise
        </h3>
      </div>

      <div class="p-5 flex-1 overflow-y-auto">
        @if (events().length === 0) {
          <div class="h-full flex flex-col items-center justify-center text-text-muted opacity-50 py-8">
            <mat-icon class="!text-4xl mb-2">pending</mat-icon>
            <p class="text-sm">Aguardando dados da análise...</p>
          </div>
        } @else {
          <div class="relative pl-6 ml-1">
            <!-- Vertical line -->
            <div class="absolute left-[5px] top-2 bottom-2 w-0.5 bg-border"></div>

            <div class="flex flex-col gap-5">
              @for (event of events(); track $index) {
                <div class="relative animate-fade-in" [style.animation-delay]="($index * 0.1) + 's'">
                  <!-- Dot -->
                  <div class="absolute -left-[21px] top-1.5 w-3 h-3 rounded-full border-[3px] border-bg"
                    [class]="dotClass(event.type)">
                  </div>

                  <!-- Content -->
                  <div class="flex items-start justify-between gap-3">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-0.5">
                        <span class="text-sm font-semibold text-text-muted font-mono">{{ event.time }}</span>
                        @if (event.participantId) {
                          <span class="text-xs font-bold text-info ml-1 flex items-center gap-1"><mat-icon class="!text-[12px] !w-[12px] !h-[12px]">person</mat-icon> {{ event.participantId }}</span>
                        }
                        @if (event.technology) {
                          <span class="text-[10px] font-medium px-1.5 py-0.5 rounded bg-surface2 text-text-muted border border-border">
                            {{ event.technology }}
                          </span>
                        }
                      </div>
                      <p class="text-sm text-white leading-snug mt-1">{{ event.description }}</p>
                    </div>
                    <span class="flex-shrink-0 text-xs font-medium px-2.5 py-1 rounded-full whitespace-nowrap"
                      [class]="chipClass(event.type)">
                      {{ event.classification }}
                    </span>
                  </div>
                </div>
              }
            </div>
          </div>
        }
      </div>

      <div class="p-4 border-t border-border">
        <a routerLink="/sessoes" class="text-sm font-medium text-primary-400 hover:text-primary-300 hover:underline transition-colors flex items-center gap-1">
          Ver linha do tempo completa
          <mat-icon class="!text-base !w-4 !h-4">arrow_forward</mat-icon>
        </a>
      </div>
    </div>
  `
})
export class DashboardTimelineComponent {
  sessionId = input<number | null>(null);
  rawEvents = input<TimelineEvent[]>([]);

  events = computed(() => {
    const raw = this.rawEvents();
    if (raw.length > 0) return raw;

    // Default mock events when no data
    return [];
  });

  dotClass(type: string): string {
    switch (type) {
      case 'positive': return 'bg-success';
      case 'neutral': return 'bg-primary-400';
      case 'warning': return 'bg-warning';
      case 'critical': return 'bg-danger-500';
      default: return 'bg-text-muted';
    }
  }

  chipClass(type: string): string {
    switch (type) {
      case 'positive': return 'bg-success/15 text-success border border-success/30';
      case 'neutral': return 'bg-primary-500/15 text-primary-400 border border-primary-500/30';
      case 'warning': return 'bg-warning/15 text-warning border border-warning/30';
      case 'critical': return 'bg-danger-500/15 text-danger-500 border border-danger-500/30';
      default: return 'bg-surface2 text-text-muted';
    }
  }
}
