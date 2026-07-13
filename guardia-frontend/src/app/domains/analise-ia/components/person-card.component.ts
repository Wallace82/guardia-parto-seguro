import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-person-card',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="flex items-center gap-3 py-2">
      <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm"
        [style.background]="avatarBg()">
        {{ initials() }}
      </div>
      <div class="flex-1 min-w-0">
        <span class="block text-sm font-medium text-white truncate">{{ name() }}</span>
        <span class="inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full mt-0.5"
          [class]="roleBadgeClass()">
          {{ roleLabel() }}
        </span>
      </div>
    </div>
  `
})
export class PersonCardComponent {
  name = input<string>('');
  role = input<'paciente' | 'medico' | 'enfermeiro' | 'acompanhante'>('paciente');

  initials = () => {
    const n = this.name();
    if (!n) return '?';
    const parts = n.split(' ');
    return parts.length >= 2 ? `${parts[0][0]}${parts[1][0]}`.toUpperCase() : n.substring(0, 2).toUpperCase();
  };

  avatarBg = () => {
    switch (this.role()) {
      case 'paciente': return '#2563EB';
      case 'medico': return '#16A34A';
      case 'enfermeiro': return '#7c3aed';
      case 'acompanhante': return '#64748B';
    }
  };

  roleLabel = () => {
    switch (this.role()) {
      case 'paciente': return 'Paciente';
      case 'medico': return 'Médico';
      case 'enfermeiro': return 'Enfermeiro';
      case 'acompanhante': return 'Acompanhante';
    }
  };

  roleBadgeClass = () => {
    switch (this.role()) {
      case 'paciente': return 'bg-primary-500/20 text-primary-400';
      case 'medico': return 'bg-success/20 text-success';
      case 'enfermeiro': return 'bg-purple-500/20 text-purple-400';
      case 'acompanhante': return 'bg-surface2 text-text-muted';
    }
  };
}
