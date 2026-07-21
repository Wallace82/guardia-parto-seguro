import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-fusion-result',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="glass-card p-6 flex flex-col md:flex-row gap-8 hover:!transform-none">
      
      <!-- Gauge section -->
      <div class="flex-1 flex flex-col items-center justify-center">
        <h3 class="text-sm font-bold text-white mb-6 self-start w-full">Resultado da fusão multimodal</h3>
        
        <div class="relative w-[240px] h-[120px] overflow-hidden mb-4">
          <!-- Semicircle background -->
          <div class="absolute top-0 left-0 w-full h-[240px] rounded-full border-[12px] border-surface2"></div>
          
          <!-- Semicircle progress -->
          <div class="absolute top-0 left-0 w-full h-[240px] rounded-full border-[12px] border-success transition-all duration-1000 ease-out"
            style="clip-path: polygon(0 50%, 100% 50%, 100% 100%, 0 100%); transform-origin: center;"
            [style.transform]="'rotate(' + rotation() + 'deg)'"
            [style.border-color]="riskColor()">
          </div>
          
          <!-- Value -->
          <div class="absolute bottom-0 left-0 w-full text-center pb-2">
            <span class="block text-xs text-text-muted mb-1 uppercase font-semibold tracking-wider">Score de risco</span>
            <span class="block text-5xl font-bold leading-none mb-2" [style.color]="riskColor()">{{ score() }}%</span>
            <span class="block text-sm font-bold" [style.color]="riskColor()">{{ riskLabel() }}</span>
          </div>
        </div>
        
        <div class="w-[240px] flex justify-between text-xs text-text-muted font-mono font-medium">
          <span>0%</span>
          <span>100%</span>
        </div>
      </div>

      <!-- Contributions section -->
      <div class="flex-1">
        <h3 class="text-sm font-bold text-white mb-6">Contribuição das fontes</h3>
        
        <div class="flex flex-col gap-4">
          @for (source of contributions(); track source.label) {
            <div class="flex items-center gap-3 w-full">
              <span class="text-sm text-text-muted min-w-[70px]">{{ source.label }}</span>
              <div class="flex-1 h-2 bg-surface2 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-700 ease-out"
                  [style.width.%]="source.value"
                  [style.background]="source.color">
                </div>
              </div>
              <span class="text-sm font-semibold min-w-[36px] text-right" [style.color]="source.color">{{ source.value }}%</span>
            </div>
          }
        </div>
      </div>
      
    </div>
  `
})
export class FusionResultComponent {
  score = input<number>(0);
  scoreVideo = input<number | null | undefined>(null);
  scoreAudio = input<number | null | undefined>(null);
  scoreDocument = input<number | null | undefined>(null);
  scoreNotes = input<number | null | undefined>(null);
  
  riskLabel = computed(() => {
    const s = this.score();
    if (s <= 30) return 'Baixo risco';
    if (s <= 60) return 'Risco moderado';
    return 'Risco crítico';
  });

  riskColor = computed(() => {
    const s = this.score();
    if (s <= 30) return '#16A34A';
    if (s <= 60) return '#EAB308';
    return '#DC2626';
  });

  rotation = computed(() => {
    const s = Math.min(Math.max(this.score(), 0), 100);
    return -180 + (s * 1.8);
  });

  contributions = computed(() => {
    const hasVideo = this.scoreVideo() !== null && this.scoreVideo() !== undefined;
    const hasAudio = this.scoreAudio() !== null && this.scoreAudio() !== undefined;
    const hasDoc = this.scoreDocument() !== null && this.scoreDocument() !== undefined;
    const hasNotes = this.scoreNotes() !== null && this.scoreNotes() !== undefined;

    return [
      { label: 'Vídeo (35%)', value: hasVideo ? 35 : 0, color: hasVideo ? '#2563EB' : '#4b5563' },
      { label: 'Áudio (30%)', value: hasAudio ? 30 : 0, color: hasAudio ? '#8B5CF6' : '#4b5563' },
      { label: 'Documentos (20%)', value: hasDoc ? 20 : 0, color: hasDoc ? '#EAB308' : '#4b5563' },
      { label: 'Anotações (15%)', value: hasNotes ? 15 : 0, color: hasNotes ? '#14B8A6' : '#4b5563' }
    ];
  });
}
