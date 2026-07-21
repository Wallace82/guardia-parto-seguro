import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-emotion-meter',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="flex items-center gap-3 w-full">
      <span class="text-sm text-text-muted min-w-[90px]">{{ label() }}</span>
      <div class="flex-1 h-2.5 bg-surface2 rounded-full overflow-hidden">
        <div class="h-full rounded-full transition-all duration-700 ease-out"
          [style.width.%]="value()"
          [style.background]="barColor()">
        </div>
      </div>
      <span class="text-sm font-semibold min-w-[40px] text-right" [style.color]="barColor()">{{ value() }}%</span>
    </div>
  `
})
export class EmotionMeterComponent {
  label = input<string>('');
  value = input<number>(0);
  color = input<string>('');

  barColor = computed(() => {
    if (this.color()) return this.color();
    const v = this.value();
    if (v >= 60) return '#16A34A';
    if (v >= 30) return '#EAB308';
    return '#DC2626';
  });
}
