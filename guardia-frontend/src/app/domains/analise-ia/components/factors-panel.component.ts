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
          <h4 class="text-sm font-semibold text-success mb-4">Fatores positivos</h4>
          <div class="flex flex-col gap-3">
            @if (factors()?.positive?.length) {
              @for (factor of factors()?.positive; track factor) {
                <div class="flex items-start gap-3 bg-success/5 border border-success/10 rounded-lg p-3">
                  <mat-icon class="text-success !text-[18px] !w-[18px] !h-[18px] mt-0.5">check_circle</mat-icon>
                  <span class="text-sm text-success font-medium leading-snug">{{ factor }}</span>
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
          <h4 class="text-sm font-semibold text-warning mb-4">Fatores de atenção</h4>
          <div class="flex flex-col gap-3">
            @if (factors()?.attention?.length) {
              @for (factor of factors()?.attention; track factor) {
                <div class="flex items-start gap-3 bg-warning/5 border border-warning/10 rounded-lg p-3">
                  <mat-icon class="text-warning !text-[18px] !w-[18px] !h-[18px] mt-0.5">warning</mat-icon>
                  <span class="text-sm text-warning font-medium leading-snug">{{ factor }}</span>
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
        <div class="flex flex-col">
          <h4 class="text-sm font-semibold text-white mb-4">Recomendação da IA</h4>
          <div class="flex flex-col items-center text-center bg-primary-500/10 border border-primary-500/30 rounded-xl p-5 h-full">
            <div class="w-14 h-14 rounded-full bg-success/20 flex items-center justify-center mb-4">
              <mat-icon class="text-success !text-3xl">verified_user</mat-icon>
            </div>
            <p class="text-sm font-semibold text-white mb-3">{{ factors()?.recommendation || 'Sem recomendações no momento.' }}</p>
            <p class="text-xs text-text-muted font-medium">Avaliação humana recomendada.</p>
          </div>
        </div>
        
      </div>
    </div>
  `
})
export class FactorsPanelComponent {
  factors = input<any>();
}
