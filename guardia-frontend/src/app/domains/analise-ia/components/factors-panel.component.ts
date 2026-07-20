import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-factors-panel',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="glass-card p-6 hover:!transform-none">
      <h3 class="text-sm font-bold text-white mb-6">Principais fatores identificados</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <!-- Fatores positivos -->
        <div class="flex flex-col">
          <h4 class="text-sm font-semibold text-success mb-4 flex items-center gap-2">
            <mat-icon class="!text-lg !w-5 !h-5">thumb_up</mat-icon> Fatores positivos
          </h4>
          <div class="flex flex-col gap-3 max-h-[320px] overflow-y-auto pr-2 custom-scrollbar">
            @if (factors()?.positive?.length) {
              @for (factor of factors()?.positive; track factor) {
                <div class="flex items-start gap-3 bg-success/5 border border-success/10 rounded-lg p-3 hover:bg-success/10 transition-colors">
                  <mat-icon class="text-success !text-[18px] !w-[18px] !h-[18px] mt-0.5 shrink-0">check_circle</mat-icon>
                  <div class="flex flex-col gap-1">
                    @if (parseFactor(factor).source) {
                      <span class="text-[10px] uppercase font-bold px-2 py-0.5 bg-success/20 text-success rounded-full w-fit tracking-wider">
                        {{ parseFactor(factor).source }}
                      </span>
                    }
                    <span class="text-sm text-success font-medium leading-snug">{{ parseFactor(factor).text }}</span>
                  </div>
                </div>
              }
            } @else {
              <div class="flex items-start gap-3 bg-surface2/50 border border-border rounded-lg p-3">
                <span class="text-sm text-text-muted font-medium leading-snug">Nenhum fator positivo identificado.</span>
              </div>
            }
          </div>
        </div>

        <!-- Fatores de atenção -->
        <div class="flex flex-col">
          <h4 class="text-sm font-semibold text-warning mb-4 flex items-center gap-2">
            <mat-icon class="!text-lg !w-5 !h-5">warning</mat-icon> Fatores de atenção
          </h4>
          <div class="flex flex-col gap-3 max-h-[320px] overflow-y-auto pr-2 custom-scrollbar">
            @if (factors()?.attention?.length) {
              @for (factor of factors()?.attention; track factor) {
                <div class="flex items-start gap-3 bg-warning/5 border border-warning/10 rounded-lg p-3 hover:bg-warning/10 transition-colors">
                  <mat-icon class="text-warning !text-[18px] !w-[18px] !h-[18px] mt-0.5 shrink-0">priority_high</mat-icon>
                  <div class="flex flex-col gap-1.5">
                    @if (parseFactor(factor).source) {
                      <span class="text-[10px] uppercase font-bold px-2 py-0.5 bg-warning/20 text-warning rounded-full w-fit tracking-wider">
                        {{ parseFactor(factor).source }}
                      </span>
                    }
                    <span class="text-sm text-warning/90 font-medium leading-snug">{{ parseFactor(factor).text }}</span>
                  </div>
                </div>
              }
            } @else {
              <div class="flex items-start gap-3 bg-surface2/50 border border-border rounded-lg p-3">
                <mat-icon class="text-text-muted !text-[18px] !w-[18px] !h-[18px] mt-0.5">check</mat-icon>
                <span class="text-sm text-text-muted font-medium leading-snug">Nenhum fator de atenção identificado.</span>
              </div>
            }
          </div>
        </div>

        <!-- Recomendação da IA -->
        <div class="flex flex-col h-full">
          <h4 class="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <mat-icon class="!text-lg !w-5 !h-5" [ngClass]="iconColorClass()">lightbulb</mat-icon> Recomendação da IA
          </h4>
          <div class="flex flex-col items-center justify-center text-center bg-gradient-to-b to-transparent border rounded-xl p-6 h-[320px] relative overflow-hidden group transition-colors" [ngClass]="bgGradientClass()">
            <!-- Glow effect -->
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-32 rounded-full blur-3xl transition-all" [ngClass]="glowClass()"></div>
            
            <div class="w-16 h-16 rounded-full border flex items-center justify-center mb-6 relative z-10" [ngClass]="iconBgClass()">
              <mat-icon class="!text-4xl" [ngClass]="iconColorClass()">{{ recIcon() }}</mat-icon>
            </div>
            
            <p class="text-base font-semibold text-white mb-4 relative z-10 leading-relaxed">{{ factors()?.recommendation || 'Sem recomendações no momento.' }}</p>
            <div class="inline-flex items-center gap-1.5 px-3 py-1 bg-surface2 rounded-full border border-border relative z-10">
              <mat-icon class="text-text-muted !text-[14px] !w-[14px] !h-[14px]">psychology</mat-icon>
              <p class="text-xs text-text-muted font-medium uppercase tracking-wider">Avaliação humana necessária</p>
            </div>
          </div>
        </div>
        
      </div>
    </div>
  `,
  styles: [`
    .custom-scrollbar::-webkit-scrollbar {
      width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.2);
      border-radius: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  `]
})
export class FactorsPanelComponent {
  factors = input<any>();
  riskLevel = input<string | null | undefined>();

  isCritical = computed(() => this.riskLevel() === 'critico');
  isWarning = computed(() => this.riskLevel() === 'moderado');

  iconColorClass = computed(() => {
    if (this.isCritical()) return 'text-danger-500';
    if (this.isWarning()) return 'text-warning';
    return 'text-primary-400';
  });

  bgGradientClass = computed(() => {
    if (this.isCritical()) return 'from-danger-500/10 border-danger-500/30 hover:border-danger-500/50';
    if (this.isWarning()) return 'from-warning/10 border-warning/30 hover:border-warning/50';
    return 'from-primary-500/10 border-primary-500/30 hover:border-primary-500/50';
  });

  glowClass = computed(() => {
    if (this.isCritical()) return 'bg-danger-500/20 group-hover:bg-danger-500/30';
    if (this.isWarning()) return 'bg-warning/20 group-hover:bg-warning/30';
    return 'bg-primary-500/20 group-hover:bg-primary-500/30';
  });

  iconBgClass = computed(() => {
    if (this.isCritical()) return 'bg-danger-500/20 border-danger-500/30 shadow-[0_0_15px_rgba(239,68,68,0.3)]';
    if (this.isWarning()) return 'bg-warning/20 border-warning/30 shadow-[0_0_15px_rgba(245,158,11,0.3)]';
    return 'bg-primary-500/20 border-primary-500/30 shadow-[0_0_15px_rgba(var(--primary-500),0.3)]';
  });
  
  recIcon = computed(() => {
    if (this.isCritical()) return 'emergency';
    if (this.isWarning()) return 'warning';
    return 'verified_user';
  });

  parseFactor(text: string) {
    if (!text) return { source: null, text: '' };
    const match = text.match(/^(.*?):\s*(.*)$/);
    if (match) {
      return { source: match[1].trim(), text: match[2].trim() };
    }
    return { source: null, text: text };
  }
}
