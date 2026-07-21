import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-circular-gauge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="circular-gauge" [style.width.px]="size()" [style.height.px]="size()">
      <svg [attr.viewBox]="'0 0 ' + size() + ' ' + size()">
        <!-- Background arc -->
        <circle
          [attr.cx]="center()"
          [attr.cy]="center()"
          [attr.r]="radius()"
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          [attr.stroke-width]="strokeWidth()"
          stroke-linecap="round"
        />
        <!-- Progress arc -->
        <circle
          [attr.cx]="center()"
          [attr.cy]="center()"
          [attr.r]="radius()"
          fill="none"
          [attr.stroke]="gaugeColor()"
          [attr.stroke-width]="strokeWidth()"
          stroke-linecap="round"
          [attr.stroke-dasharray]="circumference()"
          [attr.stroke-dashoffset]="dashOffset()"
          class="gauge-progress"
          [attr.transform]="'rotate(-90, ' + center() + ', ' + center() + ')'"
        />
      </svg>
      <div class="gauge-value">
        <span class="gauge-percent" [style.color]="gaugeColor()">{{ value() }}%</span>
      </div>
    </div>
  `,
  styles: [`
    :host { display: inline-block; }

    .circular-gauge {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    svg {
      position: absolute;
      inset: 0;
    }

    .gauge-progress {
      transition: stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .gauge-value {
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .gauge-percent {
      font-size: 1.5rem;
      font-weight: 700;
      line-height: 1;
    }
  `]
})
export class CircularGaugeComponent {
  value = input<number>(0);
  color = input<string>('#10B981');
  size = input<number>(120);

  center = computed(() => this.size() / 2);
  radius = computed(() => (this.size() - this.strokeWidth()) / 2 - 2);
  strokeWidth = computed(() => Math.max(8, this.size() * 0.08));
  circumference = computed(() => 2 * Math.PI * this.radius());
  dashOffset = computed(() => {
    const clamped = Math.max(0, Math.min(100, this.value()));
    return this.circumference() * (1 - clamped / 100);
  });
  gaugeColor = computed(() => this.color());
}
