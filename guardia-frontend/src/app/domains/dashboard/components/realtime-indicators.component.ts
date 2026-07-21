import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { CircularGaugeComponent } from '../../../shared/components/circular-gauge.component';

interface IndicatorData {
  icon: string;
  iconColor: string;
  title: string;
  subtitle: string;
  value: number;
  level: string;
  description: string;
  color: string;
}

@Component({
  selector: 'app-realtime-indicators',
  standalone: true,
  imports: [CommonModule, MatIconModule, CircularGaugeComponent],
  template: `
    <div class="mb-8 animate-fade-in" style="animation-delay: 0.15s">
      <h3 class="text-xl font-semibold text-white mb-5 flex items-center gap-2">
        <mat-icon class="text-primary-400">monitoring</mat-icon>
        Indicadores em tempo real
      </h3>

      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        @for (ind of indicators(); track ind.title) {
          <div class="glass-card p-5 flex flex-col items-center text-center gap-3 hover:!transform-none">
            <!-- Icon badge + title -->
            <div class="flex items-center gap-2 self-start w-full">
              <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm"
                [style.background]="ind.iconColor + '1a'"
                [style.color]="ind.iconColor">
                <mat-icon class="!text-lg !w-[18px] !h-[18px]">{{ ind.icon }}</mat-icon>
              </div>
              <div class="text-left">
                <span class="block text-sm font-semibold text-white leading-tight">{{ ind.title }}</span>
                <span class="block text-xs text-text-muted leading-tight">{{ ind.subtitle }}</span>
              </div>
            </div>

            <!-- Gauge -->
            <app-circular-gauge
              [value]="ind.value"
              [color]="ind.color"
              [size]="110"
            />

            <!-- Level + description -->
            <div>
              <span class="block text-sm font-bold" [style.color]="ind.color">{{ ind.level }}</span>
              <span class="block text-xs text-text-subtle mt-0.5">{{ ind.description }}</span>
            </div>
          </div>
        }
      </div>
    </div>
  `
})
export class RealtimeIndicatorsComponent {
  // Scores from session analysis (0-100)
  scoreVideo = input<number | null>(null);
  scoreAudio = input<number | null>(null);
  scoreDocument = input<number | null>(null);
  iraScore = input<number | null>(null);
  
  // Real specific AI components
  emotionScore = input<number | null>(null);
  poseScore = input<number | null>(null);
  commScore = input<number | null>(null);

  indicators = computed<IndicatorData[]>(() => {
    const video = this.scoreVideo();
    const audio = this.scoreAudio();
    const doc = this.scoreDocument();
    
    // Check if we have detailed analysis available
    const hasEmotion = this.emotionScore() !== null && this.emotionScore() !== undefined;
    const hasPose = this.poseScore() !== null && this.poseScore() !== undefined;
    const hasComm = this.commScore() !== null && this.commScore() !== undefined;

    const hasVideo = video !== null && video !== undefined;
    const hasAudio = audio !== null && audio !== undefined;
    const hasDoc = doc !== null && doc !== undefined;

    // Use detailed scores if available, otherwise fallback to the old calculation or 0
    let emotionalValue = 0;
    if (hasEmotion) {
       emotionalValue = Math.round(100 - this.emotionScore()!);
    } else if (hasVideo) {
       emotionalValue = Math.round(100 - video!);
    }
    
    let bodyValue = 0;
    if (hasPose) {
       bodyValue = Math.round(100 - this.poseScore()!);
    } else if (hasVideo) {
       bodyValue = Math.round(100 - video! * 0.7);
    }

    let commValue = 0;
    if (hasComm) {
       commValue = this.commScore()!;
    } else if (hasDoc) {
       commValue = Math.round(100 - doc!);
    } else if (hasAudio) {
       commValue = Math.round(100 - audio!);
    }

    const anxietyValue = hasAudio ? Math.round(audio!) : 0;
    
    const commIsActive = hasComm || hasDoc || hasAudio;

    return [
      {
        icon: 'psychology',
        iconColor: '#8B5CF6',
        title: 'Estado emocional',
        subtitle: 'Confiança',
        value: emotionalValue,
        level: (hasEmotion || hasVideo) ? this.getPositiveLevel(emotionalValue) : 'Aguardando',
        description: (hasEmotion || hasVideo) ? this.getPositiveDescription(emotionalValue, 'emocional') : 'Sem dados de vídeo',
        color: (hasEmotion || hasVideo) ? this.getPositiveColor(emotionalValue) : '#4b5563',
      },
      {
        icon: 'forum',
        iconColor: '#10B981',
        title: 'Comunicação',
        subtitle: 'Humanizada',
        value: commValue,
        level: commIsActive ? this.getPositiveLevel(commValue) : 'Aguardando',
        description: commIsActive ? this.getPositiveDescription(commValue, 'comunicação') : 'Sem dados textuais/áudio',
        color: commIsActive ? this.getPositiveColor(commValue) : '#4b5563',
      },
      {
        icon: 'accessibility_new',
        iconColor: '#3B82F6',
        title: 'Linguagem corporal',
        subtitle: 'Postura positiva',
        value: bodyValue,
        level: (hasPose || hasVideo) ? this.getPositiveLevel(bodyValue) : 'Aguardando',
        description: (hasPose || hasVideo) ? this.getPositiveDescription(bodyValue, 'corporal') : 'Sem dados de vídeo',
        color: (hasPose || hasVideo) ? this.getPositiveColor(bodyValue) : '#4b5563',
      },
      {
        icon: 'mic',
        iconColor: '#F59E0B',
        title: 'Análise vocal',
        subtitle: 'Nível de ansiedade',
        value: anxietyValue,
        level: hasAudio ? this.getRiskLevel(anxietyValue) : 'Aguardando',
        description: hasAudio ? this.getRiskDescription(anxietyValue) : 'Sem dados de áudio',
        color: hasAudio ? this.getRiskColor(anxietyValue) : '#4b5563',
      },
    ];
  });

  private getPositiveLevel(value: number): string {
    if (value >= 85) return 'Excelente';
    if (value >= 70) return 'Bom';
    if (value >= 50) return 'Alto';
    if (value >= 30) return 'Moderado';
    return 'Baixo';
  }

  private getPositiveColor(value: number): string {
    if (value >= 70) return '#10B981';
    if (value >= 40) return '#F59E0B';
    return '#EF4444';
  }

  private getPositiveDescription(value: number, type: string): string {
    if (type === 'emocional') {
      if (value >= 70) return 'Estável nas últimas 2h';
      if (value >= 40) return 'Variações moderadas';
      return 'Instabilidade emocional';
    }
    if (type === 'comunicação') {
      if (value >= 70) return 'Interações positivas';
      if (value >= 40) return 'Comunicação regular';
      return 'Comunicação deficiente';
    }
    if (value >= 70) return 'Postura relaxada';
    if (value >= 40) return 'Postura tensa';
    return 'Sinais de desconforto';
  }

  private getRiskLevel(value: number): string {
    if (value <= 30) return 'Baixo';
    if (value <= 60) return 'Moderado';
    return 'Alto';
  }

  private getRiskColor(value: number): string {
    if (value <= 30) return '#10B981';
    if (value <= 60) return '#F59E0B';
    return '#EF4444';
  }

  private getRiskDescription(value: number): string {
    if (value <= 30) return 'Voz calma e estável';
    if (value <= 60) return 'Leve tensão vocal';
    return 'Ansiedade elevada';
  }
}
